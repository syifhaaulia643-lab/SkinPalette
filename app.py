"""
SkinPalette: AI Skin & Personal Color Analyzer
Engine: DermaTone AI (CIELAB Colorimetry, Face Mesh & Cosmetic Formulation)
Aplikasi Web Prototipe - Mata Kuliah Farmasi AI
Platform: Streamlit, OpenCV, MediaPipe Face Mesh, NumPy, (Opsional) TensorFlow/Keras
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageOps
import streamlit as st

# ==============================================================================
# 0. KONFIGURASI HALAMAN STREAMLIT & TEMA
# ==============================================================================

st.set_page_config(
    page_title="SkinPalette - AI Skin & Personal Color Analyzer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS untuk estetika modern, kartu metrik, palet swatch, dan tabel farmasi
st.markdown(
    """
    <style>
    /* Styling Umum */
    .main-header {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        border-left: 6px solid #e07a5f;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #94a3b8;
    }
    .swatch-box {
        display: inline-block;
        width: 100%;
        height: 55px;
        border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.12);
        margin-bottom: 6px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }
    .palette-card {
        text-align: center;
        background: #f8fafc;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    .palette-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #334155;
    }
    .palette-hex {
        font-size: 0.70rem;
        color: #64748b;
        font-family: monospace;
    }
    .info-callout {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.90rem;
        color: #166534;
        margin-bottom: 16px;
    }
    .pharmacy-badge {
        display: inline-block;
        padding: 3px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 4px;
        background-color: #e0e7ff;
        color: #3730a3;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 1. KONSTANTA & INDEKS LANDMARK MEDIAPIPE FACE MESH
# ==============================================================================

# Indeks poligon Region of Interest (ROI) wajah (standar 468/478 landmarks)
# Dahi (Forehead): Area tengah dahi antara alis dan garis rambut
FOREHEAD_LANDMARKS = [10, 338, 297, 332, 284, 9, 54, 103, 67, 109]

# Pipi Kiri (Subjek kanan / Penampil kiri)
LEFT_CHEEK_LANDMARKS = [116, 117, 118, 101, 123, 147, 213, 192, 138, 135, 50, 205]

# Pipi Kanan (Subjek kiri / Penampil kanan)
RIGHT_CHEEK_LANDMARKS = [345, 346, 347, 330, 352, 376, 433, 416, 367, 364, 280, 425]

# Landmark pengecualian (Mata, Alis, Bibir) agar tidak tercampur dalam sampling kulit
LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
LEFT_EYEBROW_LANDMARKS = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
RIGHT_EYEBROW_LANDMARKS = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]
LIPS_LANDMARKS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

# Urutan kelas default bila model CNN digunakan (FR-4.5)
CNN_CLASS_NAMES = ["Dry", "Normal", "Oily"]

# ==============================================================================
# 2. FUNGSI PEMROSESAN CITRA & FACE MESH
# ==============================================================================

def load_and_preprocess_image(image_file: Any, max_side: int = 1024) -> np.ndarray:
    """
    FR-1.4: Memuat citra, mengoreksi orientasi EXIF (kamera ponsel),
    dan mengubah ukuran bila melebihi dimensi sisi terpanjang 1024 px.
    Mengembalikan array numpy RGB (H, W, 3) tipe uint8.
    """
    pil_img = Image.open(image_file)
    # Koreksi orientasi EXIF secara otomatis
    pil_img = ImageOps.exif_transpose(pil_img)
    pil_img = pil_img.convert("RGB")

    width, height = pil_img.size
    if max(width, height) > max_side:
        scale = max_side / float(max(width, height))
        new_w = int(round(width * scale))
        new_h = int(round(height * scale))
        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    return np.array(pil_img, dtype=np.uint8)


def apply_gray_world_wb(img_rgb: np.ndarray) -> np.ndarray:
    """
    FR-2.5: Gray World White Balance untuk menetralkan colour cast lingkungan.
    Faktor koreksi dibatasi pada interval [0.6, 1.6] untuk mencegah distorsi
    apabila terdapat warna dominan pada latar belakang.
    """
    img_float = img_rgb.astype(np.float32)
    mean_r = float(np.mean(img_float[:, :, 0]))
    mean_g = float(np.mean(img_float[:, :, 1]))
    mean_b = float(np.mean(img_float[:, :, 2]))

    gray_target = (mean_r + mean_g + mean_b) / 3.0

    k_r = np.clip(gray_target / (mean_r + 1e-6), 0.6, 1.6)
    k_g = np.clip(gray_target / (mean_g + 1e-6), 0.6, 1.6)
    k_b = np.clip(gray_target / (mean_b + 1e-6), 0.6, 1.6)

    img_wb = np.zeros_like(img_float)
    img_wb[:, :, 0] = np.clip(img_float[:, :, 0] * k_r, 0, 255)
    img_wb[:, :, 1] = np.clip(img_float[:, :, 1] * k_g, 0, 255)
    img_wb[:, :, 2] = np.clip(img_float[:, :, 2] * k_b, 0, 255)

    return img_wb.astype(np.uint8)


def shrink_polygon(points: np.ndarray, factor: float = 0.8) -> np.ndarray:
    """
    FR-2.4: Mengecilkan poligon ROI ke arah centroidnya (faktor 0.8)
    untuk menghindari piksel tepi atau perbatasan rambut/latar belakang.
    """
    if len(points) < 3:
        return points
    centroid = np.mean(points, axis=0)
    shrunk = centroid + factor * (points - centroid)
    return shrunk.astype(np.int32)


