# 🤖 AI JobMatcher Indonesia (Scraper + Skill Gap Analysis)

Aplikasi pencari lowongan kerja cerdas yang membandingkan CV Anda dengan lowongan kerja dari portal **Jora** dan **Careerjet Indonesia** secara real-time. Aplikasi ini tidak hanya mencari, tapi juga menganalisis kecocokan skill menggunakan AI.

## ✨ Fitur Utama
* **Smart Scraper:** Mengambil data lowongan secara real-time dari beberapa sumber sekaligus tanpa batas (Unlimited).
* **AI Match Scoring:** Menghitung persentase kecocokan antara CV (PDF) dengan deskripsi pekerjaan menggunakan metode *TF-IDF* dan *Cosine Similarity*.
* **Skill Gap Analysis:** Mendeteksi skill yang diminta oleh pemberi kerja namun belum tertulis di CV Anda (Membantu Anda belajar lebih spesifik).
* **Filter Lokasi:** Mendukung pencarian di berbagai kota besar di Indonesia.
* **Modern UI:** Antarmuka bersih dengan desain kartu modern dan indikator skor yang intuitif.
* **Export PDF:** Download laporan hasil rekomendasi dalam format PDF untuk disimpan.

## 🚀 Teknologi yang Digunakan
* **Backend:** Python & Flask
* **AI/ML:** Scikit-learn (TF-IDF Vectorizer)
* **Scraping:** BeautifulSoup4 & Cloudscraper (Anti-Bot Bypass)
* **PDF Engine:** PyMuPDF (Ekstraksi CV) & ReportLab (Generate Laporan)
* **Frontend:** Bootstrap 5 & Bootstrap Icons

## 🛠️ Cara Instalasi

1. **Clone repositori ini:**
   ```bash
   git clone [https://github.com/dinastiarputra1-netizen/jobmatcher-Indonesia.git](https://github.com/dinastiarputra1-netizen/jobmatcher-Indonesia.git)
   cd jobmatcher-Indonesia
2. **Instal library yang dibutuhkan:**
   pip install -r requirements.txt
3. **Jalankan Aplikasi:**
   python app.py
4. Buka di browser: Akses **http://127.0.0.1:5000**
   
📝 **Catatan Penting**
Aplikasi ini melakukan scraping secara real-time. Jika hasil tidak muncul, pastikan koneksi internet stabil atau coba ganti lokasi pencarian ke wilayah yang lebih luas seperti "Indonesia".
