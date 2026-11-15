# Aura Color Match ✨ - Next-Gen Cosmetic AI & Personal Color Analyzer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](http://localhost:8501)
[![Python 3.10 | 3.11 | 3.12](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh%20468-00C4B4?logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Color Space](https://img.shields.io/badge/Color%20Space-CIELAB%20(D65)-FFA500)](#-spesifikasi-algoritma-kolorimetri)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Academic Project](https://img.shields.io/badge/Mata%20Kuliah-Farmasi%20AI-4CAF50)](#)

> **Aura Color Match** adalah aplikasi web kecerdasan buatan terpadu untuk menganalisis karakteristik warna kulit manusia secara kuantitatif berbasis ruang warna **CIELAB ($L^*a^*b^*$)**, mengklasifikasikan jenis kulit (Oily/Dry/Normal), menentukan **Personal Color (4 Musim)**, serta menghasilkan **rekomendasi formulasi kosmetik farmasetik** (basis sediaan, bahan aktif terapeutik, dan rasio pigmen foundation).

---

## 🌟 Fitur Utama (Key Features)

### 1. 👤 Deteksi Wajah Presisi & Ekstraksi ROI Cerdas
- Memanfaatkan **MediaPipe Face Mesh** dengan `refine_landmarks=True` (468/478 titik landmark 3D).
- Isolasi Region of Interest (ROI) pada 3 area kunci: **Dahi (Forehead)**, **Pipi Kiri**, dan **Pipi Kanan** dengan penskalaan poligon $0.8$ terhadap centroid.
- Pengecualian otomatis area non-kulit: Mata, Alis, Bibir, dan batas garis rambut menggunakan dilatasi morfologi kernel $7 \times 7$.
- Koreksi orientasi EXIF otomatis untuk foto kamera ponsel dan auto-resize cerdas (maks 1024 px).

### 2. 🎨 Analisis Kuantitatif Ruang Warna CIELAB ($L^*, a^*, b^*$)
- Konversi RGB ke CIELAB standar D65 matematis ($L^* \in [0, 100], a^* \in [-128, 127], b^* \in [-128, 127]$).
- Penyaringan piksel kulit menggunakan filter YCrCb dan pemangkasan persentil $5\% - 95\%$ pada $L^*$ untuk mengeliminasi bayangan ekstrem dan pantulan kilap berlebih.
- **Skintone:** Klasifikasi 5 tingkat (Fair, Light, Medium, Tan, Deep) berbasis nilai kecerahan $L^*$.
- **Undertone:** Penentuan objektif berdasarkan rasio kromatik $b^* / a^*$ dan sudut Hue $\text{atan2}(b^*, a^*)$ (Cool, Neutral, Warm).

### 3. 💇 Analisis Personal Color & Mode Hijab
- Pengukuran kontras relatif wajah-rambut ($\Delta L^* = L^*_{\text{kulit}} - L^*_{\text{rambut}}$).
- Pengelompokan 4 musim: **Spring** (Warm & Bright), **Summer** (Cool & Soft), **Autumn** (Warm & Deep), dan **Winter** (Cool & Vivid).
- Dilengkapi **Mode Hijab** (pengukuran kontras dialihkan ke alis) dan opsi **Input Manual Warna Rambut**.
- Rekomendasi palet warna swatch interaktif dalam kode HEX untuk busana, lipstik, dan blush on terbaik.

### 4. 🧪 Klasifikasi Jenis Kulit Modular (CNN & Heuristik)
- **Arsitektur Modular:** Siap memuat model deep learning TensorFlow/Keras (`models/skin_type_cnn.h5`).
- **Heuristik Tekstur Cerdas (Fallback Otomatis):**
  - **Rasio Kilap Sebum Specular:** Mengukur fraksi piksel berkilau ($L^* > \text{median} + 10$ dan $\text{kroma} < \text{median}$) dengan pembobotan dahi 50% dan pipi 25%.
  - **Kekasaran Mikro-Tekstur:** Varians operator Laplacian pada kanal $L^*$ ter-blur untuk mendeteksi dehidrasi stratum korneum.
  - Slider kalibrasi ambang batas sensitivitas di sidebar untuk adaptasi terhadap kamera pengguna.

### 5. 🧴 Rekomendasi Formulasi Skincare Farmasetik
- **Basis Sediaan:** Gel hidrofilik / emulsi ringan O/W bebas minyak (Oily), Emulsi W/O kaya oklusif (Dry), dan Emulsi O/W seimbang (Normal).
- **Rasional Farmasetik:** Menjelaskan pencegahan Transepidermal Water Loss (TEWL), fungsi sawar lipid lamellar, dan regulasi kelenjar sebasea.
- **Bahan Aktif Terapeutik:** Konsentrasi standar farmasi seperti Niacinamide 2-5%, Asam Salisilat (BHA) 0.5-2%, Zinc PCA 1%, Kompleks Ceramide $\approx 3:1:1$, Urea 2-5%, Glycerin, dan Panthenol.
- **Eksipien & Larangan:** Rekomendasi pembawa ramah kulit serta daftar bahan komedogenik atau iritan yang wajib dihindari.

### 6. 💄 Kalkulator Formulasi Rasio Pigmen Foundation
- Penentuan titik awal formula (% b/b) untuk:
  - **Titanium Dioxide ($\text{TiO}_2$, CI 77891)** — Opasitas & pencerah dasar
  - **Iron Oxide Yellow (CI 77492)** — Kromofor kuning kehangatan
  - **Iron Oxide Red (CI 77491)** — Kromofor rona alami vaskular
  - **Iron Oxide Black (CI 77499)** — Kromofor peredam kedalaman shade
- Penyesuaian faktor pengali undertone: Warm ($\times 1.25$ kuning / $\times 0.85$ merah) dan Cool ($\times 0.80$ kuning / $\times 1.25$ merah).
- Perhitungan total kadar pigmen (% b/b) dan porsi relatif terhadap 100% total pigmen.

---

## 📊 Spesifikasi Algoritma Kolorimetri

### 1. Klasifikasi Skintone ($L^*$)
| Nilai $L^*$ | Kategori Skintone | Karakteristik Klinis |
|---|---|---|
| $\ge 68$ | **Fair** | Kulit porselen sangat terang dengan reflektansi tinggi |
| $60 - < 68$ | **Light** | Kulit terang umum dengan kecerahan sedang-tinggi |
| $52 - < 60$ | **Medium** | Kulit kuning langsat / sawo matang muda (khas Asia) |
| $42 - < 52$ | **Tan** | Kulit sawo matang / kecokelatan eksotis |
| $< 42$ | **Deep** | Kulit gelap eksotis kaya melanin |

### 2. Klasifikasi Undertone (Rasio $b^* / a^*$)
| Rasio $b^* / a^*$ | Undertone | Sudut Hue ($\theta$) | Karakteristik Vaskular |
|---|---|---|---|
| $\le 1.20$ | **Cool** | $\approx 40^\circ - 49^\circ$ | Rona kemerahan (pinkish), vena tampak kebiruan/ungu |
| $1.20 - 1.50$ | **Neutral** | $\approx 50^\circ - 56^\circ$ | Seimbang antara spektrum kuning dan merah |
| $\ge 1.50$ | **Warm** | $\ge 57^\circ$ | Rona hangat keemasan (golden), vena tampak kehijauan |

---

## 🏗️ Arsitektur Sistem & Alur Data

```
Foto Wajah (Unggah / Kamera)
        │
        ▼
Pra-pemrosesan: Koreksi EXIF & Auto-Resize 1024 px
        │
        ▼
Deteksi Landmark: MediaPipe Face Mesh (468/478 Titik)
        │
        ├─► Ekstraksi ROI Kulit (Dahi & Kedua Pipi, Skala 0.8)
        │   └─ Masking Pengecualian: Mata, Alis, Bibir (Dilatasi 7x7)
        │
        ▼
Normalisasi Cahaya: Gray World White Balance (0.6 - 1.6)
        │
        ├─► Ekstraksi Nilai Warna: CIELAB (L*, a*, b* Median)
        │        ├─ Klasifikasi Skintone (L*)
        │        ├─ Klasifikasi Undertone (b*/a* & Hue)
        │        ├─ Pengukuran Kontras Rambut-Kulit (Mode Hijab/Manual)
        │        └─ Penentuan Personal Color (Spring/Summer/Autumn/Winter)
        │
        └─► Klasifikasi Jenis Kulit (predict_skin_type)
                 ├─ Model CNN Deep Learning (.h5) [Bila Ada]
                 └─ Fallback: Heuristik Kilap Sebum & Kekasaran Laplacian
        │
        ▼
Sistem Formulasi Farmasi & Kosmetik
  ├─ Skincare Terapeutik (Basis Sediaan, Bahan Aktif, Eksipien)
  ├─ Pigmen Foundation (% b/b TiO2, FeO Yellow, Red, Black)
  └─ Palet Warna HEX Interaktif (Busana, Lipstik, Blush On)
        │
        ▼
Antarmuka Interaktif Streamlit & Verifikasi Visual ROI
```

---

## 📁 Struktur Repositori

```text
Aura-Color-Match/
├── app.py                  # Aplikasi utama Streamlit modular
├── requirements.txt        # Dependensi pustaka Python
├── PRD.md                  # Product Requirements Document (PRD v1.0)
├── BREAKDOWN_TUGAS.md      # Work Breakdown Structure (WBS)
├── README.md               # Dokumentasi utama proyek
├── CONTRIBUTING.md         # Panduan kontribusi
├── LICENSE                 # Lisensi MIT
├── .gitignore              # Pengabaian file cache & virtual environment
├── .gitattributes         # Konfigurasi normalisasi line-ending Git
├── push-to-github.bat      # Skrip pembantu push Git untuk Windows
└── models/
    └── README.md           # Panduan penempatan model CNN Keras/TensorFlow
```

---

## 🚀 Panduan Instalasi & Menjalankan

### Prasyarat
- Python 3.10, 3.11, atau 3.12 terpasang pada komputer Anda.
- Web browser modern (Google Chrome, Microsoft Edge, Mozilla Firefox, atau Opera).

### Langkah Menjalankan:
```bash
# 1. Clone repositori ini
git clone https://github.com/syifhaaulia643-lab/Aura-Color-Match.git
cd Aura-Color-Match

# 2. Buat dan aktifkan lingkungan virtual
python -m venv .venv
# Pada Windows:
.\.venv\Scripts\activate
# Pada macOS/Linux:
source .venv/bin/activate

# 3. Pasang seluruh dependensi pustaka
pip install --upgrade pip
pip install -r requirements.txt

# 4. Jalankan aplikasi Streamlit
streamlit run app.py
```
Aplikasi akan secara otomatis terbuka di browser pada alamat **`http://localhost:8501`**.

---

## 🔒 Privasi, Etika & Disclaimer Farmasi
1. **Privasi Pengguna:** Seluruh pemrosesan citra dilakukan secara lokal pada memori komputasi saat runtime (*in-memory*) dan tidak pernah disimpan ke penyimpanan permanen atau server pihak ketiga.
2. **Tujuan Edukatif:** Aplikasi ini dirancang sebagai prototipe akademik pada mata kuliah **Farmasi AI** dan bukan merupakan alat diagnosis klinis medis dermatologi.
3. **Validasi Formulasi:** Rekomendasi persentase pigmen dan bahan aktif adalah *starting point* kuantitatif teoritis. Formulasi sediaan kosmetik riil wajib melalui pengujian laboratorium farmasetik (*stability test*, *challenge test*, dan evaluasi kompatibilitas kulit).

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi **MIT License** - lihat berkas [LICENSE](LICENSE) untuk rincian lengkap.
