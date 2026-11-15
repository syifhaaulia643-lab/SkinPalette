# Panduan Kontribusi (Contributing Guidelines)

Terima kasih atas minat Anda untuk berkontribusi pada pengembangan **SkinPalette (AI Skin & Personal Color Analyzer - DermaTone AI)**! Proyek ini dikembangkan dalam lingkup riset dan praktikum mata kuliah **Farmasi AI**.

---

## 🛠️ Alur Kontribusi

1. **Fork Repositori:**
   Klik tombol `Fork` di pojok kanan atas repository GitHub ini.

2. **Clone Fork Anda:**
   ```bash
   git clone https://github.com/syifhaaulia643-lab/SkinPalette.git
   cd SkinPalette
   ```

3. **Buat Branch Fitur Baru:**
   ```bash
   git checkout -b fitur/nama-fitur-baru
   ```

4. **Kembangkan & Uji Perubahan:**
   - Pastikan aplikasi berjalan tanpa error pada Streamlit: `streamlit run app.py`
   - Pastikan fungsi deteksi wajah MediaPipe dan perhitungan CIELAB tetap akurat.

5. **Commit & Push:**
   ```bash
   git commit -m "feat: deskripsi penambahan fitur"
   git push origin fitur/nama-fitur-baru
   ```

6. **Ajukan Pull Request (PR):**
   Buka PR ke branch `main` repositori ini dengan menjelaskan ringkasan perubahan dan alasan farmasetik/teknis di baliknya.

---

## 📋 Standar Kode & Etika Farmasi
- Gunakan penamaan variabel yang deskriptif dan sertakan type hints pada fungsi Python.
- Nilai pigmen dan bahan aktif sediaan kosmetik harus mengacu pada literatur farmasetik resmi (Farmakope Indonesia / Handbook of Pharmaceutical Excipients / Regulasi BPOM).
- Menghormati privasi data: dilarang menyimpan citra wajah pengguna secara permanen ke server eksternal tanpa persetujuan eksplisit.
