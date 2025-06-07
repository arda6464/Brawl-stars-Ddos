import sys
import time
from src import AccountManager, ClubManager, ProxyManager, NetworkManager

def test_account_manager():
    print("\n=== Account Manager Test ===")
    try:
        account = AccountManager()
        print("✓ AccountManager başarıyla oluşturuldu")
        print(f"Device ID: {account.device_id}")
        print(f"Device Model: {account.device_model}")
        print(f"OS Version: {account.os_version}")
        
        packet = account.create_account_packet(version=1)
        print(f"✓ Hesap paketi oluşturuldu (boyut: {len(packet)} bytes)")
        return True
    except Exception as e:
        print(f"✗ AccountManager testi başarısız: {str(e)}")
        return False

def test_club_manager():
    print("\n=== Club Manager Test ===")
    try:
        club = ClubManager()
        print("✓ ClubManager başarıyla oluşturuldu")
        
        # Kulüp oluşturma paketi testi
        create_packet = club.create_club_packet("Test Club", "Test Description")
        print(f"✓ Kulüp oluşturma paketi oluşturuldu (boyut: {len(create_packet)} bytes)")
        
        # Kulübe katılma paketi testi
        join_packet = club.join_club_by_tag_packet("#TEST123")
        print(f"✓ Kulübe katılma paketi oluşturuldu (boyut: {len(join_packet)} bytes)")
        return True
    except Exception as e:
        print(f"✗ ClubManager testi başarısız: {str(e)}")
        return False

def test_proxy_manager():
    print("\n=== Proxy Manager Test ===")
    try:
        # Test proxy listesi
        test_proxies = [
            "192.168.1.1:8080",
            "10.0.0.1:3128",
            "172.16.0.1:80"
        ]
        
        proxy_mgr = ProxyManager(test_proxies)
        print("✓ ProxyManager başarıyla oluşturuldu")
        
        # Proxy alma testi
        proxy = proxy_mgr.get_proxy()
        print(f"✓ Proxy alındı: {proxy}")
        
        # Proxy başarı/başarısızlık testi
        proxy_mgr.report_success(proxy)
        print("✓ Proxy başarı raporu gönderildi")
        
        proxy_mgr.report_failure(proxy)
        print("✓ Proxy başarısızlık raporu gönderildi")
        
        # İstatistik testi
        stats = proxy_mgr.get_stats()
        print(f"✓ İstatistikler alındı: {stats}")
        return True
    except Exception as e:
        print(f"✗ ProxyManager testi başarısız: {str(e)}")
        return False

def test_network_manager():
    print("\n=== Network Manager Test ===")
    try:
        network = NetworkManager()
        print("✓ NetworkManager başarıyla oluşturuldu")
        
        # Bağlantı testi (timeout ile)
        print("Bağlantı testi yapılıyor (5 saniye timeout)...")
        connected = network.connect()
        if connected:
            print("✓ Sunucuya bağlantı başarılı")
            
            # Hello paketi testi
            if network.send_hello_packet(version=1):
                print("✓ Hello paketi gönderildi")
                
                # Paket alma testi
                response = network.receive_packet(timeout=2)
                if response:
                    print(f"✓ Yanıt alındı (boyut: {len(response)} bytes)")
                else:
                    print("! Yanıt alınamadı (timeout)")
            
            network.disconnect()
            print("✓ Bağlantı kapatıldı")
        else:
            print("! Sunucuya bağlanılamadı (timeout)")
        
        return True
    except Exception as e:
        print(f"✗ NetworkManager testi başarısız: {str(e)}")
        return False

def main():
    print("=== Modül Testleri Başlıyor ===")
    
    tests = [
        ("Account Manager", test_account_manager),
        ("Club Manager", test_club_manager),
        ("Proxy Manager", test_proxy_manager),
        ("Network Manager", test_network_manager)
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for name, test_func in tests:
        print(f"\n{name} testi başlıyor...")
        if test_func():
            success_count += 1
            print(f"✓ {name} testi başarılı")
        else:
            print(f"✗ {name} testi başarısız")
        time.sleep(1)  # Testler arası kısa bekleme
    
    print("\n=== Test Sonuçları ===")
    print(f"Toplam Test: {total_tests}")
    print(f"Başarılı: {success_count}")
    print(f"Başarısız: {total_tests - success_count}")
    print(f"Başarı Oranı: {(success_count/total_tests)*100:.1f}%")

if __name__ == "__main__":
    main() 