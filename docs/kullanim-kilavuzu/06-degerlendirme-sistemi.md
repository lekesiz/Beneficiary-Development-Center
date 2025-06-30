# BDC Platform - Değerlendirme Sistemi Detaylı Rehberi

## 🎯 Bu Belge Hakkında

Değerlendirme Sistemi modülü, BDC platformunda öğrenci başarısının ölçülmesi, takibi ve raporlanması için kullanılan kapsamlı bir sistemdir. Bu belgede sınav, quiz, ödev değerlendirmesi ve notlandırma sisteminin tüm detayları açıklanmaktadır.

---

## 📋 İçindekiler

1. [Değerlendirme Sistemi Genel Bakış](#değerlendirme-sistemi-genel-bakış)
2. [Değerlendirme Türleri](#değerlendirme-türleri)
3. [Sınav ve Quiz Yönetimi](#sınav-ve-quiz-yönetimi)
4. [Soru Bankası](#soru-bankası)
5. [Değerlendirme Oluşturma](#değerlendirme-oluşturma)
6. [Notlandırma ve Puanlama](#notlandırma-ve-puanlama)
7. [Rubrik Yönetimi](#rubrik-yönetimi)
8. [Geri Bildirim Sistemi](#geri-bildirim-sistemi)
9. [Raporlama ve Analiz](#raporlama-ve-analiz)
10. [Güvenlik ve Denetim](#güvenlik-ve-denetim)

---

## 📊 Değerlendirme Sistemi Genel Bakış

### Erişim Yolu
```
Ana Menü → Değerlendirmeler → Değerlendirme Yönetimi
veya
Program Detayı → Değerlendirmeler
```

### Kimler Erişebilir?
- ✅ **Yönetici:** Tüm değerlendirmeleri oluşturma ve yönetme
- ✅ **Eğitmen:** Kendi programlarındaki değerlendirmeleri yönetme
- ⚠️ **Öğrenci:** Sadece kendisine atanan değerlendirmelere erişim

### Değerlendirme Sistemi Nedir?
Öğrencilerin öğrenme çıktılarını ölçmek, gelişimlerini takip etmek ve başarı durumlarını belirlemek için kullanılan çok yönlü bir sistemdir.

### Ana Bileşenler
```
📊 DEĞERLENDİRME SİSTEMİ
├── 📝 Sınavlar
├── ❓ Quiz'ler
├── 📄 Ödevler
├── 🎯 Projeler
├── 💬 Tartışmalar
├── 🎤 Sunumlar
├── 📊 Portfolyolar
└── 🏆 Sertifikasyonlar
```

---

## 📝 Değerlendirme Türleri

### 1. Formative (Biçimlendirici) Değerlendirme

```
📈 BİÇİMLENDİRİCİ DEĞERLENDİRME
├── Amaç: Öğrenme sürecini izleme
├── Sıklık: Düzenli aralıklarla
├── Puan Etkisi: Düşük (%10-20)
└── Örnekler:
    ├── Haftalık quiz'ler
    ├── Sınıf içi aktiviteler
    ├── Peer review
    └── Self-assessment
```

### 2. Summative (Sonuç Odaklı) Değerlendirme

```
🎯 SONUÇ ODAKLI DEĞERLENDİRME
├── Amaç: Öğrenme çıktılarını ölçme
├── Sıklık: Dönem sonu
├── Puan Etkisi: Yüksek (%60-80)
└── Örnekler:
    ├── Final sınavları
    ├── Dönem projeleri
    ├── Sertifika sınavları
    └── Capstone projeler
```

### 3. Diagnostic (Tanısal) Değerlendirme

```
🔍 TANISAL DEĞERLENDİRME
├── Amaç: Başlangıç seviyesi belirleme
├── Sıklık: Program başında
├── Puan Etkisi: Yok
└── Örnekler:
    ├── Seviye tespit sınavı
    ├── Ön bilgi değerlendirmesi
    ├── Beceri analizi
    └── İlgi alanı anketi
```

---

## 📝 Sınav ve Quiz Yönetimi

### Sınav Oluşturma Süreci

#### Adım 1: Temel Bilgiler
```
📋 SINAV BİLGİLERİ
├── Sınav Adı* (Örn: "Web Geliştirme Final Sınavı")
├── Sınav Kodu* (Örn: "WEB-FIN-2025")
├── Açıklama (500 karakter)
├── Talimatlar (detaylı açıklama)
├── Sınav Türü
│   ├── Online
│   ├── Yüz yüze
│   └── Karma
└── Değerlendirme Kategorisi
    ├── Quiz
    ├── Ara sınav
    ├── Final
    └── Özel
```

#### Adım 2: Zaman ve Erişim Ayarları
```
⏰ ZAMAN AYARLARI
├── Başlangıç Tarihi ve Saati*
├── Bitiş Tarihi ve Saati*
├── Sınav Süresi (dakika)*
├── Geç Başlama İzni
│   ├── İzin ver/verme
│   └── Maksimum gecikme (dakika)
├── Zaman Aşımı Politikası
│   ├── Otomatik gönder
│   ├── Uyarı ver
│   └── Ek süre tanı
└── Deneme Hakkı
    ├── Tek deneme
    ├── Sınırlı deneme (sayı)
    └── Sınırsız deneme
```

#### Adım 3: Güvenlik Ayarları
```
🔒 GÜVENLİK AYARLARI
├── Tarayıcı Kilitleme (Lockdown Browser)
├── Webcam Gözetimi
├── Ekran Kayıt
├── Kopya Önleme
│   ├── Sağ tık engelleme
│   ├── Kopyalama engelleme
│   └── Yazdırma engelleme
├── IP Kısıtlaması
├── Soru Karıştırma
└── Şık Karıştırma
```

### Quiz Özellikleri

#### Quiz Türleri
| Tür | Açıklama | Kullanım Alanı |
|-----|----------|----------------|
| **Pop Quiz** | Anlık, kısa quiz | Ders içi kontrol |
| **Practice Quiz** | Alıştırma amaçlı | Öğrenme pekiştirme |
| **Graded Quiz** | Notlu quiz | Değerlendirme |
| **Self-Assessment** | Öz değerlendirme | Kendi kendine test |

#### Quiz Ayarları
```
⚙️ QUIZ AYARLARI
├── Anında Geri Bildirim
│   ├── Her sorudan sonra
│   ├── Quiz sonunda
│   └── Belirli tarihte
├── Doğru Cevapları Göster
│   ├── Hemen
│   ├── Tüm öğrenciler bitirince
│   └── Hiçbir zaman
├── Puan Görüntüleme
│   ├── Toplam puan
│   ├── Soru bazlı puan
│   └── Yüzde olarak
└── İlerleme Takibi
    ├── İlerleme çubuğu
    ├── Kalan süre
    └── Tamamlanan sorular
```

---

## 🏦 Soru Bankası

### Soru Bankası Yönetimi

```
📚 SORU BANKASI
├── 📁 Kategoriler
│   ├── Konu bazlı
│   ├── Zorluk seviyesi
│   ├── Öğrenme çıktısı
│   └── Soru tipi
├── 🏷️ Etiketleme Sistemi
│   ├── Bloom taksonomisi
│   ├── Beceri alanı
│   ├── Bilişsel seviye
│   └── Özel etiketler
└── 🔍 Arama ve Filtreleme
    ├── Anahtar kelime
    ├── Soru kodu
    ├── Oluşturma tarihi
    └── Kullanım sayısı
```

### Soru Türleri

#### 1. Çoktan Seçmeli
```
❓ ÇOKTAN SEÇMELİ SORU
├── Soru Metni*
├── Seçenekler (2-10 arası)
│   ├── Doğru cevap(lar)
│   └── Yanlış seçenekler
├── Puan Değeri*
├── Kısmi Puan
│   ├── Var/Yok
│   └── Puan dağılımı
└── Açıklama (opsiyonel)
```

#### 2. Doğru/Yanlış
```
✓✗ DOĞRU/YANLIŞ SORU
├── Soru Metni*
├── Doğru Cevap*
├── Puan Değeri*
└── Açıklama
```

#### 3. Boşluk Doldurma
```
📝 BOŞLUK DOLDURMA
├── Metin ve Boşluklar*
├── Kabul Edilecek Cevaplar
│   ├── Tam eşleşme
│   ├── Yakın eşleşme
│   └── Regex pattern
├── Büyük/Küçük Harf Duyarlılığı
└── Puan Değeri*
```

#### 4. Eşleştirme
```
🔗 EŞLEŞTİRME SORUSU
├── Sol Taraf Öğeleri*
├── Sağ Taraf Öğeleri*
├── Eşleşme Kuralları
│   ├── Bire bir
│   ├── Çoktan çoğa
│   └── Fazla seçenek
├── Karıştırma
└── Puanlama
    ├── Tümü doğru
    └── Kısmi puan
```

#### 5. Açık Uçlu
```
📄 AÇIK UÇLU SORU
├── Soru Metni*
├── Cevap Alanı
│   ├── Metin kutusu
│   ├── Rich text editor
│   └── Kod editörü
├── Karakter/Kelime Limiti
├── Dosya Yükleme
└── Manuel Değerlendirme
    ├── Rubrik seçimi
    └── Puanlama rehberi
```

#### 6. Kod Soruları
```
💻 KOD SORUSU
├── Problem Tanımı*
├── Başlangıç Kodu
├── Test Case'leri
│   ├── Görünür testler
│   └── Gizli testler
├── Dil Seçenekleri
│   ├── Python
│   ├── JavaScript
│   ├── Java
│   └── C++
├── Zaman/Bellek Limiti
└── Otomatik Puanlama
```

### Soru İçe/Dışa Aktarma

#### Desteklenen Formatlar
- 📄 **QTI 2.1:** Standart format
- 📊 **Excel:** Toplu düzenleme
- 📝 **Word:** Görsel sorular
- 🎯 **Moodle XML:** Uyumluluk
- 💾 **JSON:** API entegrasyonu

---

## 🛠️ Değerlendirme Oluşturma

### Değerlendirme Tasarım Süreci

#### 1. Hedef Belirleme
```
🎯 HEDEF BELİRLEME
├── Öğrenme Çıktıları
│   ├── Bilgi seviyesi
│   ├── Beceri kontrolü
│   └── Yetkinlik ölçümü
├── Bloom Taksonomisi Seviyesi
│   ├── Hatırlama
│   ├── Anlama
│   ├── Uygulama
│   ├── Analiz
│   ├── Değerlendirme
│   └── Yaratma
└── Değerlendirme Ağırlığı
```

#### 2. İçerik Planlama
```
📋 İÇERİK PLANLAMA
├── Konu Dağılımı
│   ├── Modül 1: %30
│   ├── Modül 2: %40
│   └── Modül 3: %30
├── Soru Sayısı ve Türü
│   ├── Çoktan seçmeli: 20
│   ├── Kısa cevap: 5
│   └── Açık uçlu: 2
└── Zorluk Dağılımı
    ├── Kolay: %30
    ├── Orta: %50
    └── Zor: %20
```

### Adaptif Değerlendirme

#### Akıllı Soru Seçimi
```
🤖 ADAPTİF SİSTEM
├── Başlangıç Seviyesi
│   └── İlk 5 soru orta zorlukta
├── Dinamik Ayarlama
│   ├── Doğru → Zorluk artır
│   └── Yanlış → Zorluk azalt
├── Güven Aralığı
│   └── %95 güvenle seviye belirleme
└── Minimum/Maksimum Soru
    ├── En az: 15 soru
    └── En fazla: 40 soru
```

---

## 📊 Notlandırma ve Puanlama

### Puanlama Sistemleri

#### 1. Sayısal Notlandırma
```
💯 SAYISAL NOTLANDIRMA
├── 100 Üzerinden
│   ├── Ham puan
│   ├── Ağırlıklı puan
│   └── Normalize puan
├── Harf Notu Dönüşümü
│   ├── A: 90-100
│   ├── B: 80-89
│   ├── C: 70-79
│   ├── D: 60-69
│   └── F: 0-59
└── GPA Hesaplama
    └── 4.0 ölçeği
```

#### 2. Yeterlik Bazlı
```
✅ YETERLİK BAZLI
├── Seviyeler
│   ├── Uzman
│   ├── Yeterli
│   ├── Gelişmekte
│   └── Başlangıç
├── Kriterler
│   ├── Tüm yetkinlikler
│   ├── Minimum eşik
│   └── Portfolyo kanıtı
└── İlerleme Takibi
```

### Otomatik Puanlama

#### Puanlama Kuralları
```
⚙️ PUANLAMA KURALLARI
├── Doğru Cevap Puanı
├── Yanlış Cevap
│   ├── Puan kesintisi (-1/4)
│   └── Kesinti yok
├── Boş Bırakma
│   └── 0 puan
├── Kısmi Puan
│   ├── Çoklu doğru
│   ├── Kısmi eşleşme
│   └── Adım bazlı
└── Bonus Puanlar
```

### Manuel Değerlendirme

#### Değerlendirme Arayüzü
```
📝 MANUEL DEĞERLENDİRME
├── Öğrenci Cevabı Görüntüleme
├── Rubrik Uygulama
├── Satır İçi Yorumlar
├── Genel Geri Bildirim
├── Puan Atama
└── Değerlendirme Onayı
```

---

## 📐 Rubrik Yönetimi

### Rubrik Oluşturma

```
📊 RUBRİK OLUŞTURMA
├── Rubrik Bilgileri
│   ├── Ad ve açıklama
│   ├── Tip (Analitik/Holistik)
│   └── Puan aralığı
├── Kriterler
│   ├── Kriter adı
│   ├── Ağırlık (%)
│   └── Açıklama
├── Performans Seviyeleri
│   ├── Mükemmel
│   ├── İyi
│   ├── Orta
│   └── Gelişmeli
└── Puan Matrisi
```

### Rubrik Türleri

#### 1. Analitik Rubrik
| Kriter | Mükemmel (4) | İyi (3) | Orta (2) | Gelişmeli (1) |
|--------|--------------|---------|----------|---------------|
| **İçerik** | Kapsamlı, derin | Yeterli detay | Temel seviye | Yetersiz |
| **Organizasyon** | Mükemmel akış | İyi yapı | Karışık | Dağınık |
| **Dil Kullanımı** | Hatasız, akıcı | Az hata | Anlaşılır | Çok hatalı |
| **Kaynaklar** | Çeşitli, güncel | Yeterli | Az kaynak | Yetersiz |

#### 2. Holistik Rubrik
```
🎯 HOLİSTİK RUBRİK
├── Seviye 4 (90-100)
│   └── Tüm beklentileri aşar
├── Seviye 3 (80-89)
│   └── Beklentileri karşılar
├── Seviye 2 (70-79)
│   └── Kısmen karşılar
└── Seviye 1 (0-69)
    └── Beklentilerin altında
```

---

## 💬 Geri Bildirim Sistemi

### Geri Bildirim Türleri

#### 1. Otomatik Geri Bildirim
```
🤖 OTOMATİK GERİ BİLDİRİM
├── Anında Geri Bildirim
│   ├── Doğru/Yanlış
│   ├── Açıklama
│   └── Kaynak önerisi
├── Detaylı Analiz
│   ├── Güçlü yönler
│   ├── Gelişim alanları
│   └── Öneriler
└── İlerleme Raporu
```

#### 2. Eğitmen Geri Bildirimi
```
👨‍🏫 EĞİTMEN GERİ BİLDİRİMİ
├── Yazılı Yorumlar
├── Ses Kaydı
├── Video Geri Bildirim
├── Satır İçi Notlar
└── Rubrik Bazlı
```

### Geri Bildirim Şablonları

#### Yapıcı Geri Bildirim Modeli
```
📝 YAPICI GERİ BİLDİRİM
├── Olumlu Başlangıç
│   └── "İyi yapılan..."
├── Gelişim Alanları
│   └── "Geliştirilebilir..."
├── Spesifik Öneriler
│   └── "Bunun için..."
└── Motivasyon
    └── "Devam et..."
```

---

## 📊 Raporlama ve Analiz

### Değerlendirme Raporları

#### 1. Öğrenci Performans Raporu
```
📈 PERFORMANS RAPORU
├── Genel Başarı
│   ├── Ortalama puan
│   ├── Sınıf sıralaması
│   └── Gelişim trendi
├── Detaylı Analiz
│   ├── Konu bazlı başarı
│   ├── Soru tipi performansı
│   └── Zaman yönetimi
├── Karşılaştırmalar
│   ├── Sınıf ortalaması
│   ├── Önceki performans
│   └── Hedefler
└── Öneriler
```

#### 2. Sınıf Analiz Raporu
```
👥 SINIF ANALİZİ
├── Dağılım Grafikleri
│   ├── Not dağılımı
│   ├── Normal dağılım
│   └── Box plot
├── İstatistikler
│   ├── Ortalama
│   ├── Medyan
│   ├── Standart sapma
│   └── Min/Max
├── Soru Analizi
│   ├── Zorluk indeksi
│   ├── Ayırt edicilik
│   └── Güvenirlik
└── Trend Analizi
```

### Analitik Dashboard

```
📊 ANALİTİK DASHBOARD
├── Gerçek Zamanlı Metrikler
│   ├── Aktif sınav sayısı
│   ├── Tamamlanma oranı
│   └── Ortalama süre
├── Performans Göstergeleri
│   ├── Başarı oranı
│   ├── Risk altındaki öğrenciler
│   └── Gelişim hızı
├── Tahminleme
│   ├── Başarı tahmini
│   ├── Tamamlanma tahmini
│   └── Risk analizi
└── Karşılaştırmalı Analiz
    ├── Dönemsel
    ├── Program bazlı
    └── Demografik
```

---

## 🔒 Güvenlik ve Denetim

### Sınav Güvenliği

#### Online Proctoring
```
👁️ ONLINE PROCTORING
├── Kimlik Doğrulama
│   ├── Yüz tanıma
│   ├── Kimlik kartı
│   └── Çift faktörlü
├── Davranış İzleme
│   ├── Göz takibi
│   ├── Ses algılama
│   ├── Ekran değişimi
│   └── Klavye/fare deseni
├── Ortam Kontrolü
│   ├── 360° oda taraması
│   ├── Masa kontrolü
│   └── Cihaz kontrolü
└── Bayrak Sistemi
    ├── Otomatik bayraklar
    ├── Manuel inceleme
    └── Kanıt toplama
```

### Kopya Tespiti

#### Plagiarism Kontrolü
```
🔍 KOPYA TESPİTİ
├── Metin Benzerliği
│   ├── Turnitin entegrasyonu
│   ├── Dahili veritabanı
│   └── İnternet taraması
├── Kod Benzerliği
│   ├── MOSS analizi
│   ├── Syntax kontrolü
│   └── Algoritma benzerliği
├── Davranış Analizi
│   ├── Yazma deseni
│   ├── Zaman analizi
│   └── IP kontrolü
└── Raporlama
    ├── Benzerlik yüzdesi
    ├── Kaynak gösterimi
    └── Detaylı rapor
```

### Denetim ve Log

```
📋 DENETİM KAYITLARI
├── Sınav Logları
│   ├── Giriş/çıkış
│   ├── Soru görüntüleme
│   ├── Cevap değişiklikleri
│   └── Zaman damgaları
├── Sistem Olayları
│   ├── Bağlantı kopması
│   ├── Tarayıcı değişimi
│   ├── Kopyalama girişimi
│   └── Anormal davranış
└── Değerlendirme Logları
    ├── Not değişiklikleri
    ├── Rubrik uygulaması
    ├── Geri bildirimler
    └── Onay süreçleri
```

---

## 🎓 Sertifikasyon

### Sertifika Yönetimi

```
🏆 SERTİFİKA SİSTEMİ
├── Sertifika Türleri
│   ├── Katılım sertifikası
│   ├── Başarı sertifikası
│   ├── Yeterlik sertifikası
│   └── Onur sertifikası
├── Kriterler
│   ├── Minimum başarı
│   ├── Devam zorunluluğu
│   ├── Proje teslimi
│   └── Özel şartlar
├── Tasarım
│   ├── Şablon seçimi
│   ├── Logo/imza
│   ├── QR kod
│   └── Blockchain doğrulama
└── Dağıtım
    ├── Otomatik gönderim
    ├── PDF indirme
    ├── Dijital cüzdan
    └── Basılı kopya
```

---

## 💡 En İyi Uygulamalar

### Değerlendirme Tasarımı
1. **Çeşitlilik**
   - Farklı soru türleri kullan
   - Çoklu değerlendirme yöntemi
   - Değişik zorluk seviyeleri

2. **Adalet**
   - Net yönergeler
   - Objektif kriterler
   - Eşit fırsatlar

3. **Geçerlik ve Güvenirlik**
   - Öğrenme hedefleriyle uyum
   - Tutarlı puanlama
   - Test-tekrar test güvenirliği

### Öğrenci Deneyimi
- 🎯 Açık beklentiler
- ⏰ Yeterli hazırlık süresi
- 💬 Düzenli geri bildirim
- 📊 İlerleme görünürlüğü

---

**📊 Değerlendirme Sistemi, BDC platformunun öğrenci başarısını objektif ve kapsamlı şekilde ölçen kritik modülüdür. Etkin kullanımı için değerlendirme çeşitliliği ve düzenli geri bildirim sağlanması önemlidir.**

*Son güncelleme: 27 Haziran 2025 | Versiyon 1.0*