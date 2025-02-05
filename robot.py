from libs.xbee import Address, FunCode, XBee

# Maître down => esclaves sans réponse depuis plus d'une seconde (comparer timestamp)

xbee = XBee(Address.ROBOT, "/dev/ttyUSB0", debug=True)
xbee.apply_config({
    b"ATAP": b"0",
    b"ATCH": b"D",
    b"ATID": b"3c39",
    b"ATCE": b"1",
    b"ATMY": b"1",
    b"ATDL": b"FFFF",
    b"ATDH": b"0",
    b"ATRN": b"1"
})

xbee.send(Address.CAMERA_1, FunCode.ACK, b"HELLO?")
xbee.send(Address.CAMERA_1, FunCode.ACK, b"HELLO?")
