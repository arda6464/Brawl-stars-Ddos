class Writer:
    def __init__(self):
        self.buffer = b''
    
    def writeInt(self, value):
        return value.to_bytes(4, 'big')
    
    def writeShort(self, value):
        return value.to_bytes(2, 'big')
    
    def writeString(self, value):
        if not value:
            return b'\x00'
        encoded = value.encode('utf-8')
        return len(encoded).to_bytes(2, 'big') + encoded
    
    def writeStringLength(self, value):
        if not value:
            return b'\x00'
        return len(value.encode('utf-8')).to_bytes(2, 'big')
    
    def writeVInt(self, value):
        if value < 0:
            value = (value & 0x7fffffff) | 0x80000000
        result = bytearray()
        while True:
            byte = value & 0x7f
            value >>= 7
            if value:
                byte |= 0x80
            result.append(byte)
            if not value:
                break
        return bytes(result) 