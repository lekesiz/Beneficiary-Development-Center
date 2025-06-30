# BDC Platform - Kullanıcı Yönetimi Detaylı Rehberi

## 🎯 Bu Belge Hakkında

Kullanıcı Yönetimi modülü, BDC platformundaki tüm kullanıcıların (yönetici, eğitmen, öğrenci) oluşturulması, düzenlenmesi ve yönetilmesi işlemlerini kapsar. Bu belgede modülün tüm özellikleri detaylıca açıklanmaktadır.

---

## 📋 İçindekiler

1. [Kullanıcı Yönetimi Genel Bakış](#kullanıcı-yönetimi-genel-bakış)
2. [Kullanıcı Listesi Ekranı](#kullanıcı-listesi-ekranı)
3. [Yeni Kullanıcı Oluşturma](#yeni-kullanıcı-oluşturma)
4. [Kullanıcı Profil Yönetimi](#kullanıcı-profil-yönetimi)
5. [Rol ve Yetki Yönetimi](#rol-ve-yetki-yönetimi)
6. [Toplu İşlemler](#toplu-i̇şlemler)
7. [Güvenlik Ayarları](#güvenlik-ayarları)
8. [Raporlama ve Denetim](#raporlama-ve-denetim)

---

## 👥 Kullanıcı Yönetimi Genel Bakış

### Erişim Yolu
```
Ana Menü → Kullanıcılar → Kullanıcı Yönetimi
```

### Kimler Erişebilir?
- ✅ **Yönetici (Admin):** Tam erişim
- ⚠️ **Eğitmen:** Sadece kendi öğrencilerini görüntüleme
- ❌ **Öğrenci:** Erişim yok

### Temel Özellikler
- 👤 Kullanıcı oluşturma, düzenleme, silme
- 🔐 Rol ve yetki atama
- 📧 Davet e-postası gönderme
- 🔄 Toplu kullanıcı içe/dışa aktarma
- 📊 Kullanıcı aktivite takibi
- 🔍 Gelişmiş arama ve filtreleme

---

## 📋 Kullanıcı Listesi Ekranı

Kullanıcı Yönetimi'ne girdiğinizde karşınıza çıkan ana ekran.

### Ekran Bileşenleri

```
Kullanıcı Listesi Ekranı
├── 🔍 Arama ve Filtre Çubuğu
├── 📊 Kullanıcı Tablosu
├── 📄 Sayfalama Kontrolleri
└── ⚡ Hızlı İşlem Butonları
```

### Tablo Sütunları

| Sütun | Açıklama | Sıralanabilir | Gizlenebilir |
|-------|----------|---------------|--------------|
| **☐** | Çoklu seçim | ❌ | ❌ |
| **ID** | Benzersiz kullanıcı numarası | ✅ | ✅ |
| **Ad Soyad** | Kullanıcının tam adı | ✅ | ❌ |
| **E-posta** | Giriş için kullanılan e-posta | ✅ | ❌ |
| **Rol** | Kullanıcı rolü (Admin/Eğitmen/Öğrenci) | ✅ | ❌ |
| **Durum** | Aktif/Pasif/Beklemede | ✅ | ❌ |
| **Kayıt Tarihi** | Sisteme katılma tarihi | ✅ | ✅ |
| **Son Giriş** | En son giriş zamanı | ✅ | ✅ |
| **İşlemler** | Düzenle/Sil/Detay butonları | ❌ | ❌ |

### Arama ve Filtreleme

#### 🔍 Arama Özellikleri
- **Ad/Soyad ile arama**
- **E-posta ile arama**
- **Telefon numarası ile arama**
- **Kullanıcı ID ile arama**

#### 🎛️ Filtre Seçenekleri

**Rol Filtresi:**
- [ ] Tümü
- [ ] Yönetici
- [ ] Eğitmen
- [ ] Öğrenci

**Durum Filtresi:**
- [ ] Tümü
- [ ] Aktif
- [ ] Pasif
- [ ] Beklemede
- [ ] Askıya Alınmış

**Tarih Filtresi:**
- Kayıt tarihi aralığı
- Son giriş tarihi aralığı
- Özel tarih aralığı

### Sıralama Seçenekleri

Tablodaki herhangi bir sütun başlığına tıklayarak sıralama yapabilirsiniz:
- ⬆️ Artan sıralama
- ⬇️ Azalan sıralama
- ↕️ Varsayılan sıralama

---

## ➕ Yeni Kullanıcı Oluşturma

### Kullanıcı Oluşturma Yöntemleri

#### 1. Tekil Kullanıcı Ekleme

**Adımlar:**
1. "Yeni Kullanıcı" butonuna tıklayın
2. Açılan formda bilgileri doldurun
3. Rol seçin
4. "Kaydet" butonuna basın

**Form Alanları:**

##### Temel Bilgiler
```
👤 KİŞİSEL BİLGİLER
├── Ad* (zorunlu)
├── Soyad* (zorunlu)
├── E-posta* (zorunlu, benzersiz)
├── Telefon (opsiyonel)
├── Doğum Tarihi (opsiyonel)
└── Cinsiyet (opsiyonel)
```

##### İletişim Bilgileri
```
📍 ADRES BİLGİLERİ
├── Ülke
├── Şehir
├── İlçe
├── Mahalle
├── Adres Detayı
└── Posta Kodu
```

##### Hesap Ayarları
```
⚙️ HESAP AYARLARI
├── Kullanıcı Rolü* (zorunlu)
├── Departman/Birim
├── Yönetici Ataması
├── Başlangıç Tarihi
├── Dil Tercihi
└── Zaman Dilimi
```

#### 2. Toplu Kullanıcı Ekleme (CSV)

**CSV Dosya Formatı:**
```csv
ad,soyad,email,telefon,rol,departman
Ahmet,Yılmaz,ahmet@example.com,5551234567,student,IT
Ayşe,Kaya,ayse@example.com,5559876543,trainer,HR
```

**İçe Aktarma Adımları:**
1. "Toplu Ekle" → "CSV'den İçe Aktar"
2. Şablon dosyasını indirin
3. Dosyayı doldurun
4. Dosyayı yükleyin
5. Önizlemeyi kontrol edin
6. "İçe Aktar" butonuna basın

### Davet E-postası Gönderme

Yeni kullanıcı oluşturduktan sonra:

**Otomatik Davet:**
- [ ] Kayıt sonrası otomatik davet gönder

**Manuel Davet:**
1. Kullanıcıyı listeden seçin
2. "İşlemler" → "Davet Gönder"
3. Davet mesajını özelleştirin (opsiyonel)
4. "Gönder" butonuna basın

**Davet E-postası İçeriği:**
```
Konu: BDC Platform'a Davetlisiniz

Merhaba [Ad Soyad],

[Kurum Adı] BDC platformuna davet edildiniz.

Rol: [Kullanıcı Rolü]
Davet Eden: [Yönetici Adı]

Hesabınızı aktifleştirmek için aşağıdaki linke tıklayın:
[Aktivasyon Linki]

Bu link 7 gün geçerlidir.

Saygılarımızla,
BDC Platform Ekibi
```

---

## 👤 Kullanıcı Profil Yönetimi

### Profil Görüntüleme

Herhangi bir kullanıcının detaylı profilini görüntülemek için:
1. Listeden kullanıcıyı bulun
2. "İşlemler" → "Detay" veya kullanıcı adına tıklayın

### Profil Bölümleri

#### 1. Genel Bilgiler
```
📋 GENEL BİLGİLER
├── Profil Fotoğrafı
├── Ad Soyad
├── E-posta
├── Telefon
├── Rol ve Yetki
├── Departman
├── Kayıt Tarihi
└── Son Güncelleme
```

#### 2. Aktivite Özeti
```
📊 AKTİVİTE ÖZETİ
├── Toplam Giriş Sayısı
├── Son Giriş Zamanı
├── Ortalama Oturum Süresi
├── Tamamlanan Görevler
├── Aktif Program Sayısı
└── Platform Kullanım Oranı
```

#### 3. Güvenlik Bilgileri
```
🔐 GÜVENLİK
├── Şifre Son Değiştirilme
├── İki Faktörlü Doğrulama
├── Aktif Oturumlar
├── Giriş Geçmişi
├── Başarısız Giriş Denemeleri
└── IP Kısıtlamaları
```

### Profil Düzenleme

**Düzenlenebilir Alanlar:**
- ✅ Kişisel bilgiler
- ✅ İletişim bilgileri
- ✅ Profil fotoğrafı
- ✅ Dil ve zaman dilimi
- ⚠️ Rol (sadece admin)
- ⚠️ E-posta (onay gerekli)

**Düzenleme Adımları:**
1. Profil sayfasında "Düzenle" butonuna tıklayın
2. Gerekli değişiklikleri yapın
3. "Değişiklikleri Kaydet" butonuna basın
4. Onay mesajını bekleyin

---

## 🔐 Rol ve Yetki Yönetimi

### Sistem Rolleri

#### 1. 👨‍💼 Yönetici (Admin)
**Yetkiler:**
```
✅ Tüm kullanıcıları yönetme
✅ Sistem ayarlarına erişim
✅ Rol ve yetki atama
✅ Platform yapılandırması
✅ Güvenlik ayarları
✅ Tüm raporlara erişim
```

#### 2. 👨‍🏫 Eğitmen (Trainer)
**Yetkiler:**
```
✅ Öğrenci yönetimi
✅ Program oluşturma
✅ Değerlendirme yapma
✅ İçerik yükleme
✅ Raporlama (sınırlı)
❌ Sistem ayarları
```

#### 3. 👨‍🎓 Öğrenci (Student)
**Yetkiler:**
```
✅ Profil düzenleme
✅ Program katılımı
✅ Değerlendirmelere katılma
✅ Sertifika indirme
❌ Diğer kullanıcıları görme
❌ İçerik oluşturma
```

### Rol Değiştirme

**Adımlar:**
1. Kullanıcı profilini açın
2. "Rol ve Yetkiler" sekmesine gidin
3. Yeni rolü seçin
4. Değişiklik nedenini yazın
5. "Rolü Güncelle" butonuna basın

**Dikkat Edilmesi Gerekenler:**
- ⚠️ Rol değişiklikleri denetim kaydına alınır
- ⚠️ Kullanıcı otomatik olarak bilgilendirilir
- ⚠️ Aktif oturumlar sonlandırılır

### Özel Yetkiler

Rollere ek olarak özel yetkiler atanabilir:

**Özel Yetki Türleri:**
- 📊 Gelişmiş raporlama
- 📥 Veri dışa aktarma
- 🔄 Toplu işlem yapma
- 📧 Toplu e-posta gönderme
- 🎯 Özel modül erişimi

---

## 🔄 Toplu İşlemler

### Çoklu Kullanıcı Seçimi

1. Tabloda kullanıcıların yanındaki checkbox'ları işaretleyin
2. Veya üst checkbox ile tüm sayfayı seçin
3. "X kullanıcı seçildi" mesajı görünür

### Toplu İşlem Seçenekleri

#### 1. Toplu Durum Değiştirme
```
Seçenekler:
├── Aktif Yap
├── Pasif Yap
├── Askıya Al
└── Hesabı Kilitle
```

#### 2. Toplu Rol Atama
```
Adımlar:
1. Kullanıcıları seçin
2. "Toplu İşlemler" → "Rol Ata"
3. Yeni rolü seçin
4. Onaylayın
```

#### 3. Toplu E-posta Gönderme
```
E-posta Türleri:
├── Hoş geldin mesajı
├── Şifre sıfırlama
├── Duyuru
└── Özel mesaj
```

#### 4. Toplu Dışa Aktarma
```
Format Seçenekleri:
├── Excel (.xlsx)
├── CSV (.csv)
├── PDF (liste)
└── JSON (API için)
```

### İşlem Onayı ve Geri Alma

**Onay Süreci:**
1. İşlem özeti gösterilir
2. Etkilenecek kullanıcı sayısı
3. "Onayla" veya "İptal"

**Geri Alma:**
- Son 24 saat içindeki toplu işlemler geri alınabilir
- "İşlem Geçmişi" → "Geri Al"

---

## 🔒 Güvenlik Ayarları

### Şifre Politikaları

**Varsayılan Şifre Kuralları:**
```
✅ Minimum 8 karakter
✅ En az 1 büyük harf
✅ En az 1 küçük harf
✅ En az 1 rakam
✅ En az 1 özel karakter
✅ Son 5 şifre kullanılamaz
✅ 90 günde bir değiştirilmeli
```

### İki Faktörlü Doğrulama (2FA)

**Aktivasyon:**
1. Kullanıcı profiline gidin
2. "Güvenlik" sekmesi
3. "2FA'yı Etkinleştir"
4. QR kodu tarayın
5. Doğrulama kodunu girin

**2FA Yöntemleri:**
- 📱 Authenticator uygulaması
- 📧 E-posta kodu
- 💬 SMS kodu

### Oturum Yönetimi

**Oturum Ayarları:**
- ⏱️ Maksimum oturum süresi: 8 saat
- 🔄 Otomatik çıkış süresi: 30 dakika hareketsizlik
- 📱 Eşzamanlı oturum limiti: 3 cihaz

**Aktif Oturumları Görüntüleme:**
```
Oturum Bilgileri:
├── IP Adresi
├── Cihaz Türü
├── Tarayıcı
├── Konum (yaklaşık)
├── Başlangıç Zamanı
└── Son Aktivite
```

### IP Kısıtlamaları

**IP Beyaz Liste:**
- Sadece belirli IP'lerden giriş
- Ofis IP aralıkları
- VPN sunucuları

**Kara Liste:**
- Yasaklı IP'ler
- Otomatik spam tespiti
- Brute force koruması

---

## 📊 Raporlama ve Denetim

### Kullanıcı Raporları

#### 1. Aktivite Raporu
```
İçerik:
├── Giriş istatistikleri
├── Platform kullanım süreleri
├── En aktif saatler
├── Cihaz dağılımı
└── Konum analizi
```

#### 2. Performans Raporu
```
Metrikler:
├── Görev tamamlama oranı
├── Ortalama yanıt süresi
├── Etkileşim skoru
├── İlerleme hızı
└── Başarı oranı
```

### Denetim Kayıtları

**Kaydedilen İşlemler:**
- 🔐 Giriş/çıkış işlemleri
- 👤 Profil değişiklikleri
- 🔑 Şifre değişiklikleri
- 🎭 Rol değişiklikleri
- 🗑️ Hesap silme işlemleri
- 📧 E-posta gönderim logları

**Denetim Kaydı Görüntüleme:**
1. "Raporlar" → "Denetim Kayıtları"
2. Kullanıcı veya tarih filtresi uygulayın
3. Detaylı logu inceleyin

### Uyumluluk Raporları

**KVKK/GDPR Uyumluluğu:**
- Kişisel veri envanteri
- Veri işleme kayıtları
- Kullanıcı onay logları
- Veri silme talepleri

---

## 🛠️ Gelişmiş Özellikler

### API Erişimi

**Kullanıcı API Endpoints:**
```
GET    /api/v1/users          # Tüm kullanıcılar
GET    /api/v1/users/{id}     # Tekil kullanıcı
POST   /api/v1/users          # Yeni kullanıcı
PUT    /api/v1/users/{id}     # Güncelleme
DELETE /api/v1/users/{id}     # Silme
```

### Webhook Entegrasyonu

**Tetiklenen Olaylar:**
- user.created
- user.updated
- user.deleted
- user.role_changed
- user.logged_in

### LDAP/Active Directory

**Entegrasyon Özellikleri:**
- Otomatik kullanıcı senkronizasyonu
- Single Sign-On (SSO)
- Grup bazlı rol atama
- Şifre politikası senkronizasyonu

---

## 💡 İpuçları ve En İyi Uygulamalar

### Verimli Kullanıcı Yönetimi

1. **Düzenli Temizlik:**
   - Pasif hesapları düzenli kontrol edin
   - 6 ay girmeyen hesapları askıya alın
   - Yılda bir denetim yapın

2. **Güvenlik Önlemleri:**
   - 2FA'yı zorunlu yapın
   - Güçlü şifre politikası uygulayın
   - IP kısıtlamalarını kullanın

3. **Dokümantasyon:**
   - Rol değişikliklerini belgeleyin
   - Özel yetkileri kaydedin
   - Denetim loglarını arşivleyin

### Sorun Giderme

**Sık Karşılaşılan Sorunlar:**

1. **Kullanıcı giriş yapamıyor:**
   - Hesap durumunu kontrol edin
   - Şifre deneme limitini kontrol edin
   - 2FA sorunlarını giderin

2. **E-posta gitmiyor:**
   - E-posta adresini doğrulayın
   - Spam klasörünü kontrol ettirin
   - E-posta sunucu ayarlarını kontrol edin

3. **Rol değişiklikleri yansımıyor:**
   - Kullanıcının çıkış yapıp girmesini sağlayın
   - Tarayıcı önbelleğini temizletin
   - Oturum süresini kontrol edin

---

**👥 Kullanıcı Yönetimi, BDC platformunun güvenli ve verimli çalışması için kritik öneme sahiptir. Düzenli bakım ve takip ile sorunsuz bir deneyim sağlayabilirsiniz.**

*Son güncelleme: 27 Haziran 2025 | Versiyon 1.0*