def extract_landmarks_and_rois(
    img_rgb: np.ndarray,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    FR-2.1, FR-2.2, FR-2.3, FR-2.4:
    Mendeteksi wajah menggunakan MediaPipe Face Mesh,
    membuat mask ROI dahi, pipi kiri, pipi kanan, serta area pengecualian.
    Mengembalikan: (face_data_dict, error_msg, warning_msg)
    """
    try:
        import mediapipe as mp
    except ImportError:
        return None, "Pustaka 'mediapipe' belum terpasang. Harap instal melalui pip install mediapipe.", None

    mp_face_mesh = mp.solutions.face_mesh
    h, w, _ = img_rgb.shape

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:
        results = face_mesh.process(img_rgb)

    if not results.multi_face_landmarks:
        return None, "Wajah tidak terdeteksi. Pastikan pencahayaan cukup dan wajah menghadap langsung ke kamera.", None

    warning_msg = None
    if len(results.multi_face_landmarks) > 1:
        warning_msg = "Terdeteksi lebih dari satu wajah. Analisis diprioritaskan pada wajah yang paling dominan."

    # Pilih wajah dengan bounding box terbesar
    best_face = None
    max_area = 0
    for face_lms in results.multi_face_landmarks:
        xs = [int(p.x * w) for p in face_lms.landmark]
        ys = [int(p.y * h) for p in face_lms.landmark]
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        if area > max_area:
            max_area = area
            best_face = face_lms

    landmarks = best_face.landmark
    pts_all = np.array([[int(p.x * w), int(p.y * h)] for p in landmarks], dtype=np.int32)

    # 1. Bangun mask area pengecualian (mata, alis, bibir) dan dilasikan (FR-2.4)
    exclusion_mask = np.zeros((h, w), dtype=np.uint8)
    for part_idx in [LEFT_EYE_LANDMARKS, RIGHT_EYE_LANDMARKS, LEFT_EYEBROW_LANDMARKS, RIGHT_EYEBROW_LANDMARKS, LIPS_LANDMARKS]:
        part_pts = pts_all[part_idx]
        hull = cv2.convexHull(part_pts)
        cv2.fillPoly(exclusion_mask, [hull], 255)

    # Dilasikan mask pengecualian dengan kernel 7x7 agar aman dari tepi
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    exclusion_mask = cv2.dilate(exclusion_mask, kernel_dilate, iterations=2)

    # 2. Bangun mask masing-masing ROI (dikecilkan 0.8)
    def make_roi_mask(indices: List[int]) -> np.ndarray:
        raw_pts = pts_all[indices]
        hull = cv2.convexHull(raw_pts)
        shrunk_pts = shrink_polygon(hull, factor=0.8)
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [shrunk_pts], 255)
        # Subtraksi area pengecualian
        mask = cv2.bitwise_and(mask, cv2.bitwise_not(exclusion_mask))
        return mask

    forehead_mask = make_roi_mask(FOREHEAD_LANDMARKS)
    left_cheek_mask = make_roi_mask(LEFT_CHEEK_LANDMARKS)
    right_cheek_mask = make_roi_mask(RIGHT_CHEEK_LANDMARKS)

    combined_roi_mask = cv2.bitwise_or(forehead_mask, left_cheek_mask)
    combined_roi_mask = cv2.bitwise_or(combined_roi_mask, right_cheek_mask)

    # Estimasi bounding box wajah untuk normalisasi heuristik
    xs = pts_all[:, 0]
    ys = pts_all[:, 1]
    bbox_x1, bbox_y1 = max(0, int(np.min(xs))), max(0, int(np.min(ys)))
    bbox_x2, bbox_y2 = min(w, int(np.max(xs))), min(h, int(np.max(ys)))
    face_crop = img_rgb[bbox_y1:bbox_y2, bbox_x1:bbox_x2]

    # Sampling patch rambut (di atas landmark 10 dahi)
    pt10 = pts_all[10]
    face_height = bbox_y2 - bbox_y1
    hair_y1 = max(0, int(pt10[1] - 0.20 * face_height))
    hair_y2 = max(0, int(pt10[1] - 0.04 * face_height))
    forehead_width = int(0.35 * (bbox_x2 - bbox_x1))
    hair_x1 = max(0, int(pt10[0] - forehead_width / 2))
    hair_x2 = min(w, int(pt10[0] + forehead_width / 2))

    hair_patch = None
    if hair_y2 > hair_y1 and hair_x2 > hair_x1:
        hair_patch = img_rgb[hair_y1:hair_y2, hair_x1:hair_x2]

    # Sampling alis sebagai fallback kecerahan rambut (Mode Hijab / rambut tidak terlihat)
    eyebrow_pts = np.vstack([pts_all[LEFT_EYEBROW_LANDMARKS], pts_all[RIGHT_EYEBROW_LANDMARKS]])
    eyebrow_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(eyebrow_mask, [cv2.convexHull(pts_all[LEFT_EYEBROW_LANDMARKS])], 255)
    cv2.fillPoly(eyebrow_mask, [cv2.convexHull(pts_all[RIGHT_EYEBROW_LANDMARKS])], 255)

    face_data = {
        "landmarks": pts_all,
        "forehead_mask": forehead_mask,
        "left_cheek_mask": left_cheek_mask,
        "right_cheek_mask": right_cheek_mask,
        "combined_mask": combined_roi_mask,
        "face_bbox": (bbox_x1, bbox_y1, bbox_x2, bbox_y2),
        "face_crop": face_crop,
        "hair_patch": hair_patch,
        "eyebrow_mask": eyebrow_mask,
    }

    return face_data, None, warning_msg


def generate_roi_overlay(img_rgb: np.ndarray, face_data: Dict[str, Any]) -> np.ndarray:
    """
    FR-2.6: Membuat overlay visual semi-transparan dari ketiga ROI
    (dahi = Cyan, pipi kiri = Hijau Zamrud, pipi kanan = Oranye)
    agar pengguna dapat memverifikasi area kulit yang dianalisis.
    """
    overlay = img_rgb.copy()
    h, w, _ = img_rgb.shape

    color_forehead = (0, 200, 255)   # Cyan
    color_left = (46, 204, 113)      # Hijau Zamrud
    color_right = (255, 127, 80)     # Coral / Oranye

    # Buat kanvas warna
    color_layer = np.zeros_like(img_rgb)
    color_layer[face_data["forehead_mask"] > 0] = color_forehead
    color_layer[face_data["left_cheek_mask"] > 0] = color_left
    color_layer[face_data["right_cheek_mask"] > 0] = color_right

    # Gabungkan dengan transparansi
    combined_mask = face_data["combined_mask"] > 0
    alpha = 0.38
    overlay[combined_mask] = cv2.addWeighted(img_rgb, 1 - alpha, color_layer, alpha, 0)[combined_mask]

    # Gambar garis batas halus (kontur)
    for mask, color in [
        (face_data["forehead_mask"], color_forehead),
        (face_data["left_cheek_mask"], color_left),
        (face_data["right_cheek_mask"], color_right),
    ]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, color, 2)

    return overlay

# ==============================================================================
# 3. ANALISIS WARNA KULIT (CIELAB) & KONVERSI
# ==============================================================================

def rgb_to_cielab(img_rgb: np.ndarray) -> np.ndarray:
    """
    FR-3.1: Mengonversi citra RGB ke ruang warna standar CIELAB (L*, a*, b*).
    Menggunakan konversi float32 OpenCV sehingga:
    - L* bernilai dalam rentang [0.0, 100.0]
    - a* bernilai dalam rentang [-128.0, 127.0]
    - b* bernilai dalam rentang [-128.0, 127.0]
    """
    img_float = img_rgb.astype(np.float32) / 255.0
    lab = cv2.cvtColor(img_float, cv2.COLOR_RGB2Lab)
    return lab


def lab_to_hex(L: float, a: float, b: float) -> str:
    """
    Mengonversi nilai CIELAB (L*, a*, b*) kembali ke nilai representasi sRGB dan kode HEX.
    """
    lab_pixel = np.array([[[L, a, b]]], dtype=np.float32)
    rgb_pixel = cv2.cvtColor(lab_pixel, cv2.COLOR_Lab2RGB)
    rgb_clipped = np.clip(rgb_pixel[0, 0] * 255.0, 0, 255).astype(np.uint8)
    return f"#{rgb_clipped[0]:02X}{rgb_clipped[1]:02X}{rgb_clipped[2]:02X}"


def extract_skin_cielab(
    img_rgb: np.ndarray, roi_mask: np.ndarray
) -> Tuple[float, float, float, np.ndarray]:
    """
    FR-3.2: Ekstraksi nilai warna kulit pada ROI dengan:
    1. Filter rentang kulit YCrCb untuk mengeliminasi bayangan ekstrem/noise rambut.
    2. Pemangkasan persentil 5-95% pada kanal L* untuk menyaring highlight dan bayangan.
    3. Perhitungan nilai akhir berupa MEDIAN L*, a*, b*.
    """
    lab = rgb_to_cielab(img_rgb)
    ycrcb = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)

    # Filter ruang warna YCrCb untuk piksel kulit manusia
    skin_ycrcb = (
        (ycrcb[:, :, 0] >= 60) & (ycrcb[:, :, 0] <= 250) &
        (ycrcb[:, :, 1] >= 130) & (ycrcb[:, :, 1] <= 180) &
        (ycrcb[:, :, 2] >= 75) & (ycrcb[:, :, 2] <= 145)
    )

    combined_filter = (roi_mask > 0) & skin_ycrcb

    # Fallback bila filter YCrCb terlalu ketat
    if np.sum(combined_filter) < 60:
        combined_filter = (roi_mask > 0)

    sampled_lab = lab[combined_filter]

    if len(sampled_lab) == 0:
        # Fallback darurat
        return 55.0, 12.0, 16.0, np.array([])

    L_vals = sampled_lab[:, 0]
    p5 = np.percentile(L_vals, 5)
    p95 = np.percentile(L_vals, 95)

    trimmed_mask = (L_vals >= p5) & (L_vals <= p95)
    trimmed_lab = sampled_lab[trimmed_mask]

    if len(trimmed_lab) == 0:
        trimmed_lab = sampled_lab

    median_L = float(np.median(trimmed_lab[:, 0]))
    median_a = float(np.median(trimmed_lab[:, 1]))
    median_b = float(np.median(trimmed_lab[:, 2]))

    return median_L, median_a, median_b, trimmed_lab


def classify_skintone(L: float) -> Tuple[str, str]:
    """
    FR-3.3, Spesifikasi 8.1: Klasifikasi Skintone berdasarkan L*
    >= 68: Fair
    60 - < 68: Light
    52 - < 60: Medium
    42 - < 52: Tan
    < 42: Deep
    """
    if L >= 68.0:
        return "Fair", "Kulit sangat terang / porselen dengan pantulan cahaya tinggi"
    elif L >= 60.0:
        return "Light", "Kulit terang umum dengan kecerahan sedang-tinggi"
    elif L >= 52.0:
        return "Medium", "Kulit langsat / sawo matang muda (khas Asia Tenggara)"
    elif L >= 42.0:
        return "Tan", "Kulit sawo matang / kecokelatan eksotis"
    else:
        return "Deep", "Kulit gelap eksotis / kaya melanin"


def classify_undertone(a: float, b: float) -> Tuple[str, float, float, str]:
    """
    FR-3.4, Spesifikasi 8.2: Klasifikasi Undertone berdasarkan rasio b*/a*
    Rasio <= 1.20: Cool (Cenderung kemerahan/pink)
    1.20 - 1.50: Neutral (Seimbang)
    >= 1.50: Warm (Cenderung kekuningan/keemasan)
    Dilengkapi sudut Hue (atan2(b*, a*)) dalam derajat.
    """
    # Mencegah pembagian nol bila a* mendekati nol
    safe_a = a if abs(a) > 1e-4 else 0.1
    ratio = b / safe_a

    # Sudut Hue dalam derajat
    hue_rad = math.atan2(b, safe_a)
    hue_deg = math.degrees(hue_rad)
    if hue_deg < 0:
        hue_deg += 360.0

    if ratio <= 1.20:
        category = "Cool"
        desc = "Nuansa dingin / kemerahan (pinkish), pembuluh darah tampak kebiruan/ungu"
    elif ratio < 1.50:
        category = "Neutral"
        desc = "Nuansa netral seimbang antara spektrum kuning dan merah"
    else:
        category = "Warm"
        desc = "Nuansa hangat / keemasan (golden/peachy), pembuluh darah tampak kehijauan"

    return category, ratio, hue_deg, desc


def estimate_hair_lightness(
    img_rgb: np.ndarray,
    face_data: Dict[str, Any],
    mode: str = "auto",
    manual_val: float = 25.0,
) -> float:
    """
    FR-3.6: Mengestimasi kecerahan rambut (L*).
    Pilihan mode:
    - 'auto': Ambil patch di atas dahi; bila tidak valid, fallback ke alis.
    - 'hijab': Langsung sampling dari alis.
    - 'manual': Menggunakan nilai manual dari pilihan dropdown pengguna.
    """
    if mode == "manual":
        return manual_val

    if mode == "hijab":
        # Gunakan kecerahan alis
        eyebrow_mask = face_data["eyebrow_mask"]
        if np.sum(eyebrow_mask) > 10:
            lab = rgb_to_cielab(img_rgb)
            eyebrow_L = lab[eyebrow_mask > 0][:, 0]
            return float(np.median(eyebrow_L))
        return 25.0

    # Mode Otomatis: Coba patch rambut dahi
    hair_patch = face_data.get("hair_patch")
    if hair_patch is not None and hair_patch.size > 100:
        lab_hair = rgb_to_cielab(hair_patch)
        med_L = float(np.median(lab_hair[:, :, 0]))
        # Validasi: jika patch rambut terlalu terang (mis. latar belakang putih polos), fallback ke alis
        if med_L < 80.0:
            return med_L

    # Fallback ke alis bila patch dahi tidak representatif
    eyebrow_mask = face_data["eyebrow_mask"]
    if np.sum(eyebrow_mask) > 10:
        lab = rgb_to_cielab(img_rgb)
        eyebrow_L = lab[eyebrow_mask > 0][:, 0]
        return float(np.median(eyebrow_L))

    return 25.0  # Default nilai rambut gelap umum (L* ≈ 25)


def determine_personal_color(
    skin_L: float,
    undertone: str,
    undertone_ratio: float,
    hair_L: float,
) -> Tuple[str, str, float, str]:
    """
    FR-3.5, Spesifikasi 8.3:
    Menentukan Personal Color (Spring / Summer / Autumn / Winter)
    berdasarkan Skintone (L*), Undertone, dan Kontras wajah-rambut.
    Kontras = L*_kulit - L*_rambut.
    - Rendah: Kontras < 30
    - Sedang: 30 <= Kontras < 42
    - Tinggi: Kontras >= 42
    Kulit dianggap terang bila L* >= 55.
    """
    contrast = skin_L - hair_L
    is_fair_skin = (skin_L >= 55.0)

    # Tentukan undertone efektif
    effective_undertone = undertone
    neutral_note = ""
    if undertone == "Neutral":
        # Titik tengah rasio netral 1.35
        if undertone_ratio >= 1.35:
            effective_undertone = "Warm"
            neutral_note = " (Undertone netral condong ke spektrum Warm)"
        else:
            effective_undertone = "Cool"
            neutral_note = " (Undertone netral condong ke spektrum Cool)"

    if effective_undertone == "Warm":
        if is_fair_skin:
            season = "Spring"
            desc = "Warm & Bright: Palet warna cerah, hangat, segar, dan berenergi."
        else:
            season = "Autumn"
            desc = "Warm & Deep: Palet warna bumi (earthy), hangat, kaya, dan teduh."
    else:  # Cool
        if is_fair_skin and contrast < 42.0:
            season = "Summer"
            desc = "Cool & Soft: Palet warna sejuk, lembut, bernuansa pastel dan anggun."
        else:
            season = "Winter"
            desc = "Cool & Vivid: Palet warna sejuk kontras tinggi, tegas, berani, dan tajam."

    contrast_desc = (
        f"Kontras {contrast:.1f} ({'Tinggi' if contrast >= 42 else 'Sedang' if contrast >= 30 else 'Rendah'})"
    )
    full_desc = f"{desc}{neutral_note}"

    return season, full_desc, contrast, contrast_desc

# ==============================================================================
# 4. KLASIFIKASI JENIS KULIT (MODULAR CNN & HEURISTIK TEKSTUR)
# ==============================================================================

def predict_skin_type_cnn(
    face_crop: np.ndarray, model_path: str, class_names: List[str]
) -> Optional[Tuple[str, float, Dict[str, float]]]:
    """
    FR-4.2: Klasifikasi jenis kulit menggunakan model CNN Keras/TensorFlow (.h5).
    Mengembalikan: (predicted_class, confidence, all_probs) bila berhasil,
    atau None bila model/TensorFlow tidak tersedia.
    """
    if not os.path.exists(model_path):
        return None

    try:
        import tensorflow as tf  # type: ignore
        model = tf.keras.models.load_model(model_path, compile=False)

        # Preprocessing standar CNN: Resize ke input size model (224x224) dan normalisasi 0-1
        input_size = (224, 224)
        resized = cv2.resize(face_crop, input_size)
        input_tensor = np.expand_dims(resized.astype(np.float32) / 255.0, axis=0)

        preds = model.predict(input_tensor, verbose=0)[0]
        pred_idx = int(np.argmax(preds))
        confidence = float(preds[pred_idx])

        probs = {class_names[i]: float(preds[i]) for i in range(min(len(class_names), len(preds)))}
        return class_names[pred_idx], confidence, probs
    except Exception as e:
        # Fallback gracefully tanpa menyebabkan crash (FR-9 Keandalan)
        return None


def calculate_roi_shine(img_lab: np.ndarray, mask: np.ndarray) -> float:
    """
    Menghitung fraksi piksel berkilau sebum pada satu ROI.
    Kriteria: L* > median(L*) + 10 DAN kroma < median(kroma).
    Pantulan sebum specular bersifat terang dan mengalami desaturasi warna.
    """
    roi_pixels = img_lab[mask > 0]
    if len(roi_pixels) < 20:
        return 0.0

    L_vals = roi_pixels[:, 0]
    a_vals = roi_pixels[:, 1]
    b_vals = roi_pixels[:, 2]
    chroma_vals = np.sqrt(a_vals**2 + b_vals**2)

    med_L = float(np.median(L_vals))
    med_chroma = float(np.median(chroma_vals))

    shine_pixels = (L_vals > (med_L + 10.0)) & (chroma_vals < med_chroma)
    return float(np.mean(shine_pixels))


def predict_skin_type_heuristic(
    img_rgb: np.ndarray,
    face_data: Dict[str, Any],
    threshold_oily: float = 0.06,
    threshold_dry_shine: float = 0.02,
    threshold_dry_roughness: float = 3.0,
) -> Tuple[str, Dict[str, Any]]:
    """
    FR-4.3, FR-4.4, Spesifikasi 8.4:
    Heuristik jenis kulit berbasis kilap sebum dan kekasaran mikro-tekstur.
    1. Normalisasi resolusi via face_crop 256x256 px.
    2. Rasio Kilap: Bobot dahi 50%, pipi kiri 25%, pipi kanan 25%.
    3. Kekasaran: Varians Laplacian kanal L* (setelah Gaussian blur 3x3).
    4. Aturan klasifikasi:
       - kilap >= threshold_oily -> Oily
       - kilap <= threshold_dry_shine DAN kekasaran >= threshold_dry_roughness -> Dry
       - selain itu -> Normal
    """
    lab = rgb_to_cielab(img_rgb)

    # 1. Rasio kilap per ROI
    shine_forehead = calculate_roi_shine(lab, face_data["forehead_mask"])
    shine_left = calculate_roi_shine(lab, face_data["left_cheek_mask"])
    shine_right = calculate_roi_shine(lab, face_data["right_cheek_mask"])

    # Rata-rata tertimbang
    weighted_shine = (0.50 * shine_forehead) + (0.25 * shine_left) + (0.25 * shine_right)

    # 2. Kekasaran (Varians Laplacian kanal L*)
    L_channel = lab[:, :, 0]
    L_blur = cv2.GaussianBlur(L_channel, (3, 3), 0)
    laplacian = cv2.Laplacian(L_blur, cv2.CV_32F)

    combined_mask = face_data["combined_mask"] > 0
    if np.sum(combined_mask) > 50:
        roi_laplacian = laplacian[combined_mask]
        roughness = float(np.var(roi_laplacian))
    else:
        roughness = 2.0

    # 3. Evaluasi aturan keputusan
    if weighted_shine >= threshold_oily:
        skin_type = "Oily"
        reason = f"Reflektansi kilap sebum terdeteksi tinggi ({weighted_shine*100:.1f}% >= {threshold_oily*100:.1f}%)."
    elif (weighted_shine <= threshold_dry_shine) and (roughness >= threshold_dry_roughness):
        skin_type = "Dry"
        reason = (
            f"Kilap sebum minimal ({weighted_shine*100:.1f}%) disertai kekasaran mikro-tekstur "
            f"({roughness:.2f} >= {threshold_dry_roughness:.1f})."
        )
    else:
        skin_type = "Normal"
        reason = f"Keseimbangan sebum ({weighted_shine*100:.1f}%) dan tekstur stratum korneum teratur ({roughness:.2f})."

    details = {
        "shine_ratio": weighted_shine,
        "shine_forehead": shine_forehead,
        "shine_cheeks": (shine_left + shine_right) / 2.0,
        "roughness": roughness,
        "reason": reason,
        "method": "Heuristik Tekstur & Kilap Sebum",
    }

    return skin_type, details


def predict_skin_type(
    img_rgb: np.ndarray,
    face_data: Dict[str, Any],
    model_path: str = "models/skin_type_cnn.h5",
    threshold_oily: float = 0.06,
    threshold_dry_shine: float = 0.02,
    threshold_dry_roughness: float = 3.0,
) -> Tuple[str, Dict[str, Any]]:
    """
    FR-4.1: Fungsi modular terpadu klasifikasi jenis kulit.
    Memeriksa ketersediaan model CNN; bila tidak ditemukan, fallback ke heuristik.
    """
    face_crop = face_data.get("face_crop")
    if face_crop is not None and face_crop.size > 0:
        cnn_result = predict_skin_type_cnn(face_crop, model_path, CNN_CLASS_NAMES)
        if cnn_result is not None:
            pred_class, conf, all_probs = cnn_result
            details = {
                "confidence": conf,
                "all_probs": all_probs,
                "reason": f"Prediksi model CNN terlatih dengan tingkat keyakinan {conf*100:.1f}%.",
                "method": "Model CNN Deep Learning",
            }
            return pred_class, details

    # Fallback ke heuristik tekstur
    return predict_skin_type_heuristic(
        img_rgb,
        face_data,
        threshold_oily=threshold_oily,
        threshold_dry_shine=threshold_dry_shine,
        threshold_dry_roughness=threshold_dry_roughness,
    )

# ==============================================================================
# 5. DATA PALET WARNA (PERSONAL COLOR) & REKOMENDASI FARMASI
# ==============================================================================

# Definisi palet warna personal color (busana, lipstik, blush)
PERSONAL_COLOR_PALETTES = {
    "Spring": {
        "title": "Spring (Warm & Bright)",
        "accent": "#f97316",
        "clothing": [
            ("Peach Coral", "#FF8B71"),
            ("Warm Amber", "#F5A623"),
            ("Poppy Red", "#E74C3C"),
            ("Warm Turquoise", "#20B2AA"),
            ("Buttercup Yellow", "#F7D358"),
            ("Mint Leaf", "#98D8A0"),
        ],
        "lipstick": [
            ("Peach Coral", "#E76F51"),
            ("Warm Poppy", "#D94A38"),
            ("Apricot Nude", "#E58E73"),
        ],
        "blush": [
            ("Soft Apricot", "#F4A261"),
            ("Warm Peach", "#F28E79"),
            ("Coral Glow", "#FA7E61"),
        ],
    },
    "Summer": {
        "title": "Summer (Cool & Soft)",
        "accent": "#0ea5e9",
        "clothing": [
            ("Dusty Rose", "#D8A7B1"),
            ("Lavender Fog", "#B6B7DA"),
            ("Soft Sky Blue", "#87AFC7"),
            ("Sage Gray", "#8FA294"),
            ("Mauve Mist", "#A38096"),
            ("Powder Blue", "#A7C7E7"),
        ],
        "lipstick": [
            ("Rose Pink", "#C46D86"),
            ("Soft Berry", "#A84C62"),
            ("Cool Mauve", "#935A6E"),
        ],
        "blush": [
            ("Soft Rose", "#E295A2"),
            ("Petal Pink", "#F1A7B5"),
            ("Cool Orchid", "#D1869E"),
        ],
    },
    "Autumn": {
        "title": "Autumn (Warm & Deep)",
        "accent": "#b45309",
        "clothing": [
            ("Terracotta", "#C85A32"),
            ("Olive Green", "#6B793E"),
            ("Burnt Orange", "#CC5500"),
            ("Mustard Gold", "#DDA221"),
            ("Rust Red", "#8E3218"),
            ("Warm Chestnut", "#7B3F00"),
        ],
        "lipstick": [
            ("Warm Terracotta", "#B84A39"),
            ("Brick Red", "#9E2A2B"),
            ("Cinnamon Brown", "#8A3C2A"),
        ],
        "blush": [
            ("Warm Tawny", "#C2704E"),
            ("Spiced Amber", "#C67B5C"),
            ("Burnt Peach", "#BF6B56"),
        ],
    },
    "Winter": {
        "title": "Winter (Cool & Vivid)",
        "accent": "#6366f1",
        "clothing": [
            ("Pure White", "#FFFFFF"),
            ("Royal Navy", "#002366"),
            ("Ruby Crimson", "#9B111E"),
            ("Emerald Vivid", "#046307"),
            ("Cool Magenta", "#C71585"),
            ("Midnight Black", "#1A1A1A"),
        ],
        "lipstick": [
            ("Classic Crimson", "#A10024"),
            ("Deep Blackberry", "#6B0A29"),
            ("Vivid Fuchsia", "#B80062"),
        ],
        "blush": [
            ("Cool Plum", "#A44967"),
            ("Deep Rosewood", "#8F384D"),
            ("Crisp Fuchsia", "#B63B66"),
        ],
    },
}

# Formula pigmen foundation dasar per Skintone (FR-5.5, Tabel 8.5)
PIGMENT_BASE_FORMULAS = {
    "Fair": {"tio2": 10.0, "yellow": 0.80, "red": 0.30, "black": 0.05},
    "Light": {"tio2": 8.0, "yellow": 1.10, "red": 0.45, "black": 0.10},
    "Medium": {"tio2": 6.0, "yellow": 1.50, "red": 0.70, "black": 0.20},
    "Tan": {"tio2": 4.0, "yellow": 1.90, "red": 1.00, "black": 0.40},
    "Deep": {"tio2": 2.0, "yellow": 2.20, "red": 1.40, "black": 0.90},
}


def calculate_pigment_recommendation(
    skintone: str, undertone: str
) -> Tuple[Dict[str, float], Dict[str, float], float]:
    """
    FR-5.5, Spesifikasi 8.5:
    Menghitung rekomendasi rasio pigmen kosmetik dekoratif foundation
    (TiO2, Iron Oxide Yellow, Red, Black) sebagai:
    1. % b/b dalam total sediaan sediaan emulsi foundation.
    2. Porsi relatif (%) terhadap 100% total pigmen.
    Penyesuaian undertone:
    - Warm: Yellow x 1.25, Red x 0.85
    - Cool: Yellow x 0.80, Red x 1.25
    - Neutral: tanpa penyesuaian (faktor 1.00)
    """
    base = PIGMENT_BASE_FORMULAS.get(skintone, PIGMENT_BASE_FORMULAS["Medium"]).copy()

    if undertone == "Warm":
        factor_y, factor_r = 1.25, 0.85
    elif undertone == "Cool":
        factor_y, factor_r = 0.80, 1.25
    else:  # Neutral
        factor_y, factor_r = 1.00, 1.00

    adjusted = {
        "tio2": base["tio2"],
        "yellow": base["yellow"] * factor_y,
        "red": base["red"] * factor_r,
        "black": base["black"],
    }

    total_pigment_pct = sum(adjusted.values())

    # Porsi relatif terhadap total pigmen
    portions = {k: (v / total_pigment_pct) * 100.0 for k, v in adjusted.items()}

    return adjusted, portions, total_pigment_pct


def get_skincare_recommendation(skin_type: str) -> Dict[str, Any]:
    """
    FR-5.4, Spesifikasi 8.5: Rekomendasi formulasi skincare dari sudut pandang farmasi.
    """
    if skin_type == "Oily":
        return {
            "basis": "Gel Hidrofilik / Emulsi Ringan O/W (Oil-in-Water), Bebas Minyak (Oil-Free)",
            "alasan": (
                "Meminimalkan beban lipid oklusif pada stratum korneum, mencegah penyumbatan duktus "
                "pilosebasea, menyerap sekresi sebum berlebih tanpa memicu kompensasi hipersekresi."
            ),
            "aktif": [
                ("Niacinamide (2 - 5%)", "Mengatur produksi sebum, memperbaiki barier, dan anti-inflamasi."),
                ("Asam Salisilat / BHA (0.5 - 2%)", "Lipofilik; menembus pori-pori untuk melarutkan sumbatan sebum."),
                ("Zinc PCA (1%)", "Menghambat enzim 5α-reduktase dan menekan proliferasi mikrobial jerawat."),
                ("Asam Azelat (5 - 10%)", "Menghambat keratinisasi abnormal dan meredakan eritema kemerahan."),
            ],
            "eksipien": [
                "Gelling agent: Carbomer 940 / Hydroxyethylcellulose (bebas minyak)",
                "Humektan: Butylene Glycol & Sodium Hyaluronate bobot molekul rendah",
                "Sensory modifier: Silika mikronisasi untuk efek mattifying dan soft-focus",
            ],
            "hindari": [
                "Minyak nabati sangat komedogenik (Minyak kelapa / Coconut oil, Cocoa butter)",
                "Ester lemak rantai panjang oklusif berat (Isopropyl Myristate pekat)",
                "Alkohol berkadar sangat tinggi yang mengiritasi dan memicu rebound sebum",
            ],
        }
    elif skin_type == "Dry":
        return {
            "basis": "Emulsi Kaya W/O (Water-in-Oil) atau Krim O/W dengan Lipid Oklusif Tinggi",
            "alasan": (
                "Memperbaiki disfungsi sawar kulit (stratum corneum lipid barrier) yang defisien, "
                "menekan Transepidermal Water Loss (TEWL) dengan lapisan film oklusif semi-permeabel."
            ),
            "aktif": [
                ("Kompleks Ceramide + Kolesterol + Asam Lemak Bebas (~3:1:1)", "Mereplikasi matriks lipid interselular lamellar alami."),
                ("Urea (2 - 5%)", "Komponen NMF fisiologis dengan daya hidrasi osmotik dan keratolitik ringan."),
                ("Glycerin (5 - 10%)", "Humektan higroskopis kuat yang menarik air ke stratum korneum."),
                ("Panthenol / D-Panthenol (2 - 5%)", "Provitamin B5 untuk stimulasi sintesis lipid dan epitelisasi."),
            ],
            "eksipien": [
                "Emolien & Oklusif: Shea Butter, Squalane nabati, Petrolatum murni farmasetis",
                "Emulsifier: Cetearyl Alcohol & Ceteareth-20 pembentuk kristal cair lamellar",
                "Penenang: Bisabolol & Allantoin",
            ],
            "hindari": [
                "Surfaktan anionik keras (Sodium Lauryl Sulfate / SLS murni tanpa buffer)",
                "Etanol murni / alkohol denat berkonsentrasi tinggi",
                "Scrub abrasif fisik berbutiran tajam yang merusak integritas sawar fisik",
            ],
        }
    else:  # Normal
        return {
            "basis": "Emulsi Seimbang O/W (Lotion / Light Cream) dengan Rasio Hidrasi Fisiologis",
            "alasan": (
                "Mempertahankan kelembapan faktor alami (NMF), menjaga rasio hidrasi-sebum ideal, "
                "serta memberikan perlindungan preventif dari fotopenuaan dan stres oksidatif lingkungan."
            ),
            "aktif": [
                ("Niacinamide (2%)", "Menjaga homeostasis barier kulit dan elastisitas dermal."),
                ("Sodium Hyaluronate (0.1 - 1%)", "Mempertahankan turgor dan cadangan hidrasi dermal."),
                ("Kombinasi Antioksidan: Tocopherol (0.5%) + Sodium Ascorbyl Phosphate", "Melindungi membran sel dari radikal bebas UV."),
                ("Tabir Surya Spektrum Luas (SPF 30 - 50, PA++++)", "Fotoproteksi harian terhadap penuaan dini (photoaging)."),
            ],
            "eksipien": [
                "Lipid netral: Caprylic/Capric Triglyceride (fraksi minyak kelapa termurnikan)",
                "Humektan: Glycerin & Propylene Glycol farmasi",
                "Tekstur: Cetyl Alcohol sebagai konsistensi agent lembut",
            ],
            "hindari": [
                "Produk dengan pH ekstrem (< 4.5 atau > 6.5 secara berkepanjangan)",
                "Eksfoliasi kimiawi over-frekuensi yang menipiskan stratum korneum sehat",
            ],
        }

# ==============================================================================
# 6. SIDEBAR KONTROL & PENGATURAN KALIBRASI
# ==============================================================================

def render_sidebar() -> Dict[str, Any]:
    st.sidebar.markdown("## ⚙️ Pengaturan & Kalibrasi")
    st.sidebar.markdown("Konfigurasi parameter analisis dan pra-pemrosesan citra.")

    # 1. Kontrol White Balance
    enable_wb = st.sidebar.toggle(
        "Aktifkan Gray World White Balance",
        value=True,
        help="FR-2.5: Menetralkan bias warna kuning/biru dari lampu ruangan (koreksi dibatasi 0.6 - 1.6).",
    )

    # 2. Mode Rambut & Kontras
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💇 Kecerahan Rambut & Kontras")
    hair_mode = st.sidebar.radio(
        "Sumber Pengukuran Rambut:",
        ["Deteksi Otomatis (Dahi)", "Mode Hijab (Gunakan Alis)", "Input Manual Warna Rambut"],
        index=0,
        help="FR-3.6: Kontras kulit-rambut menentukan pembagian musim Personal Color.",
    )

    manual_hair_L = 25.0
    if hair_mode == "Input Manual Warna Rambut":
        hair_choice = st.sidebar.selectbox(
            "Pilih Warna Rambut Pengguna:",
            [
                ("Hitam Pekat / Jet Black (L* ≈ 15)", 15.0),
                ("Coklat Gelap / Dark Brown (L* ≈ 25)", 25.0),
                ("Coklat Terang / Auburn (L* ≈ 40)", 40.0),
                ("Pirang / Blonde (L* ≈ 65)", 65.0),
                ("Beruban / Abu-abu / Putih (L* ≈ 75)", 75.0),
            ],
            format_func=lambda x: x[0],
            index=1,
        )
        manual_hair_L = hair_choice[1]

    # 3. Model CNN & Kalibrasi Heuristik
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧪 Model & Kalibrasi Jenis Kulit")
    model_path = st.sidebar.text_input(
        "Path Model CNN (.h5 opsional):",
        value="models/skin_type_cnn.h5",
        help="FR-4.2: Jalur file model Keras/TensorFlow. Jika belum ada, otomatis beralih ke heuristik.",
    )

    with st.sidebar.expander("Kalibrasi Ambang Heuristik", expanded=False):
        st.markdown(
            "<small>Sesuaikan ambang awal (Spesifikasi 8.4) untuk menyesuaikan sensitivitas kamera:</small>",
            unsafe_allow_html=True,
        )
        threshold_oily = st.slider(
            "Ambang Kilap Oily (% piksel kilap)",
            min_value=2.0,
            max_value=15.0,
            value=6.0,
            step=0.5,
            help="Persentase piksel ROI dengan L* tinggi dan kroma rendah untuk kelas Oily.",
        ) / 100.0

        threshold_dry_shine = st.slider(
            "Ambang Maksimal Kilap Dry (%)",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.5,
            help="Batas atas kilap sebum untuk kulit Dry.",
        ) / 100.0

        threshold_dry_roughness = st.slider(
            "Ambang Minimal Kekasaran Dry",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.5,
            help="Varians Laplacian pada kanal L* untuk mendeteksi tekstur kering berkerut.",
        )

    # Info Modul Farmasi AI
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.76rem; color: #64748b; line-height: 1.4;">
        <b>SkinPalette v1.0 (MVP)</b><br>
        DermaTone AI - Farmasi AI<br>
        Ruang Warna: CIELAB (D65)<br>
        Metode Deteksi: MediaPipe Face Mesh
        </div>
        """,
        unsafe_allow_html=True,
    )

    hair_internal_mode = (
        "manual" if hair_mode == "Input Manual Warna Rambut"
        else "hijab" if hair_mode == "Mode Hijab (Gunakan Alis)"
        else "auto"
    )

    return {
        "enable_wb": enable_wb,
        "hair_mode": hair_internal_mode,
        "manual_hair_L": manual_hair_L,
        "model_path": model_path,
        "threshold_oily": threshold_oily,
        "threshold_dry_shine": threshold_dry_shine,
        "threshold_dry_roughness": threshold_dry_roughness,
    }

