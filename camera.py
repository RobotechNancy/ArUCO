from libs.xbee import Address, FunCode, Message, XBee


def ack(xbee: XBee, message: Message) -> None:
    print("ACK:", message.data)


xbee = XBee(Address.CAMERA_1, "/dev/ttyUSB0")
xbee.apply_config({
    b"ATAP": b"\x00",
    b"ATCH": b"\xba",
    b"ATID": b"\xde",
    b"ATCE": b"\x00",
    b"ATDL": b'\xff\xff',
    b"ATDH": b"\x00",
    b"ATRN": b"\x01"
})

xbee.bind(FunCode.ACK, ack)
xbee.listen()
