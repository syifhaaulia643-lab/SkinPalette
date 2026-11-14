# Product Requirements Document (PRD)

## Cosmetic AI: Skin Type, Skintone, Undertone & Personal Color Analyzer

| Item | Keterangan |
|---|---|
| Mata kuliah | Farmasi AI |
| Versi dokumen | 1.0 (draf) |
| Jenis produk | Aplikasi web (Streamlit) |
| Stack utama | Python, Streamlit, OpenCV, MediaPipe Face Mesh, NumPy, (opsional) TensorFlow/Keras |
| Status | Prototipe akademik (MVP) |

---

## 1. Ringkasan Produk

Cosmetic AI adalah aplikasi web yang menganalisis foto wajah untuk menentukan **jenis kulit** (Oily/Dry/Normal), **skintone**, **undertone**, dan **personal color** (Spring/Summer/Autumn/Winter) berbasis ruang warna **CIELAB**. Hasil analisis diterjemahkan menjadi **rekomendasi formulasi kosmetik** dari sudut pandang farmasi: pemilihan basis sediaan, bahan aktif, serta rasio pigmen kosmetik dekoratif (Iron Oxides dan Titanium Dioxide).

## 2. Latar Belakang dan Masalah

- Pemilihan produk skincare dan makeup sering dilakukan secara coba-coba sehingga boros dan berisiko iritasi atau ketidakcocokan warna.
- Penentuan undertone dan personal color umumnya subjektif dan bergantung pada konsultan.
- Dalam pengembangan sediaan kosmetik, penyesuaian warna foundation membutuhkan dasar kuantitatif (nilai L\*a\*b\*) agar rasio pigmen dapat dirancang secara sistematis.

## 3. Tujuan

### 3.1 Tujuan produk
1. Memberikan analisis warna kulit yang objektif dan terukur (L\*, a\*, b\*) dari foto.
2. Memberikan klasifikasi jenis kulit yang modular dan siap ditingkatkan dengan model CNN.
3. Menghubungkan hasil analisis dengan rekomendasi formulasi yang berbasis ilmu farmasi kosmetik.

### 3.2 Tujuan akademik
- Mendemonstrasikan integrasi computer vision dan AI pada bidang farmasi/kosmetik.
- Menyediakan basis kode yang bersih agar mahasiswa dapat mengganti placeholder dengan model terlatih.

### 3.3 Di luar tujuan (non-goals)
- Bukan alat diagnosis kondisi kulit atau penyakit kulit.
- Tidak menggantikan konsultasi dokter, apoteker, atau formulator profesional.
- Tidak menyimpan foto atau data pribadi pengguna.

## 4. Target Pengguna

| Persona | Kebutuhan |
|---|---|
| Mahasiswa farmasi | Memahami hubungan data warna kulit dengan formulasi kosmetik |
| Konsumen umum | Mengetahui jenis kulit, skintone, dan personal color untuk memilih produk |
| Formulator/peneliti kosmetik | Titik awal kuantitatif untuk pencocokan warna foundation |

## 5. Ruang Lingkup

**Termasuk (In scope):** input foto, deteksi wajah, ekstraksi ROI, white balance, analisis CIELAB, klasifikasi jenis kulit (placeholder CNN + heuristik), rekomendasi skincare dan pigmen, antarmuka Streamlit.

**Tidak termasuk (Out of scope, versi 1.0):** akun pengguna, basis data, analisis video real-time, deteksi kondisi (jerawat, flek, keriput), e-commerce, aplikasi mobile native.

## 6. User Stories

1. Sebagai pengguna, saya ingin **mengunggah foto atau memotret langsung** agar mudah memberi input.
2. Sebagai pengguna, saya ingin **melihat panduan foto** agar hasil analisis akurat.
3. Sebagai pengguna, saya ingin **melihat area wajah yang dianalisis** agar saya yakin hasilnya valid.
4. Sebagai pengguna, saya ingin **melihat jenis kulit, skintone, undertone, dan personal color** dalam kartu yang jelas.
5. Sebagai mahasiswa, saya ingin **memuat model CNN (.h5) sendiri** tanpa mengubah banyak kode.
6. Sebagai formulator, saya ingin **rekomendasi rasio pigmen** sebagai titik awal pencocokan warna.

## 7. Kebutuhan Fungsional (Functional Requirements)

### FR-1 Input Pengguna
| ID | Kebutuhan | Prioritas |
|---|---|---|
| FR-1.1 | Pengguna dapat mengunggah foto JPG/PNG | Must |
| FR-1.2 | Pengguna dapat mengambil foto lewat `st.camera_input` | Must |
| FR-1.3 | UI menampilkan panduan: cahaya alami, tanpa makeup, wajah lurus, tanpa filter | Must |
| FR-1.4 | Gambar besar dikecilkan otomatis (sisi terpanjang 1024 px) dan orientasi EXIF dikoreksi | Should |

