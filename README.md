# Brawl Stars DDoS Aracı

Brawl Stars için çoklu hesap yönetimi, kulüp oluşturma ve sunucu test aracı.

## ⚠️ Uyarı

Bu araç sadece eğitim ve test amaçlıdır. Bu aracı gerçek DDoS saldırıları için kullanmak yasadışı ve etik değildir. Yazarlar, bu yazılımın yanlış kullanımından sorumlu değildir.

## 🚀 Özellikler

- Dağıtık test için proxy desteği
- Çoklu bağlantı test yöntemleri
- Sunucu yanıt analizi
- Proxy doğrulama ve yönetimi
- Kulüp keşif fonksiyonları
- Hesap oluşturma
- Kulüp oluşturma
- hesap ve kulüp ismi özelleştirme

## 📋 Gereksinimler

- Python 3.7+
- Gerekli Python paketleri (`pip install -r requirements.txt` ile yükleyin):
  - requests
  - aiohttp
  - asyncio
  - colorama
  - tqdm

## 🛠️ Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/arda6464/Brawl-stars-Ddos.git
cd Brawl-stars-Ddos
```

2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. `proxies.txt` dosyasında proxy'lerinizi yapılandırın (her satıra bir proxy, format: `ip:port`)

## 💻 Kullanım

1. Proxy'leri doğrula:
```bash
python proxy.py
```

2. Ana programı çalıştır:
```bash
python main.py
```

## 📁 Proje Yapısı

- `main.py` - Ana program
- `server.py` - Sunucu test modülü
- `proxy.py` - Proxy yönetimi ve doğrulama
- `utils.py` - Yardımcı fonksiyonlar
- `login.py` - Hesap oluşturma

## 📝 Dosya Açıklamaları

- `proxies.txt` - Proxy sunucuları listesi
- `working_proxies.txt` - Doğrulanmış çalışan proxy'ler
- `found_clubs.txt` - Keşfedilen kulüp bilgileri
- `valid_proxies.txt` - Ek proxy doğrulama sonuçları

## 🔒 Güvenlik Notu

Bu araç eğitim amaçlı ve ağ testi için tasarlanmıştır. Her zaman:
- Sorumlu kullanın
- Sadece sahip olduğunuz veya test izniniz olan sistemlerde test yapın
- Yerel yasaları ve düzenlemeleri takip edin
- Hizmet kullanım şartlarına saygı gösterin

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakın.