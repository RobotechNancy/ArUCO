from libs.xbee import Address, FunCode, Message, XBee


def ack(xbee: XBee, message: Message) -> None:
    print("ACK:", message.data)


xbee = XBee(Address.CAMERA_1, "/dev/ttyS0")
xbee.apply_config({
    b"ATAP": b"\x00",
    b"ATCH": b"\x0d",
    b"ATID": b"\x9c\xb3",
    b"ATCE": b"\x00",
    b"ATDL": b'\xff\xff',
    b"ATDH": b"\x00",
    b"ATRN": b"\x01"
})

xbee.bind(FunCode.ACK, ack)
xbee.listen()
