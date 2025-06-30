# BDC Platform - Eğitim Yönetimi Detaylı Rehberi

## 🎯 Bu Belge Hakkında

Eğitim Yönetimi modülü, BDC platformunda eğitim içeriklerinin oluşturulması, düzenlenmesi, sunulması ve takibini sağlayan kapsamlı bir modüldür. Bu belgede, eğitim materyalleri, ders yönetimi, içerik türleri ve öğrenme araçlarının detayları açıklanmaktadır.

---

## 📋 İçindekiler

1. [Eğitim Yönetimi Genel Bakış](#eğitim-yönetimi-genel-bakış)
2. [Ders ve Modül Yönetimi](#ders-ve-modül-yönetimi)
3. [İçerik Türleri ve Yönetimi](#i̇çerik-türleri-ve-yönetimi)
4. [Video Ders Yönetimi](#video-ders-yönetimi)
5. [Canlı Ders ve Webinar](#canlı-ders-ve-webinar)
6. [Ödev ve Proje Yönetimi](#ödev-ve-proje-yönetimi)
7. [Kaynak ve Döküman Yönetimi](#kaynak-ve-döküman-yönetimi)
8. [Etkileşimli İçerikler](#etkileşimli-i̇çerikler)
9. [Öğrenme Yolu Tasarımı](#öğrenme-yolu-tasarımı)
10. [İlerleme Takibi ve Analitik](#i̇lerleme-takibi-ve-analitik)

---

## 📚 Eğitim Yönetimi Genel Bakış

### Erişim Yolu
```
Ana Menü → Eğitim → Eğitim Yönetimi
veya
Program Detayı → Eğitim İçerikleri
```

### Kimler Erişebilir?
- ✅ **Yönetici:** Tüm eğitim içeriklerini oluşturma ve yönetme
- ✅ **Eğitmen:** Kendi programlarındaki içerikleri yönetme
- ⚠️ **Öğrenci:** Sadece kayıtlı olduğu içeriklere erişim

### Eğitim Yönetimi Nedir?
Eğitim Yönetimi, öğrencilere sunulacak tüm eğitim materyallerinin, ders içeriklerinin ve öğrenme aktivitelerinin planlandığı, oluşturulduğu ve yönetildiği merkezi sistemdir.

### Ana Bileşenler
```
📚 EĞİTİM YÖNETİMİ
├── 📖 Dersler ve Modüller
├── 🎥 Video İçerikler
├── 📺 Canlı Dersler
├── 📝 Ödevler ve Projeler
├── 📄 Dökümanlar
├── 🎮 Etkileşimli İçerikler
├── 🛤️ Öğrenme Yolları
└── 📊 İlerleme Analizi
```

---

## 📖 Ders ve Modül Yönetimi

### Modül Yapısı

Eğitim içerikleri hiyerarşik yapıda organize edilir:

```
Program
└── Modül
    └── Ders
        └── Bölüm
            └── İçerik
```

### Yeni Modül Oluşturma

#### Adım 1: Modül Bilgileri
```
📋 MODÜL BİLGİLERİ
├── Modül Adı* (Örn: "Web Geliştirme Temelleri")
├── Modül Kodu* (Örn: "WEB-101")
├── Açıklama (500 karakter)
├── Öğrenme Hedefleri (liste halinde)
├── Ön Koşullar (varsa)
├── Tahmini Süre (saat)
├── Sıralama (modül sırası)
└── Durum (Aktif/Pasif)
```

#### Adım 2: Modül Ayarları
```
⚙️ MODÜL AYARLARI
├── Erişim Türü
│   ├── Sıralı (önceki modül tamamlanmalı)
│   ├── Paralel (aynı anda erişilebilir)
│   └── Kilitli (manuel açılır)
├── Tamamlama Kriterleri
│   ├── Tüm dersler tamamlanmalı
│   ├── Minimum %X ilerleme
│   └── Quiz başarısı gerekli
└── Sertifika Ayarları
    ├── Modül sertifikası ver
    └── Sertifika şablonu seç
```

### Ders Oluşturma ve Düzenleme

#### Ders Türleri
| Tür | Açıklama | Özellikler |
|-----|----------|------------|
| **Video Ders** | Kayıtlı video içerikler | Altyazı, hız kontrolü, notlar |
| **Canlı Ders** | Gerçek zamanlı eğitim | Zoom/Teams entegrasyonu |
| **Okuma Materyali** | PDF, döküman | Highlight, not alma |
| **Etkileşimli** | Simülasyon, oyun | SCORM desteği |
| **Karma** | Çoklu içerik türü | Esnek yapı |

#### Ders Oluşturma Formu
```
📝 DERS BİLGİLERİ
├── Ders Başlığı* (Örn: "HTML5 Temelleri")
├── Ders Kodu* (Örn: "WEB-101-01")
├── Ders Türü* (dropdown)
├── Açıklama (1000 karakter)
├── Öğrenme Çıktıları (liste)
├── Tahmini Süre (dakika)
├── Puan Değeri (0-100)
└── Yayın Durumu
    ├── Taslak
    ├── Yayında
    └── Arşivlenmiş
```

### Ders İçeriği Düzenleme

#### İçerik Editörü Özellikleri
```
WYSIWYG EDİTÖR
├── 📝 Metin Formatlama
│   ├── Başlıklar (H1-H6)
│   ├── Paragraflar
│   ├── Listeler
│   └── Alıntılar
├── 📸 Medya Ekleme
│   ├── Resim yükleme
│   ├── Video embed
│   ├── Ses dosyası
│   └── GIF/animasyon
├── 🔗 Bağlantılar
│   ├── İç linkler
│   ├── Dış linkler
│   └── Dosya linkleri
├── 📊 Özel Bileşenler
│   ├── Kod blokları
│   ├── Tablolar
│   ├── Uyarı kutuları
│   └── Bilgi kartları
└── 🎨 Stil Ayarları
    ├── Renk paleti
    ├── Font seçimi
    └── Tema uyumu
```

---

## 🎬 İçerik Türleri ve Yönetimi

### Video İçerikler

#### Video Yükleme Süreci
1. **Dosya Seçimi**
   - Desteklenen formatlar: MP4, WebM, MOV
   - Maksimum boyut: 2 GB
   - Önerilen çözünürlük: 1080p

2. **Video İşleme**
   ```
   🎥 VİDEO İŞLEME
   ├── Otomatik sıkıştırma
   ├── Çoklu kalite oluşturma (360p, 720p, 1080p)
   ├── Thumbnail oluşturma
   └── Altyazı senkronizasyonu
   ```

3. **Video Ayarları**
   - ⏱️ Bölüm işaretleri ekleme
   - 📝 Video içi notlar
   - ❓ Video içi quiz
   - 🔒 İlerleme kilitleme

### Döküman ve PDF İçerikler

#### Döküman Yönetimi
```
📄 DÖKÜMAN ÖZELLİKLERİ
├── PDF Viewer entegrasyonu
├── Sayfa bazlı ilerleme takibi
├── Highlight ve not alma
├── Arama fonksiyonu
├── İndirme kontrolü
└── Yazdırma ayarları
```

### SCORM ve xAPI İçerikler

#### SCORM Paket Yükleme
1. SCORM 1.2 veya 2004 paketi seçin
2. ZIP dosyasını yükleyin
3. Otomatik doğrulama
4. Puan ve tamamlama ayarları

#### xAPI (Tin Can) Desteği
- Detaylı öğrenme analitiği
- Offline öğrenme takibi
- Çoklu platform senkronizasyonu

---

## 🎥 Video Ders Yönetimi

### Video Ders Paneli

```
VİDEO DERS PANELİ
├── 📹 Video Player
│   ├── Oynatma kontrolleri
│   ├── Hız ayarı (0.5x - 2x)
│   ├── Kalite seçimi
│   ├── Tam ekran
│   └── Picture-in-Picture
├── 📊 İzleme İstatistikleri
│   ├── Toplam izlenme
│   ├── Ortalama izlenme süresi
│   ├── Bırakma noktaları
│   └── Tekrar izleme oranı
└── 🛠️ Düzenleme Araçları
    ├── Video kesme
    ├── Altyazı ekleme
    ├── Bölüm oluşturma
    └── Quiz ekleme
```

### Altyazı Yönetimi

#### Altyazı Ekleme Yöntemleri
1. **Otomatik Oluşturma**
   - AI tabanlı konuşma tanıma
   - Otomatik zaman kodlama
   - Düzenleme arayüzü

2. **Manuel Yükleme**
   - SRT, VTT formatları
   - Çoklu dil desteği
   - Senkronizasyon araçları

### Video İçi Etkileşimler

#### Quiz Noktaları
```
❓ VİDEO İÇİ QUIZ
├── Zaman damgası belirleme
├── Soru türü seçimi
│   ├── Çoktan seçmeli
│   ├── Doğru/Yanlış
│   └── Açık uçlu
├── Puan değeri
└── İlerleme kontrolü
```

#### Etkileşimli Alanlar
- 🔗 Tıklanabilir bağlantılar
- 📝 Pop-up bilgi kartları
- 🎯 Hotspot alanları
- 📊 Anket ve oylamalar

---

## 📺 Canlı Ders ve Webinar

### Canlı Ders Planlama

#### Ders Oluşturma
```
📅 CANLI DERS PLANLAMA
├── Ders Bilgileri
│   ├── Başlık ve açıklama
│   ├── Tarih ve saat
│   ├── Süre (dakika)
│   └── Maksimum katılımcı
├── Platform Seçimi
│   ├── Zoom
│   ├── Microsoft Teams
│   ├── Google Meet
│   └── Dahili sistem
├── Kayıt Ayarları
│   ├── Otomatik kayıt
│   ├── Kayıt paylaşımı
│   └── Kayıt düzenleme
└── Katılımcı Ayarları
    ├── Otomatik davet
    ├── Hatırlatmalar
    └── Katılım zorunluluğu
```

### Canlı Ders Yönetimi

#### Ders Öncesi
1. **Teknik Kontroller**
   - Bağlantı testi
   - Ses/video kontrolü
   - Ekran paylaşım testi

2. **İçerik Hazırlığı**
   - Sunum yükleme
   - Materyalleri paylaşma
   - Anket hazırlama

#### Ders Sırasında
```
🎙️ CANLI DERS KONTROL PANELİ
├── Katılımcı Yönetimi
│   ├── Katılımcı listesi
│   ├── Mikrofon kontrolü
│   ├── Kamera kontrolü
│   └── Çıkarma/engelleme
├── İçerik Paylaşımı
│   ├── Ekran paylaşımı
│   ├── Beyaz tahta
│   ├── Dosya paylaşımı
│   └── Anket başlatma
├── Etkileşim Araçları
│   ├── Sohbet penceresi
│   ├── Soru-Cevap
│   ├── El kaldırma
│   └── Emoji tepkiler
└── Kayıt Kontrolü
    ├── Başlat/Durdur
    ├── Duraklat
    └── Bölüm işaretle
```

### Webinar Özellikleri

#### Webinar vs Canlı Ders
| Özellik | Canlı Ders | Webinar |
|---------|------------|---------|
| Katılımcı Sayısı | 50-100 | 500+ |
| Etkileşim | Yüksek | Orta |
| Sunum Odaklı | Hayır | Evet |
| Q&A Moderasyonu | Opsiyonel | Zorunlu |

---

## 📝 Ödev ve Proje Yönetimi

### Ödev Oluşturma

#### Ödev Türleri
```
📋 ÖDEV TÜRLERİ
├── 📄 Yazılı Ödev
│   ├── Kompozisyon
│   ├── Rapor
│   └── Makale
├── 💻 Kod Ödevi
│   ├── Algoritma
│   ├── Proje
│   └── Debug
├── 🎨 Tasarım Ödevi
│   ├── UI/UX
│   ├── Logo
│   └── Mockup
└── 🎥 Video Ödevi
    ├── Sunum
    ├── Demo
    └── Tutorial
```

#### Ödev Detayları
```
📝 ÖDEV OLUŞTURMA FORMU
├── Temel Bilgiler
│   ├── Ödev başlığı*
│   ├── Açıklama*
│   ├── Talimatlar
│   └── Değerlendirme kriterleri
├── Teslim Ayarları
│   ├── Son teslim tarihi*
│   ├── Geç teslim politikası
│   ├── Dosya formatları
│   └── Maksimum dosya boyutu
├── Puanlama
│   ├── Toplam puan
│   ├── Rubrik tanımlama
│   ├── Otomatik puanlama
│   └── Peer review
└── Ek Özellikler
    ├── Grup ödevi
    ├── Plagiarism kontrolü
    ├── Kod similarity check
    └── AI detection
```

### Proje Yönetimi

#### Proje Aşamaları
```
🚀 PROJE AŞAMALARI
├── 1️⃣ Planlama
│   ├── Proje önerisi
│   ├── Onay süreci
│   └── Takım oluşturma
├── 2️⃣ Geliştirme
│   ├── Sprint planları
│   ├── İlerleme raporları
│   └── Kod incelemeleri
├── 3️⃣ Test ve Revizyon
│   ├── Test senaryoları
│   ├── Bug raporları
│   └── Düzeltmeler
└── 4️⃣ Sunum ve Teslim
    ├── Demo hazırlığı
    ├── Dokümantasyon
    └── Final sunumu
```

### Değerlendirme Sistemi

#### Rubrik Oluşturma
| Kriter | Mükemmel (25) | İyi (20) | Orta (15) | Gelişmeli (10) |
|--------|---------------|----------|-----------|----------------|
| **İçerik Kalitesi** | Kapsamlı ve detaylı | Yeterli detay | Temel seviye | Eksik içerik |
| **Teknik Doğruluk** | Hatasız | Küçük hatalar | Birkaç hata | Çok hatalı |
| **Sunum** | Profesyonel | Düzenli | Karışık | Dağınık |
| **Zamanında Teslim** | Erken | Zamanında | 1 gün geç | 2+ gün geç |

---

## 📚 Kaynak ve Döküman Yönetimi

### Kaynak Kütüphanesi

```
📂 KAYNAK KÜTÜPHANESİ
├── 📁 Kategoriler
│   ├── Ders Notları
│   ├── Sunumlar
│   ├── Kod Örnekleri
│   ├── Şablonlar
│   └── Ek Okumalar
├── 🏷️ Etiketleme
│   ├── Konu bazlı
│   ├── Seviye bazlı
│   ├── Format bazlı
│   └── Özel etiketler
└── 🔍 Arama ve Filtreleme
    ├── Tam metin arama
    ├── Metadata arama
    ├── Tarih filtreleri
    └── Popülerlik sıralaması
```

### Döküman Yönetimi

#### Yükleme ve Organizasyon
1. **Toplu Yükleme**
   - Drag & drop desteği
   - Klasör yapısını koruma
   - Otomatik kategorizasyon

2. **Metadata Yönetimi**
   ```
   📋 DÖKÜMAN METADATA
   ├── Başlık ve açıklama
   ├── Yazar bilgisi
   ├── Versiyon kontrolü
   ├── Lisans bilgisi
   └── İlişkili içerikler
   ```

### İndirme ve Erişim Kontrolü

#### Erişim Seviyeleri
- 🔓 **Herkese Açık:** Tüm kullanıcılar
- 🔒 **Kayıtlı Kullanıcılar:** Giriş yapmış
- 🎓 **Program Öğrencileri:** Kayıtlı öğrenciler
- 👨‍🏫 **Sadece Eğitmenler:** Eğitmen rolü

---

## 🎮 Etkileşimli İçerikler

### H5P İçerik Türleri

```
🎯 ETKİLEŞİMLİ İÇERİKLER
├── 🎲 Oyunlar
│   ├── Memory oyunu
│   ├── Kelime bulma
│   ├── Puzzle
│   └── Quiz oyunları
├── 📊 Simülasyonlar
│   ├── İş simülasyonu
│   ├── Kod simülatörü
│   ├── Laboratuvar
│   └── Case study
├── 🎬 İnteraktif Videolar
│   ├── Dallanmış video
│   ├── 360° video
│   ├── Hotspot video
│   └── Quiz video
└── 📈 Görselleştirmeler
    ├── İnfografikler
    ├── Timeline
    ├── Process flow
    └── Mind map
```

### Etkileşimli İçerik Oluşturma

#### Editör Arayüzü
```
🛠️ H5P EDİTÖR
├── İçerik Türü Seçimi
├── Görsel Editör
├── Davranış Ayarları
├── Puanlama Yapılandırması
└── Önizleme ve Test
```

### Gamification Öğeleri

#### Oyunlaştırma Bileşenleri
- 🏆 **Başarı Rozetleri:** Milestone ödülleri
- 📊 **Puan Sistemi:** XP kazanma
- 🎯 **Seviye Sistemi:** İlerleme seviyeleri
- 🏅 **Liderlik Tablosu:** Rekabet öğesi
- 💎 **Sanal Ödüller:** Motivasyon araçları

---

## 🛤️ Öğrenme Yolu Tasarımı

### Learning Path Oluşturma

```
🗺️ ÖĞRENME YOLU TASARIMI
├── 📍 Başlangıç Noktası
│   ├── Ön değerlendirme
│   ├── Seviye tespiti
│   └── Hedef belirleme
├── 🛤️ Ana Yol
│   ├── Zorunlu modüller
│   ├── Sıralı ilerleme
│   └── Kontrol noktaları
├── 🔀 Alternatif Yollar
│   ├── İleri seviye
│   ├── Destek modülleri
│   └── Özel ilgi alanları
└── 🏁 Bitiş Noktası
    ├── Final değerlendirme
    ├── Sertifikasyon
    └── Sonraki adımlar
```

### Kişiselleştirilmiş Öğrenme

#### Adaptif Öğrenme Sistemi
1. **Öğrenci Profili Analizi**
   - Öğrenme stili tespiti
   - Hız ve kapasite ölçümü
   - İlgi alanları belirleme

2. **İçerik Önerisi**
   ```
   🤖 AI ÖNERİ SİSTEMİ
   ├── Performans bazlı öneriler
   ├── İlgi alanı eşleştirme
   ├── Zorluk seviyesi ayarlama
   └── Zaman optimizasyonu
   ```

### Prerequisite (Ön Koşul) Yönetimi

#### Ön Koşul Türleri
- ✅ **Modül Tamamlama:** Önceki modül %100
- 📊 **Minimum Puan:** Quiz'de en az %70
- ⏰ **Zaman Geçirme:** Minimum X saat
- 🎯 **Özel Başarı:** Belirli rozet kazanma

---

## 📊 İlerleme Takibi ve Analitik

### Öğrenci İlerleme Paneli

```
📈 İLERLEME PANELİ
├── 📊 Genel İlerleme
│   ├── Tamamlama yüzdesi
│   ├── Harcanan süre
│   ├── Ortalama puan
│   └── Aktif gün sayısı
├── 📚 Modül Bazlı İlerleme
│   ├── Her modül için %
│   ├── Tamamlanan dersler
│   ├── Bekleyen ödevler
│   └── Quiz sonuçları
├── 🎯 Hedef Takibi
│   ├── Günlük hedefler
│   ├── Haftalık hedefler
│   ├── Milestone'lar
│   └── Deadline'lar
└── 📊 Performans Analizi
    ├── Güçlü yönler
    ├── Gelişim alanları
    ├── Öneriler
    └── Tahminler
```

### Eğitmen Analitik Paneli

#### Sınıf Genel Görünümü
```
👥 SINIF ANALİTİĞİ
├── Katılım Oranları
├── Ortalama İlerleme
├── Başarı Dağılımı
├── Risk Altındaki Öğrenciler
└── Trend Analizleri
```

#### Detaylı Raporlar
1. **İçerik Performansı**
   - En çok izlenen içerikler
   - Tamamlanma oranları
   - Ortalama geçirilen süre
   - Geri bildirim skorları

2. **Öğrenci Segmentasyonu**
   - Hızlı öğrenenler
   - Normal tempo
   - Destek gerektirenler
   - Pasif öğrenciler

### Öğrenme Analitiği

#### xAPI Verileri
```
📊 xAPI VERİ NOKTALARI
├── Verb (Eylem)
│   ├── Started
│   ├── Completed
│   ├── Passed/Failed
│   └── Interacted
├── Object (Nesne)
│   ├── Video
│   ├── Quiz
│   ├── Document
│   └── Simulation
└── Context (Bağlam)
    ├── Duration
    ├── Score
    ├── Location
    └── Device
```

---

## 🛠️ Gelişmiş Özellikler

### AI Destekli Özellikler

#### Otomatik İçerik Önerisi
- Öğrenci performansına göre
- Öğrenme stiline uygun
- Zorluk seviyesi eşleştirme

#### Akıllı Değerlendirme
- Otomatik not verme
- Plagiarism kontrolü
- Kod kalitesi analizi

### Entegrasyonlar

#### LTI (Learning Tools Interoperability)
- Harici araç entegrasyonu
- Single Sign-On
- Not senkronizasyonu

#### API Erişimi
```
API ENDPOINTS
├── GET /api/courses
├── POST /api/content
├── PUT /api/progress
└── GET /api/analytics
```

---

## 💡 En İyi Uygulamalar

### İçerik Oluşturma
1. **Mikroöğrenme Yaklaşımı**
   - 5-10 dakikalık içerikler
   - Tek konsept odaklı
   - Hızlı tüketilebilir

2. **Multimedya Dengesi**
   - %40 Video
   - %30 Okuma
   - %20 Pratik
   - %10 Değerlendirme

3. **Erişilebilirlik**
   - Altyazı ve transkript
   - Yüksek kontrast
   - Klavye navigasyonu
   - Ekran okuyucu uyumu

### Öğrenci Motivasyonu
- 🎯 Net öğrenme hedefleri
- 🏆 Düzenli ödüllendirme
- 💬 Aktif geri bildirim
- 👥 Sosyal öğrenme fırsatları

---

**📚 Eğitim Yönetimi modülü, BDC platformunun öğrenme deneyimini zenginleştiren en kapsamlı modülüdür. Etkili kullanım için düzenli içerik güncellemesi ve öğrenci geri bildirimlerini dikkate almak kritik öneme sahiptir.**

*Son güncelleme: 27 Haziran 2025 | Versiyon 1.0*