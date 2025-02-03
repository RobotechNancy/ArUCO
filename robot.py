from threading import Thread
from libs.xbee import Address, FunCode, Message, XBee

# Maître down => esclaves sans réponse depuis plus d'une seconde (comparer timestamp)

xbee = XBee(Address.ROBOT, "/dev/ttyUSB0")
xbee.apply_config({
    b"ATAP": b"0",
    b"ATEE": b"1",
    b"ATKY": b"32303032",
    b"ATCH": b"C",
    b"ATID": b"3332",
    b"ATCE": b"1",
    b"ATMY": b"1",
    b"ATDL": b"FFFF",
    b"ATDH": b"0"
})

print("Sending")
xbee.send(Address.CAMERA_1, FunCode.ACK, b"HELLO?")
xbee.send(Address.CAMERA_1, FunCode.ACK, b"HELLO?")
