# BDC Platform - Koç Notları Sistemi Detaylı Rehberi

## 🎯 Bu Belge Hakkında

Koç Notları modülü, BDC platformunda eğitmenler ve koçların öğrenciler hakkında detaylı notlar tutmasını, gelişim takibi yapmasını ve öğrenci performansını değerlendirmesini sağlayan kapsamlı bir sistemdir. Bu belgede koç notları sisteminin tüm özellikleri detaylıca açıklanmaktadır.

---

## 📋 İçindekiler

1. [Koç Notları Genel Bakış](#koç-notları-genel-bakış)
2. [Not Kategorileri ve Türleri](#not-kategorileri-ve-türleri)
3. [Not Oluşturma ve Yönetimi](#not-oluşturma-ve-yönetimi)
4. [Öğrenci Takip Sistemi](#öğrenci-takip-sistemi)
5. [Gelişim Planları](#gelişim-planları)
6. [Görüşme Kayıtları](#görüşme-kayıtları)
7. [Performans Değerlendirmeleri](#performans-değerlendirmeleri)
8. [İşbirliği ve Paylaşım](#i̇şbirliği-ve-paylaşım)
9. [Raporlama ve Analiz](#raporlama-ve-analiz)
10. [Gizlilik ve Güvenlik](#gizlilik-ve-güvenlik)

---

## 📝 Koç Notları Genel Bakış

### Erişim Yolu
```
Ana Menü → Koç Notları → Not Listesi
veya
Öğrenci Profili → Koç Notları Sekmesi
```

### Kimler Erişebilir?
- ✅ **Yönetici:** Tüm notları görüntüleme (gizli notlar hariç)
- ✅ **Eğitmen/Koç:** Kendi yazdığı ve paylaşılan notlar
- ⚠️ **Öğrenci:** Kendisi için paylaşılan notlar (opsiyonel)

### Koç Notları Nedir?
Koç notları, öğrencilerin akademik, sosyal ve kişisel gelişimlerini takip etmek için kullanılan yapılandırılmış bir not alma ve değerlendirme sistemidir.

### Temel Özellikler
```
📝 KOÇ NOTLARI SİSTEMİ
├── 📋 Kategorize not alma
├── 🔒 Gizlilik seviyeleri
├── 🏷️ Etiketleme sistemi
├── 📊 Gelişim takibi
├── 🔔 Hatırlatıcılar
├── 📤 Paylaşım kontrolü
├── 📈 Trend analizi
└── 🔍 Gelişmiş arama
```

---

## 🏷️ Not Kategorileri ve Türleri

### Ana Kategoriler

#### 1. Akademik Gelişim
```
📚 AKADEMİK GELİŞİM
├── Ders Performansı
│   ├── Katılım durumu
│   ├── Ödev teslimi
│   ├── Sınav sonuçları
│   └── Proje başarısı
├── Öğrenme Stili
│   ├── Görsel öğrenci
│   ├── İşitsel öğrenci
│   ├── Kinestetik öğrenci
│   └── Karma stil
├── Güçlü Yönler
│   ├── Analitik düşünme
│   ├── Problem çözme
│   ├── Yaratıcılık
│   └── Eleştirel düşünme
└── Gelişim Alanları
    ├── Zaman yönetimi
    ├── Odaklanma
    ├── Not tutma
    └── Araştırma becerileri
```

#### 2. Sosyal ve Duygusal Gelişim
```
👥 SOSYAL/DUYGUSAL GELİŞİM
├── Sosyal Beceriler
│   ├── İletişim
│   ├── Takım çalışması
│   ├── Liderlik
│   └── Empati
├── Duygusal Durum
│   ├── Motivasyon seviyesi
│   ├── Özgüven
│   ├── Stres yönetimi
│   └── Uyum süreci
├── Davranışsal Gözlemler
│   ├── Sınıf içi davranış
│   ├── Akran ilişkileri
│   ├── Çatışma çözme
│   └── Sorumluluk alma
└── Destek İhtiyaçları
    ├── Mentorluk
    ├── Psikolojik destek
    ├── Sosyal aktiviteler
    └── Güven inşası
```

#### 3. Kariyer ve Mesleki Gelişim
```
💼 KARİYER GELİŞİMİ
├── Kariyer Hedefleri
│   ├── Kısa vadeli
│   ├── Orta vadeli
│   ├── Uzun vadeli
│   └── Alternatif planlar
├── Beceri Değerlendirmesi
│   ├── Teknik beceriler
│   ├── Soft skills
│   ├── Sektörel bilgi
│   └── Sertifikalar
├── İş Deneyimi
│   ├── Stajlar
│   ├── Projeler
│   ├── Gönüllü işler
│   └── Freelance
└── Network Oluşturma
    ├── Mentor ilişkileri
    ├── Sektör bağlantıları
    ├── Alumni network
    └── Profesyonel platformlar
```

### Not Türleri

| Tür | Açıklama | Kullanım Alanı |
|-----|----------|----------------|
| **Gözlem Notu** | Anlık gözlemler | Günlük takip |
| **Değerlendirme Notu** | Detaylı analiz | Dönemsel değerlendirme |
| **Görüşme Notu** | Birebir görüşmeler | Mentorluk seansları |
| **İlerleme Notu** | Gelişim takibi | Milestone kontrolü |
| **Uyarı Notu** | Dikkat gerektiren durumlar | Risk yönetimi |
| **Başarı Notu** | Pozitif gelişmeler | Motivasyon |

---

## ✍️ Not Oluşturma ve Yönetimi

### Yeni Not Oluşturma

#### Not Oluşturma Formu
```
📝 YENİ NOT FORMU
├── Temel Bilgiler
│   ├── Öğrenci Seçimi* (dropdown/arama)
│   ├── Not Başlığı* (150 karakter)
│   ├── Kategori* (dropdown)
│   ├── Not Türü* (dropdown)
│   └── Öncelik (Yüksek/Normal/Düşük)
├── Not İçeriği
│   ├── Detaylı Not* (rich text editor)
│   ├── Gözlem Tarihi
│   ├── İlgili Ders/Program
│   └── Ek Bilgiler
├── Etiketler
│   ├── Hazır etiketler
│   ├── Özel etiket ekleme
│   └── Maksimum 10 etiket
└── Gizlilik Ayarları
    ├── Tamamen gizli
    ├── Yönetici görebilir
    ├── Diğer koçlarla paylaş
    └── Öğrenci görebilir
```

#### Rich Text Editör Özellikleri
```
🛠️ EDİTÖR ÖZELLİKLERİ
├── Metin Formatlama
│   ├── Bold, italic, underline
│   ├── Başlıklar (H1-H3)
│   ├── Listeler (sıralı/sırasız)
│   └── Alıntı blokları
├── Eklentiler
│   ├── Tablo ekleme
│   ├── Link ekleme
│   ├── Resim yükleme
│   └── Dosya ekleme
├── Şablonlar
│   ├── Haftalık değerlendirme
│   ├── Görüşme özeti
│   ├── Performans analizi
│   └── Özel şablonlar
└── Otomatik Kayıt
    └── Her 30 saniyede
```

### Not Düzenleme ve Versiyon Kontrolü

#### Versiyon Takibi
```
🔄 VERSİYON KONTROLÜ
├── Otomatik Versiyonlama
│   ├── Her düzenlemede
│   ├── Tarih/saat damgası
│   └── Değiştiren kullanıcı
├── Versiyon Karşılaştırma
│   ├── Değişiklikleri göster
│   ├── Eski versiyona dön
│   └── Versiyon notları
└── Değişiklik Logları
    ├── Kim değiştirdi
    ├── Ne zaman
    ├── Neler değişti
    └── Değişiklik nedeni
```

### Not Organizasyonu

#### Klasör Sistemi
```
📁 KLASÖR YAPISI
├── 📂 Dönemsel Klasörler
│   ├── 2025 Bahar
│   ├── 2025 Yaz
│   └── 2025 Güz
├── 📂 Program Bazlı
│   ├── Web Geliştirme
│   ├── Veri Bilimi
│   └── Dijital Pazarlama
├── 📂 Öğrenci Bazlı
│   └── Her öğrenci için klasör
└── 📂 Özel Klasörler
    ├── Acil durumlar
    ├── Başarı hikayeleri
    └── Arşiv
```

---

## 👤 Öğrenci Takip Sistemi

### Öğrenci Profil Entegrasyonu

```
👤 ÖĞRENCİ PROFİL GÖRÜNÜMÜ
├── 📊 Özet Bilgiler
│   ├── Program kaydı
│   ├── Devam durumu
│   ├── Genel not ortalaması
│   └── Son aktiviteler
├── 📝 Koç Notları
│   ├── Kronolojik liste
│   ├── Kategori filtreleme
│   ├── Arama fonksiyonu
│   └── Not ekleme butonu
├── 📈 Gelişim Grafiği
│   ├── Zaman bazlı trend
│   ├── Kategori dağılımı
│   ├── Duygu analizi
│   └── İlerleme göstergesi
└── 🎯 Hedefler ve Görevler
    ├── Aktif hedefler
    ├── Tamamlanan görevler
    ├── Yaklaşan deadlinelar
    └── Başarı yüzdesi
```

### Timeline (Zaman Çizelgesi) Görünümü

```
📅 TIMELINE GÖRÜNÜMÜ
├── Tarih Bazlı Sıralama
├── Not Türü İkonları
├── Hızlı Önizleme
├── Filtreleme Seçenekleri
│   ├── Tarih aralığı
│   ├── Kategori
│   ├── Öncelik
│   └── Etiketler
└── Dışa Aktarma
    ├── PDF rapor
    ├── Excel
    └── Yazdır
```

### Öğrenci Karşılaştırma

#### Karşılaştırma Matrisi
| Öğrenci | Akademik | Sosyal | Katılım | İlerleme |
|---------|----------|---------|---------|----------|
| Ali Y. | 85% | 90% | 95% | ↗️ |
| Ayşe K. | 92% | 85% | 88% | → |
| Mehmet S. | 78% | 95% | 92% | ↗️ |

---

## 📈 Gelişim Planları

### Bireysel Gelişim Planı (IDP)

```
🎯 BİREYSEL GELİŞİM PLANI
├── Plan Bilgileri
│   ├── Plan adı
│   ├── Başlangıç/Bitiş tarihi
│   ├── Sorumlu koç
│   └── Durum (Aktif/Pasif)
├── Hedefler
│   ├── SMART hedefler
│   ├── Ölçülebilir kriterler
│   ├── Zaman çerçevesi
│   └── Başarı göstergeleri
├── Eylem Adımları
│   ├── Görev listesi
│   ├── Sorumlular
│   ├── Deadline'lar
│   └── İlerleme takibi
└── Değerlendirme
    ├── Ara değerlendirmeler
    ├── Final değerlendirme
    ├── Geri bildirim
    └── Revizyon
```

### Hedef Belirleme

#### SMART Hedef Şablonu
```
🎯 SMART HEDEF
├── Specific (Spesifik)
│   └── "Python'da veri analizi yapabilme"
├── Measurable (Ölçülebilir)
│   └── "3 gerçek proje tamamlama"
├── Achievable (Ulaşılabilir)
│   └── "Haftada 15 saat çalışma"
├── Relevant (İlgili)
│   └── "Kariyer hedefiyle uyumlu"
└── Time-bound (Zamanlı)
    └── "3 ay içinde tamamlama"
```

### İlerleme Takibi

```
📊 İLERLEME TAKİBİ
├── Milestone'lar
│   ├── Başlangıç noktası
│   ├── Ara kontrol noktaları
│   ├── Hedef nokta
│   └── Gerçekleşen
├── Performans Göstergeleri
│   ├── Tamamlanan görevler
│   ├── Kazanılan beceriler
│   ├── Alınan sertifikalar
│   └── Proje çıktıları
├── Görselleştirme
│   ├── İlerleme çubuğu
│   ├── Radar grafik
│   ├── Gantt chart
│   └── Burndown chart
└── Otomatik Uyarılar
    ├── Geciken görevler
    ├── Yaklaşan deadlinelar
    ├── Milestone hatırlatıcıları
    └── Başarı bildirimleri
```

---

## 🗣️ Görüşme Kayıtları

### Görüşme Planlama

```
📅 GÖRÜŞME PLANLAMA
├── Görüşme Bilgileri
│   ├── Öğrenci adı
│   ├── Tarih ve saat
│   ├── Süre (dakika)
│   ├── Görüşme türü
│   └── Platform (yüz yüze/online)
├── Gündem
│   ├── Ana konular
│   ├── Tartışılacak sorunlar
│   ├── Hedef belirleme
│   └── Önceki aksiyon takibi
├── Hazırlık
│   ├── Önceki notları gözden geçir
│   ├── Performans raporları
│   ├── Hazırlanacak dökümanlar
│   └── Sorular listesi
└── Davet ve Hatırlatma
    ├── Takvim daveti
    ├── Email bildirimi
    ├── SMS hatırlatma
    └── Platform bildirimi
```

### Görüşme Şablonları

#### 1. Haftalık Check-in
```
📋 HAFTALIK CHECK-IN
├── Geçen Hafta
│   ├── Tamamlanan görevler
│   ├── Karşılaşılan zorluklar
│   └── Başarılar
├── Bu Hafta
│   ├── Öncelikler
│   ├── Planlanan aktiviteler
│   └── Destek ihtiyaçları
├── Genel Durum
│   ├── Motivasyon seviyesi (1-10)
│   ├── Stres seviyesi (1-10)
│   └── Genel memnuniyet
└── Aksiyon Adımları
    ├── Öğrenci görevleri
    ├── Koç görevleri
    └── Sonraki görüşme
```

#### 2. Performans Değerlendirme
```
📊 PERFORMANS DEĞERLENDİRME
├── Akademik Performans
│   ├── Not ortalaması
│   ├── Ödev teslim oranı
│   ├── Sınav sonuçları
│   └── Proje kalitesi
├── Beceri Gelişimi
│   ├── Teknik beceriler
│   ├── Soft skills
│   ├── Problem çözme
│   └── Yaratıcılık
├── Güçlü Yönler
├── Gelişim Alanları
└── Gelecek Dönem Hedefleri
```

### Görüşme Sonrası

```
📝 GÖRÜŞME SONRASI
├── Görüşme Özeti
│   ├── Tartışılan konular
│   ├── Alınan kararlar
│   ├── Belirlenen hedefler
│   └── Aksiyon adımları
├── Takip Edilecekler
│   ├── Görev atamaları
│   ├── Deadline'lar
│   ├── Kontrol noktaları
│   └── Sorumlular
├── Paylaşım
│   ├── Öğrenci ile paylaş
│   ├── Yönetim ile paylaş
│   ├── Diğer koçlar
│   └── Veliler (gerekirse)
└── Sonraki Adımlar
    ├── Takip görüşmesi
    ├── Email özeti
    ├── Görev hatırlatıcıları
    └── İlerleme kontrolü
```

---

## 📊 Performans Değerlendirmeleri

### 360 Derece Değerlendirme

```
🔄 360 DERECE DEĞERLENDİRME
├── Değerlendirme Kaynakları
│   ├── Öz değerlendirme
│   ├── Koç değerlendirmesi
│   ├── Akran değerlendirmesi
│   ├── Proje ortağı geri bildirimi
│   └── İşveren değerlendirmesi (staj)
├── Değerlendirme Kriterleri
│   ├── Teknik yetkinlikler
│   ├── İletişim becerileri
│   ├── Takım çalışması
│   ├── Problem çözme
│   ├── Liderlik
│   └── Adaptasyon
├── Puanlama Sistemi
│   ├── 1-5 ölçek
│   ├── Ağırlıklı ortalama
│   ├── Radar grafik
│   └── Karşılaştırmalı analiz
└── Sonuç Raporu
    ├── Güçlü yönler
    ├── Gelişim alanları
    ├── Öneriler
    └── Aksiyon planı
```

### Yetkinlik Matrisi

| Yetkinlik | Başlangıç | Mevcut | Hedef | Durum |
|-----------|-----------|---------|--------|--------|
| Python Programlama | 2/5 | 4/5 | 5/5 | 🟡 |
| Veri Analizi | 1/5 | 3/5 | 4/5 | 🟢 |
| Proje Yönetimi | 2/5 | 3/5 | 4/5 | 🟡 |
| İletişim | 3/5 | 4/5 | 5/5 | 🟡 |
| Liderlik | 2/5 | 3/5 | 4/5 | 🟡 |

---

## 🤝 İşbirliği ve Paylaşım

### Koç Takımı İşbirliği

```
👥 KOÇ TAKIMI İŞBİRLİĞİ
├── Paylaşılan Notlar
│   ├── Genel gözlemler
│   ├── Ortak öğrenciler
│   ├── Best practices
│   └── Uyarı notları
├── Vaka Tartışmaları
│   ├── Zor vakalar
│   ├── Başarı hikayeleri
│   ├── Çözüm önerileri
│   └── Deneyim paylaşımı
├── Takım Toplantıları
│   ├── Haftalık senkronizasyon
│   ├── Vaka sunumları
│   ├── Eğitim paylaşımları
│   └── Strateji belirleme
└── Ortak Raporlama
    ├── Dönemsel analizler
    ├── Trend raporları
    ├── Risk değerlendirmesi
    └── Başarı metrikleri
```

### Öğrenci ile Paylaşım

```
📤 ÖĞRENCİ PAYLAŞIMI
├── Paylaşım Seviyeleri
│   ├── Tam erişim
│   ├── Özet görünüm
│   ├── Seçili notlar
│   └── Sadece hedefler
├── Paylaşım Formatları
│   ├── Platform içi görünüm
│   ├── PDF rapor
│   ├── Email özeti
│   └── Mobil bildirim
├── Geri Bildirim Alma
│   ├── Yorum ekleme
│   ├── Onay/red
│   ├── Sorular
│   └── Öz değerlendirme
└── İzleme ve Takip
    ├── Görüntülenme takibi
    ├── Etkileşim analizi
    ├── Geri bildirim oranı
    └── Aksiyona geçme
```

---

## 📊 Raporlama ve Analiz

### Bireysel Öğrenci Raporları

```
📈 BİREYSEL RAPORLAR
├── Dönemsel Özet Raporu
│   ├── Genel performans
│   ├── Not kategorileri dağılımı
│   ├── İlerleme trendi
│   └── Öne çıkan başarılar
├── Detaylı Analiz Raporu
│   ├── Kategori bazlı analiz
│   ├── Zaman serisi analizi
│   ├── Duygu durumu analizi
│   └── Tahminsel analiz
├── Karşılaştırmalı Rapor
│   ├── Önceki dönemler
│   ├── Peer karşılaştırma
│   ├── Program ortalaması
│   └── Hedef karşılaştırma
└── Özel Raporlar
    ├── Staj değerlendirmesi
    ├── Proje performansı
    ├── Soft skill analizi
    └── Kariyer hazırlığı
```

### Toplu Raporlar

```
📊 TOPLU RAPORLAR
├── Sınıf/Program Raporu
│   ├── Genel başarı durumu
│   ├── Risk altındaki öğrenciler
│   ├── Üstün başarı gösterenler
│   └── Ortak sorun alanları
├── Koç Performans Raporu
│   ├── Not yazma sıklığı
│   ├── Öğrenci etkileşimi
│   ├── Başarı oranları
│   └── Geri bildirim kalitesi
├── Trend Analizi
│   ├── Dönemsel trendler
│   ├── Kategori trendleri
│   ├── Başarı faktörleri
│   └── Risk faktörleri
└── Yönetim Özeti
    ├── KPI'lar
    ├── Kritik metrikler
    ├── Öneriler
    └── Aksiyon planı
```

### Analitik Dashboard

```
📊 ANALİTİK DASHBOARD
├── Gerçek Zamanlı Metrikler
│   ├── Aktif öğrenci sayısı
│   ├── Bugünkü notlar
│   ├── Bekleyen görevler
│   └── Risk uyarıları
├── Görselleştirmeler
│   ├── Heat map
│   ├── Word cloud
│   ├── Network diagram
│   └── Sankey diagram
├── Prediktif Analiz
│   ├── Başarı tahmini
│   ├── Risk skorlaması
│   ├── Terk etme riski
│   └── Performans projeksiyonu
└── İleri Analitik
    ├── Makine öğrenmesi modelleri
    ├── Doğal dil işleme
    ├── Sentiment analizi
    └── Pattern recognition
```

---

## 🔒 Gizlilik ve Güvenlik

### Gizlilik Seviyeleri

```
🔐 GİZLİLİK SEVİYELERİ
├── 1. Seviye - Tamamen Gizli
│   ├── Sadece yazan koç
│   ├── Şifreleme
│   ├── Paylaşım yok
│   └── Dışa aktarım yok
├── 2. Seviye - Yönetim Erişimli
│   ├── Koç + Yönetici
│   ├── Audit log
│   ├── Onay gerektiren paylaşım
│   └── Kısıtlı dışa aktarım
├── 3. Seviye - Takım Paylaşımlı
│   ├── Tüm koçlar
│   ├── Ortak erişim
│   ├── Yorum ekleme
│   └── Standart dışa aktarım
└── 4. Seviye - Öğrenci Görünür
    ├── Koç + Öğrenci
    ├── Read-only öğrenci
    ├── Geri bildirim alınabilir
    └── PDF/Email paylaşım
```

### Veri Güvenliği

```
🛡️ VERİ GÜVENLİĞİ
├── Erişim Kontrolü
│   ├── Role-based access
│   ├── IP kısıtlaması
│   ├── 2FA zorunluluğu
│   └── Session yönetimi
├── Veri Şifreleme
│   ├── At-rest encryption
│   ├── In-transit encryption
│   ├── Field-level encryption
│   └── Backup şifreleme
├── Audit Trail
│   ├── Her işlem loglanır
│   ├── Kim, ne zaman, ne yaptı
│   ├── Değişiklik geçmişi
│   └── Anormal aktivite tespiti
└── Uyumluluk
    ├── KVKK uyumlu
    ├── GDPR uyumlu
    ├── Veri saklama politikası
    └── Silme/anonimleştirme
```

### Etik Kurallar

```
📜 ETİK KURALLAR
├── Objektiflik
│   └── Tarafsız gözlem ve değerlendirme
├── Gizlilik
│   └── Öğrenci bilgilerini koruma
├── Profesyonellik
│   └── Uygun dil ve üslup kullanımı
├── Yapıcı Yaklaşım
│   └── Pozitif ve geliştirici geri bildirim
└── Sınırlar
    └── Kişisel sınırlara saygı
```

---

## 💡 En İyi Uygulamalar

### Etkili Not Yazma

1. **STAR Metodu**
   - **S**ituation: Durum/bağlam
   - **T**ask: Görev/beklenti
   - **A**ction: Alınan aksiyon
   - **R**esult: Sonuç/etki

2. **Objektif Gözlem**
   - Gerçeklere dayalı
   - Ölçülebilir kriterler
   - Spesifik örnekler
   - Tarafsız dil

3. **Düzenli Takip**
   - Haftalık notlar
   - Milestone değerlendirmeleri
   - Trend takibi
   - Proaktif yaklaşım

### Öğrenci Motivasyonu

- 🎯 Güçlü yönlere odaklan
- 🌟 Küçük başarıları kutla
- 📈 İlerlemeyi görselleştir
- 💬 Açık iletişim kur
- 🤝 İşbirlikçi hedefler belirle

---

**📝 Koç Notları sistemi, BDC platformunda öğrenci gelişiminin sistematik takibi ve desteklenmesi için kritik öneme sahiptir. Düzenli, objektif ve yapıcı notlar, öğrenci başarısını doğrudan etkiler.**

*Son güncelleme: 27 Haziran 2025 | Versiyon 1.0*