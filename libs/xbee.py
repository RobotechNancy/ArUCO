from __future__ import annotations
import signal, threading

from enum import Enum
from serial import Serial
from types import FrameType
from typing import Optional, Callable


class Address(Enum):
    ROBOT    = 1
    CAMERA_1 = 2
    CAMERA_2 = 3
    CAMERA_3 = 4

class FunCode(Enum):
    ACK = 1


class Message:
    def __init__(self, raw: bytes) -> None:
        self.__raw = raw

    @staticmethod
    def from_response(raw: bytes) -> Optional[Message]:
        if len(raw) < 5: return None
        return Message(raw) if Message.__crc8(raw[:-1]) == raw[-1] else None

    @property
    def dest(self): return self.__raw[0]

    @property
    def src(self): return self.__raw[1]

    @property
    def code(self): return self.__raw[2]

    @property
    def id(self): return self.__raw[3]

    @property
    def data(self): return self.__raw[4:-1]

    @staticmethod
    def __crc8(data: bytes, polynomial: int = 0x07, initial: int = 0xff) -> int:
        crc = initial

        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = ((crc << 1)^polynomial if (crc & 0x80) else (crc << 1)) & 0xff

        return crc

    @staticmethod
    def to_bytes(dest: Address, src: Address, code: FunCode, id: int, data: bytes):
        message = (dest.value.to_bytes(1, "big")
                    + src.value.to_bytes(1, "big")
                    + code.value.to_bytes(1, "big")
                    + id.to_bytes(1, "big") + data)

        return message + Message.__crc8(message).to_bytes(1, "big")


class Request:
    def __init__(self) -> None:
        self.__event = threading.Event()
        self.data: Optional[bytes] = None

    def set_data(self, data: bytes) -> None:
        self.data = data
        self.__event.set()

    def wait(self, timeout: float) -> bool:
        return self.__event.wait(timeout)


class XBee:
    def __init__(self, source: Address, port: str, baudrate: int = 9600) -> None:
        self.__running = True
        self.__ser = Serial(port, baudrate)

        self.__count = 0
        self.__addr = source
        self.__requests: dict[int, Request] = {}
        self.__callbacks: dict[int, Callable[[XBee, Message]]] = {}

        signal.signal(signal.SIGINT, self.__stop)
        signal.signal(signal.SIGTERM, self.__stop)

    def __stop(self, signum: int, frame: Optional[FrameType]) -> None:
        self.__running = False

    def __send_command(self, command: bytes) -> bool:
        self.__ser.write(command)
        return self.__ser.read(3) != b"OK\r"

    def apply_config(self, config: dict[bytes, bytes]) -> None:
        if self.__send_command(b"+++"):
            raise Exception("Couldn't enter command mode")

        for command, value in config.items():
            if self.__send_command(command + b" " + value + b"\r"):
                raise Exception(f"Couldn't set {command} to {value}")

        if self.__send_command(b"ATWR\r"):
            raise Exception("Couldn't write config")

        if self.__send_command(b"ATCN\r"):
            raise Exception("Couldn't leave command mode")

    def bind(self, code: FunCode, callback: Callable[[XBee, Message]]) -> None:
        self.__callbacks[code.value] = callback

    def listen(self) -> None:
        self.__ser.timeout = 1

        while self.__running:
            message = Message.from_response(self.__ser.readline())
            if message is None or message.dest != self.__addr.value: continue

            if callback := self.__callbacks.get(message.code, None):
                threading.Thread(target=callback, args=(self, message)).start()
            elif message.id in self.__requests:
                self.__requests[message.id].set_data(message.data)

    def send(self, address: Address, code: FunCode, data: bytes) -> None:
        self.__ser.write(Message.to_bytes(address, self.__addr, code, self.__count, data))
        self.__count = (self.__count+1) % 255

    def request(self, address: Address, code: FunCode, data: bytes, timeout: float = 3) -> Optional[bytes]:
        request_id = self.__count
        self.__requests[request_id] = Request()

        self.send(address, code, data)
        self.__requests[request_id].wait(timeout)
        return self.__requests.pop(request_id).data

    def reply(self, message: Message, data: bytes) -> None:
        self.__ser.write(Message.to_bytes(
            Address(message.src), self.__addr, FunCode(message.code), message.id, data
        ))
