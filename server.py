import socket
import struct
import threading
import time
import sys

# Renkli çıktı için ANSI renk kodları
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

class DeviceServer:
    def __init__(self, host="87.106.36.114", port=6349):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.connections = 0
        self.device_infos = {}  # {ip: {device_id, model, os, visits}}
        
    def start(self):
        """Sunucuyu başlatır"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            
            self.running = True
            print(f"{Colors.GREEN}[+] Sunucu başlatıldı - {self.host}:{self.port}{Colors.ENDC}")
            print(f"{Colors.YELLOW}[*] Client IP ve Device bilgileri bekleniyor...{Colors.ENDC}")
            
            # Her 30 saniyede bir özet rapor gösteren thread
            threading.Thread(target=self.report_thread, daemon=True).start()
            
            # Ana dinleme döngüsü
            while self.running:
                client_socket, address = self.server_socket.accept()
                client_ip = address[0]
                
                # Yeni bağlantı geldiğinde
                print(f"\n{Colors.CYAN}[*] Yeni bağlantı: {client_ip}{Colors.ENDC}")
                self.connections += 1
                
                # Her bağlantı için yeni thread başlat
                threading.Thread(target=self.handle_client, 
                                args=(client_socket, client_ip), daemon=True).start()
                
        except KeyboardInterrupt:
            print(f"{Colors.YELLOW}[!] Sunucu kapatılıyor (Ctrl+C)...{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}[!] Sunucu hatası: {str(e)}{Colors.ENDC}")
        finally:
            self.stop()
            
    def stop(self):
        """Sunucuyu durdurur"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.show_summary()
        print(f"{Colors.RED}[!] Sunucu kapatıldı.{Colors.ENDC}")
    
    def handle_client(self, client_socket, client_ip):
        """Client bağlantısını işler"""
        try:
            # Veriyi alır
            data = client_socket.recv(4096)
            
            if data:
                # Paketi analiz et
                self.analyze_packet(data, client_ip)
                
                # Basit bir yanıt gönder
                response = b"\x00\x00\x00\x00\x00\x00\x00"
                client_socket.send(response)
        except Exception as e:
            print(f"{Colors.RED}[!] Client hatası ({client_ip}): {str(e)}{Colors.ENDC}")
        finally:
            client_socket.close()
    
    def analyze_packet(self, packet_data, client_ip):
        """Paketi analiz eder ve device bilgilerini çıkarır"""
        try:
            if len(packet_data) < 7:
                print(f"{Colors.RED}[!] Paket çok kısa: {len(packet_data)} byte{Colors.ENDC}")
                return
            
            # Header'ı ayrıştır
            msg_id = struct.unpack(">H", packet_data[0:2])[0]
            length = int.from_bytes(packet_data[2:5], 'big')
            
            print(f"{Colors.YELLOW}[*] Paket: ID={msg_id}, Uzunluk={length} byte{Colors.ENDC}")
            
            # Login paketi (10101) ise device bilgilerini çıkar
            if msg_id == 10101:
                self.extract_device_info(packet_data[7:], client_ip)
            else:
                print(f"{Colors.YELLOW}[*] Login paketi değil (ID: {msg_id}){Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.RED}[!] Paket analiz hatası: {str(e)}{Colors.ENDC}")
    
    def extract_device_info(self, data, client_ip):
        """Paketten device bilgilerini çıkarır"""
        # Metin parçalarını bul
        strings = []
        current_str = b""
        
        for i in range(len(data)):
            if 32 <= data[i] <= 126:  # ASCII yazdırılabilir karakter
                current_str += bytes([data[i]])
            else:
                if len(current_str) >= 3:  # En az 3 karakter olan string'leri kaydet
                    strings.append(current_str.decode('utf-8', errors='ignore'))
                current_str = b""
        
        if current_str and len(current_str) >= 3:
            strings.append(current_str.decode('utf-8', errors='ignore'))
        
        # Device bilgilerini tanımla
        device_id = None
        model = None
        os_version = None
        
        # String'leri tarayarak bilgileri bul
        for s in strings:
            # Device ID formatı UUID olabilir (36 karakter, tireler ile)
            if len(s) > 20 and "-" in s and s.count("-") == 4:
                device_id = s
            # Cihaz modeli
            elif "iPhone" in s or "iPad" in s or "SM-" in s:
                model = s
            # İşletim sistemi
            elif "iOS" in s or "Android" in s:
                os_version = s
        
        # Sonuçları göster ve kaydet
        if device_id or model or os_version:
            print(f"\n{Colors.GREEN}[+] Client Bilgileri:{Colors.ENDC}")
            print(f"  IP          : {client_ip}")
            print(f"  Device ID   : {device_id or 'Bulunamadı'}")
            print(f"  Model       : {model or 'Bulunamadı'}")
            print(f"  İşletim Sis.: {os_version or 'Bulunamadı'}")
            
            # İstatistikleri güncelle
            if client_ip not in self.device_infos:
                self.device_infos[client_ip] = {
                    "device_id": device_id,
                    "model": model,
                    "os": os_version,
                    "visits": 1,
                    "last_seen": time.time()
                }
            else:
                self.device_infos[client_ip]["visits"] += 1
                self.device_infos[client_ip]["last_seen"] = time.time()
                if device_id:
                    self.device_infos[client_ip]["device_id"] = device_id
                if model:
                    self.device_infos[client_ip]["model"] = model
                if os_version:
                    self.device_infos[client_ip]["os"] = os_version
            
            # Bulunan tüm string'leri yazdır (debug için)
            print(f"\n{Colors.YELLOW}[*] Paketten çıkarılan tüm string'ler:{Colors.ENDC}")
            for i, s in enumerate(strings):
                print(f"  {i+1}. {s}")
        
        else:
            print(f"{Colors.RED}[!] Cihaz bilgileri bulunamadı{Colors.ENDC}")
    
    def report_thread(self):
        """Periyodik rapor thread'i"""
        while self.running:
            time.sleep(30)  # 30 saniyede bir rapor
            self.show_summary()
    
    def show_summary(self):
        """Özet rapor göster"""
        if not self.device_infos:
            return
            
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}CLIENT IP VE DEVICE ID RAPORU{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'-'*60}{Colors.ENDC}")
        print(f"Toplam Bağlantı: {self.connections}")
        print(f"Benzersiz IP: {len(self.device_infos)}")
        
        print(f"\n{Colors.BOLD}{'IP':<15} {'Device ID':<36} {'Model':<15} {'OS':<12} {'Ziyaret':<7}{Colors.ENDC}")
        print(f"{'-'*85}")
        
        for ip, info in self.device_infos.items():
            device_id = info.get("device_id", "?")
            model = info.get("model", "?")
            os = info.get("os", "?")
            visits = info.get("visits", 0)
            
            print(f"{ip:<15} {(device_id or '?')[:36]:<36} {(model or '?')[:15]:<15} {(os or '?')[:12]:<12} {visits:<7}")
        
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}")

if __name__ == "__main__":
    # Komut satırı parametresi ile host ve port değiştirilebilir
    host = "87.106.36.114"
    port = 6349  # Varsayılan port
    
    # Komut satırı parametreleri ile host ve port değiştirilebilir
    if len(sys.argv) > 1:
        if ":" in sys.argv[1]:
            parts = sys.argv[1].split(":")
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                print(f"{Colors.RED}[!] Geçersiz port numarası. Varsayılan port kullanılıyor: {port}{Colors.ENDC}")
        else:
            try:
                port = int(sys.argv[1])
            except ValueError:
                print(f"{Colors.RED}[!] Geçersiz port numarası. Varsayılan port kullanılıyor: {port}{Colors.ENDC}")
    
    print(f"{Colors.BOLD}{Colors.CYAN}TIME TEAM DeviceID Sunucusu{Colors.ENDC}")
    print(f"{Colors.CYAN}Powered by arda64{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    # Sunucuyu başlat
    server = DeviceServer(host=host, port=port)
    server.start() 