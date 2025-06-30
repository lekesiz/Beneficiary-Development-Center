# BDC Platform - Bildirimler ve Mesajlaşma Sistemi Detaylı Rehberi

## 🎯 Bu Belge Hakkında

Bildirimler ve Mesajlaşma modülü, BDC platformunda kullanıcılar arasında etkili iletişimi sağlayan, önemli olayları bildiren ve platform içi etkileşimi artıran kapsamlı bir iletişim sistemidir. Bu belgede bildirim türleri, mesajlaşma özellikleri ve iletişim araçlarının tüm detayları açıklanmaktadır.

---

## 📋 İçindekiler

1. [Bildirim Sistemi Genel Bakış](#bildirim-sistemi-genel-bakış)
2. [Bildirim Türleri ve Kategorileri](#bildirim-türleri-ve-kategorileri)
3. [Bildirim Ayarları ve Yönetimi](#bildirim-ayarları-ve-yönetimi)
4. [Mesajlaşma Sistemi](#mesajlaşma-sistemi)
5. [Grup Mesajlaşma ve Kanallar](#grup-mesajlaşma-ve-kanallar)
6. [E-posta Entegrasyonu](#e-posta-entegrasyonu)
7. [Mobil Bildirimler](#mobil-bildirimler)
8. [Duyuru ve Haber Sistemi](#duyuru-ve-haber-sistemi)
9. [Bildirim Merkezi](#bildirim-merkezi)
10. [İletişim Güvenliği](#i̇letişim-güvenliği)

---

## 🔔 Bildirim Sistemi Genel Bakış

### Erişim Yolu
```
Üst Menü → Bildirim İkonu (🔔)
veya
Ana Menü → Bildirimler → Bildirim Merkezi
```

### Kimler Erişebilir?
- ✅ **Tüm Kullanıcılar:** Kendi bildirimlerini görüntüleme
- ✅ **Yönetici:** Sistem geneli bildirim gönderme
- ✅ **Eğitmen:** Öğrencilere bildirim gönderme

### Bildirim Sistemi Nedir?
Platform üzerindeki önemli olayları, güncellemeleri ve etkileşimleri kullanıcılara ileten çok kanallı bir iletişim sistemidir.

### Ana Bileşenler
```
🔔 BİLDİRİM SİSTEMİ
├── 📱 Platform İçi Bildirimler
├── 📧 E-posta Bildirimleri
├── 💬 Push Notifications
├── 📢 Duyurular
├── 💌 Mesajlaşma
├── 🔊 Ses Bildirimleri
├── 📊 Bildirim Merkezi
└── ⚙️ Bildirim Ayarları
```

---

## 📬 Bildirim Türleri ve Kategorileri

### Sistem Bildirimleri

```
🖥️ SİSTEM BİLDİRİMLERİ
├── Hesap İşlemleri
│   ├── Giriş bildirimi
│   ├── Şifre değişikliği
│   ├── Güvenlik uyarıları
│   ├── Oturum sona erme
│   └── Profil güncellemeleri
├── Platform Güncellemeleri
│   ├── Yeni özellikler
│   ├── Bakım duyuruları
│   ├── Sistem durumu
│   ├── Versiyon notları
│   └── Politika değişiklikleri
├── Teknik Bildirimler
│   ├── API limitleri
│   ├── Depolama uyarıları
│   ├── Performans bildirimleri
│   ├── Hata raporları
│   └── Entegrasyon durumu
└── Güvenlik Bildirimleri
    ├── Şüpheli aktivite
    ├── Yeni cihaz girişi
    ├── IP değişikliği
    ├── 2FA aktivasyonu
    └── Erişim logları
```

### Eğitim Bildirimleri

```
📚 EĞİTİM BİLDİRİMLERİ
├── Program Bildirimleri
│   ├── Yeni program kaydı
│   ├── Program başlangıcı
│   ├── Ders hatırlatıcıları
│   ├── Program güncellemeleri
│   └── Sertifika hazır
├── Ders ve İçerik
│   ├── Yeni içerik eklendi
│   ├── Canlı ders başlıyor
│   ├── Video yayınlandı
│   ├── Materyal güncellendi
│   └── İçerik süresi doluyor
├── Ödev ve Projeler
│   ├── Yeni ödev atandı
│   ├── Teslim tarihi yaklaşıyor
│   ├── Geç teslim uyarısı
│   ├── Ödev değerlendirildi
│   └── Geri bildirim var
└── Değerlendirmeler
    ├── Sınav programı
    ├── Quiz hatırlatıcı
    ├── Sonuç açıklandı
    ├── Not güncellendi
    └── Sertifika kazandınız
```

### Sosyal Bildirimler

```
👥 SOSYAL BİLDİRİMLER
├── Mesajlar
│   ├── Yeni mesaj
│   ├── Mesaj okundu
│   ├── Grup mesajı
│   ├── Mention (@bahsetme)
│   └── Mesaj tepkisi
├── Forum ve Tartışmalar
│   ├── Yeni yorum
│   ├── Konu takibi
│   ├── Beğeni aldınız
│   ├── En iyi cevap seçildi
│   └── Moderatör uyarısı
├── Bağlantılar
│   ├── Arkadaşlık isteği
│   ├── Takip bildirimi
│   ├── Profil görüntüleme
│   ├── Ortak bağlantı
│   └── Grup daveti
└── Etkinlikler
    ├── Etkinlik daveti
    ├── Etkinlik hatırlatıcı
    ├── Katılım onayı
    ├── Etkinlik iptali
    └── Etkinlik değişikliği
```

### Performans Bildirimleri

```
📊 PERFORMANS BİLDİRİMLERİ
├── Başarı Bildirimleri
│   ├── Milestone tamamlandı
│   ├── Rozet kazandınız
│   ├── Sıralama yükseldi
│   ├── Rekor kırdınız
│   └── Başarı açıldı
├── İlerleme Bildirimleri
│   ├── Haftalık özet
│   ├── İlerleme raporu
│   ├── Hedef tamamlandı
│   ├── Streak devam ediyor
│   └── Seviye atladınız
├── Motivasyon
│   ├── Günün sözü
│   ├── Tebrik mesajı
│   ├── Teşvik bildirimi
│   ├── Başarı hikayesi
│   └── Peer takdiri
└── Uyarılar
    ├── Performans düşüşü
    ├── Devamsızlık uyarısı
    ├── Hedeften sapma
    ├── Risk bildirimi
    └── Destek önerisi
```

---

## ⚙️ Bildirim Ayarları ve Yönetimi

### Bildirim Tercihleri

```
🎛️ BİLDİRİM TERCİHLERİ
├── Kanal Tercihleri
│   ├── Platform içi
│   │   ├── ✅ Etkin/Pasif
│   │   ├── 🔊 Ses açık/kapalı
│   │   └── 🎨 Görsel stil
│   ├── E-posta
│   │   ├── 📧 Birincil e-posta
│   │   ├── 📅 Gönderim sıklığı
│   │   └── 📦 Toplu/Anlık
│   ├── SMS
│   │   ├── 📱 Telefon numarası
│   │   ├── ⏰ Gönderim saatleri
│   │   └── 🌍 Ülke kodu
│   └── Push Notifications
│       ├── 📲 Cihaz izinleri
│       ├── 🔔 Bildirim sesleri
│       └── 📍 Konum bazlı
├── Kategori Ayarları
│   ├── Her kategori için ayrı kontrol
│   ├── Öncelik seviyeleri
│   ├── Sessiz saatler
│   └── Tatil modu
└── Frekans Kontrolü
    ├── Anlık bildirimler
    ├── Saatlik özet
    ├── Günlük özet
    ├── Haftalık özet
    └── Özel zamanlama
```

### Bildirim Filtreleme

```
🔍 FİLTRELEME SEÇENEKLERİ
├── Gönderen Bazlı
│   ├── Sistem bildirimleri
│   ├── Eğitmen bildirimleri
│   ├── Öğrenci bildirimleri
│   ├── Yönetim bildirimleri
│   └── Bot bildirimleri
├── Öncelik Bazlı
│   ├── 🔴 Kritik (Her zaman)
│   ├── 🟡 Önemli (Çalışma saatleri)
│   ├── 🟢 Normal (Tercih edilen)
│   ├── ⚪ Düşük (Özet olarak)
│   └── 🔇 Sessiz (Sadece kayıt)
├── İçerik Bazlı
│   ├── Anahtar kelimeler
│   ├── Konu filtreleri
│   ├── Dil tercihi
│   └── İçerik türü
└── Zaman Bazlı
    ├── Çalışma saatleri
    ├── Hafta sonu ayarı
    ├── Tatil günleri
    └── Timezone ayarı
```

### Bildirim Yönetim Paneli

```
📊 YÖNETİM PANELİ
├── Bildirim Geçmişi
│   ├── Tüm bildirimler
│   ├── Okunmuş/Okunmamış
│   ├── Arşivlenmiş
│   ├── Silinmiş
│   └── Favoriler
├── İstatistikler
│   ├── Günlük bildirim sayısı
│   ├── Kategori dağılımı
│   ├── Etkileşim oranı
│   ├── En aktif saatler
│   └── Trend analizi
├── Toplu İşlemler
│   ├── Tümünü okundu işaretle
│   ├── Toplu silme
│   ├── Kategori değiştirme
│   ├── Arşivleme
│   └── Dışa aktarma
└── Arama ve Filtreleme
    ├── Tarih aralığı
    ├── Kategori seçimi
    ├── Metin arama
    ├── Gönderen filtresi
    └── Durum filtresi
```

---

## 💬 Mesajlaşma Sistemi

### Mesajlaşma Özellikleri

```
💌 MESAJLAŞMA ÖZELLİKLERİ
├── Mesaj Türleri
│   ├── Birebir mesajlar
│   ├── Grup mesajları
│   ├── Broadcast mesajlar
│   ├── Otomatik mesajlar
│   └── Sistem mesajları
├── Mesaj Formatları
│   ├── Metin mesajları
│   ├── Rich text (zengin metin)
│   ├── Emoji ve sticker
│   ├── Dosya paylaşımı
│   │   ├── Dökümanlar
│   │   ├── Resimler
│   │   ├── Videolar
│   │   └── Ses kayıtları
│   └── Link önizleme
├── Etkileşim Özellikleri
│   ├── Mesaj tepkileri (👍❤️😊)
│   ├── Mention (@kullanıcı)
│   ├── Reply (yanıtlama)
│   ├── Forward (iletme)
│   └── Pin (sabitleme)
└── Durum Göstergeleri
    ├── Online/Offline durumu
    ├── Son görülme
    ├── Yazıyor... göstergesi
    ├── Okundu bilgisi
    └── Teslim durumu
```

### Mesajlaşma Arayüzü

```
🖥️ MESAJLAŞMA ARAYÜZÜ
├── Sol Panel - Sohbet Listesi
│   ├── Aktif sohbetler
│   ├── Son mesajlar
│   ├── Okunmamış sayısı
│   ├── Arama çubuğu
│   └── Yeni mesaj butonu
├── Orta Panel - Mesaj Alanı
│   ├── Mesaj geçmişi
│   ├── Tarih ayırıcıları
│   ├── Mesaj baloncukları
│   ├── Medya galerisi
│   └── Scroll kontrolü
├── Sağ Panel - Detaylar
│   ├── Kullanıcı/Grup bilgisi
│   ├── Paylaşılan medya
│   ├── Paylaşılan linkler
│   ├── Ortak gruplar
│   └── Ayarlar
└── Alt Panel - Mesaj Gönderme
    ├── Mesaj input alanı
    ├── Emoji picker
    ├── Dosya ekleme
    ├── Ses kaydı
    └── Gönder butonu
```

### Gelişmiş Mesajlaşma Özellikleri

```
🚀 GELİŞMİŞ ÖZELLİKLER
├── Mesaj Şifreleme
│   ├── End-to-end encryption
│   ├── Mesaj kilitleme
│   ├── Kendini imha eden mesajlar
│   └── Güvenli dosya paylaşımı
├── Akıllı Özellikler
│   ├── Otomatik çeviri
│   ├── Spell check
│   ├── Smart reply önerileri
│   ├── Mesaj özetleme
│   └── Sentiment analizi
├── Zamanlama
│   ├── Zamanlanmış mesajlar
│   ├── Hatırlatıcı mesajlar
│   ├── Tekrarlayan mesajlar
│   └── Timezone desteği
└── Entegrasyonlar
    ├── Takvim entegrasyonu
    ├── Task oluşturma
    ├── Video konferans başlatma
    ├── Dosya yönetimi
    └── Third-party apps
```

---

## 👥 Grup Mesajlaşma ve Kanallar

### Grup Oluşturma ve Yönetimi

```
👥 GRUP YÖNETİMİ
├── Grup Oluşturma
│   ├── Grup adı ve açıklaması
│   ├── Grup fotoğrafı
│   ├── Gizlilik ayarları
│   │   ├── Açık grup
│   │   ├── Kapalı grup
│   │   └── Gizli grup
│   ├── Üye ekleme
│   └── Rol ataması
├── Grup Rolleri
│   ├── 👑 Grup sahibi
│   ├── 👮 Moderatör
│   ├── 👤 Normal üye
│   ├── 👻 Misafir
│   └── 🤖 Bot
├── Grup Ayarları
│   ├── Mesaj izinleri
│   ├── Dosya paylaşım limiti
│   ├── Üye ekleme yetkisi
│   ├── Mesaj düzenleme süresi
│   └── Otomatik silme
└── Grup Araçları
    ├── Anket oluşturma
    ├── Etkinlik planlama
    ├── Dosya arşivi
    ├── Duyuru sistemi
    └── Grup istatistikleri
```

### Kanal Sistemi

```
📢 KANAL SİSTEMİ
├── Kanal Türleri
│   ├── 📰 Haber kanalı
│   ├── 📚 Eğitim kanalı
│   ├── 💬 Tartışma kanalı
│   ├── 📊 Veri kanalı
│   └── 🎯 Proje kanalı
├── Kanal Özellikleri
│   ├── Tek yönlü iletişim
│   ├── Çift yönlü iletişim
│   ├── Moderasyon
│   ├── Otomatik içerik
│   └── RSS entegrasyonu
├── Abone Yönetimi
│   ├── Abone listesi
│   ├── Davet sistemi
│   ├── Onay mekanizması
│   ├── Abone segmentasyonu
│   └── Bildirim tercihleri
└── İçerik Yönetimi
    ├── İçerik takvimi
    ├── Zamanlanmış yayın
    ├── İçerik kategorileri
    ├── Etiketleme sistemi
    └── Arşiv yönetimi
```

### Thread (Konu) Sistemi

```
🔗 THREAD SİSTEMİ
├── Thread Oluşturma
│   ├── Ana mesajdan thread
│   ├── Konu başlığı
│   ├── Katılımcı kontrolü
│   └── Thread ayarları
├── Thread Özellikleri
│   ├── Alt konuşmalar
│   ├── Bağımsız bildirimler
│   ├── Thread içi arama
│   ├── Dosya organizasyonu
│   └── Thread özeti
├── Thread Yönetimi
│   ├── Thread kilitleme
│   ├── Thread taşıma
│   ├── Thread birleştirme
│   ├── Thread silme
│   └── Thread arşivleme
└── Thread Analitik
    ├── Katılım metrikleri
    ├── Mesaj istatistikleri
    ├── En aktif threadler
    └── Thread yaşam döngüsü
```

---

## 📧 E-posta Entegrasyonu

### E-posta Bildirimleri

```
📧 E-POSTA BİLDİRİMLERİ
├── E-posta Şablonları
│   ├── Hoş geldin e-postası
│   ├── Şifre sıfırlama
│   ├── Ders hatırlatıcısı
│   ├── Performans özeti
│   ├── Sertifika bildirimi
│   └── Özel şablonlar
├── Kişiselleştirme
│   ├── Dinamik içerik
│   ├── Kullanıcı bilgileri
│   ├── Kişisel öneriler
│   ├── Özel selamlamalar
│   └── İmza yönetimi
├── E-posta Tasarımı
│   ├── Responsive tasarım
│   ├── Dark mode desteği
│   ├── Brand guidelines
│   ├── CTA butonları
│   └── Sosyal medya linkleri
└── Gönderim Ayarları
    ├── Gönderim zamanlaması
    ├── Batch processing
    ├── Öncelik sıralaması
    ├── Retry mekanizması
    └── Bounce yönetimi
```

### E-posta Özet Sistemi

```
📊 E-POSTA ÖZETLERİ
├── Günlük Özet
│   ├── Bugünkü aktiviteler
│   ├── Yarınki program
│   ├── Bekleyen görevler
│   ├── Önemli bildirimler
│   └── Quick actions
├── Haftalık Özet
│   ├── Haftalık performans
│   ├── Tamamlanan görevler
│   ├── Gelecek hafta planı
│   ├── Başarılar ve rozetler
│   └── Öneriler
├── Aylık Rapor
│   ├── Detaylı analiz
│   ├── İlerleme grafikleri
│   ├── Karşılaştırmalar
│   ├── Hedef takibi
│   └── Sonraki ay hedefleri
└── Özel Raporlar
    ├── Dönem sonu raporu
    ├── Proje özeti
    ├── Başarı raporu
    └── Yıllık değerlendirme
```

---

## 📱 Mobil Bildirimler

### Push Notification Sistemi

```
📲 PUSH NOTIFICATIONS
├── Bildirim Türleri
│   ├── Alert notifications
│   ├── Silent notifications
│   ├── Rich notifications
│   ├── Interactive notifications
│   └── Location-based
├── Rich Media
│   ├── Resimli bildirimler
│   ├── Video thumbnails
│   ├── Action buttons
│   ├── Quick reply
│   └── Custom sounds
├── Targeting
│   ├── Tüm kullanıcılar
│   ├── Segment bazlı
│   ├── Davranış bazlı
│   ├── Lokasyon bazlı
│   └── Cihaz bazlı
└── Optimizasyon
    ├── A/B testing
    ├── Gönderim zamanı
    ├── Frekans kontrolü
    ├── Engagement tracking
    └── Conversion analizi
```

### Mobil Uygulama Entegrasyonu

```
📱 MOBİL ENTEGRASYON
├── Native Integration
│   ├── iOS (APNS)
│   ├── Android (FCM)
│   ├── Huawei (HMS)
│   └── Web Push
├── In-App Messaging
│   ├── Pop-up mesajlar
│   ├── Banner bildirimleri
│   ├── Full-screen mesajlar
│   ├── Tooltip'ler
│   └── Badges
├── Deep Linking
│   ├── Doğrudan sayfa yönlendirme
│   ├── Parametre taşıma
│   ├── Deferred deep linking
│   ├── Universal links
│   └── App indexing
└── Offline Desteği
    ├── Mesaj kuyrukları
    ├── Senkronizasyon
    ├── Cache yönetimi
    └── Conflict resolution
```

---

## 📢 Duyuru ve Haber Sistemi

### Duyuru Yönetimi

```
📣 DUYURU YÖNETİMİ
├── Duyuru Oluşturma
│   ├── Başlık ve içerik
│   ├── Kategori seçimi
│   ├── Öncelik seviyesi
│   ├── Hedef kitle
│   ├── Yayın zamanı
│   └── Bitiş tarihi
├── Duyuru Türleri
│   ├── 🚨 Acil duyurular
│   ├── 📅 Etkinlik duyuruları
│   ├── 🎓 Akademik duyurular
│   ├── 💼 İdari duyurular
│   └── 🎉 Sosyal duyurular
├── Görünürlük Ayarları
│   ├── Platform geneli
│   ├── Program bazlı
│   ├── Rol bazlı
│   ├── Departman bazlı
│   └── Özel gruplar
└── Etkileşim Takibi
    ├── Görüntülenme sayısı
    ├── Okuma oranı
    ├── Etkileşim metrikleri
    ├── Geri bildirimler
    └── Anket entegrasyonu
```

### Haber Akışı

```
📰 HABER AKIŞI
├── Haber Kategorileri
│   ├── Platform haberleri
│   ├── Eğitim haberleri
│   ├── Başarı hikayeleri
│   ├── Etkinlik haberleri
│   └── Sektör haberleri
├── İçerik Yönetimi
│   ├── Editör arayüzü
│   ├── Multimedya desteği
│   ├── SEO optimizasyonu
│   ├── Etiketleme
│   └── Yayın akışı
├── Personalizasyon
│   ├── İlgi alanları
│   ├── Okuma geçmişi
│   ├── Öneri algoritması
│   ├── Takip sistemi
│   └── Bookmark
└── Sosyal Özellikler
    ├── Beğeni sistemi
    ├── Yorum yapma
    ├── Paylaşım
    ├── Reaksiyon
    └── Trending topics
```

---

## 🏢 Bildirim Merkezi

### Merkezi Kontrol Paneli

```
🎛️ KONTROL PANELİ
├── Dashboard
│   ├── Bildirim özeti
│   ├── Aktif kampanyalar
│   ├── Performans metrikleri
│   ├── Sistem sağlığı
│   └── Quick actions
├── Kampanya Yönetimi
│   ├── Kampanya oluşturma
│   ├── Hedef kitle seçimi
│   ├── A/B test kurulumu
│   ├── Zamanlama
│   └── Bütçe kontrolü
├── Şablon Kütüphanesi
│   ├── Hazır şablonlar
│   ├── Özel şablonlar
│   ├── Değişken yönetimi
│   ├── Önizleme
│   └── Test gönderimi
└── Analitik ve Raporlama
    ├── Gerçek zamanlı metrikler
    ├── Engagement analizi
    ├── Conversion tracking
    ├── ROI hesaplama
    └── Custom raporlar
```

### Otomasyon ve Workflow

```
🤖 OTOMASYON
├── Tetikleyiciler
│   ├── Zaman bazlı
│   ├── Event bazlı
│   ├── Davranış bazlı
│   ├── API tetikleyiciler
│   └── Manual tetikleme
├── Koşullar
│   ├── IF-THEN kuralları
│   ├── AND/OR logic
│   ├── Segment kontrolü
│   ├── Zaman koşulları
│   └── Custom conditions
├── Aksiyonlar
│   ├── Bildirim gönder
│   ├── E-posta gönder
│   ├── SMS gönder
│   ├── Task oluştur
│   └── API call
└── Workflow Örnekleri
    ├── Hoş geldin serisi
    ├── Terk önleme
    ├── Re-engagement
    ├── Milestone kutlama
    └── Feedback toplama
```

---

## 🔒 İletişim Güvenliği

### Mesaj Güvenliği

```
🔐 MESAJ GÜVENLİĞİ
├── Şifreleme
│   ├── TLS/SSL transport
│   ├── End-to-end encryption
│   ├── At-rest encryption
│   ├── Key management
│   └── Forward secrecy
├── Kimlik Doğrulama
│   ├── Two-factor auth
│   ├── Biometric auth
│   ├── Device verification
│   ├── Session management
│   └── OAuth integration
├── İçerik Kontrolü
│   ├── Spam filtreleme
│   ├── Malware tarama
│   ├── Phishing koruması
│   ├── İçerik moderasyonu
│   └── Profanity filter
└── Gizlilik Kontrolleri
    ├── Mesaj saklama süresi
    ├── Silme hakları
    ├── Görünürlük ayarları
    ├── Block/Report
    └── Data portability
```

### Uyumluluk ve Denetim

```
📋 UYUMLULUK
├── Yasal Uyumluluk
│   ├── KVKK/GDPR
│   ├── CAN-SPAM
│   ├── CCPA
│   ├── ePrivacy
│   └── Local regulations
├── Denetim Kayıtları
│   ├── Mesaj logları
│   ├── Erişim kayıtları
│   ├── Değişiklik geçmişi
│   ├── Consent tracking
│   └── Deletion records
├── Veri Yönetimi
│   ├── Data retention
│   ├── Data minimization
│   ├── Purpose limitation
│   ├── Access controls
│   └── Breach protocol
└── Raporlama
    ├── Compliance reports
    ├── Audit trails
    ├── Risk assessments
    ├── Incident reports
    └── Training records
```

---

## 💡 En İyi Uygulamalar

### Etkili İletişim

1. **Hedef Kitle Odaklı**
   - Doğru mesaj, doğru kişiye
   - Personalizasyon kullanımı
   - Segment bazlı iletişim

2. **Zamanlama**
   - Optimal gönderim zamanları
   - Timezone dikkati
   - Frekans kontrolü

3. **İçerik Kalitesi**
   - Kısa ve net mesajlar
   - Clear call-to-action
   - Değer odaklı içerik

### Kullanıcı Deneyimi

- 🎯 Relevans sağlama
- ⚡ Hızlı yanıt süresi
- 🔔 Bildirim yorgunluğunu önleme
- 📱 Cross-platform tutarlılık
- ♿ Erişilebilirlik standartları

---

**💬 Bildirimler ve Mesajlaşma sistemi, BDC platformunda etkili iletişimin temelini oluşturur. Doğru kullanıldığında kullanıcı katılımını artırır ve platform başarısına katkıda bulunur.**

*Son güncelleme: 27 Haziran 2025 | Versiyon 1.0*