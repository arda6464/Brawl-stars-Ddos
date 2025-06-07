from login import login
import socket
import time
import random

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_device_id_server(server_ip, server_port=9339, num_tests=5):
    """Sunucuya cihaz bilgilerini içeren test paketleri gönderir"""
    print(f"{Colors.BOLD}{Colors.CYAN}Device ID Sunucu Testi{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Sunucu: {server_ip}:{server_port}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Test sayısı: {num_tests}{Colors.ENDC}")
    
    successful = 0
    failed = 0
    
    for i in range(num_tests):
        print(f"\n{Colors.BOLD}Test #{i+1}{Colors.ENDC}")
        try:
            # Login nesnesi oluştur (bu rastgele bir device ID oluşturacak)
            l = login()
            print(f"{Colors.CYAN}Device ID:  {l.device_id}{Colors.ENDC}")
            print(f"{Colors.CYAN}Model:      {l.device_model}{Colors.ENDC}")
            print(f"{Colors.CYAN}OS:         {l.os_version}{Colors.ENDC}")
            
            # Sunucuya bağlan
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            
            print(f"{Colors.YELLOW}Sunucuya bağlanılıyor...{Colors.ENDC}")
            s.connect((server_ip, server_port))
            
            # Hesap oluşturma paketi gönder
            version = random.randint(1, 10)  # Rastgele versiyon
            packet = l.create_account(version)
            
            print(f"{Colors.YELLOW}Paket gönderiliyor... ({len(packet)} byte){Colors.ENDC}")
            s.send(packet)
            
            # Sunucudan yanıt al
            try:
                response = s.recv(1024)
                print(f"{Colors.GREEN}Yanıt alındı: {len(response)} byte{Colors.ENDC}")
            except:
                print(f"{Colors.YELLOW}Yanıt alınamadı (sorun değil){Colors.ENDC}")
            
            s.close()
            successful += 1
            print(f"{Colors.GREEN}Test başarılı!{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.RED}Hata: {str(e)}{Colors.ENDC}")
            failed += 1
        
        # Testler arasında bekleme
        if i < num_tests - 1:
            delay = random.uniform(1, 3)
            print(f"{Colors.YELLOW}Sonraki test için {delay:.1f} saniye bekleniyor...{Colors.ENDC}")
            time.sleep(delay)
    
    # Sonuçları göster
    print(f"\n{Colors.BOLD}{'-'*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Test Sonuçları:{Colors.ENDC}")
    print(f"Toplam test:    {num_tests}")
    print(f"Başarılı:       {successful}")
    print(f"Başarısız:      {failed}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}✓ TÜM TESTLER BAŞARILI!{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}✗ {failed} TEST BAŞARISIZ!{Colors.ENDC}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Hata: Sunucu IP adresi belirtilmedi!{Colors.ENDC}")
        print(f"Kullanım: python {sys.argv[0]} <sunucu_ip> [port] [test_sayısı]")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 9339
    num_tests = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    test_device_id_server(server_ip, server_port, num_tests) 