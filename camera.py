from libs.xbee import Address, FunCode, Message, XBee


def ack(xbee: XBee, message: Message) -> None:
    print("ACK:", message.data)


xbee = XBee(Address.CAMERA_1, "/dev/ttyS0")
xbee.apply_config({
    b"ATAP": b"0",
    b"ATEE": b"1",
    b"ATKY": b"32303032",
    b"ATCH": b"C",
    b"ATID": b"3332",
    b"ATCE": b"0",
    b"ATMY": b"1",
    b"ATDL": b"FFFF",
    b"ATDH": b"0"
})

xbee.bind(FunCode.ACK, ack)
xbee.listen()
