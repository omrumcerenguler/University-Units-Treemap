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


## 🌍 English Version

# 🌳 YÖKSİS Unit Hierarchy – Treemap Visualization

This project visualizes the hierarchy of units (faculties, institutes, departments, main science branches, etc.) using Çukurova University's YÖKSİS data with a **treemap visualization** method. The project allows users to easily explore faculties and their subunits.

## 🚀 Features
- Hierarchical structure visualization with treemap
- Navigation through Faculty → Department → Subunit levels
- Filtering by unit name using a search bar
- "Reset Zoom" button to return to the main view
- Filtering only active units
- Detailed name display on hovering over subunits

## 🛠 Technologies Used
- [Python 3.13](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [Pandas](https://pandas.pydata.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PyODBC](https://github.com/mkleehammer/pyodbc)
- [Watchdog](https://pypi.org/project/watchdog/) (optional, for better performance)

## 📂 File Structure
```
.
├── agaclandirma.py      # Main application file
├── requirements.txt     # List of required dependencies
├── .env                 # Database connection information (hidden by gitignore)
├── .gitignore           # Prevents unnecessary files from being committed
└── README.md            # Project documentation
```

## ⚙️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/CukurovaUniversity/YapayZekaStaj3.git
   cd YapayZekaStaj3
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # MacOS/Linux
   .venv\Scripts\activate      # Windows
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit application:
   ```bash
   streamlit run agaclandirma.py
   ```

## 🎯 Usage
- Use the **search box** and **active units filter** on the left panel to search.
- Click on a faculty to see its subunits.
- Long names are abbreviated in small boxes.
- Use the "Reset Zoom" button to return to the main screen.

## 📌 Notes
- Database connection information must be defined in the `.env` file.
- This information is not uploaded to GitHub for security reasons.

## 👩‍💻 Developer
Ömrüm Ceren Güler
