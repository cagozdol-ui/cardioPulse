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

# Bunlar genel dahiliye dergileri — sadece dergi adıyla aranırsa kardiyoloji
# dışı tüm makaleler de gelir. Bu yüzden BROAD_JOURNAL_KEYWORD_FILTER ile
# birlikte kullanılırlar (bkz. aşağıdaki BROAD_JOURNALS).
BROAD_JOURNALS_TIER1 = [
    "The New England Journal of Medicine",
    "Lancet (London, England)",
]

# Bu dergilerden sadece bu anahtar kelimelerden en az birini içeren
# makaleler alınır (PubMed [tiab] = title/abstract alanı taraması)
BROAD_JOURNAL_KEYWORD_FILTER = (
    "(cardiac[tiab] OR cardiovascular[tiab] OR coronary[tiab] OR "
    "heart[tiab] OR myocardial[tiab] OR arrhythmia[tiab] OR "
    "atrial fibrillation[tiab] OR heart failure[tiab] OR "
    "valve[tiab] OR aortic[tiab])"
)

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

# ---------------------------------------------------------------------------
# KATEGORİ 3: DERLEMELER (review-odaklı dergiler)
# ---------------------------------------------------------------------------
# Bu kategori "tier" ayrımı yapmaz — derleme/review ağırlıklı dergilerin
# tamamından makale alır, skorlama tamamen makale tipine (Review,
# Systematic Review vb.) ve güncelliğe dayanır.
REVIEW_JOURNALS = [
    "Cardiology Clinics",
    "Progress in Cardiovascular Diseases",
    "Current Problems in Cardiology",
    "Current Cardiology Reports",
    "Heart Failure Clinics",
    "Cardiac Electrophysiology Clinics",
    "Interventional Cardiology Clinics",
    "Current Opinion in Cardiology",
    "Trends in Cardiovascular Medicine",
    "Reviews in Cardiovascular Medicine",
]

CATEGORIES = {
    "genel": {
        "label": "Genel Kardiyoloji",
        "tier1": GENERAL_TIER1,
        "tier2": GENERAL_TIER2,
        "broad_tier1": BROAD_JOURNALS_TIER1,  # NEJM/Lancet gibi - anahtar kelime filtreli
    },
    "girisimsel": {
        "label": "Girişimsel & Koroner",
        "tier1": INTERVENTIONAL_TIER1,
        "tier2": INTERVENTIONAL_TIER2,
    },
    "derlemeler": {
        "label": "Derlemeler",
        "tier1": [],
        "tier2": REVIEW_JOURNALS,  # hepsi tier2 muamelesi görür, ayrım yok
        "review_only": True,  # sadece Review/Systematic Review tipi makaleler alınır
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
