# Direktori Model CNN (Opsional)

Simpan model Keras / TensorFlow Anda di folder ini:
`models/skin_type_cnn.h5`

### Konvensi Input & Output Model:
1. **Input:** Citra wajah yang dipotong (crop) berukuran 224x224 atau 256x256 (RGB, skala 0-1 atau -1 sampai 1 sesuai arsitektur model Anda).
2. **Output:** 3 probabilitas kelas (Softmax).
3. **Kelas Default (`CNN_CLASS_NAMES`):** `["Dry", "Normal", "Oily"]` (dapat disesuaikan di `app.py` atau di sidebar aplikasi).

Jika berkas `.h5` tidak ditemukan atau TensorFlow belum terpasang, aplikasi akan secara otomatis beralih ke **Heuristik Tekstur & Kilap Sebum** (Texture & Sebum Shine Heuristic) tanpa menyebabkan error (graceful fallback).