### FR-2 Pemrosesan Citra dan Deteksi Wajah
| ID | Kebutuhan | Prioritas |
|---|---|---|
| FR-2.1 | Deteksi wajah dengan MediaPipe Face Mesh (refine landmarks) | Must |
| FR-2.2 | Pesan kesalahan ramah bila wajah tidak terdeteksi; peringatan bila lebih dari satu wajah | Must |
| FR-2.3 | ROI: dahi, pipi kiri, pipi kanan; **mengecualikan** mata, alis, bibir, dan rambut | Must |
| FR-2.4 | Poligon ROI dikecilkan (faktor 0,8) dan area pengecualian di-dilate agar aman dari tepi | Should |
| FR-2.5 | Gray World White Balance sebelum analisis warna (dapat dimatikan pengguna) | Must |
| FR-2.6 | Tampilkan overlay ROI di atas foto untuk verifikasi visual | Should |

### FR-3 Analisis Warna Kulit (CIELAB)
| ID | Kebutuhan | Prioritas |
|---|---|---|
| FR-3.1 | Konversi piksel ROI ke CIELAB (L\*, a\*, b\*) | Must |
| FR-3.2 | Penyaringan piksel: filter rentang kulit YCrCb, pemangkasan persentil 5-95 pada L\*, nilai akhir berupa **median** | Must |
| FR-3.3 | Skintone dari L\* (lihat tabel 8.1) | Must |
| FR-3.4 | Undertone dari rasio b\*/a\* (lihat tabel 8.2) | Must |
| FR-3.5 | Personal Color dari Skintone + Undertone + kontras wajah-rambut (lihat 8.3) | Must |
| FR-3.6 | Kecerahan rambut diambil dari patch di atas dahi; fallback ke alis; pengguna dapat memilih manual atau mode hijab | Should |

### FR-4 Klasifikasi Jenis Kulit
| ID | Kebutuhan | Prioritas |
|---|---|---|
| FR-4.1 | Fungsi modular `predict_skin_type()` dengan kelas Oily, Dry, Normal | Must |
| FR-4.2 | Bila berkas `.h5` ada dan TensorFlow terpasang, gunakan model CNN (`predict_skin_type_cnn`) | Must |
| FR-4.3 | Bila model belum tersedia atau gagal dimuat, gunakan heuristik tekstur (kilap sebum dan kekasaran) | Must |
| FR-4.4 | Ambang heuristik dapat dikalibrasi lewat slider di sidebar | Should |
| FR-4.5 | Urutan kelas model dikonfigurasi lewat `CNN_CLASS_NAMES` | Must |

### FR-5 Output dan Rekomendasi
| ID | Kebutuhan | Prioritas |
|---|---|---|
| FR-5.1 | Kartu metrik: Jenis Kulit, Skintone, Undertone, Personal Color | Must |
| FR-5.2 | Tampilkan nilai L\*a\*b\* dan swatch HEX warna kulit terukur | Must |
| FR-5.3 | Tampilkan kotak palet HEX utama, lipstik, dan blush sesuai Personal Color | Must |
| FR-5.4 | Rekomendasi skincare: basis sediaan, alasan farmasetik, bahan aktif, eksipien, bahan yang dihindari | Must |
| FR-5.5 | Rekomendasi pigmen foundation (TiO₂, Iron Oxide Yellow/Red/Black) sebagai % b/b dan porsi terhadap total pigmen | Must |
| FR-5.6 | Disclaimer edukatif dan catatan batasan hasil | Must |

### FR-6 Struktur Kode
| ID | Kebutuhan | Prioritas |
|---|---|---|
| FR-6.1 | Satu berkas `app.py` yang modular (fungsi terpisah per tahap) dengan komentar Bahasa Indonesia | Must |
| FR-6.2 | `requirements.txt` bersih dengan versi minimum/rentang yang kompatibel | Must |

## 8. Spesifikasi Algoritma

### 8.1 Skintone (berdasarkan L\*)
| L\* | Skintone |
|---|---|
| ≥ 68 | Fair |
| 60 - < 68 | Light |
| 52 - < 60 | Medium |
| 42 - < 52 | Tan |
| < 42 | Deep |

### 8.2 Undertone (berdasarkan rasio b\*/a\*)
| Rasio b\*/a\* | Undertone | Makna |
|---|---|---|
| ≤ 1,20 | Cool | Cenderung kemerahan/pink |
| 1,20 - 1,50 | Neutral | Seimbang |
| ≥ 1,50 | Warm | Cenderung kekuningan/keemasan |

