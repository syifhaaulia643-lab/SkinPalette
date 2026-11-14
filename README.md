# ✨ Aura Color Match: Skin Type, Skintone, Undertone & Personal Color Analyzer

[![GitHub Repository](https://img.shields.io/badge/GitHub-Aura--Color--Match-blue?logo=github)](https://github.com/syifhaaulia643-lab/Aura-Color-Match)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Computer Vision](https://img.shields.io/badge/OpenCV-MediaPipe%20Face%20Mesh-green)](https://mediapipe.dev/)

Aplikasi web prototipe akademik **Cosmetic AI** untuk mata kuliah **Farmasi AI**. Aplikasi ini menganalisis foto wajah untuk menentukan:
- **Jenis Kulit** (Oily / Dry / Normal) menggunakan integrasi modular CNN (`.h5`) dan fallback Heuristik Tekstur & Kilap Sebum.
- **Skintone** (Fair / Light / Medium / Tan / Deep) berbasis nilai $L^*$.
- **Undertone** (Cool / Neutral / Warm) berbasis rasio $b^* / a^*$ dan sudut Hue $\text{atan2}(b^*, a^*)$.
- **Personal Color** (Spring / Summer / Autumn / Winter) berbasis kombinasi skintone, undertone, dan kontras kecerahan wajah-rambut.
- **Rekomendasi Formulasi Farmasi**: Basis sediaan skincare, bahan aktif utama, eksipien, bahan yang dihindari, serta rasio kuantitatif pigmen foundation (TiO₂, Iron Oxide Yellow, Red, Black).

Repository GitHub: **[https://github.com/syifhaaulia643-lab/Aura-Color-Match](https://github.com/syifhaaulia643-lab/Aura-Color-Match)**

---

## 📁 Struktur Repositori

```text
Aura-Color-Match/
├── app.py                  # Aplikasi utama Streamlit modular
├── requirements.txt        # Dependensi pustaka Python
├── .gitignore              # Konfigurasi file yang diabaikan Git
├── PRD.md                  # Product Requirements Document (PRD) versi 1.0
├── README.md               # Dokumentasi instalasi dan penggunaan
└── models/
    ├── README.md           # Panduan integrasi model CNN Keras/TensorFlow
    └── skin_type_cnn.h5    # (Opsional) Tempat meletakkan model CNN terlatih
```

---

## 🚀 Panduan Menghubungkan dan Push ke GitHub

Jika Anda belum melakukan push berkas lokal ini ke repository GitHub Anda, ikuti langkah berikut:

```powershell
# 1. Pindah ke direktori proyek lokal
cd C:\Users\UNIQ\.gemini\antigravity\scratch\Aura-Color-Match

# 2. Inisialisasi Git
git init

# 3. Tambahkan remote repository GitHub Anda
git remote add origin https://github.com/syifhaaulia643-lab/Aura-Color-Match.git

# 4. Tambahkan seluruh berkas ke staging
git add .

# 5. Buat commit pertama
git commit -m "feat: inisialisasi MVP Aura Color Match (Cosmetic AI Streamlit app)"

# 6. Ganti branch utama menjadi main dan push ke GitHub
git branch -M main
git push -u origin main
```

---

## 💻 Panduan Instalasi & Menjalankan Aplikasi Lokal

### 1. Prasyarat Sistem
- **Python**: Versi 3.10, 3.11, atau 3.12.
- **Git** (opsional untuk version control).

### 2. Langkah Instalasi (Windows PowerShell / Command Prompt)

```powershell
# 1. Buat lingkungan virtual (virtual environment)
python -m venv .venv

# 2. Aktifkan virtual environment
# Pada Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# (Atau pada Command Prompt: .\.venv\Scripts\activate.bat)

# 3. Perbarui pip dan pasang dependensi
pip install --upgrade pip
pip install -r requirements.txt

# 4. Jalankan aplikasi Streamlit
streamlit run app.py
```

### 3. Pengguna macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Setelah perintah dijalankan, antarmuka web Aura Color Match akan terbuka secara otomatis di peramban Anda pada alamat `http://localhost:8501`.

---

## 🔬 Spesifikasi Algoritma

### 1. Ruang Warna CIELAB (D65)
- Citra dikonversi ke ruang warna CIELAB standar menggunakan konversi float32 OpenCV.
- Area ekstraksi dibatasi pada 3 ROI: **Dahi, Pipi Kiri, dan Pipi Kanan**, dengan pengecualian otomatis pada **Mata, Alis, dan Bibir**.
- Poligon ROI dikecilkan (faktor 0.8) dan area pengecualian di-dilate agar piksel tepi dan rambut tidak tercampur.
- Filter warna kulit YCrCb dan pemangkasan persentil 5–95% pada $L^*$ diterapkan sebelum menghitung nilai akhir **median $L^*, a^*, b^*$**.

### 2. Klasifikasi Skintone & Undertone
- **Skintone ($L^*$):**
  - $L^* \ge 68$: Fair
  - $60 \le L^* < 68$: Light
  - $52 \le L^* < 60$: Medium
  - $42 \le L^* < 52$: Tan
  - $L^* < 42$: Deep
- **Undertone (Rasio $b^* / a^*$):**
  - $\le 1.20$: Cool (kemerahan/pinkish)
  - $1.20 - 1.50$: Neutral (seimbang)
  - $\ge 1.50$: Warm (keemasan/golden)

### 3. Personal Color Analysis
- Kontras dihitung dari $L^*_{\text{kulit}} - L^*_{\text{rambut}}$.
  - Rendah: $< 30$ | Sedang: $30 - 42$ | Tinggi: $\ge 42$
- Mendukung **Mode Hijab** (pengukuran kontras dialihkan ke alis) dan **Input Manual Warna Rambut**.

### 4. Klasifikasi Jenis Kulit (Modular)
- **Model CNN:** Jika file `models/skin_type_cnn.h5` tersedia dan TensorFlow terpasang, aplikasi memprediksi probabilitas 3 kelas: `["Dry", "Normal", "Oily"]`.
- **Heuristik Tekstur (Fallback Otomatis):**
  - **Rasio Kilap Sebum:** Fraksi piksel dengan $L^* > \text{median}(L^*) + 10$ dan $\text{kroma} < \text{median}(\text{kroma})$. Bobot: Dahi 50%, Pipi Kiri 25%, Pipi Kanan 25%.
  - **Kekasaran Permukaan:** Varians operator Laplacian pada kanal $L^*$ ter-blur.
  - Ambang dapat dikalibrasi langsung melalui slider di sidebar.

---

## 🧪 Rekomendasi Formulasi Farmasi

Aplikasi secara otomatis menghasilkan formula kosmetik berbasis kuantitatif:
1. **Skincare**: Basis sediaan (gel/emulsi O/W/W/O), rasio bahan aktif terapeutik (Niacinamide, BHA, Ceramide 3:1:1, Urea, Panthenol), eksipien fungsional, dan bahan yang dihindari.
2. **Pigmen Foundation**: Titik awal formula (% b/b) dan porsi relatif terhadap total pigmen untuk:
   - Titanium Dioxide ($\text{TiO}_2$, CI 77891)
   - Iron Oxide Yellow (CI 77492)
   - Iron Oxide Red (CI 77491)
   - Iron Oxide Black (CI 77499)
   dengan penyesuaian faktor pengali undertone (Warm $\times 1.25$ kuning / $\times 0.85$ merah; Cool $\times 0.80$ kuning / $\times 1.25$ merah).

---

## 🔒 Privasi dan Etika
- Seluruh pemrosesan foto dilakukan secara lokal di memori (*in-memory processing*) dan tidak pernah disimpan ke disk atau dikirim ke pihak ketiga.
- Aplikasi dirancang untuk tujuan edukasi akademik farmasi, bukan untuk diagnosis medis klinis.
