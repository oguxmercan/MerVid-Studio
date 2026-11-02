# MerVid Studio (v1.0.0)

Yüksek sadakatli 4K video, kayıpsız ses ve medya kapak görseli indirme stüdyosu.

**Geliştirici:** [Oğuzhan Mercan](https://github.com/oguxmercan)

---

## 🚀 Öne Çıkan Özellikler

1. **Her Platformdan DRM'siz Medya İndirme**:
   - YouTube (4K / 8K, 60 FPS, HDR, Shorts, Oynatma Listeleri, Kanallar)
   - Instagram (Reels, Gönderiler, Hikayeler)
   - TikTok (Filigransız HD)
   - X / Twitter, Facebook, Reddit, Twitch, Vimeo, SoundCloud ve 1000'den fazla site desteği.

2. **Kapak / Banner İndirme Yetenekleri**:
   - **Tek Tıkla Doğrudan Banner İndirme**: `Banner İndir (.jpg)` butonu ile tam çözünürlüklü kapak görselini anında kaydetme.
   - **Videoyla Birlikte Banner İndirme**: Video veya ses dosyası inerken yanına otomatik olarak `.jpg` formatında kapak resmi kaydetme.
   - **Kapak Görseli Gömme**: İndirilen MP3, MP4 veya MKV dosyasına albüm kapağı olarak ekleme.

3. **Real-Debrid Entegrasyonu**:
   - **Hız Kısıtlamasız Premium İndirme**: Rapidgator, Mega, 1fichier, Turbobit ve Magnet/Torrent linklerini doğrudan Real-Debrid API desteğiyle gigabit hızında indirme.
   - Ayarlar sekmesinden tek tıkla API anahtarı ekleme ve üyelik durumu kontrolü.

4. **Gelişmiş Ayarlar & Araçlar**:
   - **Analyze Butonu & Enter Desteği**: Linki yapıştırıp tek tıkla veya Enter ile anında analiz etme.
   - **SponsorBlock**: Videolardaki sponsor bölümlerini, introları ve reklamları otomatik atlama.
   - **Altyazı Gömme**: Türkçe ve İngilizce altyazıları doğrudan video içine yerleştirme.
   - **Cookie Kasası (Ayarlar İçinde)**: Özel ve üyelik gerektiren videolar için yerel `cookies.txt` içe aktarma (%100 yerel ve gizli).
   - **Çok Kanallı Hızlandırma**: 16 eşzamanlı bağlantıya kadar yüksek indirme hızı.

---

## 🛠️ Kaynak Koddan Çalıştırma ve Derleme

Gerekli paketleri kurmak için:
```bash
pip install -r requirements.txt
```

Uygulamayı geliştirme modunda çalıştırmak için:
```bash
python app.py
```

Bağımsız Windows `.exe` dosyasını derlemek için:
```bash
python build_exe.py
```

---

## 💻 .EXE Konumu ve Çalıştırma

Derlenmiş Windows `.exe` dosyası:
```
F:\MerVid Studio\dist\MerVid-Studio\MerVid-Studio.exe
```

Bu klasörü istediğiniz konuma taşıyabilir ve `MerVid-Studio.exe`'ye çift tıklayarak hemen kullanabilirsiniz.
