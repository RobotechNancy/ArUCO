from libs.xbee import Address, FunCode, XBee

# Maître down => esclaves sans réponse depuis plus d'une seconde (comparer timestamp)

xbee = XBee(Address.ROBOT, "/dev/ttyUSB0")
xbee.apply_config({
    b"ATAP": b"\x00",
    b"ATCH": b"\xba",
    b"ATID": b"\xde",
    b"ATCE": b"\x01",
    b"ATDL": b'\xff\xff',
    b"ATDH": b"\x00",
    b"ATRN": b"\x01"
})

print("Sending")
xbee.send(Address.CAMERA_1, FunCode.ACK, b"HELLO?")
xbee.send(Address.CAMERA_1, FunCode.ACK, b"HELLO?")
