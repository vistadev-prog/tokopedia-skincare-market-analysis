"""
Template konfigurasi. Salin file ini menjadi config.py, lalu isi nilai yang
kosong.
"""

from pathlib import Path

# --- Pengaturan umum (aman dipublikasikan) ---------------------------------
SEARCH_KEYWORDS = ["sunscreen", "moisturizer"]
MAX_PAGES = 5            # jumlah batch scroll per keyword
MIN_DELAY = 3            # jeda minimum antar batch (detik)
MAX_DELAY = 6            # jeda maksimum antar batch (detik)

DATA_DIR = Path("data/raw")
RAW_DATA_PATH = DATA_DIR / "raw_skincare.csv"
BROWSER_PROFILE_PATH = Path(".browser_profile")

# --- Nilai spesifik situs (KOSONGKAN di file yang di-upload) ---------------
BASE_URL = ""            # gunakan {keyword} sebagai placeholder pencarian
SEL_CARD = ""            # selector wadah kartu produk
SEL_NAME = ""            # selector nama produk
SEL_FINAL_PRICE = ""     # selector harga akhir
SEL_ORIGINAL_PRICE = ""  # selector harga asli (sebelum diskon)
SEL_SHOP_INFO = ""       # selector wadah info toko (nama + lokasi)
SEL_BADGE_IMG = ""       # selector gambar badge toko

# Pemetaan potongan teks di URL gambar badge -> label
# contoh bentuk: {"potongan_teks": "Label Badge"}
BADGE_RULES = {}

# Regex untuk mengambil ID produk dari link (ID diambil dari grup terakhir)
PRODUCT_ID_PATTERN = ""
