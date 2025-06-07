import struct
import random
import string
import uuid
from utils import Writer

class login:
    # Cihaz modelleri, Android ve iOS cihazlar
    DEVICE_MODELS = [
        "iPhone8,1", "iPhone8,2", "iPhone9,1", "iPhone9,3", "iPhone10,1", "iPhone11,8", "iPhone12,1", "iPhone13,1",
        "iPad6,11", "iPad7,5", "iPad8,1", "iPad8,10",
        "SM-G930F", "SM-G950F", "SM-G965F", "SM-G973F", "SM-G975F", "SM-G980F", "SM-G990F", "SM-S901E",
        "SAMSUNG-SM-G935A", "SAMSUNG-SM-G955U", "SM-N950F", "SM-N960F", "SM-N975F", "SM-N980F", "SM-T830", "SM-T970"
    ]
    
    # İşletim sistemi sürümleri
    OS_VERSIONS = [
        "iOS 13.5.1", "iOS 14.2", "iOS 14.5", "iOS 15.0.1", "iOS 15.2.1", "iOS 15.4", "iOS 16.0", "iOS 16.1.1",
        "Android 9", "Android 10", "Android 11", "Android 12", "Android 13"
    ]
    
    def __init__(self):
        # Her login nesnesi için rastgele cihaz bilgileri oluştur
        self.device_id = self.generate_device_id()
        self.device_model = random.choice(self.DEVICE_MODELS)
        self.os_version = random.choice(self.OS_VERSIONS)
        self.android_id = self.generate_android_id() if "Android" in self.os_version else None
        
    def generate_device_id(self):
        """Gerçekçi bir device ID oluşturur"""
        # UUID tabanlı device ID
        return str(uuid.uuid4()).upper()
        
    def generate_android_id(self):
        """Android için benzersiz ID oluşturur"""
        # 16 karakterli hexadecimal bir değer
        hex_chars = string.hexdigits[:-6]  # a-f, 0-9
        return ''.join(random.choice(hex_chars) for _ in range(16)).lower()
    
    def header(self, message_id, data):
        w = Writer()
        header = b''
        header += w.writeShort(message_id)
        header += len(data).to_bytes(3, 'big')
        header += w.writeShort(0)
        header += data
        return header

    def header_with_id(self, msg_id, data):  
        header = b""  
        header += struct.pack(">H", msg_id)  
        header += len(data).to_bytes(3, "big")  
        header += struct.pack(">H", 0)  
        header += data  
        return header  

    def send_hello(self, version: int):  
        w = Writer()  
        message = b''  
        message += w.writeInt(0)  
        message += w.writeInt(0)  
        message += w.writeStringLength("")  
        message += w.writeString("")  
        message += w.writeInt(version)  
        message += w.writeInt(version)  
        message += w.writeInt(165)  
        message += w.writeStringLength("")  
        message += w.writeString("")  
        message += w.writeString("")  
        message += w.writeVInt(2)  
        message += w.writeVInt(0)  
        message += w.writeString("ar")  
        message += w.writeString("10")  
        message += w.writeInt(0)  
        message += w.writeVInt(0)  
        message += w.writeString("BRUH")  
        message += w.writeVInt(0)  
        message += w.writeInt(0)  
        message += w.writeInt(0)  
        message += w.writeString("")  
        return self.header(10101, message)  

    def create_account(self, version: int):  
        w = Writer()  
        username = f"Player{random.randint(1000, 9999)}"  
        message = b''  
        message += w.writeInt(0)  
        message += w.writeInt(0)  
        message += w.writeStringLength(username)  
        message += w.writeString("")  
        message += w.writeInt(version)  
        message += w.writeInt(version)  
        message += w.writeInt(165)  
        
        # Device bilgilerini ekle
        device_info = w.writeString(self.device_id)  # Device ID
        message += device_info
        
        model_info = w.writeString(self.device_model)  # Device Model
        message += model_info
        
        os_info = w.writeString(self.os_version)  # OS Version
        message += os_info
        
        message += w.writeVInt(2)  
        message += w.writeVInt(0)  
        message += w.writeString("en")  
        message += w.writeString("10")  
        message += w.writeInt(0)  
        message += w.writeVInt(0)  
        message += w.writeString("BRUH")  
        message += w.writeVInt(0)  
        message += w.writeInt(0)  
        message += w.writeInt(0)  
        message += w.writeString("")  
        return self.header(10101, message)  

    def create_club(self, club_name: str, description: str):  
        w = Writer()  
        
        # String verilerini direkt buffer'a ekliyoruz
        name_data = w.writeString(club_name)
        w.buffer += name_data
        
        desc_data = w.writeString(description)
        w.buffer += desc_data

        # Diğer özellikleri buffer'a ekliyoruz
        w.buffer += w.writeVInt(1)                # Badge Identifier  
        w.buffer += w.writeVInt(1)                # Badge ID  
        w.buffer += w.writeVInt(2)                # Club type (Only creator can join)
        w.buffer += w.writeVInt(0)                # Trophy required (0 trophies needed)
        w.buffer += w.writeVInt(1)                # Family friendly  

        return self.header_with_id(14301, w.buffer)
        
    def join_club(self, club_high_id: int, club_low_id: int):
        """Kulübe ID ile katılma paketi oluşturur"""
        w = Writer()
        
        # Club ID'leri yazıyoruz
        w.buffer += w.writeInt(club_high_id)  # Club High ID
        w.buffer += w.writeInt(club_low_id)   # Club Low ID
        
        return self.header_with_id(14306, w.buffer)  # 14306: Join Alliance Message ID
        
    def join_club_by_tag(self, club_tag: str):
        """Kulübe etiket (#QO8JSL3 gibi) ile katılma paketi oluşturur"""
        w = Writer()
        
        # # işaretini kaldır (eğer varsa)
        if club_tag.startswith('#'):
            club_tag = club_tag[1:]
            
        # Kulüp etiketini yaz
        tag_data = w.writeString(club_tag)
        w.buffer += tag_data
        
        return self.header_with_id(14303, w.buffer)  # 14303: Etiket ile kulübe katılma