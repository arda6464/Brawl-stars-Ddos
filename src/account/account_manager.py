import random
import string
import uuid
from ..utils.writer import Writer

class AccountManager:
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
        self.device_id = self.generate_device_id()
        self.device_model = random.choice(self.DEVICE_MODELS)
        self.os_version = random.choice(self.OS_VERSIONS)
        self.android_id = self.generate_android_id() if "Android" in self.os_version else None
        
    def generate_device_id(self):
        """Gerçekçi bir device ID oluşturur"""
        return str(uuid.uuid4()).upper()
        
    def generate_android_id(self):
        """Android için benzersiz ID oluşturur"""
        hex_chars = string.hexdigits[:-6]  # a-f, 0-9
        return ''.join(random.choice(hex_chars) for _ in range(16)).lower()
    
    def create_account_packet(self, version: int):
        """Yeni hesap oluşturma paketi oluşturur"""
        w = Writer()
        username = f"Player{random.randint(1000, 9999)}"
        message = b''
        
        # Temel bilgiler
        message += w.writeInt(0)
        message += w.writeInt(0)
        message += w.writeStringLength(username)
        message += w.writeString("")
        message += w.writeInt(version)
        message += w.writeInt(version)
        message += w.writeInt(165)
        
        # Cihaz bilgileri
        message += w.writeString(self.device_id)
        message += w.writeString(self.device_model)
        message += w.writeString(self.os_version)
        
        # Ek bilgiler
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
        
        return self._create_header(10101, message)
    
    def _create_header(self, message_id, data):
        """Paket başlığı oluşturur"""
        w = Writer()
        header = b''
        header += w.writeShort(message_id)
        header += len(data).to_bytes(3, 'big')
        header += w.writeShort(0)
        header += data
        return header 