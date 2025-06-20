import requests
import sys
from concurrent.futures import ThreadPoolExecutor
import time

# Renkli çıktı için ANSI renk kodları
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'



def test_proxy(proxy):
    
    try:
        
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=8)
        if r.status_code == 200:
            print(f"{Colors.GREEN}[+] Proxy {proxy} çalışıyor.{Colors.ENDC} ")

            return True
    except requests.exceptions.ConnectTimeout:
        print(f"{Colors.RED}[-] Proxy {proxy} zaman aşımına uğradı.{Colors.ENDC}")
    except requests.exceptions.ProxyError:
        print(f"{Colors.RED}[-] Proxy {proxy} bağlantı hatası.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}[-] Proxy {proxy} hatası: {str(e)}{Colors.ENDC}")
    return False

def main():
    # Başlık
    print(f"\n{Colors.BOLD}{Colors.CYAN}TIME TEAM PROXY CHECKER{Colors.ENDC}")
    print(f"{Colors.YELLOW}Powered by arda64{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*40}{Colors.ENDC}\n")

    try:
        # proxies.txt'den oku
        input_file = "proxies.txt"
        output_file = "working_proxies.txt"  # Burada düzelttim
        
        print(f"{Colors.CYAN}[*] {input_file} dosyasından proxy'ler okunuyor...{Colors.ENDC}")
        with open(input_file, "r") as f:
            proxy_list = [line.strip() for line in f if line.strip()]
        
        total = len(proxy_list)
        print(f"{Colors.CYAN}[*] Toplam {total} proxy test edilecek.{Colors.ENDC}")
        
        # çalışan proxy'leri kontrol et
        working_proxies = []
        print(f"{Colors.CYAN}[*] Proxy'ler test ediliyor...{Colors.ENDC}")
        
        start_time = time.time()
        
        # Thread havuzu ile paralel test
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(test_proxy, proxy_list))
        
        # Çalışan proxy'leri topla
        working_proxies = [proxy for proxy, result in zip(proxy_list, results) if result]
        
        # Sonuç zamanı
        elapsed = time.time() - start_time
        
        # Dosyaya yaz
        if working_proxies:
            with open(output_file, "w") as f:
                for p in working_proxies:
                    f.write(p + "\n")
            print(f"\n{Colors.GREEN}[✓] {len(working_proxies)}/{total} çalışan proxy '{output_file}' dosyasına yazıldı.{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}[!] Çalışan proxy bulunamadı.{Colors.ENDC}")
        
        print(f"{Colors.YELLOW}[⏱] İşlem {elapsed:.2f} saniyede tamamlandı.{Colors.ENDC}")
        
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Hata: {input_file} dosyası bulunamadı!{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}[!] Beklenmeyen hata: {str(e)}{Colors.ENDC}")

if __name__ == "__main__":
    main()  