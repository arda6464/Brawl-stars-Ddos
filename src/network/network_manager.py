import socket
import threading
import time
from datetime import datetime
from ..utils.writer import Writer

class NetworkManager:
    def __init__(self, host="game.clashroyaleapp.com", port=9339):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.lock = threading.Lock()
        self.writer = Writer()
    
    def connect(self, proxy=None):
        """Sunucuya bağlanır"""
        try:
            if proxy:
                proxy_host, proxy_port = proxy.split(':')
                proxy_port = int(proxy_port)
                
                # Proxy üzerinden bağlantı
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((proxy_host, proxy_port))
                
                # CONNECT isteği gönder
                connect_request = f"CONNECT {self.host}:{self.port} HTTP/1.1\r\n"
                connect_request += f"Host: {self.host}:{self.port}\r\n"
                connect_request += "Proxy-Connection: Keep-Alive\r\n\r\n"
                
                self.socket.send(connect_request.encode())
                response = self.socket.recv(4096)
                
                if not response.startswith(b"HTTP/1.1 200"):
                    raise Exception("Proxy connection failed")
            else:
                # Direkt bağlantı
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
            
            self.connected = True
            return True
            
        except Exception as e:
            self.connected = False
            if self.socket:
                self.socket.close()
            return False
    
    def disconnect(self):
        """Bağlantıyı kapatır"""
        with self.lock:
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                finally:
                    self.socket = None
                    self.connected = False
    
    def send_packet(self, packet):
        """Paket gönderir"""
        with self.lock:
            if not self.connected or not self.socket:
                return False
            
            try:
                self.socket.send(packet)
                return True
            except:
                self.connected = False
                return False
    
    def receive_packet(self, timeout=5):
        """Paket alır"""
        with self.lock:
            if not self.connected or not self.socket:
                return None
            
            try:
                self.socket.settimeout(timeout)
                data = self.socket.recv(4096)
                if not data:
                    self.connected = False
                    return None
                return data
            except socket.timeout:
                return None
            except:
                self.connected = False
                return None
    
    def send_hello_packet(self, version: int):
        """Hello paketi gönderir"""
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
        message += w.writeString("en")
        message += w.writeString("10")
        message += w.writeInt(0)
        message += w.writeVInt(0)
        message += w.writeString("BRUH")
        message += w.writeVInt(0)
        message += w.writeInt(0)
        message += w.writeInt(0)
        message += w.writeString("")
        
        return self.send_packet(self._create_header(10101, message))
    
    def _create_header(self, message_id, data):
        """Paket başlığı oluşturur"""
        w = Writer()
        header = b''
        header += w.writeShort(message_id)
        header += len(data).to_bytes(3, 'big')
        header += w.writeShort(0)
        header += data
        return header 