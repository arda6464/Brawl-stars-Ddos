import random
import threading
from queue import Queue

class ProxyManager:
    def __init__(self, proxy_list):
        self.all_proxies = proxy_list.copy()
        self.working_proxies = proxy_list.copy()
        self.failed_proxies = []
        self.proxy_queue = Queue()
        self.proxy_stats = {}  # Proxy başarı oranı istatistikleri
        self.lock = threading.Lock()
        
        # Proxy'leri kuyruğa ekle
        for proxy in self.working_proxies:
            self.proxy_queue.put(proxy)
            self.proxy_stats[proxy] = {"success": 0, "fail": 0}
    
    def get_proxy(self):
        """Sıradaki proxy'yi döndürür, yoksa rastgele bir proxy seçer"""
        with self.lock:
            if self.proxy_queue.empty():
                # Başarısız proxyleri tekrar deneme (bazıları geçici olarak düşmüş olabilir)
                retry_candidates = [p for p in self.failed_proxies 
                                   if self.proxy_stats[p]["fail"] < 3]  # 3'ten az başarısız olan
                
                if retry_candidates and random.random() < 0.3:  # %30 olasılıkla başarısız proxy'yi tekrar dene
                    proxy = random.choice(retry_candidates)
                    self.failed_proxies.remove(proxy)
                    return proxy
                
                if not self.working_proxies:
                    # Tüm proxy'ler bitti, listeyi yeniden yükle
                    if not self.reload_proxies():
                        return None  # Yeniden yükleme başarısız oldu
                    
                return random.choice(self.working_proxies)
            
            return self.proxy_queue.get()
    
    def reload_proxies(self):
        """Proxy listesini yeniden yükler"""
        try:
            with open("working_proxies.txt", "r") as f:
                new_proxies = [line.strip() for line in f if line.strip()]
            
            # Yeni proxy'lerin hepsini ekle
            for proxy in new_proxies:
                if proxy not in self.proxy_stats:
                    self.proxy_stats[proxy] = {"success": 0, "fail": 0}
            
            # Çalışan proxy'leri güncelle
            self.all_proxies = new_proxies.copy()
            self.working_proxies = new_proxies.copy()
            self.failed_proxies = []
            
            # Proxy'leri kuyruğa ekle
            for proxy in self.working_proxies:
                self.proxy_queue.put(proxy)
            
            return True
        except Exception as e:
            return False
    
    def report_success(self, proxy):
        """Proxy başarılı olduğunda çağrılır"""
        with self.lock:
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]["success"] += 1
            
            # Başarılı proxy'yi tekrar kuyruğa ekle
            self.proxy_queue.put(proxy)
            
            # Başarısız listesindeyse çıkar
            if proxy in self.failed_proxies:
                self.failed_proxies.remove(proxy)
                
            # Çalışan listesine ekle
            if proxy not in self.working_proxies:
                self.working_proxies.append(proxy)
    
    def report_failure(self, proxy):
        """Proxy başarısız olduğunda çağrılır"""
        with self.lock:
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]["fail"] += 1
            
            # Çalışan listesinden çıkar
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                
            # Başarısız listesine ekle
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