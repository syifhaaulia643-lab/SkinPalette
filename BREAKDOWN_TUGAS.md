# 📋 Dokumen Breakdown Tugas (Work Breakdown Structure)
## Proyek: Aura Color Match (Cosmetic AI)
### Analisis Jenis Kulit, Skintone, Undertone, Personal Color & Formulasi Kosmetik Farmasetik

| Metadata | Keterangan |
|---|---|
| **Mata Kuliah** | Farmasi AI |
| **Repositori GitHub** | [syifhaaulia643-lab/Aura-Color-Match](https://github.com/syifhaaulia643-lab/Aura-Color-Match) |
| **Target Deliverable** | Aplikasi Web Prototipe Akademik (MVP Streamlit) |
| **Dokumen Acuan** | [PRD.md](PRD.md) Versi 1.0 |
| **Status Dokumen** | Rencana Kerja Eksekusi & Pembagian Tugas (Task Breakdown) |

---

## 🎯 Gambaran Umum Alur Eksekusi Proyek

```
[FASE 1: Perencanaan & Arsitektur]
       │
       ▼
[FASE 2: Input Citra & Deteksi ROI Face Mesh] ──► [White Balance Gray World]
       │
       ├───────────────────────────────────────┐
       ▼                                       ▼
[FASE 3: Analisis Kolorimetri CIELAB]   [FASE 4: Klasifikasi Jenis Kulit]
  ├─ Skintone (L*)                        ├─ Model CNN (.h5)
  ├─ Undertone (b*/a* & Hue)              └─ Heuristik Kilap Sebum & Kekasaran
  └─ Personal Color & Kontras Rambut
       │                                       │
       └───────────────────┬───────────────────┘
                           │
                           ▼
          [FASE 5: Sistem Formulasi Farmasi]
            ├─ Skincare Terapeutik (Basis, Aktif, Eksipien)
            └─ Pigmen Foundation (% b/b TiO2 & Iron Oxides)
                           │
                           ▼
          [FASE 6: UI/UX Streamlit & Validasi]
```

---

## 📑 Rincian Rencana Kerja (Work Breakdown Structure)

### FASE 1: PERENCANAAN, ARSITEKTUR & SETUP REPOSITORI
**Tujuan:** Menyusun fondasi ilmiah farmasetik, desain sistem modular, dan struktur version control yang bersih.

- [x] **WBS 1.1: Kajian Kebutuhan Farmasi AI & Kolorimetri**
  - **Deskripsi:** Menetapkan hubungan kuantitatif ruang warna CIELAB dengan kadar pigmen sediaan dekoratif serta profil biologis sawar kulit.
  - **Deliverable:** Matriks aturan skintone, undertone, personal color, dan tabel formula pigmen.
  - **Status:** Selesai (tertuang di `PRD.md`).
- [x] **WBS 1.2: Desain Arsitektur Data Flow & Modularitas**
  - **Deskripsi:** Merancang struktur alur data dari gambar masuk hingga rekomendasi formula farmasi tanpa dependensi sirkular.
  - **Deliverable:** Diagram alur dan spesifikasi modul fungsi per tahap.
  - **Status:** Selesai.
- [x] **WBS 1.3: Konfigurasi Repositori Git & Lingkungan Proyek**
  - **Deskripsi:** Menyiapkan struktur repositori lokal, `.gitignore`, direktori `models/`, dan dependensi `requirements.txt`.
  - **Deliverable:** Berkas `.gitignore`, `requirements.txt`, `models/README.md`, dan sinkronisasi ke remote GitHub `syifhaaulia643-lab/Aura-Color-Match`.
  - **Status:** Selesai.

---

### FASE 2: INPUT CITRA, PRA-PEMROSESAN & EKSTRAKSI ROI (FACE MESH)
**Tujuan:** Mengakuisisi foto dengan andal, mengoreksi orientasi/dimensi, serta mengisolasi area kulit dahi dan pipi bebas dari gangguan rambut, alis, mata, dan bibir.

- [x] **WBS 2.1: Modul Masukan Citra & Koreksi EXIF (FR-1)**
  - **2.1.1** Implementasi antarmuka pemilihan input: File Upload (JPG/PNG) dan `st.camera_input`.
  - **2.1.2** Penanganan orientasi gambar via `ImageOps.exif_transpose` untuk foto ponsel agar tidak terbalik.
  - **2.1.3** Penskalaan cerdas citra beresolusi tinggi (maksimum sisi 1024 px) dengan mempertahankan aspect ratio.
  - **2.1.4** Tampilan panduan foto (cahaya alami, wajah bersih, ekspresi frontal, tanpa filter).
- [x] **WBS 2.2: Deteksi Landmark Wajah MediaPipe (FR-2.1, FR-2.2)**
  - **2.2.1** Integrasi `mediapipe.solutions.face_mesh` dengan `refine_landmarks=True`.
  - **2.2.2** Penanganan kondisi batas: pesan ramah jika wajah tidak terdeteksi (0 wajah).
  - **2.2.3** Penanganan multi-wajah: otomatis memilih wajah utama yang paling dominan/besar di tengah.
- [x] **WBS 2.3: Ekstraksi Poligon ROI & Area Pengecualian (FR-2.3, FR-2.4)**
  - **2.3.1** Pemetaan indeks landmark untuk 3 ROI kulit: Dahi (Forehead), Pipi Kiri, dan Pipi Kanan.
  - **2.3.2** Pengecilan poligon ROI (shrink factor 0.8 terhadap centroid) untuk mencegah sampling piksel tepi.
  - **2.3.3** Pemetaan area pengecualian: Mata kiri/kanan, Alis kiri/kanan, dan Bibir.
  - **2.3.4** Dilatasi mask pengecualian (kernel elips 7×7) dan pengurangan dari mask ROI (`bitwise_and`).
- [x] **WBS 2.4: Normalisasi Cahaya Gray World White Balance (FR-2.5)**
  - **2.4.1** Implementasi algoritma Gray World untuk menetralkan colour cast lampu ruangan.
  - **2.4.2** Pembatasan gain faktor koreksi pada rentang aman $[0.6, 1.6]$ agar tidak mendistorsi foto dengan warna dominan.
  - **2.4.3** Penambahan kontrol toggle di sidebar agar pengguna dapat mengaktifkan/menonaktifkan White Balance.
- [x] **WBS 2.5: Pembuatan Overlay Visual Verifikasi ROI (FR-2.6)**
  - **2.5.1** Rendering layer warna semi-transparan (Dahi = Cyan, Pipi Kiri = Hijau Zamrud, Pipi Kanan = Oranye Coral).
  - **2.5.2** Penggambaran garis kontur batas ROI untuk mempermudah verifikasi visual oleh pengguna/penguji.

---

### FASE 3: PIPELINE ANALISIS WARNA KULIT KUANTITATIF (CIELAB SPACE)
**Tujuan:** Mengukur warna kulit secara objektif dalam ruang warna CIELAB serta mengklasifikasikan skintone, undertone, dan personal color.

- [x] **WBS 3.1: Konversi Ruang Warna CIELAB & sRGB (FR-3.1)**
  - **3.1.1** Konversi RGB ke CIELAB standar menggunakan format float32 ($L^* \in [0, 100], a^* \in [-128, 127], b^* \in [-128, 127]$).
  - **3.1.2** Pembuatan fungsi `lab_to_hex()` untuk visualisasi swatch representasi sRGB dari nilai CIELAB.
- [x] **WBS 3.2: Filter Piksel Kulit & Agregasi Median (FR-3.2)**
  - **3.2.1** Penerapan filter ruang warna YCrCb untuk membuang piksel non-kulit/bayangan gelap.
  - **3.2.2** Pemangkasan persentil 5–95% pada kanal $L^*$ untuk menyaring pantulan kilap ekstrem dan celah bayangan.
  - **3.2.3** Ekstraksi nilai akhir berupa **median $L^*, a^*, b^*$** dari piksel ROI yang lolos filter.
- [x] **WBS 3.3: Klasifikasi Skintone (FR-3.3, Tabel 8.1)**
  - **3.3.1** Pemetaan $L^* \ge 68 \to$ Fair; $60-68 \to$ Light; $52-60 \to$ Medium; $42-52 \to$ Tan; $<42 \to$ Deep.
  - **3.3.2** Penyertaan narasi karakteristik klinis/organoleptik warna kulit.
- [x] **WBS 3.4: Klasifikasi Undertone & Kolorimetri (FR-3.4, Tabel 8.2)**
  - **3.4.1** Perhitungan rasio $b^* / a^*$: $\le 1.20 \to$ Cool; $1.20 - 1.50 \to$ Neutral; $\ge 1.50 \to$ Warm.
  - **3.4.2** Perhitungan sudut Hue $\text{atan2}(b^*, a^*)$ dalam derajat sebagai parameter penunjang.
- [x] **WBS 3.5: Analisis Personal Color & Kecerahan Rambut (FR-3.5, FR-3.6, Tabel 8.3)**
  - **3.5.1** Pengambilan patch kecerahan rambut ($L^*_{\text{rambut}}$) di atas dahi dengan fallback ke alis.
  - **3.5.2** Dukungan **Mode Hijab** dan **Input Manual Warna Rambut** via sidebar.
  - **3.5.3** Perhitungan kontras $\Delta L^* = L^*_{\text{kulit}} - L^*_{\text{rambut}}$ (Rendah $< 30$, Sedang $30-42$, Tinggi $\ge 42$).
  - **3.5.4** Evaluasi pohon keputusan 4 musim (Spring, Summer, Autumn, Winter) beserta pemetaan condong bagi undertone Netral.

---

### FASE 4: KLASIFIKASI JENIS KULIT (MODULAR CNN & HEURISTIK TEKSTUR)
**Tujuan:** Mengidentifikasi jenis kulit (Oily, Dry, Normal) secara modular, siap diintegrasikan dengan model deep learning terlatih atau menggunakan heuristik tekstur berbasis bukti.

- [x] **WBS 4.1: Desain Fungsi Modular `predict_skin_type` (FR-4.1)**
  - **4.1.1** Merancang fungsi antarmuka terpadu yang dapat menerima data wajah dan mengembalikan label kelas serta detail metrik.
- [x] **WBS 4.2: Jalur Inferensi Model CNN Keras (.h5) (FR-4.2, FR-4.5)**
  - **4.2.1** Integrasi loader TensorFlow/Keras yang aman (*graceful degradation* jika belum terpasang atau berkas tidak ada).
  - **4.2.2** Preprocessing pemotongan wajah (*face crop*) ke dimensi 224×224 px dan normalisasi piksel.
  - **4.2.3** Konfigurasi urutan kelas dinamis via `CNN_CLASS_NAMES = ["Dry", "Normal", "Oily"]`.
- [x] **WBS 4.3: Algoritma Heuristik Kilap Sebum & Kekasaran (FR-4.3, Spesifikasi 8.4)**
  - **4.3.1** Normalisasi citra wajah ke ukuran acuan 256×256 px.
  - **4.3.2** Perhitungan rasio kilap sebum specular ($L^* > \text{median} + 10$ dan $\text{kroma} < \text{median}$) dengan pembobotan dahi 50%, pipi kiri 25%, pipi kanan 25%.
  - **4.3.3** Perhitungan kekasaran mikro-tekstur stratum korneum menggunakan varians operator Laplacian pada kanal $L^*$ ter-blur.
  - **4.3.4** Penerapan aturan keputusan: kilap $\ge 0.06 \to$ Oily; kilap $\le 0.02$ dan kekasaran $\ge 3.0 \to$ Dry; selain itu $\to$ Normal.
- [x] **WBS 4.4: Kalibrasi Parameter Heuristik di Sidebar (FR-4.4)**
  - **4.4.1** Pembuatan slider kalibrasi ambang batas kilap dan kekasaran di sidebar untuk memfasilitasi pengujian di kondisi kamera yang berbeda.

---

### FASE 5: REKOMENDASI FORMULASI KOSMETIK & FARMASI
**Tujuan:** Menerjemahkan data analitis citra menjadi rekomendasi formulasi farmasetik yang aplikatif dan berbasis ilmu formulasi sediaan kosmetik.

- [x] **WBS 5.1: Rekomendasi Formulasi Skincare Terapeutik (FR-5.4, Spesifikasi 8.5)**
  - **5.1.1** Penentuan basis sediaan: Gel hidrofilik / emulsi O/W ringan oil-free (Oily), Emulsi W/O kaya lipid oklusif (Dry), Emulsi O/W seimbang (Normal).
  - **5.1.2** Penyusunan rasional farmasetik terkait TEWL, fungsi sawar stratum korneum, dan aktivitas kelenjar sebasea.
  - **5.1.3** Rekomendasi bahan aktif farmasi dengan konsentrasi standar (Niacinamide 2-5%, BHA 0.5-2%, Zinc PCA 1%, Kompleks Ceramide rasio 3:1:1, Urea 2-5%, Panthenol).
  - **5.1.4** Pemilihan eksipien pembawa (gelling agent, emolien, pengemulsi lamellar) dan identifikasi bahan yang wajib dihindari.
- [x] **WBS 5.2: Rekomendasi Kuantitatif Pigmen Foundation (FR-5.5, Spesifikasi 8.5)**
  - **5.2.1** Penentuan komposisi dasar % b/b untuk 5 tingkatan skintone (TiO₂, Iron Oxide Yellow, Red, Black).
  - **5.2.2** Penyesuaian faktor pengali undertone: Warm (kuning $\times 1.25$, merah $\times 0.85$); Cool (kuning $\times 0.80$, merah $\times 1.25$); Neutral ($\times 1.00$).
  - **5.2.3** Perhitungan total kadar pigmen (% b/b dalam total sediaan emulsi) dan porsi relatif masing-masing pigmen terhadap 100% total pigmen.
- [x] **WBS 5.3: Kurasi Palet Personal Color (FR-5.3)**
  - **5.3.1** Kurasi palet warna busana utama (6 swatch HEX).
  - **5.3.2** Kurasi warna lipstik terbaik (3 swatch HEX) dan blush on (3 swatch HEX) per musim personal color.

---

### FASE 6: IMPLEMENTASI ANTARMUKA (UI/UX), PENGUJIAN & DOKUMENTASI
**Tujuan:** Menyajikan hasil dalam antarmuka interaktif yang informatif, estetis, responsif, dan menyertakan pengujian komprehensif.

- [x] **WBS 6.1: Antarmuka Interaktif Streamlit (Seksi 11)**
  - **6.1.1** Desain CSS modern (kartu metrik elevasi, palet swatch box, info callout).
  - **6.1.2** Panel perbandingan berdampingan: foto input asli vs overlay visual ROI.
  - **6.1.3** Tampilan 4 kartu metrik utama responsif.
  - **6.1.4** Tab terpisah untuk eksplorasi palet warna dan tab formulasi farmasi (skincare vs pigmen dekoratif).
- [x] **WBS 6.2: Keamanan, Privasi & Disclaimer Akademik (FR-5.6, Seksi 13, 14)**
  - **6.2.1** Pemrosesan gambar strictly in-memory (tanpa penyimpanan ke disk/server).
  - **6.2.2** Penyertaan disclaimer akademik farmasi bahwa hasil bersifat edukatif dan bukan diagnosis klinis.
- [x] **WBS 6.3: Rencana Pengujian & Validasi Kinerja (Seksi 12)**
  - **6.3.1** Validasi ketahanan deteksi wajah pada berbagai kondisi pencahayaan.
  - **6.3.2** Evaluasi pengaruh Gray World White Balance sebelum dan sesudah koreksi warna.
  - **6.3.3** Uji beban komputasi (target waktu eksekusi $\le 5$ detik per foto pada CPU standar).

---

## 📊 Matriks Penanggung Jawab & Status Modul

| No | Modul Pekerjaan | Komponen File | Status Saat Ini | Rencana Pengembangan Lanjutan |
|:---:|---|---|:---:|---|
| 1 | Input & Preprocessing | `app.py` (`load_and_preprocess_image`) | ✅ Lengkap | Dukungan kartu kalibrasi warna (ColorChecker) |
| 2 | Deteksi & ROI Face Mesh | `app.py` (`extract_landmarks_and_rois`) | ✅ Lengkap | Penambahan ROI area leher/jawline |
| 3 | Normalisasi White Balance | `app.py` (`apply_gray_world_wb`) | ✅ Lengkap | Algoritma White Patch / Shades of Gray |
| 4 | Kolorimetri CIELAB | `app.py` (`extract_skin_cielab`, dll.) | ✅ Lengkap | Integrasi pemetaan shade foundation pasar nyata |
| 5 | Klasifikasi Jenis Kulit | `app.py` (`predict_skin_type`) | ✅ Lengkap (Heuristik) | Pelatihan CNN mandiri dan export file `.h5` |
| 6 | Formulasi Farmasi | `app.py` (`get_skincare_recommendation`) | ✅ Lengkap | Ekspor lembar kerja formula ke PDF/Excel |
| 7 | Antarmuka Pengguna | `app.py` (`main`) | ✅ Lengkap | Mode gelap (Dark Mode) adaptif |
