# BDC Platform - Dashboard (Ana Panel) Kullanım Rehberi

## 🎯 Bu Belge Hakkında

Dashboard, BDC platformuna giriş yaptığınızda karşınıza çıkan ana kontrol panelidir. Bu belgede, Dashboard'un tüm bileşenleri, widget'ları ve kullanım detayları açıklanmaktadır.

---

## 📋 İçindekiler

1. [Dashboard'a Genel Bakış](#dashboarda-genel-bakış)
2. [İstatistik Kartları](#i̇statistik-kartları)
3. [Performans Görünümü](#performans-görünümü)
4. [Son Aktiviteler](#son-aktiviteler)
5. [Hızlı İşlemler](#hızlı-i̇şlemler)
6. [Yaklaşan Etkinlikler](#yaklaşan-etkinlikler)
7. [AI İçgörüleri](#ai-i̇çgörüleri)
8. [Dashboard Özelleştirme](#dashboard-özelleştirme)

---

## 📊 Dashboard'a Genel Bakış

Dashboard, platformdaki tüm önemli bilgileri tek bir ekranda toplar. Kullanıcı rolüne göre gösterilen içerik değişir.

### Dashboard Bileşenleri

```
Dashboard Ana Ekranı
├── 📈 İstatistik Kartları (4 adet)
├── 📊 Performans Görünümü
├── 📝 Son Aktiviteler
├── ⚡ Hızlı İşlemler
├── 📅 Yaklaşan Etkinlikler
└── 🤖 AI İçgörüleri
```

### Rol Bazlı Dashboard Görünümleri

| Kullanıcı Rolü | Görünen İçerikler |
|----------------|-------------------|
| **Yönetici** | Tüm sistem istatistikleri, kullanıcı metrikleri, platform sağlığı |
| **Eğitmen** | Öğrenci performansları, program ilerlemeleri, değerlendirme sonuçları |
| **Öğrenci** | Kişisel ilerleme, yaklaşan görevler, başarılar |

---

## 📈 İstatistik Kartları

Dashboard'un en üstünde 4 ana istatistik kartı bulunur. Bu kartlar anlık veri gösterir ve otomatik olarak güncellenir.

### 1. Toplam Faydalanıcılar

![Beneficiaries Card](./images/stat-beneficiaries.png)

**Gösterilen Bilgiler:**
- 👥 **Ana Sayı:** Sistemdeki toplam faydalanıcı sayısı
- 📈 **Trend:** Son 30 güne göre artış/azalış yüzdesi
- 🎨 **Renk:** Mavi (Primary)

**Detaylar:**
- Tıklandığında faydalanıcı listesine yönlendirir
- Sadece aktif faydalanıcıları gösterir
- Gerçek zamanlı güncelleme

**Örnek Görünüm:**
```
Toplam Faydalanıcılar
    1,234
    ↑ 12% (son 30 gün)
```

### 2. Aktif Programlar

![Programs Card](./images/stat-programs.png)

**Gösterilen Bilgiler:**
- 📚 **Ana Sayı:** Şu anda devam eden program sayısı
- 📈 **Trend:** Yeni başlayan program sayısı
- 🎨 **Renk:** Yeşil (Success)

**Detaylar:**
- Sadece "aktif" statüsündeki programlar
- Başlangıç ve bitiş tarihleri arasında olanlar
- Minimum katılımcı sayısını karşılayanlar

**Program Statüleri:**
- ✅ **Aktif:** Devam eden
- ⏸️ **Beklemede:** Başlamamış
- 🏁 **Tamamlanmış:** Bitmiş
- ❌ **İptal:** Gerçekleşmemiş

### 3. Değerlendirmeler

![Evaluations Card](./images/stat-evaluations.png)

**Gösterilen Bilgiler:**
- 📝 **Ana Sayı:** Tamamlanan değerlendirme sayısı
- 📈 **Trend:** Son dönemdeki artış
- 🎨 **Renk:** Turuncu (Warning)

**Detay Bilgileri:**
- Tüm değerlendirme türlerini kapsar
- Quiz, sınav, ödev değerlendirmeleri
- Ortalama başarı oranı göstergesi

### 4. Başarı Oranı

![Success Rate Card](./images/stat-success.png)

**Gösterilen Bilgiler:**
- 🎯 **Ana Sayı:** Genel başarı yüzdesi
- 📈 **Trend:** Önceki döneme göre değişim
- 🎨 **Renk:** Açık Mavi (Info)

**Hesaplama Metodu:**
```
Başarı Oranı = (Tamamlanan Programlar / Toplam Kayıtlar) × 100
```

---

## 📊 Performans Görünümü

Dashboard'un ana içerik alanında yer alan detaylı performans paneli.

### Performans Metrikleri

#### 1. Program Tamamlama Oranı

**Görsel Öğeler:**
- 📊 İlerleme çubuğu (Progress Bar)
- 🎯 Hedef göstergesi
- 📈 Trend okları

**Gösterge Seviyeleri:**
- 🟢 **Mükemmel:** %90-100
- 🟡 **İyi:** %70-89
- 🟠 **Orta:** %50-69
- 🔴 **Düşük:** %0-49

**Örnek Görünüm:**
```
🎯 Program Tamamlama Oranı                    78%
[████████████████░░░░]
```

#### 2. Beceri Sertifikasyon Oranı

**Açıklama:** Sertifika almaya hak kazanan öğrencilerin yüzdesi

**Detaylar:**
- Minimum başarı notu: %70
- Devam zorunluluğu: %80
- Proje teslimi: Zorunlu

#### 3. Aktif Katılım

**Ölçüm Kriterleri:**
- Platform giriş sıklığı
- Ödev teslim oranı
- Forum/tartışma katılımı
- Canlı ders katılımı

### Hızlı İstatistikler

Dashboard'da 3 küçük istatistik kutusu:

| Metrik | Açıklama | Örnek Değer |
|--------|----------|-------------|
| **Verilen Sertifikalar** | Toplam sertifika sayısı | 156 |
| **İş Yerleştirme** | İstihdam oranı | %89 |
| **Ortalama Puan** | Platform geneli değerlendirme | 4.8/5.0 |

---

## 📝 Son Aktiviteler

Platformdaki son gerçekleşen olayların kronolojik listesi.

### Aktivite Türleri

#### 1. 👥 Faydalanıcı Aktiviteleri
- Yeni kayıt
- Program kaydı
- Profil güncelleme
- Sertifika kazanımı

**Örnek Görünüm:**
```
👥 Yeni faydalanıcı kaydı
   Ahmet Yılmaz programa katıldı
   2 saat önce
```

#### 2. 📚 Program Aktiviteleri
- Program başlangıcı
- Yeni modül ekleme
- Program tamamlama
- Kayıt açma/kapama

#### 3. 📝 Değerlendirme Aktiviteleri
- Sınav sonucu açıklama
- Yeni değerlendirme oluşturma
- Not güncelleme
- Sertifika verme

### Aktivite Detayları

Her aktivite kartı şunları içerir:
- 🎨 **Tip İkonu:** Aktivite türünü belirtir
- 📝 **Başlık:** Ana eylem
- 📄 **Açıklama:** Detay bilgisi
- ⏰ **Zaman:** Ne zaman gerçekleştiği

### Filtreleme Seçenekleri

Aktiviteleri filtreleyebilirsiniz:
- **Türe göre:** Faydalanıcı, Program, Değerlendirme
- **Zamana göre:** Son 24 saat, Son 7 gün, Son 30 gün
- **Kullanıcıya göre:** Belirli kullanıcının aktiviteleri

---

## ⚡ Hızlı İşlemler

En sık kullanılan işlemlere tek tıkla erişim.

### Mevcut Hızlı İşlemler

| İşlem | İkon | Açıklama | Yetki |
|-------|------|----------|-------|
| **Faydalanıcı Ekle** | ➕👤 | Yeni öğrenci kaydı | Admin, Eğitmen |
| **Program Oluştur** | ➕📚 | Yeni eğitim programı | Admin, Eğitmen |
| **Etkinlik Planla** | ➕📅 | Takvime etkinlik ekle | Admin, Eğitmen |
| **Değerlendirme Oluştur** | ➕📝 | Yeni sınav/quiz | Eğitmen |

### Hızlı İşlem Kullanımı

1. İlgili butona tıklayın
2. Açılan formda gerekli bilgileri doldurun
3. "Kaydet" butonuna basın
4. İşlem otomatik olarak tamamlanır

### Özelleştirme

Hızlı işlemler panelini özelleştirebilirsiniz:
- ⚙️ Ayarlar → Dashboard → Hızlı İşlemler
- Sık kullandığınız işlemleri ekleyin
- Sıralamayı değiştirin
- Kullanmadıklarınızı gizleyin

---

## 📅 Yaklaşan Etkinlikler

Önümüzdeki 30 gün içindeki planlanmış etkinlikler.

### Etkinlik Türleri

#### 1. 🎓 Eğitim Oturumları
**Gösterilen Bilgiler:**
- Ders adı ve kodu
- Tarih ve saat
- Eğitmen adı
- Katılımcı sayısı
- Konum (fiziksel/online)

**Örnek:**
```
🎓 Web Geliştirme - Modül 3
   15 Temmuz 2025, 14:00
   👥 25 katılımcı
```

#### 2. 📝 Değerlendirmeler
**Gösterilen Bilgiler:**
- Sınav/quiz adı
- Başlangıç zamanı
- Süre
- Katılması gerekenler

#### 3. 📊 Program Başlangıçları
**Gösterilen Bilgiler:**
- Program adı
- Başlangıç tarihi
- Kayıtlı öğrenci sayısı
- Minimum/maksimum kontenjan

### Takvim Entegrasyonu

Etkinlikleri kişisel takviminize ekleyebilirsiniz:
- 📅 **Google Calendar**
- 📅 **Outlook**
- 📅 **Apple Calendar**
- 📅 **.ics dosyası** olarak indir

---

## 🤖 AI İçgörüleri

Yapay zeka destekli öneriler ve analizler.

### İçgörü Kategorileri

#### 1. 💡 Öneriler
**Platform kullanım verilerine dayalı öneriler:**
- "Web Geliştirme programı için kapasite artırımı önerilir - %95 doluluk oranı"
- "Python atölyelerini Salı günleri planlayın - %23 daha yüksek katılım"

#### 2. ⚡ Optimizasyonlar
**Verimlilik artırıcı öneriler:**
- Ders saatleri optimizasyonu
- Kaynak kullanımı iyileştirmeleri
- Sınıf boyutu önerileri

#### 3. ⚠️ Uyarılar
**Dikkat edilmesi gereken durumlar:**
- Risk altındaki öğrenciler
- Düşük katılımlı programlar
- Tamamlanmamış değerlendirmeler

### AI Analiz Özellikleri

**Analiz Edilen Veriler:**
- 📊 Öğrenci performans trendleri
- 📈 Program başarı oranları
- 👥 Katılım desenleri
- ⏰ Zaman optimizasyonu
- 💰 Kaynak verimliliği

**Güncelleme Sıklığı:**
- Gerçek zamanlı veri analizi
- Saatlik öneri güncellemeleri
- Haftalık detaylı raporlar

---

## ⚙️ Dashboard Özelleştirme

Dashboard'unuzu ihtiyaçlarınıza göre düzenleyebilirsiniz.

### Özelleştirme Seçenekleri

#### 1. Widget Düzenleme
**Nasıl Yapılır:**
1. Sağ üst köşedeki ⚙️ ikona tıklayın
2. "Dashboard Düzenle" seçeneğini seçin
3. Widget'ları sürükle-bırak ile yerleştirin
4. "Kaydet" butonuna basın

**Widget Seçenekleri:**
- Göster/Gizle
- Boyut değiştirme (S, M, L, XL)
- Konum değiştirme
- Renk teması

#### 2. Veri Filtreleri
**Filtreleme Kriterleri:**
- 📅 Tarih aralığı
- 🏢 Departman/Birim
- 📚 Program türü
- 👥 Kullanıcı grubu

#### 3. Otomatik Yenileme
**Ayarlar:**
- ⏱️ Her 30 saniyede
- ⏱️ Her 1 dakikada
- ⏱️ Her 5 dakikada
- 🔄 Manuel yenileme

### Dashboard Şablonları

Hazır dashboard şablonları:

| Şablon | Açıklama | Uygun Rol |
|--------|----------|-----------|
| **Yönetici Görünümü** | Tüm sistem metrikleri | Admin |
| **Eğitmen Paneli** | Öğrenci odaklı metrikler | Eğitmen |
| **Öğrenci Dashboardu** | Kişisel ilerleme | Öğrenci |
| **Minimal** | Sadece temel bilgiler | Tüm roller |
| **Detaylı Analiz** | Tüm widget'lar açık | Admin |

### Dışa Aktarma Seçenekleri

Dashboard verilerini dışa aktarabilirsiniz:
- 📄 **PDF Raporu:** Anlık görüntü
- 📊 **Excel:** Detaylı veri
- 📈 **CSV:** Ham veri
- 🖼️ **PNG/JPG:** Görsel çıktı

---

## 🔍 Gelişmiş Özellikler

### Karşılaştırmalı Analiz
- Dönemler arası karşılaştırma
- Departmanlar arası analiz
- Program bazlı kıyaslama

### Tahminleme
- Gelecek dönem öğrenci sayısı tahmini
- Başarı oranı projeksiyonu
- Kaynak ihtiyacı analizi

### Entegrasyonlar
- 📊 Google Analytics
- 📈 Microsoft Power BI
- 📉 Tableau
- 🔗 API erişimi

---

## 💡 İpuçları ve Püf Noktaları

### Verimli Dashboard Kullanımı

1. **Sabah Rutini:**
   - Gün başında dashboard'u kontrol edin
   - Kritik metriklere odaklanın
   - Günlük hedeflerinizi belirleyin

2. **Haftalık Analiz:**
   - Her Cuma detaylı analiz yapın
   - Trendleri takip edin
   - Gelecek hafta planlaması yapın

3. **Aylık Raporlama:**
   - Ay sonu raporları oluşturun
   - Başarı metriklerini değerlendirin
   - İyileştirme alanlarını belirleyin

### Kısayollar

| Kısayol | İşlev |
|---------|-------|
| `R` | Dashboard'u yenile |
| `F` | Tam ekran modu |
| `?` | Yardım menüsü |
| `Esc` | Çıkış/İptal |

---

## 🆘 Sorun Giderme

### Sık Karşılaşılan Sorunlar

**1. Veriler güncellenmiyor**
- Çözüm: Tarayıcı önbelleğini temizleyin (Ctrl+F5)

**2. Widget'lar yüklenmiyor**
- Çözüm: İnternet bağlantınızı kontrol edin

**3. Yanlış veriler gösteriliyor**
- Çözüm: Filtre ayarlarını kontrol edin

**4. Yavaş performans**
- Çözüm: Otomatik yenileme süresini artırın

---

**🎯 Dashboard, BDC platformunun kalbidir. Düzenli takip ve doğru kullanım ile verimliliğinizi maksimuma çıkarabilirsiniz!**

*Son güncelleme: 27 Haziran 2025 | Versiyon 1.0*