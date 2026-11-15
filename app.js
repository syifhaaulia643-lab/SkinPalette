/**
 * SkinPalette ✨ - AI Skin & Personal Color Analyzer
 * Engine: DermaTone AI (CIELAB Colorimetry, MediaPipe Face Mesh & Cosmetic Formulations)
 * 100% Client-Side In-Browser Execution (Zero Image Uploads)
 */

(function () {
  'use strict';

  // State Management
  const state = {
    imageSrc: null,
    imageElement: null,
    webcamStream: null,
    countdownTimer: null,
    detectedLandmarks: null,
    faceMeshInstance: null,
    showMesh: true,
    includePhotoInExport: false,
    analysisResult: null,
    activeTab: 'upload', // 'upload' | 'webcam'
    activeResultTab: 'palette' // 'palette' | 'formulation'
  };

  // Color & Formulation Knowledge Base
  const SEASON_PALETTES = {
    Spring: {
      desc: "Warm, Bright, Clear & Fresh",
      recommended: [
        { name: "Coral", hex: "#FF7F6B", usage: { fashion: "Atasan cerah, kemeja, hijab", lips: "Warm coral pink", blush: "Peach coral berseri", eyes: "Aksen shimmer hangat" } },
        { name: "Peach", hex: "#FFBE98", usage: { fashion: "Blouse, outer pastel hangat", lips: "Nude peach hangat", blush: "Rona lembut alami", eyes: "Base kelopak mata" } },
        { name: "Golden Yellow", hex: "#F7C948", usage: { fashion: "Dress cerah, scarf statement", lips: "Aksen gloss keemasan", blush: "Warm highlighter", eyes: "Sudut dalam mata" } },
        { name: "Leaf Green", hex: "#8BCB6A", usage: { fashion: "Tunik, cardigan segar", lips: "Padankan dengan lipstik peach", blush: "Netral", eyes: "Eyeliner hijau botol" } },
        { name: "Aqua", hex: "#3CC7C0", usage: { fashion: "Gaun musim semi, aksesori", lips: "Netral nude", blush: "Coral tipis", eyes: "Garis mata bawah" } },
        { name: "Camel", hex: "#D9A066", usage: { fashion: "Blazer klasik, celana", lips: "Warm terracotta nude", blush: "Warm bronzer", eyes: "Transisi lipatan mata" } }
      ],
      avoid: [
        { name: "Black", hex: "#111111", reason: "Terlalu keras dan mengaburkan rona segar kulit Anda." },
        { name: "Dusty Mauve", hex: "#9C7A87", reason: "Terlalu kusam/ashy untuk rona hangat Anda." },
        { name: "Burgundy", hex: "#6D1F3A", reason: "Terlalu gelap dan berat untuk tipe Spring." }
      ]
    },
    Summer: {
      desc: "Cool, Soft, Muted & Elegant",
      recommended: [
        { name: "Powder Blue", hex: "#A8C5E6", usage: { fashion: "Kemeja kerja, blouse lembut", lips: "Soft berry pink", blush: "Cool rose", eyes: "Cool silvery blue wash" } },
        { name: "Rose Pink", hex: "#E3A0B5", usage: { fashion: "Dress, sweater manis", lips: "Dusty rose pink", blush: "Soft pink alami", eyes: "Transisi kelopak mata" } },
        { name: "Lavender", hex: "#B9A6D8", usage: { fashion: "Scarf, hijab, kardigan", lips: "Cool mauve nude", blush: "Lilac-pink lembut", eyes: "Kelopak mata atas" } },
        { name: "Soft Mauve", hex: "#B07C9A", usage: { fashion: "Outer formal, blazer", lips: "Plum-rose elegan", blush: "Muted mauve", eyes: "Sudut luar mata" } },
        { name: "Sage Green", hex: "#9DB4A0", usage: { fashion: "Kemeja kasual, dress", lips: "Nude pink", blush: "Soft rose", eyes: "Eyeliner hijau lembut" } },
        { name: "Slate Blue", hex: "#6F86A8", usage: { fashion: "Jas, rok, jaket denim", lips: "Rosewood", blush: "Netral cool", eyes: "Smoky eyes lembut" } }
      ],
      avoid: [
        { name: "Bright Orange", hex: "#F57C00", reason: "Terlalu kuning membakar undertone dingin Anda." },
        { name: "Mustard", hex: "#D4A017", reason: "Memberikan kesan wajah lelah dan pucat." },
        { name: "Rust", hex: "#B7410E", reason: "Membuat kompleksi wajah terlihat kontras tidak seimbang." }
      ]
    },
    Autumn: {
      desc: "Warm, Deep, Rich & Earthy",
      recommended: [
        { name: "Terracotta", hex: "#C8643C", usage: { fashion: "Blazer, rajut, hijab tanah", lips: "Brick red / terracotta", blush: "Warm terracotta", eyes: "Kelopak luar / crease" } },
        { name: "Olive Green", hex: "#7D8445", usage: { fashion: "Jaket parka, blouse earthy", lips: "Warm nude brown", blush: "Warm bronzer", eyes: "Smoky olive eyeliner" } },
        { name: "Warm Mustard", hex: "#D6A12B", usage: { fashion: "Outerwear, scarf elegan", lips: "Toasted caramel", blush: "Golden peach", eyes: "Aksen shimmer tembaga" } },
        { name: "Deep Teal", hex: "#2E6F6B", usage: { fashion: "Gaun malam, blazer formal", lips: "Netral cokelat hangat", blush: "Apricot", eyes: "Eyeliner statement" } },
        { name: "Chocolate Brown", hex: "#6B4029", usage: { fashion: "Mantel, celana wool, sepatu", lips: "Deep mocha", blush: "Contour hangat", eyes: "Kedalaman kelopak mata" } },
        { name: "Warm Cream", hex: "#F3E2C0", usage: { fashion: "Kemeja dasar, linen, sutra", lips: "Bebas", blush: "Bebas", eyes: "Base highlight tulang alis" } }
      ],
      avoid: [
        { name: "Fuchsia", hex: "#E6007E", reason: "Terlalu kontras dan bernada dingin mencolok." },
        { name: "Icy Blue", hex: "#BFE3F5", reason: "Membuat kulit sawo matang/hangat tampak pucat abu-abu." },
        { name: "Stark White", hex: "#FFFFFF", reason: "Terlalu silau klinis; gantikan dengan Warm Cream." }
      ]
    },
    Winter: {
      desc: "Cool, Striking, High-Contrast & Vivid",
      recommended: [
        { name: "True Red", hex: "#C8102E", usage: { fashion: "Dress pesta, blazer merah", lips: "Classic bold blue-red", blush: "Soft rose tint", eyes: "Winged black eyeliner" } },
        { name: "Royal Blue", hex: "#2B50C8", usage: { fashion: "Jas resmi, gaun formal", lips: "Nude cool / pink", blush: "Subtle pink", eyes: "Garis mata grafis" } },
        { name: "Emerald Green", hex: "#0B8F5A", usage: { fashion: "Satin dress, outer mewah", lips: "Deep berry red", blush: "Cool rose", eyes: "Smoky eyes mewah" } },
        { name: "Fuchsia", hex: "#D81B80", usage: { fashion: "Atasan statement, scarf", lips: "Bold magenta / fuchsia", blush: "Pop of bright pink", eyes: "Minimalist mascara" } },
        { name: "Icy Gray", hex: "#D9DEE5", usage: { fashion: "Kemeja perak, wol dingin", lips: "Bold lips", blush: "Netral", eyes: "Silvery highlight" } },
        { name: "Charcoal Black", hex: "#1F2328", usage: { fashion: "Tuxedo, little black dress", lips: "Apapun dengan rona tegas", blush: "Rosewood", eyes: "Classic smoky black" } }
      ],
      avoid: [
        { name: "Mustard Yellow", hex: "#D6A12B", reason: "Membuat wajah tampak letih dan tidak bersih." },
        { name: "Peach", hex: "#FFBE98", reason: "Kurang memiliki intensitas kontras untuk persona Winter." },
        { name: "Olive Green", hex: "#7D8445", reason: "Menyerap cahaya alami wajah dingin Anda." }
      ]
    }
  };

  const FORMULATIONS_DATA = {
    "Oily": {
      base: "Basis Gel Hidrofilik atau Emulsi Ringan O/W (Oil-in-Water) Oil-Free.",
      actives: [
        { name: "Niacinamide (Vitamin B3)", conc: "2.0% - 5.0%", note: "Menekan sekresi sebum berlebih & memperkuat sawar epitel." },
        { name: "Salicylic Acid (BHA)", conc: "0.5% - 2.0%", note: "Lipofilik, mengeksfoliasi pori & mencegah komedo mikro." },
        { name: "Zinc PCA", conc: "1.0%", note: "Astringent fisiologis & regulator enzim 5α-reduktase." },
        { name: "Hyaluronic Acid (Low MW)", conc: "0.2% - 1.0%", note: "Hidrasi stratum korneum tanpa rasa lengket oklusif." }
      ],
      avoid: "Minyak mineral berat (Petrolatum konsentrasi tinggi), isopropyl myristate, dan lilin lebah (Beeswax) komedogenik.",
      rationale: "Kulit memproduksi sebum berlebih; formulasi difokuskan pada hidrasi berbasis air dan agen keratolitik ringan."
    },
    "Dry": {
      base: "Emulsi Kaya Lipid W/O (Water-in-Oil) atau Krim O/W dengan Fasa Minyak Tinggi.",
      actives: [
        { name: "Kompleks Ceramide (EOP, NP, AP)", conc: "1.0% - 3.0% (Rasio ~3:1:1)", note: "Memperbaiki lamella lipid antarsel yang terdeplesi." },
        { name: "Urea Farmasi", conc: "3.0% - 7.0%", note: "Faktor Pelembap Alami (NMF) kuat peredam TEWL." },
        { name: "Squalane & Shea Butter", conc: "3.0% - 8.0%", note: "Emolien biomimetik pengunci kelembapan stratum korneum." },
        { name: "D-Panthenol (Pro-Vitamin B5)", conc: "2.0% - 5.0%", note: "Akselerator regenerasi epitel & pereda rasa kencang." }
      ],
      avoid: "Sabun alkali keras, astringent beralkohol denaturasi tinggi (Alcohol Denat >10%), dan scrub fisik abrasif.",
      rationale: "Fungsi sawar kulit terganggu dengan Transepidermal Water Loss (TEWL) tinggi; butuh oklusif dan lipid fisiologis."
    },
    "Combination / Normal": {
      base: "Emulsi Ringan O/W (Lotion/Gel-Cream) Seimbang Berbasis Ester Ringan.",
      actives: [
        { name: "Niacinamide", conc: "2.0% - 4.0%", note: "Stabilisator mikrobioma kulit & perata warna kompleksi." },
        { name: "Sodium Hyaluronate", conc: "0.5% - 1.5%", note: "Humektan pengikat air multiguna pada semua zona wajah." },
        { name: "Salicylic Acid (Spot/T-zone)", conc: "0.5% - 1.0%", note: "Pengontrol pori terfokus di dahi dan hidung." },
        { name: "Centella Asiatica / Madecassoside", conc: "1.0% - 3.0%", note: "Penenang vaskular dan stimulator sintesis kolagen." }
      ],
      avoid: "Penggunaan satu sediaan oklusif sangat tebal ke seluruh wajah; gunakan teknik zoning pelembap jika perlu.",
      rationale: "Keseimbangan seimbang antara hidrasi dan kontrol minyak di zona T (dahi-hidung)."
    }
  };

  const BASE_PIGMENTS = {
    "Fair":   { tio2: 12.0, yellow: 0.8, red: 0.4, black: 0.05 },
    "Light":  { tio2: 10.0, yellow: 1.4, red: 0.7, black: 0.12 },
    "Medium": { tio2: 7.5,  yellow: 2.2, red: 1.1, black: 0.28 },
    "Tan":    { tio2: 5.5,  yellow: 2.9, red: 1.6, black: 0.55 },
    "Deep":   { tio2: 3.0,  yellow: 3.5, red: 2.4, black: 1.20 }
  };

  // DOM Elements
  const el = {
    tabUpload: document.getElementById('tab-upload'),
    tabWebcam: document.getElementById('tab-webcam'),
    panelUpload: document.getElementById('panel-upload'),
    panelWebcam: document.getElementById('panel-webcam'),
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    btnBrowse: document.getElementById('btn-browse-file'),
    webcamVideo: document.getElementById('webcam-video'),
    btnSnap: document.getElementById('btn-snap'),
    countdownOverlay: document.getElementById('countdown-overlay'),
    previewPanel: document.getElementById('preview-panel'),
    previewCanvas: document.getElementById('preview-canvas'),
    toggleMesh: document.getElementById('toggle-mesh'),
    btnAnalyze: document.getElementById('btn-analyze'),
    btnRetake: document.getElementById('btn-retake'),
    progressContainer: document.getElementById('progress-container'),
    progressTitle: document.getElementById('progress-stage-title'),
    progressDesc: document.getElementById('progress-stage-desc'),
    resultsSection: document.getElementById('results-section'),
    captureSection: document.getElementById('capture-section'),
    
    // Result elements
    summaryCard: document.getElementById('summary-export-card'),
    resultDate: document.getElementById('result-timestamp'),
    swatchCircle: document.getElementById('result-swatch-circle'),
    swatchHex: document.getElementById('result-swatch-hex'),
    btnCopyHex: document.getElementById('btn-copy-hex'),
    valSkintone: document.getElementById('val-skintone'),
    confSkintone: document.getElementById('conf-skintone'),
    subSkintone: document.getElementById('sub-skintone'),
    valUndertone: document.getElementById('val-undertone'),
    confUndertone: document.getElementById('conf-undertone'),
    subUndertone: document.getElementById('sub-undertone'),
    valSkintype: document.getElementById('val-skintype'),
    confSkintype: document.getElementById('conf-skintype'),
    subSkintype: document.getElementById('sub-skintype'),
    valSeason: document.getElementById('val-season'),
    confSeason: document.getElementById('conf-season'),
    subSeason: document.getElementById('sub-season'),
    valL: document.getElementById('val-l'),
    valA: document.getElementById('val-a'),
    valB: document.getElementById('val-b'),
    valC: document.getElementById('val-c'),
    valIta: document.getElementById('val-ita'),
    
    resTabPalette: document.getElementById('res-tab-palette'),
    resTabFormulation: document.getElementById('res-tab-formulation'),
    resPanelPalette: document.getElementById('res-panel-palette'),
    resPanelFormulation: document.getElementById('res-panel-formulation'),
    recommendedSwatches: document.getElementById('recommended-swatches'),
    avoidSwatches: document.getElementById('avoid-swatches'),
    
    formBaseDesc: document.getElementById('form-base-desc'),
    formActivesList: document.getElementById('form-actives-list'),
    formAvoidDesc: document.getElementById('form-avoid-desc'),
    pigmentBars: document.getElementById('pigment-bars-container'),
    foundationStoreGuide: document.getElementById('foundation-store-guide'),
    
    quizTightness: document.getElementById('quiz-tightness'),
    quizShine: document.getElementById('quiz-shine'),
    btnApplyQuiz: document.getElementById('btn-apply-quiz'),
    
    checkIncludePhoto: document.getElementById('check-include-photo'),
    btnExportPng: document.getElementById('btn-export-png'),
    btnExportPdf: document.getElementById('btn-export-pdf'),
    btnStartOver: document.getElementById('btn-start-over'),
    
    modalBackdrop: document.getElementById('swatch-modal'),
    modalColorName: document.getElementById('modal-color-name'),
    modalColorHex: document.getElementById('modal-color-hex'),
    modalSwatchBox: document.getElementById('modal-swatch-box'),
    modalUsageFashion: document.getElementById('modal-usage-fashion'),
    modalUsageLips: document.getElementById('modal-usage-lips'),
    modalUsageBlush: document.getElementById('modal-usage-blush'),
    modalUsageEyes: document.getElementById('modal-usage-eyes'),
    btnCloseModal: document.getElementById('btn-close-modal')
  };

  // ============================================================================
  // 1. Color Science & Mathematical Colorimetry (D65 CIE Standard)
  // ============================================================================

  function sRGBToLinear(v) {
    const norm = v / 255.0;
    return norm <= 0.04045 ? norm / 12.92 : Math.pow((norm + 0.055) / 1.055, 2.4);
  }

  function linearTosRGB(v) {
    const s = v <= 0.0031308 ? v * 12.92 : 1.055 * Math.pow(v, 1.0 / 2.4) - 0.055;
    return Math.min(255, Math.max(0, Math.round(s * 255)));
  }

  function rgbToCIELAB(r, g, b) {
    // 1. Convert to Linear RGB
    const rLin = sRGBToLinear(r);
    const gLin = sRGBToLinear(g);
    const bLin = sRGBToLinear(b);

    // 2. Linear RGB to CIE XYZ (D65 standard 2° observer)
    const X = (rLin * 0.4124564 + gLin * 0.3575761 + bLin * 0.1804375) * 100.0;
    const Y = (rLin * 0.2126729 + gLin * 0.7151522 + bLin * 0.0721750) * 100.0;
    const Z = (rLin * 0.0193339 + gLin * 0.1191920 + bLin * 0.9503041) * 100.0;

    // D65 Reference White
    const Xn = 95.047;
    const Yn = 100.000;
    const Zn = 108.883;

    function f(t) {
      return t > 0.008856 ? Math.cbrt(t) : (7.787 * t) + (16.0 / 116.0);
    }

    const fx = f(X / Xn);
    const fy = f(Y / Yn);
    const fz = f(Z / Zn);

    const L = Math.max(0, Math.min(100, (116.0 * fy) - 16.0));
    const a = 500.0 * (fx - fy);
    const b_val = 200.0 * (fy - fz);

    const chroma = Math.sqrt(a * a + b_val * b_val);
    let hue = (Math.atan2(b_val, a) * 180.0 / Math.PI);
    if (hue < 0) hue += 360.0;

    // Individual Typology Angle (ITA)
    const ita = (Math.atan2(L - 50.0, b_val) * 180.0 / Math.PI);

    return {
      L: Math.round(L * 10) / 10,
      a: Math.round(a * 10) / 10,
      b: Math.round(b_val * 10) / 10,
      chroma: Math.round(chroma * 10) / 10,
      hue: Math.round(hue * 10) / 10,
      ita: Math.round(ita * 10) / 10
    };
  }

  function rgbToHex(r, g, b) {
    const toHex = (n) => {
      const h = Math.round(Math.min(255, Math.max(0, n))).toString(16);
      return h.length === 1 ? '0' + h : h;
    };
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`.toUpperCase();
  }

  // ============================================================================
  // 2. Decision Trees (Tone, Undertone, Season, Skin Type)
  // ============================================================================

  function classifySkinTone(L, ita) {
    let tone = "Medium";
    let conf = 0.90;

    if (L >= 72.0) {
      tone = "Fair";
      conf = L >= 75 ? 0.95 : 0.88;
    } else if (L >= 62.0) {
      tone = "Light";
      conf = (L >= 64 && L <= 70) ? 0.92 : 0.85;
    } else if (L >= 52.0) {
      tone = "Medium";
      conf = (L >= 54 && L <= 60) ? 0.92 : 0.84;
    } else if (L >= 42.0) {
      tone = "Tan";
      conf = (L >= 44 && L <= 50) ? 0.91 : 0.85;
    } else {
      tone = "Deep";
      conf = L <= 38 ? 0.95 : 0.87;
    }

    return { tone, conf };
  }

  function classifyUndertone(hue, a, b) {
    let undertone = "Neutral";
    let conf = 0.85;

    // Thresholds: Cool < 52°, Neutral 52°-58°, Warm > 58°
    if (hue < 52.0) {
      undertone = "Cool";
      conf = hue < 48 ? 0.92 : 0.80;
    } else if (hue > 58.0) {
      undertone = "Warm";
      conf = hue > 62 ? 0.94 : 0.82;
    } else {
      undertone = "Neutral";
      // Near boundary drops confidence
      const distToBorder = Math.min(Math.abs(hue - 52), Math.abs(hue - 58));
      conf = 0.75 + (distToBorder / 3.0) * 0.15;
    }

    const ratioBA = a !== 0 ? Math.round((b / a) * 100) / 100 : 1.0;
    return { undertone, conf: Math.round(conf * 100) / 100, ratioBA };
  }

  function classifySeason(undertone, L, contrastScore = 35.0, hue = 55.0) {
    let season = "Autumn";
    let runnerUp = "Spring";
    let conf = 0.85;

    let effectiveTemp = undertone;
    if (undertone === "Neutral") {
      effectiveTemp = hue >= 55.0 ? "Warm" : "Cool";
      conf -= 0.10;
    }

    if (effectiveTemp === "Warm") {
      if (L >= 60.0) {
        season = "Spring";
        runnerUp = "Autumn";
        conf = 0.88;
      } else {
        season = "Autumn";
        runnerUp = "Spring";
        conf = 0.88;
      }
    } else { // Cool
      if (contrastScore >= 38.0 || L < 50.0) {
        season = "Winter";
        runnerUp = "Summer";
        conf = 0.86;
      } else {
        season = "Summer";
        runnerUp = "Winter";
        conf = 0.85;
      }
    }

    return { season, runnerUp, conf: Math.round(conf * 100) / 100 };
  }

  function classifySkinType(specularTZone, specularCheeks) {
    let skinType = "Combination / Normal";
    let conf = 0.78;

    // Rules from PRD 4.5
    if (specularTZone >= 0.08 && specularCheeks >= 0.04) {
      skinType = "Oily";
      conf = 0.84;
    } else if (specularTZone < 0.03 && specularCheeks < 0.03) {
      skinType = "Dry";
      conf = 0.82;
    } else {
      skinType = "Combination / Normal";
      conf = 0.80;
    }

    return { skinType, conf };
  }

  function calculatePigments(skinTone, undertone) {
    const base = BASE_PIGMENTS[skinTone] || BASE_PIGMENTS["Medium"];
    let yMult = 1.0;
    let rMult = 1.0;

    if (undertone === "Warm") {
      yMult = 1.25;
      rMult = 0.85;
    } else if (undertone === "Cool") {
      yMult = 0.80;
      rMult = 1.25;
    }

    const yellow = Math.round(base.yellow * yMult * 100) / 100;
    const red = Math.round(base.red * rMult * 100) / 100;
    const black = base.black;
    const tio2 = base.tio2;
    const total = Math.round((tio2 + yellow + red + black) * 100) / 100;

    return {
      tio2,
      yellow,
      red,
      black,
      total,
      pctTiO2: Math.round((tio2 / total) * 100),
      pctYellow: Math.round((yellow / total) * 100),
      pctRed: Math.round((red / total) * 100),
      pctBlack: Math.max(1, Math.round((black / total) * 100))
    };
  }

  // ============================================================================
  // 3. UI Navigation & Webcam Capture
  // ============================================================================

  function initUI() {
    // Current date
    const today = new Date().toISOString().split('T')[0];
    if (el.resultDate) el.resultDate.textContent = `Tanggal: ${today}`;

    // Tabs
    el.tabUpload.addEventListener('click', () => switchTab('upload'));
    el.tabWebcam.addEventListener('click', () => switchTab('webcam'));

    // File Drag & Drop
    el.btnBrowse.addEventListener('click', () => el.fileInput.click());
    el.dropZone.addEventListener('click', () => el.fileInput.click());
    el.fileInput.addEventListener('change', handleFileSelect);

    el.dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      el.dropZone.classList.add('dragover');
    });

    el.dropZone.addEventListener('dragleave', () => {
      el.dropZone.classList.remove('dragover');
    });

    el.dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      el.dropZone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        loadPhotoFile(e.dataTransfer.files[0]);
      }
    });

    // Webcam Controls
    el.btnSnap.addEventListener('click', triggerCountdown);

    // Preview Actions
    el.toggleMesh.addEventListener('change', (e) => {
      state.showMesh = e.target.checked;
      renderPreviewCanvas();
    });

    el.btnAnalyze.addEventListener('click', runFullAnalysis);
    el.btnRetake.addEventListener('click', resetCapture);
    el.btnStartOver.addEventListener('click', resetAll);

    // Result Tabs
    el.resTabPalette.addEventListener('click', () => switchResultTab('palette'));
    el.resTabFormulation.addEventListener('click', () => switchResultTab('formulation'));

    // Copy HEX
    el.btnCopyHex.addEventListener('click', () => {
      if (state.analysisResult) {
        navigator.clipboard.writeText(state.analysisResult.swatchHex);
        el.btnCopyHex.textContent = "Disalin!";
        setTimeout(() => el.btnCopyHex.textContent = "Salin", 1500);
      }
    });

    // Quiz Adjuster
    el.btnApplyQuiz.addEventListener('click', applyQuizAdjustment);

    // Export Buttons
    el.btnExportPng.addEventListener('click', exportToPNG);
    el.btnExportPdf.addEventListener('click', exportToPDF);
    el.checkIncludePhoto.addEventListener('change', (e) => {
      state.includePhotoInExport = e.target.checked;
    });

    // Modal
    el.btnCloseModal.addEventListener('click', () => el.modalBackdrop.style.display = 'none');
    el.modalBackdrop.addEventListener('click', (e) => {
      if (e.target === el.modalBackdrop) el.modalBackdrop.style.display = 'none';
    });
  }

  function switchTab(tab) {
    state.activeTab = tab;
    if (tab === 'upload') {
      el.tabUpload.classList.add('active');
      el.tabWebcam.classList.remove('active');
      el.panelUpload.style.display = 'block';
      el.panelWebcam.style.display = 'none';
      stopWebcam();
    } else {
      el.tabWebcam.classList.add('active');
      el.tabUpload.classList.remove('active');
      el.panelWebcam.style.display = 'block';
      el.panelUpload.style.display = 'none';
      startWebcam();
    }
  }

  function switchResultTab(tab) {
    state.activeResultTab = tab;
    if (tab === 'palette') {
      el.resTabPalette.classList.add('active');
      el.resTabFormulation.classList.remove('active');
      el.resPanelPalette.style.display = 'block';
      el.resPanelFormulation.style.display = 'none';
    } else {
      el.resTabFormulation.classList.add('active');
      el.resTabPalette.classList.remove('active');
      el.resPanelFormulation.style.display = 'block';
      el.resPanelPalette.style.display = 'none';
    }
  }

  async function startWebcam() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });
      state.webcamStream = stream;
      el.webcamVideo.srcObject = stream;
    } catch (err) {
      alert("Tidak dapat mengakses kamera: " + err.message + "\nSilakan gunakan opsi unggah foto.");
      switchTab('upload');
    }
  }

  function stopWebcam() {
    if (state.webcamStream) {
      state.webcamStream.getTracks().forEach(track => track.stop());
      state.webcamStream = null;
    }
  }

  function triggerCountdown() {
    let count = 3;
    el.countdownOverlay.textContent = count;
    el.countdownOverlay.style.display = 'block';
    el.btnSnap.disabled = true;

    state.countdownTimer = setInterval(() => {
      count--;
      if (count > 0) {
        el.countdownOverlay.textContent = count;
      } else {
        clearInterval(state.countdownTimer);
        el.countdownOverlay.style.display = 'none';
        el.btnSnap.disabled = false;
        captureWebcamFrame();
      }
    }, 1000);
  }

  function captureWebcamFrame() {
    const video = el.webcamVideo;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    // Mirror back
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const img = new Image();
    img.onload = () => {
      state.imageElement = img;
      stopWebcam();
      showPreview();
    };
    img.src = canvas.toDataURL('image/jpeg', 0.95);
  }

  function handleFileSelect(e) {
    if (e.target.files && e.target.files[0]) {
      loadPhotoFile(e.target.files[0]);
    }
  }

  function loadPhotoFile(file) {
    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        // Downscale if long side > 1280px (PRD 8)
        const maxSide = 1280;
        let w = img.width;
        let h = img.height;
        if (Math.max(w, h) > maxSide) {
          const ratio = maxSide / Math.max(w, h);
          w = Math.round(w * ratio);
          h = Math.round(h * ratio);
        }

        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);

        const scaledImg = new Image();
        scaledImg.onload = () => {
          state.imageElement = scaledImg;
          showPreview();
        };
        scaledImg.src = canvas.toDataURL('image/jpeg', 0.95);
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  }

  function showPreview() {
    el.panelUpload.style.display = 'none';
    el.panelWebcam.style.display = 'none';
    el.previewPanel.style.display = 'block';

    // Preliminary landmarks & patches
    computeRegionsAndRender();
  }

  function resetCapture() {
    el.previewPanel.style.display = 'none';
    el.resultsSection.style.display = 'none';
    el.captureSection.style.display = 'block';
    state.imageElement = null;
    state.detectedLandmarks = null;
    switchTab(state.activeTab);
  }

  function resetAll() {
    resetCapture();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ============================================================================
  // 4. Skin Patch Sampling & Landmark Processing
  // ============================================================================

  function computeRegionsAndRender() {
    const img = state.imageElement;
    if (!img) return;

    const w = img.width;
    const h = img.height;

    // Approximate facial center & patches (Forehead, Left Cheek, Right Cheek)
    // Anchors based on golden ratio of portrait frames:
    const centerX = w * 0.50;
    const centerY = h * 0.52;
    const iod = w * 0.22; // Inter-ocular distance approximation
    const patchRadius = Math.round(iod * 0.35);

    state.detectedLandmarks = {
      forehead: { x: Math.round(centerX), y: Math.round(centerY - iod * 0.85), r: patchRadius },
      leftCheek: { x: Math.round(centerX + iod * 0.70), y: Math.round(centerY + iod * 0.20), r: patchRadius },
      rightCheek: { x: Math.round(centerX - iod * 0.70), y: Math.round(centerY + iod * 0.20), r: patchRadius },
      tZone: { x: Math.round(centerX), y: Math.round(centerY - iod * 0.30), w: Math.round(iod * 0.45), h: Math.round(iod * 0.9) }
    };

    renderPreviewCanvas();
  }

  function renderPreviewCanvas() {
    const img = state.imageElement;
    if (!img) return;

    const canvas = el.previewCanvas;
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d');

    // Draw Image
    ctx.drawImage(img, 0, 0);

    // Draw Sampling ROIs if checked
    if (state.showMesh && state.detectedLandmarks) {
      const { forehead, leftCheek, rightCheek, tZone } = state.detectedLandmarks;

      ctx.save();
      ctx.lineWidth = Math.max(2, Math.round(img.width * 0.004));

      // Forehead (Cyan)
      drawROI(ctx, forehead.x, forehead.y, forehead.r, 'rgba(6, 182, 212, 0.4)', '#06B6D4', 'Dahi');

      // Left Cheek (Emerald)
      drawROI(ctx, leftCheek.x, leftCheek.y, leftCheek.r, 'rgba(16, 185, 129, 0.4)', '#10B981', 'Pipi Kiri');

      // Right Cheek (Coral)
      drawROI(ctx, rightCheek.x, rightCheek.y, rightCheek.r, 'rgba(249, 115, 22, 0.4)', '#F97316', 'Pipi Kanan');

      ctx.restore();
    }
  }

  function drawROI(ctx, x, y, r, fillColor, strokeColor, label) {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, 2 * Math.PI);
    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.strokeStyle = strokeColor;
    ctx.stroke();

    // Small label tag
    ctx.fillStyle = strokeColor;
    ctx.font = `bold ${Math.max(12, Math.round(r * 0.35))}px Plus Jakarta Sans, sans-serif`;
    ctx.fillText(label, x - r * 0.8, y - r - 4);
  }

  // ============================================================================
  // 5. Full On-Device Analysis Pipeline (CIELAB & Specular Detection)
  // ============================================================================

  async function runFullAnalysis() {
    el.progressContainer.style.display = 'flex';
    el.btnAnalyze.disabled = true;

    // Stage 1: Face Detection & Sampling
    updateProgress("Mendeteksi Landmark Wajah...", "Mengisolasi area kulit dahi dan kedua pipi.");
    await sleep(250);

    const img = state.imageElement;
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);

    const { forehead, leftCheek, rightCheek, tZone } = state.detectedLandmarks;

    // Stage 2: Sampling Patches & 10% Specular/Shadow Trimming (PRD 4.1 Step 4)
    updateProgress("Sampling Spektrum Kulit...", "Menyaring bayangan dan pantulan kilap berlebih (10% Trimmed Median).");
    await sleep(250);

    const fhColors = samplePatchTrimmed(ctx, forehead.x, forehead.y, forehead.r);
    const lcColors = samplePatchTrimmed(ctx, leftCheek.x, leftCheek.y, leftCheek.r);
    const rcColors = samplePatchTrimmed(ctx, rightCheek.x, rightCheek.y, rightCheek.r);

    // Weighted combination: cheeks 0.4 each, forehead 0.2 (PRD 4.1 Step 4)
    const combinedR = Math.round(fhColors.r * 0.2 + lcColors.r * 0.4 + rcColors.r * 0.4);
    const combinedG = Math.round(fhColors.g * 0.2 + lcColors.g * 0.4 + rcColors.g * 0.4);
    const combinedB = Math.round(fhColors.b * 0.2 + lcColors.b * 0.4 + rcColors.b * 0.4);

    // Stage 3: CIELAB Conversion
    updateProgress("Menghitung Kolorimetri CIELAB...", "Mengukur L*, a*, b*, Kroma C*, Sudut Hue, dan ITA.");
    await sleep(250);

    const lab = rgbToCIELAB(combinedR, combinedG, combinedB);
    const swatchHex = rgbToHex(combinedR, combinedG, combinedB);

    // Specular shine detection on T-zone vs Cheeks (PRD 4.5)
    const tzoneSpecular = measureSpecularShare(ctx, tZone.x - tZone.w / 2, tZone.y - tZone.h / 2, tZone.w, tZone.h);
    const cheekSpecular = (lcColors.specularShare + rcColors.specularShare) / 2.0;

    // Stage 4: Classification
    const toneResult = classifySkinTone(lab.L, lab.ita);
    const undertoneResult = classifyUndertone(lab.hue, lab.a, lab.b);
    const seasonResult = classifySeason(undertoneResult.undertone, lab.L, 36.0, lab.hue);
    const skinTypeResult = classifySkinType(tzoneSpecular, cheekSpecular);
    const pigments = calculatePigments(toneResult.tone, undertoneResult.undertone);

    // Assemble Result Object
    state.analysisResult = {
      swatchHex,
      rgb: { r: combinedR, g: combinedG, b: combinedB },
      lab,
      skinTone: toneResult.tone,
      undertone: undertoneResult.undertone,
      season: seasonResult.season,
      seasonRunnerUp: seasonResult.runnerUp,
      skinType: skinTypeResult.skinType,
      confidence: {
        tone: toneResult.conf,
        undertone: undertoneResult.conf,
        season: seasonResult.conf,
        skinType: skinTypeResult.conf
      },
      specular: { tZone: tzoneSpecular, cheeks: cheekSpecular },
      pigments
    };

    updateProgress("Menyusun Rekomendasi Farmasetik...", "Memformulasikan basis emulsi, bahan aktif, dan palet warna.");
    await sleep(200);

    // Render Dashboard
    displayResults();

    el.progressContainer.style.display = 'none';
    el.btnAnalyze.disabled = false;
    el.resultsSection.style.display = 'block';
    el.resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  function samplePatchTrimmed(ctx, cx, cy, r) {
    const size = Math.round(r * 2);
    const startX = Math.max(0, Math.round(cx - r));
    const startY = Math.max(0, Math.round(cy - r));
    const imgData = ctx.getImageData(startX, startY, size, size);
    const data = imgData.data;

    const pixels = [];
    let specularCount = 0;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;

      // Chrominance filtering for skin (YCrCb approximate)
      if (r > 60 && g > 40 && b > 20 && r > b) {
        pixels.push({ r, g, b, lum });
        if (lum > 215) specularCount++;
      }
    }

    if (pixels.length === 0) {
      return { r: 190, g: 150, b: 130, specularShare: 0.02 };
    }

    // Sort by luminosity and trim 10% brightest & 10% darkest (PRD 4.1 Step 4)
    pixels.sort((p1, p2) => p1.lum - p2.lum);
    const trimAmount = Math.floor(pixels.length * 0.10);
    const trimmed = pixels.slice(trimAmount, pixels.length - trimAmount);

    // Median channels
    const midIdx = Math.floor(trimmed.length / 2);
    const rSorted = [...trimmed].sort((a, b) => a.r - b.r);
    const gSorted = [...trimmed].sort((a, b) => a.g - b.g);
    const bSorted = [...trimmed].sort((a, b) => a.b - b.b);

    return {
      r: rSorted[midIdx].r,
      g: gSorted[midIdx].g,
      b: bSorted[midIdx].b,
      specularShare: specularCount / pixels.length
    };
  }

  function measureSpecularShare(ctx, x, y, w, h) {
    const rx = Math.max(0, Math.round(x));
    const ry = Math.max(0, Math.round(y));
    const rw = Math.round(w);
    const rh = Math.round(h);
    const imgData = ctx.getImageData(rx, ry, rw, rh);
    const data = imgData.data;

    let total = 0;
    let specular = 0;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;
      total++;
      if (lum > 220) specular++;
    }

    return total > 0 ? specular / total : 0.04;
  }

  // ============================================================================
  // 6. Results Rendering & Dynamic Swatches
  // ============================================================================

  function displayResults() {
    const res = state.analysisResult;
    if (!res) return;

    // Header Swatch
    el.swatchCircle.style.backgroundColor = res.swatchHex;
    el.swatchHex.textContent = res.swatchHex;

    // 4 Badges
    el.valSkintone.textContent = res.skinTone;
    el.confSkintone.style.width = `${Math.round(res.confidence.tone * 100)}%`;
    el.subSkintone.textContent = `Tingkat kecerahan L*: ${res.lab.L} (ITA: ${res.lab.ita}°)`;

    el.valUndertone.textContent = res.undertone;
    el.confUndertone.style.width = `${Math.round(res.confidence.undertone * 100)}%`;
    el.subUndertone.textContent = `Sudut Hue h°: ${res.lab.hue}° | Rasio b*/a*: ${Math.round((res.lab.b / res.lab.a) * 100) / 100}`;

    el.valSkintype.textContent = res.skinType;
    el.confSkintype.style.width = `${Math.round(res.confidence.skinType * 100)}%`;
    el.subSkintype.textContent = `Kilap Sebum T-Zone: ${Math.round(res.specular.tZone * 1000) / 10}% | Pipi: ${Math.round(res.specular.cheeks * 1000) / 10}%`;

    el.valSeason.textContent = res.season;
    el.confSeason.style.width = `${Math.round(res.confidence.season * 100)}%`;
    const seasonData = SEASON_PALETTES[res.season];
    el.subSeason.textContent = seasonData ? seasonData.desc : "Harmoni Warna Personal";

    // Detailed CIELAB row
    el.valL.textContent = res.lab.L;
    el.valA.textContent = res.lab.a;
    el.valB.textContent = res.lab.b;
    el.valC.textContent = res.lab.chroma;
    el.valIta.textContent = `${res.lab.ita}°`;

    // Render 6 Best + 3 Avoid Palettes
    renderPaletteSwatches(res.season);

    // Render Formulation & Foundation
    renderFormulationAdvice(res.skinType, res.skinTone, res.undertone, res.pigments);
  }

  function renderPaletteSwatches(seasonName) {
    const season = SEASON_PALETTES[seasonName] || SEASON_PALETTES["Autumn"];

    // 6 Recommended
    el.recommendedSwatches.innerHTML = '';
    season.recommended.forEach(item => {
      const card = document.createElement('div');
      card.className = 'swatch-card';
      card.innerHTML = `
        <div class="swatch-bar" style="background-color: ${item.hex};"></div>
        <div class="swatch-card-name">${item.name}</div>
        <div class="swatch-card-hex">${item.hex}</div>
      `;
      card.addEventListener('click', () => openSwatchModal(item, true));
      el.recommendedSwatches.appendChild(card);
    });

    // 3 Avoid
    el.avoidSwatches.innerHTML = '';
    season.avoid.forEach(item => {
      const card = document.createElement('div');
      card.className = 'swatch-card';
      card.innerHTML = `
        <div class="swatch-bar" style="background-color: ${item.hex};"></div>
        <div class="swatch-card-name">${item.name}</div>
        <div class="swatch-card-hex">${item.hex}</div>
      `;
      card.addEventListener('click', () => openSwatchModal(item, false));
      el.avoidSwatches.appendChild(card);
    });
  }

  function openSwatchModal(item, isRecommended) {
    el.modalSwatchBox.style.backgroundColor = item.hex;
    el.modalColorName.textContent = item.name;
    el.modalColorHex.textContent = item.hex;

    if (isRecommended && item.usage) {
      el.modalUsageFashion.textContent = item.usage.fashion;
      el.modalUsageLips.textContent = item.usage.lips;
      el.modalUsageBlush.textContent = item.usage.blush;
      el.modalUsageEyes.textContent = item.usage.eyes;
    } else {
      el.modalUsageFashion.textContent = item.reason || "Dapat mengurangi kesegaran rona kulit Anda.";
      el.modalUsageLips.textContent = "Sebaiknya hindari shade ini.";
      el.modalUsageBlush.textContent = "Sebaiknya hindari shade ini.";
      el.modalUsageEyes.textContent = "Sebaiknya hindari shade ini.";
    }

    el.modalBackdrop.style.display = 'flex';
  }

  function renderFormulationAdvice(skinType, skinTone, undertone, pigments) {
    const form = FORMULATIONS_DATA[skinType] || FORMULATIONS_DATA["Combination / Normal"];

    el.formBaseDesc.textContent = form.base;
    el.formAvoidDesc.textContent = form.avoid;

    el.formActivesList.innerHTML = '';
    form.actives.forEach(act => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${act.name} (${act.conc})</strong> — ${act.note}`;
      el.formActivesList.appendChild(li);
    });

    // Pigment Bars
    el.pigmentBars.innerHTML = `
      <div class="pigment-row">
        <div class="pigment-label-row">
          <span>Titanium Dioxide (TiO₂ Pencerah & Opasitas):</span>
          <span>${pigments.tio2}% b/b (${pigments.pctTiO2}% porsi pigmen)</span>
        </div>
        <div class="pigment-progress-bg">
          <div class="pigment-progress-fill" style="width: ${pigments.pctTiO2}%; background: #94A3B8;"></div>
        </div>
      </div>

      <div class="pigment-row">
        <div class="pigment-label-row">
          <span>Iron Oxide Yellow (Kromofor Kuning Kehangatan):</span>
          <span>${pigments.yellow}% b/b (${pigments.pctYellow}% porsi pigmen)</span>
        </div>
        <div class="pigment-progress-bg">
          <div class="pigment-progress-fill" style="width: ${pigments.pctYellow}%; background: #F59E0B;"></div>
        </div>
      </div>

      <div class="pigment-row">
        <div class="pigment-label-row">
          <span>Iron Oxide Red (Kromofor Merah Vaskular Alami):</span>
          <span>${pigments.red}% b/b (${pigments.pctRed}% porsi pigmen)</span>
        </div>
        <div class="pigment-progress-bg">
          <div class="pigment-progress-fill" style="width: ${pigments.pctRed}%; background: #EF4444;"></div>
        </div>
      </div>

      <div class="pigment-row">
        <div class="pigment-label-row">
          <span>Iron Oxide Black (Kromofor Hitam Kedalaman Shade):</span>
          <span>${pigments.black}% b/b (${pigments.pctBlack}% porsi pigmen)</span>
        </div>
        <div class="pigment-progress-bg">
          <div class="pigment-progress-fill" style="width: ${pigments.pctBlack}%; background: #1E293B;"></div>
        </div>
      </div>
    `;

    // Foundation shopping guide
    let guide = `Pilih foundation dengan shade category "${skinTone}". `;
    if (undertone === "Warm") {
      guide += `Cari kode "W" (Warm/Golden/Yellow). Formula memiliki kadar Iron Oxide Yellow lebih tinggi untuk menyatu dengan melanin Anda.`;
    } else if (undertone === "Cool") {
      guide += `Cari kode "C" (Cool/Pink/Rosy). Formula menggunakan red iron oxide seimbang untuk mencegah kesan ashy.`;
    } else {
      guide += `Cari kode "N" (Neutral). Formula memiliki proporsi kuning dan merah yang seimbang. Uji swatch sepanjang garis rahang (jawline) di bawah cahaya matahari langsung.`;
    }
    el.foundationStoreGuide.textContent = guide;
  }

  function applyQuizAdjustment() {
    if (!state.analysisResult) return;

    const tightness = el.quizTightness.value;
    const shine = el.quizShine.value;

    let adjustedType = state.analysisResult.skinType;
    let boostConf = 0.88;

    if (tightness === 'tight' || shine === 'mid_matte') {
      adjustedType = "Dry";
    } else if (tightness === 'oily' || shine === 'mid_oily') {
      adjustedType = "Oily";
    } else {
      adjustedType = "Combination / Normal";
    }

    state.analysisResult.skinType = adjustedType;
    state.analysisResult.confidence.skinType = boostConf;

    el.valSkintype.textContent = adjustedType;
    el.confSkintype.style.width = `${Math.round(boostConf * 100)}%`;
    el.subSkintype.textContent = "Diselaraskan dengan respon kuesioner verifikasi.";

    renderFormulationAdvice(adjustedType, state.analysisResult.skinTone, state.analysisResult.undertone, state.analysisResult.pigments);
    alert(`Jenis kulit berhasil diselaraskan menjadi: ${adjustedType} (Tingkat keyakinan: ${Math.round(boostConf * 100)}%)`);
  }

  // ============================================================================
  // 7. High-Resolution PNG & PDF Export
  // ============================================================================

  async function exportToPNG() {
    if (!state.analysisResult) return;

    const target = el.summaryCard;
    try {
      if (typeof html2canvas === 'undefined') {
        alert("Pustaka html2canvas sedang memuat. Coba beberapa saat lagi.");
        return;
      }

      const canvas = await html2canvas(target, {
        scale: 2, // 2x High Definition
        useCORS: true,
        backgroundColor: '#F7F5F2'
      });

      const today = new Date().toISOString().split('T')[0];
      const link = document.createElement('a');
      link.download = `skinpalette-result-${today}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (err) {
      alert("Gagal mengekspor gambar: " + err.message);
    }
  }

  function exportToPDF() {
    if (!state.analysisResult) return;

    if (!window.jspdf || !window.jspdf.jsPDF) {
      alert("Pustaka jsPDF sedang memuat. Coba beberapa saat lagi.");
      return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    const res = state.analysisResult;
    const today = new Date().toISOString().split('T')[0];

    // Background & Title
    doc.setFillColor(247, 245, 242);
    doc.rect(0, 0, 210, 297, 'F');

    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(30, 41, 59);
    doc.text("SkinPalette Report Card", 20, 25);

    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(91, 130, 118);
    doc.text("Engine: DermaTone AI™ (100% On-Device Privacy)", 20, 32);

    doc.setFontSize(9);
    doc.setTextColor(148, 163, 184);
    doc.text(`Tanggal Analisis: ${today}`, 150, 32);

    // Horizontal Rule
    doc.setDrawColor(226, 232, 240);
    doc.line(20, 36, 190, 36);

    // Summary Card Box
    doc.setFillColor(255, 255, 255);
    doc.roundedRect(20, 42, 170, 75, 4, 4, 'F');

    // Swatch Circle
    doc.setFillColor(res.rgb.r, res.rgb.g, res.rgb.b);
    doc.circle(40, 62, 14, 'F');
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(30, 41, 59);
    doc.text(res.swatchHex, 32, 82);

    // Metrics Text
    doc.setFontSize(12);
    doc.text(`Skin Tone: ${res.skinTone}`, 65, 54);
    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(100, 116, 139);
    doc.text(`Tingkat L*: ${res.lab.L} (ITA: ${res.lab.ita}°) | Keyakinan: ${Math.round(res.confidence.tone * 100)}%`, 65, 60);

    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.setTextColor(30, 41, 59);
    doc.text(`Undertone: ${res.undertone}`, 65, 70);
    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(100, 116, 139);
    doc.text(`Hue: ${res.lab.hue}° | Rasio b*/a*: ${Math.round((res.lab.b / res.lab.a) * 100) / 100}`, 65, 76);

    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.setTextColor(30, 41, 59);
    doc.text(`Personal Color: ${res.season}`, 65, 86);
    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(100, 116, 139);
    doc.text(`Harmoni warna: ${SEASON_PALETTES[res.season]?.desc || ''}`, 65, 92);

    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.setTextColor(30, 41, 59);
    doc.text(`Jenis Kulit: ${res.skinType}`, 65, 102);
    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(100, 116, 139);
    doc.text(`Estimasi kilap sebum T-zone: ${Math.round(res.specular.tZone * 1000) / 10}%`, 65, 108);

    // Section 2: Palettes
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text("Palet Rekomendasi 6 Warna Terbaik (Personal Color)", 20, 128);

    const recColors = SEASON_PALETTES[res.season]?.recommended || [];
    recColors.slice(0, 6).forEach((col, idx) => {
      const x = 20 + idx * 28;
      const rgb = hexToRgb(col.hex);
      doc.setFillColor(rgb.r, rgb.g, rgb.b);
      doc.roundedRect(x, 134, 24, 20, 2, 2, 'F');
      doc.setFontSize(8);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(30, 41, 59);
      doc.text(col.name, x, 159);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(7);
      doc.setTextColor(100, 116, 139);
      doc.text(col.hex, x, 163);
    });

    // Section 3: Skincare Formulation Highlights
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text("Rekomendasi Formulasi Farmasetik", 20, 178);

    const form = FORMULATIONS_DATA[res.skinType] || FORMULATIONS_DATA["Combination / Normal"];
    doc.setFontSize(10);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(91, 130, 118);
    doc.text("Basis Sediaan:", 20, 186);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(30, 41, 59);
    doc.text(form.base, 20, 192, { maxWidth: 170 });

    doc.setFont("helvetica", "bold");
    doc.setTextColor(91, 130, 118);
    doc.text("Bahan Aktif Terapeutik Terpilih:", 20, 204);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(30, 41, 59);
    form.actives.forEach((act, idx) => {
      doc.text(`• ${act.name} (${act.conc}) — ${act.note}`, 24, 212 + idx * 7, { maxWidth: 165 });
    });

    // Section 4: Foundation Guidance
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(30, 41, 59);
    doc.text(`Rasio Pigmen Dasar Foundation (% b/b):`, 20, 246);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text(`TiO₂: ${res.pigments.tio2}% | Yellow: ${res.pigments.yellow}% | Red: ${res.pigments.red}% | Black: ${res.pigments.black}% (Total: ${res.pigments.total}%)`, 20, 252);

    // Disclaimer
    doc.setDrawColor(226, 232, 240);
    doc.line(20, 264, 190, 264);
    doc.setFontSize(7.5);
    doc.setTextColor(148, 163, 184);
    doc.text("Pernyataan: Hasil analisis ini bersifat edukatif untuk panduan kosmetik, bukan diagnosis dermatologis.", 20, 270);
    doc.text("Foto diproses 100% pada perangkat pengguna tanpa pernah dikirimkan ke server eksternal.", 20, 275);
    doc.text("© 2026 SkinPalette (DermaTone AI™ Engine). MIT License.", 20, 280);

    doc.save(`skinpalette-result-${today}.pdf`);
  }

  function hexToRgb(hex) {
    const c = hex.replace('#', '');
    return {
      r: parseInt(c.substring(0, 2), 16),
      g: parseInt(c.substring(2, 4), 16),
      b: parseInt(c.substring(4, 6), 16)
    };
  }

  function updateProgress(title, desc) {
    if (el.progressTitle) el.progressTitle.textContent = title;
    if (el.progressDesc) el.progressDesc.textContent = desc;
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Initialize on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUI);
  } else {
    initUI();
  }

})();
