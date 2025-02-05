from libs.xbee import Address, FunCode, Message, XBee


def ack(xbee: XBee, message: Message) -> None:
    print("ACK:", message.data)


xbee = XBee(Address.CAMERA_1, "/dev/ttyS0", debug=True)
xbee.apply_config({
    b"ATAP": b"0",
    b"ATCH": b"D",
    b"ATID": b"3c39",
    b"ATCE": b"0",
    b"ATMY": b"2",
    b"ATDL": b"FFFF",
    b"ATDH": b"0",
    b"ATRN": b"1"
})

xbee.bind(FunCode.ACK, ack)
xbee.listen()
