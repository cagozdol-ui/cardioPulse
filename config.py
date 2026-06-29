"""
CardioPulse - Yapılandırma dosyası
====================================
Dergi listelerini, ağırlıkları ve kategori tanımlarını burada düzenle.
Yeni dergi eklemek için ilgili listeye PubMed'deki TAM dergi adını ekle
(kısaltma değil — örn. "Circulation" değil "Circ Res" gibi PubMed TA alanına
uyan biçim; emin değilsen dergiyi PubMed'de ara, "Journal" filtresine bak).
"""

# ---------------------------------------------------------------------------
# KATEGORİ 1: GENEL KARDİYOLOJİ
# ---------------------------------------------------------------------------
GENERAL_TIER1 = [
    "Circulation",
    "European Heart Journal",
    "Journal of the American College of Cardiology",
    "Circulation Research",
    "Nature Reviews Cardiology",
    "JAMA Cardiology",
]

GENERAL_TIER2 = [
    "European Journal of Heart Failure",
    "Journal of the American Heart Association",
    "Heart",
    "International Journal of Cardiology",
    "American Heart Journal",
    "European Journal of Preventive Cardiology",
    "Cardiovascular Research",
    "JACC. Heart Failure",
]

# ---------------------------------------------------------------------------
# KATEGORİ 2: GİRİŞİMSEL / KORONER KARDİYOLOJİ
# ---------------------------------------------------------------------------
INTERVENTIONAL_TIER1 = [
    "JACC. Cardiovascular Interventions",
    "JACC. cardiovascular interventions",
    "EuroIntervention",
    "Circulation. Cardiovascular Interventions",
    "Circulation. cardiovascular interventions",
]

INTERVENTIONAL_TIER2 = [
    "Catheterization and Cardiovascular Interventions",
    "JACC. Cardiovascular Imaging",
    "Cardiovascular Revascularization Medicine",
    "American Journal of Cardiology",
    "Coronary Artery Disease",
    "International Journal of Cardiovascular Imaging",
]

CATEGORIES = {
    "genel": {
        "label": "Genel Kardiyoloji",
        "tier1": GENERAL_TIER1,
        "tier2": GENERAL_TIER2,
    },
    "girisimsel": {
        "label": "Girişimsel & Koroner",
        "tier1": INTERVENTIONAL_TIER1,
        "tier2": INTERVENTIONAL_TIER2,
    },
}

# ---------------------------------------------------------------------------
# SKORLAMA AĞIRLIKLARI
# ---------------------------------------------------------------------------
JOURNAL_WEIGHT_TIER1 = 40
JOURNAL_WEIGHT_TIER2 = 25

# Makale tipi ağırlıkları (PubMed PublicationType alanından okunur)
ARTICLE_TYPE_WEIGHTS = {
    "Practice Guideline": 35,
    "Guideline": 35,
    "Randomized Controlled Trial": 28,
    "Meta-Analysis": 22,
    "Systematic Review": 20,
    "Review": 10,
    "Multicenter Study": 6,
    "Observational Study": 6,
    "Comparative Study": 5,
    "Clinical Trial": 8,
    "Editorial": 3,
}
DEFAULT_ARTICLE_TYPE_WEIGHT = 5

# Güncellik ağırlığı: yayın tarihi bugünden kaç gün önceyse (0-7 gün penceresi)
RECENCY_MAX_WEIGHT = 15
RECENCY_WINDOW_DAYS = 7

# Tarama penceresi (gün) — her çalıştırmada son N günü tarar
LOOKBACK_DAYS = 7

# NCBI E-utilities (API key olmadan 3 istek/sn, anahtarla 10 istek/sn)
# Ücretsiz anahtar: https://www.ncbi.nlm.nih.gov/account/settings/  -> API Key Management
# NCBI E-utilities (API key olmadan 3 istek/sn, anahtarla 10 istek/sn)
# Ücretsiz anahtar: https://www.ncbi.nlm.nih.gov/account/settings/  -> API Key Management
# Yerelde test ederken ortam değişkeni olarak ayarlayabilirsin: export NCBI_API_KEY=...
# GitHub Actions'ta repo Settings > Secrets > Actions altına NCBI_API_KEY olarak eklenir.
import os as _os

NCBI_API_KEY = _os.environ.get("NCBI_API_KEY", "")
NCBI_EMAIL = "your-email@example.com"  # NCBI kayıt politikası için iletişim e-postan (isteğe bağlı ama önerilir)
