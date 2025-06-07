import requests
import threading

valid_proxies = []

def fetch_proxies():
    url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all"
    response = requests.get(url)
    return list(filter(None, response.text.split("\n")))

def test_proxy(proxy):
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        # https yerine http kullanıyoruz
        r = requests.get("http://example.com", proxies=proxies, timeout=5)
        if r.status_code == 200:
            print(f"[✓] ÇALIŞIYOR: {proxy}")
            valid_proxies.append(proxy)
    except:
        print(f"[x] ÇALIŞMIYOR: {proxy}")

def main():
    print("Proxy'ler çekiliyor...")
    proxies = fetch_proxies()
    print(f"{len(proxies)} adet proxy bulundu. Test ediliyor...\n")

    threads = []
    for proxy in proxies:
        t = threading.Thread(target=test_proxy, args=(proxy,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    with open("valid_proxies.txt", "w") as f:
        for proxy in valid_proxies:
            f.write(proxy + "\n")

    print(f"\nToplam çalışan proxy sayısı: {len(valid_proxies)}")
    print("valid_proxies.txt dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
