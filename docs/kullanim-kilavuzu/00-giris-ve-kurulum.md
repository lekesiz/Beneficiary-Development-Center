# BDC Platform - Giriş ve Kurulum Rehberi

## 🎯 Bu Belge Hakkında

Bu belge, **Beneficiary Development Center (BDC)** platformunu yeni kullanmaya başlayacak kullanıcılar için hazırlanmış kapsamlı bir giriş rehberidir. Platform hakkında temel bilgiler, sistem gereksinimleri, ilk giriş işlemleri ve temel kavramlar bu bölümde açıklanmaktadır.

---

## 📋 İçindekiler

1. [Platform Hakkında](#platform-hakkında)
2. [Sistem Gereksinimleri](#sistem-gereksinimleri)
3. [İlk Giriş](#ilk-giriş)
4. [Kullanıcı Rolleri](#kullanıcı-rolleri)
5. [Platform Arayüzü](#platform-arayüzü)
6. [Temel Kavramlar](#temel-kavramlar)
7. [Yardım ve Destek](#yardım-ve-destek)

---

## 🏢 Platform Hakkında

### BDC Nedir?

**Beneficiary Development Center (BDC)**, toplumsal kalkınma ve eğitim programlarının yönetimi için geliştirilmiş kapsamlı bir dijital platformdur. Bu platform ile:

- ✅ Faydalanıcıların (öğrencilerin) takibi ve yönetimi
- ✅ Eğitim programlarının planlanması ve yürütülmesi
- ✅ Değerlendirme ve sınav süreçlerinin dijitalleştirilmesi
- ✅ İlerleme raporlarının otomatik oluşturulması
- ✅ Koç/mentor takip sisteminin etkin kullanımı

gibi işlemler tek bir yerden yönetilebilir.

### Platformun Amacı

BDC platformu, sosyal gelişim programlarında yer alan tüm paydaşları (yöneticiler, eğitmenler, faydalanıcılar) bir araya getirerek:

1. **Verimliliği artırmayı**
2. **Takip ve değerlendirmeyi kolaylaştırmayı**
3. **Raporlama süreçlerini otomatikleştirmeyi**
4. **İletişimi güçlendirmeyi**
5. **Veri güvenliğini sağlamayı**

hedeflemektedir.

---

## 💻 Sistem Gereksinimleri

### Minimum Sistem Gereksinimleri

| Bileşen | Minimum Gereksinim |
|---------|-------------------|
| **İşletim Sistemi** | Windows 10, macOS 10.14, Linux (Ubuntu 18.04+) |
| **Tarayıcı** | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| **İnternet Bağlantısı** | En az 1 Mbps (stabil) |
| **Ekran Çözünürlüğü** | 1024x768 piksel |
| **RAM** | 2 GB |
| **JavaScript** | Etkin olmalı |
| **Çerezler** | Etkin olmalı |

### Önerilen Sistem Gereksinimleri

| Bileşen | Önerilen |
|---------|----------|
| **Tarayıcı** | Google Chrome (güncel versiyon) |
| **İnternet Bağlantısı** | 5+ Mbps |
| **Ekran Çözünürlüğü** | 1920x1080 piksel |
| **RAM** | 4 GB veya üzeri |

### Mobil Cihaz Desteği

- 📱 **iOS:** 12.0 veya üzeri (Safari, Chrome)
- 🤖 **Android:** 8.0 veya üzeri (Chrome, Firefox)
- ✅ Responsive tasarım sayesinde tablet ve telefonlarda sorunsuz çalışır

---

## 🔐 İlk Giriş

### 1. Platform Adresine Erişim

Platform adresine tarayıcınızdan giriş yapın:
```
https://bdc-platform.com
```

> **Not:** Kurumunuzun size verdiği özel adresi kullanın.

### 2. Giriş Ekranı

Giriş ekranında karşınıza çıkacak alanlar:

![Login Screen](./images/login-screen.png)

- **📧 E-posta Adresi:** Kayıtlı e-posta adresinizi girin
- **🔑 Şifre:** Belirlediğiniz şifreyi girin
- **🏢 Kurum Kodu:** Size verilen kurum kodunu girin (örn: 1)
- **💾 Beni Hatırla:** Güvenli cihazlarda işaretleyebilirsiniz

### 3. İlk Giriş Adımları

#### Adım 1: Davet E-postası
- Yöneticinizden gelen davet e-postasını kontrol edin
- "Daveti Kabul Et" butonuna tıklayın
- Link 7 gün içinde geçerlidir

#### Adım 2: Hesap Oluşturma
```
Gerekli Bilgiler:
├── Ad-Soyad
├── E-posta (davet gönderilen adres)
├── Telefon Numarası
├── Tercih Edilen Dil (Türkçe/İngilizce)
└── Güçlü Şifre
```

#### Adım 3: Şifre Kriterleri
Şifreniz aşağıdaki kriterleri sağlamalıdır:
- ✅ En az 8 karakter
- ✅ En az 1 büyük harf (A-Z)
- ✅ En az 1 küçük harf (a-z)
- ✅ En az 1 rakam (0-9)
- ✅ En az 1 özel karakter (!@#$%^&*)

**Örnek güçlü şifre:** `BDC2024!Platform`

#### Adım 4: E-posta Doğrulama
1. Gelen kutunuzu kontrol edin
2. Doğrulama linkine tıklayın
3. Giriş sayfasına yönlendirileceksiniz

### 4. Şifremi Unuttum

Şifrenizi unuttuysanız:

1. Giriş ekranında "Şifremi Unuttum" linkine tıklayın
2. Kayıtlı e-posta adresinizi girin
3. E-postanızdaki yenileme linkine tıklayın
4. Yeni şifrenizi belirleyin
5. Yeni şifre ile giriş yapın

---

## 👥 Kullanıcı Rolleri

BDC platformunda 3 temel kullanıcı rolü bulunur:

### 1. 👨‍💼 Yönetici (Admin)

**Yetkiler:**
- ✅ Tüm sistemi görüntüleme ve yönetme
- ✅ Kullanıcı oluşturma ve yönetimi
- ✅ Program oluşturma ve düzenleme
- ✅ Sistem ayarları ve yapılandırma
- ✅ Tüm raporlara erişim
- ✅ Platform güvenlik ayarları

**Ana Sorumluluklar:**
- Platform yönetimi
- Kullanıcı yetkilendirme
- Sistem bakımı
- Güvenlik kontrolü

### 2. 👨‍🏫 Eğitmen/Koç (Trainer)

**Yetkiler:**
- ✅ Atanan öğrencileri yönetme
- ✅ Program içeriği oluşturma
- ✅ Değerlendirme yapma
- ✅ Öğrenci notları ekleme
- ✅ İlerleme raporları görüntüleme
- ✅ Mesajlaşma ve iletişim

**Ana Sorumluluklar:**
- Öğrenci takibi
- Eğitim içeriği hazırlama
- Değerlendirme yapma
- Mentorluk hizmetleri

### 3. 👨‍🎓 Faydalanıcı/Öğrenci (Student)

**Yetkiler:**
- ✅ Kendi profilini görüntüleme
- ✅ Kayıtlı programlara erişim
- ✅ Değerlendirmelere katılma
- ✅ İlerleme takibi
- ✅ Sertifika indirme
- ✅ Koç ile iletişim

**Ana Sorumluluklar:**
- Programa aktif katılım
- Ödevleri tamamlama
- Değerlendirmelere katılma

---

## 🖥️ Platform Arayüzü

### Ana Bileşenler

```
BDC Platform Arayüzü
├── 🔝 Üst Menü (Header)
│   ├── Logo
│   ├── Arama Çubuğu
│   ├── Bildirimler
│   ├── Profil Menüsü
│   └── Çıkış
├── 📱 Sol Menü (Sidebar)
│   ├── Dashboard
│   ├── Kullanıcılar
│   ├── Faydalanıcılar
│   ├── Programlar
│   ├── Değerlendirmeler
│   ├── Koç Notları
│   ├── Raporlar
│   └── Ayarlar
├── 📄 Ana İçerik Alanı
│   └── Seçilen menüye göre değişen içerik
└── 📊 Sağ Panel (isteğe bağlı)
    ├── Hızlı İstatistikler
    └── Yaklaşan Etkinlikler
```

### Tema ve Görünüm

Platform iki tema seçeneği sunar:
- ☀️ **Açık Tema:** Gündüz kullanımı için
- 🌙 **Koyu Tema:** Göz yorgunluğunu azaltmak için

Tema değiştirmek için: Profil → Ayarlar → Görünüm

---

## 📚 Temel Kavramlar

### 1. Faydalanıcı (Beneficiary)
Programlardan yararlanan, eğitim alan kişiler. Sistemde öğrenci rolüyle tanımlanırlar.

### 2. Program
Belirli bir süre ve içerikle planlanan eğitim/gelişim aktiviteleri bütünü.

### 3. Kurs (Course)
Bir program içindeki spesifik eğitim modülleri.

### 4. Değerlendirme (Evaluation)
Öğrencilerin öğrenme seviyelerini ölçen sınav ve testler.

### 5. Öğrenme Yolu (Learning Path)
Her öğrenci için özelleştirilmiş eğitim rotası.

### 6. Koç Notu (Coach Note)
Eğitmenlerin öğrenciler hakkında tuttukları gelişim notları.

### 7. Kilometre Taşı (Milestone)
Öğrenme yolundaki önemli başarı noktaları.

### 8. Dashboard
Ana kontrol paneli, özet bilgilerin gösterildiği ekran.

### 9. Tenant
Çoklu kurum desteği için kullanılan kurum tanımlayıcısı.

---

## 🆘 Yardım ve Destek

### Platform İçi Yardım

- **❓ Yardım İkonu:** Her sayfada sağ altta bulunan yardım butonuna tıklayın
- **🎥 Video Rehberler:** Yardım menüsünden eğitim videolarına erişin
- **📖 Dokümantasyon:** Platform içi kullanım kılavuzları

### Destek Kanalları

#### Teknik Destek
- **📧 E-posta:** destek@bdc-platform.com
- **📞 Telefon:** 0850 123 45 67
- **🕐 Çalışma Saatleri:** Pazartesi-Cuma, 09:00-18:00

#### Eğitim Desteği
- **👨‍🏫 Koç/Eğitmen:** Size atanan koç ile doğrudan iletişim
- **📚 Eğitim Birimi:** egitim@bdc-platform.com

#### Acil Destek
- **🚨 7/24 Acil Hat:** 0850 999 88 77
- **⚡ Kritik Sorunlar:** Destek talebini "Acil" olarak işaretleyin

### Sık Sorulan Sorular

**S: Mobil cihazımdan platforma erişebilir miyim?**
C: Evet! Platform tamamen responsive tasarıma sahiptir.

**S: Şifremi nasıl değiştirebilirim?**
C: Profil → Güvenlik Ayarları → Şifre Değiştir

**S: Birden fazla programa aynı anda kayıt olabilir miyim?**
C: Evet, yöneticinizin izin verdiği kadar programa kayıt olabilirsiniz.

**S: Sertifikalarımı nereden indirebilirim?**
C: Profil → Başarılarım → Sertifikalar bölümünden

---

## 🚀 Sonraki Adımlar

Artık platforma giriş yaptınız! Sıradaki adımlar:

1. **Profilinizi Tamamlayın** - Tüm bilgilerinizi ekleyin
2. **Dashboard'u Keşfedin** - Ana kontrol panelinizi tanıyın
3. **Programlara Göz Atın** - Mevcut programları inceleyin
4. **Koçunuzla Tanışın** - Size atanan koç ile iletişime geçin

### Önerilen Okuma Sırası

1. ✅ **00-Giriş ve Kurulum** (Bu belge)
2. ➡️ **[01-Dashboard Paneli](./01-dashboard-paneli.md)**
3. ➡️ **[02-Kullanıcı Yönetimi](./02-kullanici-yonetimi.md)**
4. ➡️ **[03-Faydalanıcı Yönetimi](./03-faydalanıcı-yonetimi.md)**

---

**🎉 BDC Platform'a hoş geldiniz! Başarılı bir öğrenme yolculuğu dileriz.**

*Son güncelleme: 27 Haziran 2025 | Versiyon 1.0*