# ==============================================================================
# 7. TAMPILAN UTAMA APLIKASI (STREAMLIT UI)
# ==============================================================================

def main():
    # Render Sidebar
    config = render_sidebar()

    # Header Utama
    st.markdown(
        """
        <div class="main-header">
            <h1 style="margin:0; font-size:2.1rem; color:#1e293b; font-weight:800;">
                ✨ SkinPalette: AI Skin & Personal Color Analyzer
            </h1>
            <p style="margin:6px 0 0 0; color:#475569; font-size:1.05rem;">
                DermaTone AI: Analisis Kuantitatif CIELAB (Skintone, Undertone, Personal Color) & Jenis Kulit untuk Perancangan Kosmetik Farmasetik.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Panduan Foto Akurat (FR-1.3)
    with st.expander("📋 Panduan Pengambilan Foto yang Direkomendasikan", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown("☀️ **Cahaya Alami**<br><small>Gunakan cahaya siang hari tidak langsung (diffuse light). Hindari lampu pijar kuning kuat atau backlight.</small>", unsafe_allow_html=True)
        c2.markdown("🧼 **Wajah Bersih**<br><small>Bebas dari foundation, bedak, atau sunscreen tinted yang dapat mendistorsi warna asli kulit.</small>", unsafe_allow_html=True)
        c3.markdown("👤 **Posisi Frontal**<br><small>Tatap lurus ke kamera dengan ekspresi netral, memastikan dahi dan kedua pipi terlihat simetris.</small>", unsafe_allow_html=True)
        c4.markdown("🚫 **Tanpa Filter**<br><small>Matikan mode kecantikan (beauty filter), HDR agresif, atau efek kamera ponsel.</small>", unsafe_allow_html=True)

    # Pilihan Sumber Foto (FR-1.1, FR-1.2)
    st.markdown("### 1. Masukkan Foto Wajah")
    source_choice = st.radio(
        "Pilih metode masukan foto:",
        ["📤 Unggah Berkas Gambar (JPG / PNG)", "📸 Ambil Foto Langsung (Kamera)"],
        horizontal=True,
    )

    image_file = None
    if source_choice == "📤 Unggah Berkas Gambar (JPG / PNG)":
        image_file = st.file_uploader(
            "Unggah foto wajah beresolusi jelas (JPG, JPEG, atau PNG):",
            type=["jpg", "jpeg", "png"],
            help="FR-1.1: Foto diproses langsung di memori tanpa disimpan ke disk.",
        )
    else:
        image_file = st.camera_input("Ambil foto melalui webcam/kamera perangkat:")

    if image_file is None:
        st.info("👋 Silakan unggah foto atau gunakan kamera perangkat Anda untuk memulai analisis.")
        return

    # Memuat dan memproses citra (FR-1.4)
    with st.spinner("Memuat dan memproses citra wajah..."):
        raw_img = load_and_preprocess_image(image_file)

    # Deteksi Wajah dan Ekstraksi ROI MediaPipe (FR-2.1 s.d. FR-2.4)
    with st.spinner("Mendeteksi landmark wajah dan mengekstrak ROI (Dahi & Pipi)..."):
        face_data, error_msg, warning_msg = extract_landmarks_and_rois(raw_img)

    if error_msg:
        st.error(f"❌ {error_msg}")
        return

    if warning_msg:
        st.warning(f"⚠️ {warning_msg}")

    # Terapkan White Balance bila diaktifkan (FR-2.5)
    analyzed_img = raw_img.copy()
    if config["enable_wb"]:
        analyzed_img = apply_gray_world_wb(analyzed_img)

    # Overlay visual ROI (FR-2.6)
    roi_overlay = generate_roi_overlay(analyzed_img, face_data)

    # Tampilkan Gambar Asli vs Overlay ROI
    st.markdown("---")
    st.markdown("### 2. Verifikasi Visual Region of Interest (ROI)")
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.image(raw_img, caption="Foto Input (Asli)", use_container_width=True)
    with col_img2:
        caption_wb = "Overlay ROI Kulit (Dahi=Cyan, Pipi=Hijau/Oranye) " + ("[Dengan White Balance]" if config["enable_wb"] else "[Tanpa White Balance]")
        st.image(roi_overlay, caption=caption_wb, use_container_width=True)

    # Ekstraksi Warna Kulit CIELAB (FR-3.1, FR-3.2)
    with st.spinner("Melakukan analisis spektrum warna CIELAB dan tekstur permukaan..."):
        skin_L, skin_a, skin_b, sampled_lab = extract_skin_cielab(
            analyzed_img, face_data["combined_mask"]
        )
        skin_hex = lab_to_hex(skin_L, skin_a, skin_b)

        # Klasifikasi Skintone & Undertone (FR-3.3, FR-3.4)
        skintone, skintone_desc = classify_skintone(skin_L)
        undertone, undertone_ratio, hue_angle, undertone_desc = classify_undertone(skin_a, skin_b)

        # Sampling Rambut & Personal Color (FR-3.5, FR-3.6)
        hair_L = estimate_hair_lightness(
            analyzed_img,
            face_data,
            mode=config["hair_mode"],
            manual_val=config["manual_hair_L"],
        )
        personal_color, pc_desc, contrast_val, contrast_desc = determine_personal_color(
            skin_L, undertone, undertone_ratio, hair_L
        )

        # Klasifikasi Jenis Kulit (FR-4.1)
        skin_type, skin_type_details = predict_skin_type(
            analyzed_img,
            face_data,
            model_path=config["model_path"],
            threshold_oily=config["threshold_oily"],
            threshold_dry_shine=config["threshold_dry_shine"],
            threshold_dry_roughness=config["threshold_dry_roughness"],
        )

    # ==========================================================================
    # 8. HASIL ANALISIS (KARTU METRIK & DATA KUANTITATIF)
    # ==========================================================================
    st.markdown("---")
    st.markdown("### 3. Hasil Analisis Kuantitatif & Klasifikasi")

    # 4 Kartu Metrik Utama (FR-5.1)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Jenis Kulit (Skin Type)</div>
                <div class="metric-value">{skin_type}</div>
                <div class="metric-sub">{skin_type_details['method']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Skintone</div>
                <div class="metric-value">{skintone}</div>
                <div class="metric-sub">Kecerahan L* = {skin_L:.1f} / 100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Undertone</div>
                <div class="metric-value">{undertone}</div>
                <div class="metric-sub">Rasio b*/a* = {undertone_ratio:.2f} (Hue {hue_angle:.1f}°)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Personal Color</div>
                <div class="metric-value">{personal_color}</div>
                <div class="metric-sub">{contrast_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Panel Detail Spektrum CIELAB & Swatch Warna Kulit Terukur (FR-5.2)
    st.markdown("<br>", unsafe_allow_html=True)
    c_lab1, c_lab2 = st.columns([1, 2])

    with c_lab1:
        st.markdown(
            f"""
            <div style="background:white; border-radius:12px; padding:16px; border:1px solid #e2e8f0; text-align:center;">
                <div style="font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:8px;">Warna Kulit Terukur</div>
                <div class="swatch-box" style="background-color: {skin_hex}; height:75px;"></div>
                <div style="font-family:monospace; font-weight:700; font-size:1.1rem; color:#1e293b;">{skin_hex}</div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">
                    sRGB Representasi dari CIELAB
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_lab2:
        st.markdown(
            f"""
            <div style="background:#f8fafc; border-radius:12px; padding:16px 20px; border:1px solid #e2e8f0;">
                <h4 style="margin:0 0 10px 0; color:#1e293b; font-size:1.0rem;">Parameter Kuantitatif CIELAB (D65)</h4>
                <table style="width:100%; font-size:0.88rem; color:#334155; line-height:1.6;">
                    <tr>
                        <td style="width:30%;"><b>L* (Lightness)</b></td>
                        <td style="width:25%;"><code>{skin_L:.2f}</code></td>
                        <td>0 (Hitam pekat) hingga 100 (Putih difus sempurna)</td>
                    </tr>
                    <tr>
                        <td><b>a* (Green - Red)</b></td>
                        <td><code>{skin_a:.2f}</code></td>
                        <td>Nilai positif menunjukkan komponen eritema / kemerahan</td>
                    </tr>
                    <tr>
                        <td><b>b* (Blue - Yellow)</b></td>
                        <td><code>{skin_b:.2f}</code></td>
                        <td>Nilai positif menunjukkan komponen karoten / kekuningan</td>
                    </tr>
                    <tr>
                        <td><b>Rasio b* / a*</b></td>
                        <td><code>{undertone_ratio:.2f}</code></td>
                        <td>Indikator undertone (Cool ≤ 1.20, Neutral 1.20-1.50, Warm ≥ 1.50)</td>
                    </tr>
                    <tr>
                        <td><b>Kontras Rambut-Wajah</b></td>
                        <td><code>{contrast_val:.1f}</code></td>
                        <td>L*_kulit ({skin_L:.1f}) − L*_rambut ({hair_L:.1f})</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Rincian Diagnostik Tekstur Kulit
    with st.expander("🔍 Rincian Analisis Tekstur & Sebum (Skin Type Details)", expanded=False):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"**Metode Klasifikasi:** `{skin_type_details['method']}`")
            st.markdown(f"**Penjelasan:** {skin_type_details['reason']}")
            if "confidence" in skin_type_details:
                st.markdown(f"**Tingkat Keyakinan CNN:** `{skin_type_details['confidence']*100:.2f}%`")
                st.json(skin_type_details.get("all_probs", {}))
        with col_t2:
            if "shine_ratio" in skin_type_details:
                st.markdown(f"**Rasio Kilap Tertimbang:** `{skin_type_details['shine_ratio']*100:.2f}%`")
                st.markdown(f"- Kilap Dahi: `{skin_type_details['shine_forehead']*100:.2f}%`")
                st.markdown(f"- Kilap Pipi: `{skin_type_details['shine_cheeks']*100:.2f}%`")
                st.markdown(f"**Kekasaran Permukaan (Laplacian):** `{skin_type_details['roughness']:.3f}`")

    # ==========================================================================
    # 9. PALET WARNA PERSONAL COLOR (FR-5.3)
    # ==========================================================================
    st.markdown("---")
    st.markdown(f"### 4. Rekomendasi Palet Personal Color: {personal_color}")
    st.markdown(f"*{pc_desc}*")

    palette_info = PERSONAL_COLOR_PALETTES.get(personal_color, PERSONAL_COLOR_PALETTES["Spring"])

    tab_pal1, tab_pal2, tab_pal3 = st.tabs(["👗 Warna Busana & Aksesoris", "💄 Warna Lipstik Terbaik", "🌸 Warna Blush On"])

    with tab_pal1:
        cols = st.columns(len(palette_info["clothing"]))
        for col, (name, hex_val) in zip(cols, palette_info["clothing"]):
            with col:
                st.markdown(
                    f"""
                    <div class="palette-card">
                        <div class="swatch-box" style="background-color:{hex_val};"></div>
                        <div class="palette-label">{name}</div>
                        <div class="palette-hex">{hex_val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_pal2:
        cols_lip = st.columns(len(palette_info["lipstick"]))
        for col, (name, hex_val) in zip(cols_lip, palette_info["lipstick"]):
            with col:
                st.markdown(
                    f"""
                    <div class="palette-card">
                        <div class="swatch-box" style="background-color:{hex_val};"></div>
                        <div class="palette-label">{name}</div>
                        <div class="palette-hex">{hex_val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_pal3:
        cols_blush = st.columns(len(palette_info["blush"]))
        for col, (name, hex_val) in zip(cols_blush, palette_info["blush"]):
            with col:
                st.markdown(
                    f"""
                    <div class="palette-card">
                        <div class="swatch-box" style="background-color:{hex_val};"></div>
                        <div class="palette-label">{name}</div>
                        <div class="palette-hex">{hex_val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ==========================================================================
    # 10. REKOMENDASI FORMULASI FARMASI (SKINCARE & FOUNDATION PIGMENTS)
    # ==========================================================================
    st.markdown("---")
    st.markdown("### 5. Rekomendasi Formulasi Farmasi & Kosmetik")

    tab_form1, tab_form2 = st.tabs(["🧴 Formulasi Skincare Terapeutik", "🎨 Formulasi Pigmen Foundation"])

    # TAB 1: FORMULASI SKINCARE (FR-5.4)
    with tab_form1:
        skincare = get_skincare_recommendation(skin_type)

        st.markdown(f"#### Formulasi Berdasarkan Jenis Kulit: **{skin_type}**")
        st.info(f"**Basis Sediaan Rekomendasi:** {skincare['basis']}\n\n**Rasional Farmasetik:** {skincare['alasan']}")

        c_sk1, c_sk2 = st.columns(2)

        with c_sk1:
            st.markdown("##### 🔬 Bahan Aktif Utama & Konsentrasi Farmasetik")
            for act_name, act_purpose in skincare["aktif"]:
                st.markdown(f"- **{act_name}**  \n  <small style='color:#475569;'>{act_purpose}</small>", unsafe_allow_html=True)

            st.markdown("##### 🧪 Eksipien Penunjang yang Sesuai")
            for exc in skincare["eksipien"]:
                st.markdown(f"- <small>{exc}</small>", unsafe_allow_html=True)

        with c_sk2:
            st.markdown("##### 🚫 Bahan yang Dianjurkan Dihindari / Dibatasi")
            for avoid in skincare["hindari"]:
                st.markdown(f"- <span style='color:#b91c1c;'>⚠️ {avoid}</span>", unsafe_allow_html=True)

            st.markdown(
                """
                <div style="background:#f1f5f9; padding:12px; border-radius:8px; font-size:0.80rem; color:#475569; margin-top:16px;">
                <b>Catatan Farmakope:</b> Pemilihan pengawet (preservatives) seperti Phenoxyethanol 0.5-1%
                atau Ethylhexylglycerin dan penyesuaian pH sediaan pada rentang fisiologis asam mantel kulit (pH 4.8 - 5.5)
                wajib dilakukan untuk mempertahankan stabilitas mikrobiologis dan sawar epitel.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # TAB 2: FORMULASI PIGMEN FOUNDATION (FR-5.5)
    with tab_form2:
        adj_pigments, portions, total_pigment = calculate_pigment_recommendation(skintone, undertone)

        st.markdown(
            f"#### Rasio Pigmen Dekoratif untuk Skintone: **{skintone}** & Undertone: **{undertone}**"
        )
        st.markdown(
            f"Titik awal perancangan warna foundation berbasis CIELAB. Total kadar pigmen dalam formula: **{total_pigment:.2f}% (b/b)**."
        )

        # Tabel Komposisi Pigmen Farmasi
        pigment_data = [
            {
                "Pigmen": "Titanium Dioxide (TiO₂)",
                "CI Code": "CI 77891",
                "Peran": "Opasitas, pemutih dasar, penyesuaian L*",
                "Kadar (% b/b)": f"{adj_pigments['tio2']:.2f}%",
                "Porsi Relatif (%)": f"{portions['tio2']:.1f}%",
                "Warna": "#FFFFFF",
            },
            {
                "Pigmen": "Iron Oxide Yellow",
                "CI Code": "CI 77492",
                "Peran": "Kromofor kuning (+b*), penentu kehangatan kulit",
                "Kadar (% b/b)": f"{adj_pigments['yellow']:.2f}%",
                "Porsi Relatif (%)": f"{portions['yellow']:.1f}%",
                "Warna": "#E5A823",
            },
            {
                "Pigmen": "Iron Oxide Red",
                "CI Code": "CI 77491",
                "Peran": "Kromofor merah (+a*), rona alami darah/vaskular",
                "Kadar (% b/b)": f"{adj_pigments['red']:.2f}%",
                "Porsi Relatif (%)": f"{portions['red']:.1f}%",
                "Warna": "#A83232",
            },
            {
                "Pigmen": "Iron Oxide Black",
                "CI Code": "CI 77499",
                "Peran": "Peredam kecerahan (-L*), penentu kedalaman shade",
                "Kadar (% b/b)": f"{adj_pigments['black']:.2f}%",
                "Porsi Relatif (%)": f"{portions['black']:.1f}%",
                "Warna": "#1C1C1C",
            },
        ]

        # Tampilkan visual progress bar komposisi
        st.markdown("##### Visualisasi Porsi Relatif Pigmen:")
        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        c_p1.metric("Titanium Dioxide", f"{portions['tio2']:.1f}%", f"{adj_pigments['tio2']:.2f}% b/b")
        c_p2.metric("Iron Oxide Yellow", f"{portions['yellow']:.1f}%", f"{adj_pigments['yellow']:.2f}% b/b")
        c_p3.metric("Iron Oxide Red", f"{portions['red']:.1f}%", f"{adj_pigments['red']:.2f}% b/b")
        c_p4.metric("Iron Oxide Black", f"{portions['black']:.1f}%", f"{adj_pigments['black']:.2f}% b/b")

        st.markdown("<br>", unsafe_allow_html=True)
        st.table(pigment_data)

        st.markdown(
            f"""
            <div style="background:#fffbeb; border-left:4px solid #f59e0b; padding:12px 16px; border-radius:6px; font-size:0.83rem; color:#92400e;">
            <b>Rasional Penyesuaian Undertone ({undertone}):</b><br>
            • Untuk undertone <b>Warm</b>: Rasio Iron Oxide Yellow dinaikkan ×1.25 dan Red disesuaikan ×0.85 untuk menciptakan rona keemasan.<br>
            • Untuk undertone <b>Cool</b>: Rasio Iron Oxide Red dinaikkan ×1.25 dan Yellow diturunkan ×0.80 untuk menciptakan rona pinkish.<br>
            • Untuk undertone <b>Neutral</b>: Menggunakan rasio acuan standar tanpa modifikasi pengali.<br>
            <i>*Gunakan pigmen yang telah di-surface treatment (misal triethoxycaprylylsilane) untuk memastikan dispersi merata pada fase minyak emulsi.</i>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ==========================================================================
    # 11. DISCLAIMER EDUKATIF & FOOTER (FR-5.6, SEKSI 14)
    # ==========================================================================
    st.markdown("---")
    st.markdown(
        """
        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:16px; font-size:0.80rem; color:#64748b; line-height:1.5;">
            <b>Pernyataan Penyangkalan (Disclaimer Akademik & Farmasi):</b><br>
            1. Aplikasi ini merupakan prototipe akademik yang dikembangkan untuk keperluan praktikum/penelitian pada mata kuliah <b>Farmasi AI</b>.<br>
            2. Hasil analisis citra dipengaruhi oleh variasi sensor kamera perangkat, kondisi pencahayaan ambient, dan kompresi citra digital. Aplikasi ini <b>bukan</b> alat diagnosis klinis dermatologi dan tidak menggantikan konsultasi langsung dengan dokter spesialis kulit atau apoteker.<br>
            3. Rekomendasi formulasi skincare dan rasio pigmen foundation adalah <i>starting point</i> teoritis kuantitatif berbasis ruang warna CIELAB. Formulasi akhir wajib diuji stabilitas fisik (cycling test, freeze-thaw), efektivitas pengawet (challenge test), serta evaluasi organoleptik dan kompatibilitas kulit di laboratorium formulasi farmasi.<br>
            4. <b>Jaminan Privasi:</b> Seluruh proses pengolahan citra dilakukan secara lokal pada memori komputasi saat runtime dan tidak disimpan ke basis data atau server eksternal.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