Sudut hue (atan2(b\*, a\*)) ditampilkan sebagai informasi pendukung.

### 8.3 Personal Color
Kontras = L\* kulit − L\* rambut. Rendah < 30, Sedang 30-42, Tinggi ≥ 42. Kulit dianggap "terang" bila L\* ≥ 55.

| Undertone efektif | Kondisi | Hasil |
|---|---|---|
| Warm | Kulit terang | Spring |
| Warm | Kulit lebih dalam | Autumn |
| Cool | Kulit terang dan kontras tidak tinggi | Summer |
| Cool | Selain itu | Winter |

Undertone Neutral diarahkan ke sisi warm/cool terdekat berdasarkan titik tengah rasio (1,35), dan catatan "netral" ditampilkan.

### 8.4 Heuristik jenis kulit (sementara)
1. Wajah dipotong dan dinormalkan ke 256×256 px agar metrik tidak bergantung resolusi.
2. **Rasio kilap**: fraksi piksel ROI dengan L\* > median + 10 dan kroma < median kroma. Bobot: dahi 50%, tiap pipi 25%.
3. **Kekasaran**: varians Laplacian pada kanal L\* (setelah blur 3×3).
4. Aturan: kilap ≥ 0,06 → Oily; kilap ≤ 0,02 **dan** kekasaran ≥ 3,0 → Dry; selain itu → Normal.

> Semua ambang pada bagian 8 adalah **nilai awal heuristik** dan wajib dikalibrasi dengan data nyata (lihat bagian 12).

### 8.5 Rekomendasi farmasi

**Skincare**
| Jenis kulit | Basis sediaan | Bahan aktif utama |
|---|---|---|
| Oily | Gel / emulsi O/W ringan, oil-free | Niacinamide 2-5%, BHA 0,5-2%, zinc PCA, asam azelat |
| Dry | Emulsi W/O atau O/W kaya, oklusif | Ceramide + kolesterol + asam lemak (≈3:1:1), urea, glycerin, panthenol |
| Normal | Emulsi O/W seimbang | Glycerin, panthenol, niacinamide, antioksidan, SPF 30-50 |

**Pigmen foundation (titik awal, % b/b dalam formula)**
| Skintone | TiO₂ | Iron Oxide Yellow | Iron Oxide Red | Iron Oxide Black |
|---|---|---|---|---|
| Fair | 10,0 | 0,80 | 0,30 | 0,05 |
| Light | 8,0 | 1,10 | 0,45 | 0,10 |
| Medium | 6,0 | 1,50 | 0,70 | 0,20 |
| Tan | 4,0 | 1,90 | 1,00 | 0,40 |
| Deep | 2,0 | 2,20 | 1,40 | 0,90 |

Penyesuaian undertone: Warm → kuning ×1,25 dan merah ×0,85; Cool → kuning ×0,80 dan merah ×1,25; Neutral → tanpa perubahan.

Palet lipstik/blush ditentukan oleh Personal Color (palet HEX terdefinisi per musim di kode).

## 9. Kebutuhan Non-Fungsional

| Kategori | Kebutuhan |
|---|---|
| Kinerja | Waktu analisis ≤ 5 detik per foto pada laptop standar (tanpa GPU) |
| Privasi | Foto diproses di memori, tidak disimpan ke disk atau server pihak ketiga |
| Kompatibilitas | Python 3.10-3.12; browser modern (Chrome, Edge, Firefox, Safari) |
| Keandalan | Aplikasi tidak crash saat wajah tidak terdeteksi, model tidak ada, atau TensorFlow tidak terpasang |
| Keterbacaan kode | Fungsi modular, type hint, komentar Bahasa Indonesia |
| Aksesibilitas | Teks kontras cukup; hasil tidak hanya bergantung pada warna (selalu disertai label teks dan kode HEX) |

## 10. Arsitektur dan Alur Data

```
Foto (upload/kamera)
   │
   ▼
load_image → (resize, EXIF)
   │
   ▼
detect_face_landmarks (MediaPipe Face Mesh)
   │
   ├─► build_roi_masks (dahi, pipi kiri, pipi kanan − mata/alis/bibir)
   │
   ▼
gray_world_white_balance
   │
   ├─► extract_skin_lab → median L*a*b*
   │        ├─ classify_skintone
   │        ├─ classify_undertone
   │        ├─ sample_hair_lightness → classify_contrast
   │        └─ determine_personal_color
   │
   └─► predict_skin_type ── model .h5 tersedia? ── ya ─► CNN
                                                └─ tidak ─► heuristik tekstur
   │
   ▼
Rekomendasi: skincare + pigmen + palet HEX → UI (kartu metrik, swatch, tab rekomendasi)
```
