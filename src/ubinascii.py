import binascii


def hexlify(text) -> bytes:
    return binascii.b2a_hex(bytes(text,'utf-8'))
