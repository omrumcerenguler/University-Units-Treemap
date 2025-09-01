


# 🌳 YÖKSİS Birim Hiyerarşisi – Treemap Görselleştirme

Bu proje, Çukurova Üniversitesi’nin YÖKSİS verilerini kullanarak birimlerin (fakülteler, enstitüler, bölümler, anabilim dalları vb.) hiyerarşisini **treemap görselleştirme** yöntemiyle göstermektedir. Proje, kullanıcıların fakülte ve alt birimleri kolayca keşfetmesini sağlar.

## 🚀 Özellikler
- Treemap ile hiyerarşik yapı görselleştirmesi
- Fakülte → Bölüm → Alt Birim seviyelerinde gezinebilme
- Arama çubuğu ile birim adına göre filtreleme
- **Zoom sıfırla** butonu ile ana görünüme dönüş
- Sadece aktif birimlerin filtrelenmesi
- Alt birimler üzerine gelindiğinde detaylı isim görüntüleme

## 🛠 Kullanılan Teknolojiler
- [Python 3.13](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [Pandas](https://pandas.pydata.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PyODBC](https://github.com/mkleehammer/pyodbc)
- [Watchdog](https://pypi.org/project/watchdog/) (opsiyonel, daha iyi performans için)

## 📂 Dosya Yapısı
```
.
├── agaclandirma.py      # Ana uygulama dosyası
├── requirements.txt     # Gerekli bağımlılıkların listesi
├── .env                 # Veritabanı bağlantı bilgileri (gitignore ile gizlenir)
├── .gitignore           # Gereksiz dosyaların commit edilmesini engeller
└── README.md            # Proje dokümantasyonu
```

## ⚙️ Kurulum
1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/CukurovaUniversity/YapayZekaStaj3.git
   cd YapayZekaStaj3
   ```

2. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # MacOS/Linux
   .venv\Scripts\activate      # Windows
   ```

3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Streamlit uygulamasını çalıştırın:
   ```bash
   streamlit run agaclandirma.py
   ```

## 🎯 Kullanım
- Sol panelden **arama kutusu** ve **aktif birimler filtresi** ile arama yapabilirsiniz.
- Fakülte üzerine tıklayarak alt birimleri görebilirsiniz.
- Küçük kutularda uzun isimler kısaltılmış gösterilir.
- "Zoomu Sıfırla" butonu ile ana ekrana dönersiniz.

## 📌 Notlar
- `.env` dosyasında **veritabanı bağlantı bilgileri** tanımlanmalıdır.
- Bu bilgiler güvenlik amacıyla GitHub’a yüklenmez.

## 👩‍💻 Geliştirici
Ömrüm Ceren Güler
