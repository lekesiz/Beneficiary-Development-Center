# BDC Platform - Program Yönetimi Detaylı Rehberi

## 🎯 Bu Belge Hakkında

Program Yönetimi modülü, BDC platformunda eğitim ve gelişim programlarının oluşturulması, planlanması, yürütülmesi ve takibini sağlayan temel modüldür. Bu belgede, program yönetiminin tüm yönleri detaylıca açıklanmaktadır.

---

## 📋 İçindekiler

1. [Program Yönetimi Genel Bakış](#program-yönetimi-genel-bakış)
2. [Program Listesi ve Arama](#program-listesi-ve-arama)
3. [Yeni Program Oluşturma](#yeni-program-oluşturma)
4. [Program Detayları ve Düzenleme](#program-detayları-ve-düzenleme)
5. [Müfredat ve İçerik Yönetimi](#müfredat-ve-i̇çerik-yönetimi)
6. [Kayıt ve Kontenjan Yönetimi](#kayıt-ve-kontenjan-yönetimi)
7. [Program Takvimi ve Planlama](#program-takvimi-ve-planlama)
8. [Eğitmen Atama ve Yönetimi](#eğitmen-atama-ve-yönetimi)
9. [Program İzleme ve Raporlama](#program-i̇zleme-ve-raporlama)
10. [Program Şablonları ve Kopyalama](#program-şablonları-ve-kopyalama)

---

## 📚 Program Yönetimi Genel Bakış

### Erişim Yolu
```
Ana Menü → Programlar → Program Listesi
```

### Kimler Erişebilir?
- ✅ **Yönetici:** Tüm programları oluşturma, düzenleme, silme
- ✅ **Eğitmen:** Kendisine atanan programları düzenleme
- ⚠️ **Öğrenci:** Sadece kayıtlı olduğu programları görüntüleme

### Program Nedir?
Program, belirli bir süre içinde, belirli hedefler doğrultusunda yapılandırılmış eğitim ve gelişim aktiviteleridir. Her program kendi müfredatı, takvimi ve değerlendirme sistemine sahiptir.

### Program Türleri
```
📚 PROGRAM TÜRLERİ

1. 🎯 Bootcamp
   - Yoğun ve hızlandırılmış eğitim
   - 8-24 hafta süre
   - Tam zamanlı katılım

2. 📖 Kurs
   - Standart tempolu eğitim
   - 4-12 hafta süre
   - Esnek katılım

3. 🏃 Workshop
   - Kısa süreli atölye çalışması
   - 1-5 gün süre
   - Pratik odaklı

4. 🎓 Sertifika Programı
   - Kapsamlı eğitim
   - 3-6 ay süre
   - Sertifika odaklı

5. 🌟 Mentorlük
   - Birebir veya grup mentorlük
   - Esnek süre
   - Kişiselleştirilmiş
```

---

## 📋 Program Listesi ve Arama

### Liste Görünümü

Program listesi ekranının yapısı:

```
Program Listesi Ekranı
├── 📊 Özet İstatistikler
├── 🔍 Arama ve Filtreler
├── 📋 Program Tablosu/Kartları
├── 📄 Sayfalama
└── ⚡ Hızlı İşlemler
```

### Özet İstatistikler

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Toplam      │ Aktif       │ Yaklaşan    │ Tamamlanan  │
│ Program     │ Programlar  │ Programlar  │ Programlar  │
│    45       │     12      │      8      │     25      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Program Tablosu

| Sütun | Açıklama | İşlemler |
|-------|----------|----------|
| **Kod** | Program kodu (WEB-2025-01) | Sıralanabilir |
| **Program Adı** | Programın tam adı | Tıklanabilir |
| **Tür** | Bootcamp/Kurs/Workshop | Filtrelenebilir |
| **Durum** | Aktif/Planlanan/Tamamlanan | Renkli badge |
| **Başlangıç** | Başlangıç tarihi | Sıralanabilir |
| **Süre** | Program süresi | - |
| **Kontenjan** | Dolu/Toplam | Progress bar |
| **Eğitmen** | Atanan eğitmenler | Tıklanabilir |
| **İşlemler** | Düzenle/Kopyala/Arşivle | Dropdown menü |

### Arama ve Filtreleme

**🔍 Arama Alanları:**
```
Arama Kutusu: [Program adı, kod veya açıklama...]
```

**🎛️ Filtreler:**

```
Program Türü:     [▼ Tümü          ]
Durum:           [▼ Tümü          ]
Eğitmen:         [▼ Tümü          ]
Başlangıç:       [__/__/____] - [__/__/____]
Süre:            [Min: 1 hafta] - [Max: 6 ay]
Kontenjan:       [✓] Dolu  [✓] Müsait  [✓] Bekleme
```

### Görünüm Seçenekleri

```
Görünüm: [🔲 Tablo] [🔳 Kart] [📅 Takvim]

Sıralama: [▼ Başlangıç Tarihi (Yakından Uzağa)]
```

**Kart Görünümü Örneği:**
```
┌─────────────────────────────────────┐
│ 🎯 Web Geliştirme Bootcamp         │
│ WEB-2025-01                         │
│                                     │
│ 📅 01.08.2025 - 01.11.2025         │
│ ⏱️ 12 Hafta | 360 Saat             │
│ 👥 18/20 Kayıtlı                   │
│ 👨‍🏫 Mehmet Öz, Ayşe Kaya          │
│                                     │
│ [Detay] [Düzenle] [Kayıtlar]       │
└─────────────────────────────────────┘
```

---

## ➕ Yeni Program Oluşturma

### Program Oluşturma Sihirbazı

Yeni program oluşturma 5 adımda tamamlanır:

```
Adımlar: [1.Temel] → [2.Detay] → [3.Müfredat] → [4.Takvim] → [5.Onay]
```

### Adım 1: Temel Bilgiler

```
📝 TEMEL BİLGİLER

Program Türü*: [▼ Seçiniz         ]
              [ ] Bootcamp
              [ ] Kurs
              [ ] Workshop
              [ ] Sertifika Programı
              [ ] Mentorlük

Program Adı*: [________________________]
              Örn: Web Geliştirme Bootcamp

Program Kodu*: [WEB-2025-___] (Otomatik)
               Format: TÜR-YIL-SIRA

Kısa Açıklama*: [_______________________]
                Max 200 karakter

Kategori*: [▼ Teknoloji     ]
          [ ] Teknoloji
          [ ] İş Geliştirme
          [ ] Dil Eğitimi
          [ ] Kişisel Gelişim
          [ ] Sanat ve Tasarım
```

### Adım 2: Detaylı Bilgiler

```
📋 DETAYLI BİLGİLER

Detaylı Açıklama*:
┌─────────────────────────────────────┐
│ Program hakkında detaylı bilgi...   │
│ - Hedefler                          │
│ - Kazanımlar                        │
│ - Kimler katılabilir                │
│                                     │
└─────────────────────────────────────┘

Hedef Kitle*: [▼ Çoklu Seçim    ]
             [✓] Üniversite Öğrencileri
             [✓] Yeni Mezunlar
             [ ] Çalışanlar
             [ ] Girişimciler

Ön Koşullar:
[✓] Temel bilgisayar bilgisi
[✓] İngilizce okuma becerisi
[ ] Programlama deneyimi
[+ Yeni ekle]

Kazanımlar*:
1. [HTML/CSS ile web sayfası tasarlama]
2. [JavaScript ile dinamik uygulamalar]
3. [React.js ile modern web geliştirme]
[+ Kazanım ekle]

Eğitim Dili: [▼ Türkçe    ]
Format:      ( ) Yüz yüze
             ( ) Online
             (•) Hibrit
```

### Adım 3: Müfredat Planlama

```
📚 MÜFREDAT PLANLAMA

[+ Modül Ekle]

Modül 1: HTML ve CSS Temelleri
├── Süre: 2 hafta (40 saat)
├── İçerikler:
│   ├── HTML5 yapısı ve semantik
│   ├── CSS3 ve modern özellikler
│   ├── Responsive tasarım
│   └── Flexbox ve Grid
├── Değerlendirme: Quiz + Proje
└── [Düzenle] [Sil] [↑] [↓]

Modül 2: JavaScript Programlama
├── Süre: 3 hafta (60 saat)
├── İçerikler:
│   ├── JavaScript temelleri
│   ├── DOM manipülasyonu
│   ├── ES6+ özellikleri
│   └── Asenkron programlama
├── Değerlendirme: 2 Quiz + Ödev
└── [Düzenle] [Sil] [↑] [↓]

[+ Modül Ekle]

Toplam Süre: 12 hafta (360 saat)
```

### Adım 4: Takvim ve Planlama

```
📅 TAKVİM VE PLANLAMA

Başlangıç Tarihi*: [01/08/2025]
Bitiş Tarihi*:     [01/11/2025]
                   (Otomatik hesaplandı)

Ders Günleri*: [✓] Pazartesi  [✓] Salı
               [✓] Çarşamba   [✓] Perşembe
               [✓] Cuma       [ ] Cumartesi
               [ ] Pazar

Ders Saatleri*: [09:00] - [13:00]
                [14:00] - [18:00]

Tatil Günleri: [29/10/2025] Cumhuriyet Bayramı
               [+ Tatil ekle]

Kayıt Açılış:  [01/07/2025]
Kayıt Kapanış: [25/07/2025]

Kontenjan*:
Min: [10] Max: [20] Bekleme: [5]
```

### Adım 5: Onay ve Oluşturma

```
✅ ÖZET VE ONAY

Program: Web Geliştirme Bootcamp
Tür: Bootcamp
Süre: 12 hafta (360 saat)
Tarih: 01.08.2025 - 01.11.2025
Kontenjan: 10-20 kişi
Format: Hibrit

Müfredat:
├── 6 Ana Modül
├── 15 Alt Konu
├── 8 Değerlendirme
└── 1 Final Projesi

[✓] Bilgileri kontrol ettim
[✓] Program kurallarını onaylıyorum

[Geri] [Taslak Kaydet] [Programı Oluştur]
```

---

## 📝 Program Detayları ve Düzenleme

### Program Detay Sayfası

Program detay sayfası sekmelere ayrılmıştır:

```
Program: Web Geliştirme Bootcamp
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Genel] [Müfredat] [Takvim] [Kayıtlar] [Eğitmenler] 
[Materyaller] [Değerlendirmeler] [İstatistikler] [Ayarlar]
```

### Genel Bilgiler Sekmesi

```
📋 GENEL BİLGİLER

Durum: [🟢 Aktif ▼]
       [ ] Aktif - Devam ediyor
       [ ] Planlanan - Henüz başlamadı
       [ ] Tamamlanan - Bitmiş
       [ ] İptal - Gerçekleşmedi
       [ ] Askıda - Geçici durduruldu

Program Bilgileri:
├── Kod: WEB-2025-01
├── Başlangıç: 01.08.2025
├── Bitiş: 01.11.2025
├── Süre: 12 hafta
├── Format: Hibrit
└── Dil: Türkçe

İstatistikler:
├── Kayıtlı: 18/20
├── Aktif: 17
├── Bırakanlar: 1
├── Ortalama Devam: %92
└── Memnuniyet: 4.8/5

[Düzenle] [Duyuru Yap] [Rapor Al]
```

### Müfredat Sekmesi

```
📚 MÜFREDAT YÖNETİMİ

[+ Yeni Modül] [⬇ İçe Aktar] [⬆ Dışa Aktar]

━━━ Modül 1: HTML ve CSS ━━━━━━━━━━━
Süre: 2 hafta | İlerleme: ████████░░ 85%

▼ Ders 1.1: HTML5 Temelleri (4 saat)
  ├── Video: HTML5 Giriş (45 dk) ✓
  ├── Okuma: HTML Etiketleri PDF ✓
  ├── Quiz: HTML Temelleri (20 soru) ✓
  └── Ödev: İlk Web Sayfam

▼ Ders 1.2: CSS3 Styling (4 saat)
  ├── Video: CSS Selectors (60 dk)
  ├── Lab: CSS Uygulamaları
  └── Proje: Portfolio Sayfası

[Düzenle] [Sırala] [Materyaller]
```

### Takvim Sekmesi

```
📅 PROGRAM TAKVİMİ

Ağustos 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pzt Sal Çar Per Cum Cmt Paz
                  1   2   3
 4   5   6   7   8   9  10
[M1][M1][M1][M1][M1] -   -
11  12  13  14  15  16  17
[M2][M2][M2][M2][Q1] -   -
18  19  20  21  22  23  24
[M3][M3][M3][M3][M3] -   -
25  26  27  28  29  30  31
[M4][M4][M4][M4][T ] -   -

Açıklama:
[M#] Modül dersi
[Q#] Quiz
[T ] Tatil
[ - ] Ders yok

[Takvimi Düzenle] [Excel İndir] [Senkronize Et]
```

### Kayıtlar Sekmesi

```
👥 KAYITLI ÖĞRENCİLER (18/20)

[🔍 Ara...] [⚡ Filtrele] [+ Öğrenci Ekle]

┌────┬──────────────┬─────────┬──────────┬─────────┐
│ ID │ Ad Soyad     │ Durum   │ İlerleme │ İşlemler│
├────┼──────────────┼─────────┼──────────┼─────────┤
│ 01 │ Ahmet Yılmaz │ ✅ Aktif│ ███░ 76% │ [...]   │
│ 02 │ Ayşe Kaya    │ ✅ Aktif│ ████ 92% │ [...]   │
│ 03 │ Mehmet Öz    │ ⚠️ Risk │ ██░░ 45% │ [...]   │
└────┴──────────────┴─────────┴──────────┴─────────┘

Toplu İşlemler:
[E-posta Gönder] [Rapor Al] [Sertifika Oluştur]
```

---

## 📚 Müfredat ve İçerik Yönetimi

### İçerik Türleri

```
📁 İÇERİK TÜRLERİ

1. 🎥 Video Dersler
   - MP4, WebM formatları
   - Altyazı desteği
   - Çözünürlük seçenekleri
   - İzleme takibi

2. 📄 Okuma Materyalleri
   - PDF, DOCX, PPT
   - Online görüntüleme
   - İndirme kontrolü
   - Sayfa takibi

3. 💻 Canlı Dersler
   - Zoom/Teams entegrasyonu
   - Otomatik kayıt
   - Katılım takibi
   - Sohbet logları

4. 🧪 Laboratuvar/Pratik
   - Kod editörü
   - Simülasyonlar
   - Hands-on aktiviteler
   - Gerçek zamanlı feedback

5. 📝 Ödevler
   - Dosya yükleme
   - Online form
   - Kod gönderimi
   - Peer review

6. 🎯 Projeler
   - Milestone takibi
   - Grup çalışması
   - Versiyon kontrolü
   - Sunum hazırlama
```

### İçerik Ekleme

**Video Ders Ekleme:**
```
🎥 YENİ VİDEO DERS

Başlık*: [JavaScript Temelleri - Ders 1]

Video Yükleme:
[Dosya Seç] veya [YouTube/Vimeo URL]
├── intro-js.mp4 (450MB) ⬆️ %75
└── Tahmini süre: 2 dk

Video Detayları:
├── Süre: 45:30 (otomatik)
├── Çözünürlük: 1080p
├── Altyazı: [Yükle] TR/EN
└── Bölümler: [+ Ekle]
    ├── 00:00 Giriş
    ├── 05:30 Değişkenler
    └── 15:45 Veri Tipleri

İzleme Ayarları:
[✓] İleri sarma engellensin
[✓] Minimum %80 izlensin
[ ] Hız ayarına izin ver
[✓] Notlar alınabilsin

[İptal] [Taslak] [Yayınla]
```

### İçerik Organizasyonu

```
📂 İÇERİK AĞACI

▼ Modül 1: HTML/CSS (40 saat)
  ▼ Hafta 1: HTML Temelleri
    ├── 🎥 HTML5 Giriş (45 dk)
    ├── 📄 HTML Cheat Sheet (PDF)
    ├── 💻 Canlı Ders: Semantik HTML
    ├── 🧪 Lab: İlk Web Sayfan
    └── 📝 Ödev: Portfolio Tasarımı
  
  ▼ Hafta 2: CSS ve Responsive
    ├── 🎥 CSS3 Temelleri (60 dk)
    ├── 🎥 Flexbox Mastery (45 dk)
    ├── 📄 CSS Best Practices
    ├── 🧪 Lab: Responsive Tasarım
    └── 🎯 Proje: Landing Page

[Sürükle ve Bırak ile Sıralama]
```

### İçerik Erişim Kontrolü

```
🔐 ERİŞİM KONTROLÜ

Erişim Tipi: (•) Sıralı
            ( ) Serbest
            ( ) Tarih Bazlı

Sıralı Erişim Kuralları:
├── Önceki ders %100 tamamlanmalı
├── Quiz'den min %70 alınmalı
└── Ödev teslim edilmiş olmalı

Kilitleme Durumu:
├── 🔓 Modül 1: Açık
├── 🔓 Modül 2: Açık
├── 🔒 Modül 3: 15.08'de açılacak
└── 🔒 Modül 4-6: Kilitli
```

---

## 👥 Kayıt ve Kontenjan Yönetimi

### Kayıt Ayarları

```
⚙️ KAYIT AYARLARI

Kayıt Durumu: [✓] Açık
              [ ] Kapalı
              [ ] Sadece Davetliler

Kayıt Dönemi:
Başlangıç: [01/07/2025 09:00]
Bitiş:     [25/07/2025 23:59]
Erken Kayıt: [15/06/2025] (%10 indirim)

Kontenjan:
├── Minimum: [10] kişi
├── Maximum: [20] kişi
├── Bekleme: [5] kişi
└── Doluluk: ████████░░ 18/20

Kayıt Koşulları:
[✓] Yaş sınırı: 18-35
[✓] Eğitim: Min. Lise
[ ] Deneyim: Gerekli değil
[✓] Ön test: Zorunlu
[+] Koşul ekle
```

### Kayıt Formu Özelleştirme

```
📝 KAYIT FORMU

Zorunlu Alanlar:
[✓] Ad Soyad
[✓] TC/Pasaport
[✓] E-posta
[✓] Telefon
[✓] Eğitim Durumu

Ek Alanlar:
[✓] Motivasyon Mektubu
[✓] CV Yükleme
[ ] Referans
[✓] Nasıl Duydunuz?
[+] Alan ekle

Form Önizleme: [👁️ Görüntüle]
```

### Kayıt Onay Süreci

```
✅ KAYIT ONAY SÜRECİ

Onay Tipi: ( ) Otomatik
           (•) Manuel
           ( ) Koşullu

Manuel Onay Akışı:
1. Başvuru alınır
2. Ön değerlendirme (sistem)
3. Eğitmen incelemesi
4. Yönetici onayı
5. Sonuç bildirimi

Değerlendirme Kriterleri:
├── [40%] Motivasyon
├── [30%] Ön Bilgi
├── [20%] Uygunluk
└── [10%] Referans

Bekleme Listesi:
Otomatik sıralama: (•) Başvuru sırası
                   ( ) Puan sırası
                   ( ) Öncelik grupları
```

### Kayıt İstatistikleri

```
📊 KAYIT İSTATİSTİKLERİ

Başvuru Özeti:
├── Toplam Başvuru: 45
├── Onaylanan: 20
├── Bekleme Listesi: 5
├── Reddedilen: 15
└── Değerlendirmede: 5

Kayıt Kaynakları:
├── Web Sitesi: %40 ████
├── Sosyal Medya: %25 ██
├── E-posta: %20 ██
├── Referans: %10 █
└── Diğer: %5 ▌

Demografik Dağılım:
├── Yaş Ort: 24.5
├── Cinsiyet: %60 K / %40 E
├── Eğitim: %70 Üniversite
└── Şehir: 12 farklı il
```

---

## 📅 Program Takvimi ve Planlama

### Takvim Görünümleri

```
📅 TAKVİM GÖRÜNÜMLERİ

[Aylık] [Haftalık] [Günlük] [Liste]

Filtreler: [✓] Dersler [✓] Ödevler 
          [✓] Sınavlar [✓] Etkinlikler
```

**Haftalık Görünüm:**
```
Hafta: 12-18 Ağustos 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        09:00   12:00   15:00   18:00
Pzt  12 ┤═══════╪═══════┤       │
        │ HTML  │ Lab    │       │
Sal  13 ┤═══════╪═══════┤       │
        │ CSS   │Mentoring       │
Çar  14 ┤═══════════════════════┤
        │    Canlı Ders (Zoom)  │
Per  15 ┤═══════┤       ┤═══════┤
        │ JS    │       │ Quiz  │
Cum  16 ┤═══════════════┤       │
        │  Proje Sunumları      │
```

### Ders Planlama

```
📝 DERS PLANLAMA

Yeni Ders Ekle:
├── Başlık: [_____________________]
├── Tür: [▼ Canlı Ders    ]
├── Tarih: [15/08/2025]
├── Saat: [14:00] - [17:00]
├── Mekan: ( ) Fiziksel: [Sınıf A]
│          (•) Online: [Zoom Link]
│          ( ) Hibrit
├── Eğitmen: [▼ Mehmet Öz ]
├── İçerik: [▼ Modül 3.2  ]
└── Tekrar: [ ] Her hafta bu gün

Çakışma Kontrolü: ✅ Uygun
[İptal] [Planla]
```

### Otomatik Hatırlatıcılar

```
🔔 HATIRLAMA AYARLARI

Ders Hatırlatmaları:
├── [✓] 1 gün önce - E-posta
├── [✓] 2 saat önce - SMS
├── [✓] 30 dk önce - Push bildirim
└── [✓] Ders başında - Otomatik link

Ödev Hatırlatmaları:
├── [✓] 3 gün önce
├── [✓] 1 gün önce
└── [✓] Son 2 saat

Özel Hatırlatmalar:
[+ Yeni hatırlatma ekle]
```

---

## 👨‍🏫 Eğitmen Atama ve Yönetimi

### Eğitmen Havuzu

```
👥 EĞİTMEN HAVUZU

[🔍 Eğitmen ara...] [+ Yeni Eğitmen]

Mevcut Eğitmenler:
┌─────────────────┬────────────┬──────────┬────────┐
│ Eğitmen         │ Uzmanlık   │ Programlar│ Durum  │
├─────────────────┼────────────┼──────────┼────────┤
│ Mehmet Öz       │ Frontend   │ 3 aktif  │ ✅ Müsait│
│ Ayşe Kaya       │ Backend    │ 2 aktif  │ ⚠️ Yoğun │
│ Ali Demir       │ Full Stack │ 1 aktif  │ ✅ Müsait│
│ Zeynep Ak       │ UI/UX      │ 0 aktif  │ ✅ Müsait│
└─────────────────┴────────────┴──────────┴────────┘
```

### Eğitmen Atama

```
👨‍🏫 EĞİTMEN ATAMA

Program: Web Geliştirme Bootcamp

Ana Eğitmen*: [▼ Mehmet Öz    ]
             Uzmanlık: Frontend Dev
             Müsaitlik: ✅
             
Yardımcı Eğitmenler:
├── [▼ Ayşe Kaya     ] - Backend
├── [▼ Seçiniz       ] 
└── [+ Eğitmen ekle]

Sorumluluk Dağılımı:
├── Mehmet Öz: %60 (216 saat)
│   └── Modül 1, 2, 3, 6
├── Ayşe Kaya: %40 (144 saat)
│   └── Modül 4, 5
└── Toplam: 360 saat ✓

[Kaydet] [İptal]
```

### Eğitmen Performansı

```
📊 EĞİTMEN PERFORMANSI

Mehmet Öz - Frontend Developer
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Genel İstatistikler:
├── Verdiği Program: 12
├── Toplam Öğrenci: 245
├── Ortalama Puan: 4.8/5
└── Tamamlama Oranı: %92

Son Değerlendirmeler:
⭐⭐⭐⭐⭐ "Harika bir eğitmen!"
⭐⭐⭐⭐⭐ "Çok açıklayıcı"
⭐⭐⭐⭐☆ "Biraz hızlı ilerliyor"

Güçlü Yönler:
✓ Teknik bilgi
✓ İletişim
✓ Sabır ve anlayış

[Detaylı Rapor] [Geri Bildirimler]
```

---

## 📊 Program İzleme ve Raporlama

### Canlı İzleme Paneli

```
📊 CANLI İZLEME PANELİ

Web Geliştirme Bootcamp - Hafta 5/12
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Genel Durum:
├── İlerleme: ████████░░░░░░░░ 42%
├── Aktif Öğrenci: 17/18 (🟢)
├── Bugünkü Ders: JavaScript Arrays
└── Sonraki: Quiz #3 (2 gün)

Anlık Metrikler:
┌────────────────┬─────────┐
│ Online Öğrenci │   12    │
│ Ders İzleme    │   8     │
│ Ödev Yapan     │   4     │
│ Forumda Aktif  │   3     │
└────────────────┴─────────┘

Uyarılar:
⚠️ 3 öğrenci 1 haftadır girmedi
⚠️ Quiz #2 ortalaması düşük (%65)
```

### Detaylı Raporlar

```
📈 PROGRAM RAPORU

Rapor Türü: [▼ Haftalık Özet    ]
Dönem: [05.08.2025] - [11.08.2025]

1. Katılım Raporu
   ├── Ortalama Katılım: %89
   ├── En Yüksek: Salı (%95)
   ├── En Düşük: Cuma (%78)
   └── Trend: ↗️ Artıyor

2. Başarı Analizi
   ├── Quiz Ortalaması: 78/100
   ├── Ödev Teslim: %94
   ├── Proje İlerlemesi: %67
   └── Risk Altında: 2 öğrenci

3. İçerik Performansı
   ├── En Çok İzlenen: JS Basics
   ├── En Az İzlenen: Git/GitHub
   ├── Tekrar İzleme: %34
   └── Ortalama İzleme: 87 dk/gün

[PDF İndir] [Excel İndir] [E-posta]
```

### Karşılaştırmalı Analiz

```
📊 KARŞILAŞTIRMALI ANALİZ

Program Karşılaştırma:
                  WEB-2025-01  WEB-2024-03
Tamamlama:        %92 ↑        %85
Memnuniyet:       4.8 ↑        4.5  
İstihdam:         %78 →        %75
Ort. Süre:        11.5 hafta   12.8 hafta

Benchmark:
├── Sektör Ort: %82 tamamlama
├── Kurum Ort: %88 tamamlama
└── Performans: ⭐⭐⭐⭐⭐
```

---

## 📋 Program Şablonları ve Kopyalama

### Şablon Kütüphanesi

```
📚 PROGRAM ŞABLONLARI

[🔍 Şablon ara...] [+ Yeni Şablon]

Popüler Şablonlar:
┌─────────────────────────────────────┐
│ 🌟 Full Stack Web Development       │
│ 12 hafta | 360 saat | 6 modül      │
│ Kullanım: 15 kez                    │
│ [Önizle] [Kullan] [Düzenle]        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🌟 Digital Marketing Fundamentals   │
│ 8 hafta | 160 saat | 4 modül       │
│ Kullanım: 8 kez                     │
│ [Önizle] [Kullan] [Düzenle]        │
└─────────────────────────────────────┘

Kategoriler:
[Teknoloji] [İş] [Dil] [Sanat] [Tümü]
```

### Program Kopyalama

```
📋 PROGRAM KOPYALAMA

Kaynak Program: Web Dev Bootcamp 2024
Hedef Program: Web Dev Bootcamp 2025

Kopyalanacak Öğeler:
[✓] Temel Bilgiler
[✓] Müfredat ve İçerik
[✓] Değerlendirmeler
[ ] Kayıtlı Öğrenciler
[✓] Eğitmen Atamaları
[ ] Takvim (Tarihler güncellenecek)
[✓] Materyaller
[ ] Forumlar ve Tartışmalar

Tarih Güncelleme:
(•) Otomatik kaydır (+1 yıl)
( ) Manuel ayarla
( ) Değiştirme

[İptal] [Önizle] [Kopyala]
```

### Şablon Oluşturma

```
💾 ŞABLON OLARAK KAYDET

Şablon Adı*: [Full Stack Bootcamp Template]

Açıklama: [12 haftalık yoğun web geliştirme
          programı şablonu. Frontend ve 
          backend teknolojilerini kapsar.]

Kategori*: [▼ Teknoloji    ]

Dahil Edilecekler:
[✓] Program yapısı
[✓] Müfredat detayları
[✓] Değerlendirme kriterleri
[✓] Zaman planı (göreceli)
[ ] Spesifik içerikler
[✓] Kayıt formları

Paylaşım:
( ) Özel - Sadece ben
(•) Kurum - Tüm eğitmenler
( ) Herkese açık

[İptal] [Şablon Oluştur]
```

---

## 🔧 Gelişmiş Özellikler

### Otomasyonlar

```
⚡ PROGRAM OTOMASYONLARI

Aktif Otomasyonlar:
├── ✅ Haftalık ilerleme raporu
├── ✅ Düşük katılım uyarısı
├── ✅ Ödev hatırlatıcıları
├── ✅ Sertifika oluşturma
└── ⏸️ Anket gönderimi

Yeni Otomasyon Ekle:
Tetikleyici: [▼ Öğrenci %80 tamamladığında]
Aksiyon: [▼ Tebrik e-postası gönder]
[Kural Ekle]
```

### Entegrasyonlar

```
🔗 ENTEGRASYONLAR

Aktif Entegrasyonlar:
├── ✅ Zoom - Canlı dersler
├── ✅ Google Calendar - Takvim
├── ✅ Slack - Bildirimler
├── ✅ GitHub - Kod ödevleri
└── ⏸️ LinkedIn Learning

Yeni Entegrasyon:
[+ Entegrasyon Ekle]
```

### API ve Webhooks

```
🔌 API & WEBHOOKS

Webhook URL: https://example.com/webhook
Events:
[✓] program.created
[✓] program.started
[✓] student.enrolled
[✓] student.completed
[ ] assessment.submitted

Test: [Webhook Test Et]
```

---

## 💡 İpuçları ve En İyi Uygulamalar

### Başarılı Program Yönetimi

1. **Program Tasarımı:**
   - Hedef kitleyi net belirleyin
   - Gerçekçi süre planlayın
   - Modüler yapı kullanın
   - Esnek takvim oluşturun

2. **İçerik Organizasyonu:**
   - %70 pratik, %30 teori
   - Kısa ve öz videolar
   - İnteraktif içerikler
   - Düzenli değerlendirmeler

3. **Öğrenci Takibi:**
   - Haftalık check-in'ler
   - Erken uyarı sistemi
   - Kişiselleştirilmiş destek
   - Peer learning teşviki

### Sık Kullanılan Kısayollar

| Kısayol | İşlev |
|---------|-------|
| `Ctrl+P` | Yeni program |
| `Ctrl+M` | Modül ekle |
| `Ctrl+S` | Kaydet |
| `F2` | Düzenleme modu |
| `Esc` | İptal/Çıkış |

---

**📚 Program Yönetimi, eğitim süreçlerinin başarısı için kritik öneme sahiptir. Doğru planlama ve takip ile öğrenci başarısını maksimize edebilirsiniz!**

*Son güncelleme: 27 Haziran 2025 | Versiyon 1.0*