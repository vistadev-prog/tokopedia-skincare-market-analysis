import pandas as pd
import numpy as np
import re
import config

# ==========================================
# 1. DAFTAR MEREK SKINCARE VALID (HASIL VALIDASI)
# ==========================================
KNOWN_BRANDS = [
    "Facetology", "OMG", "Emina", "Wardah", "Glad2Glow", "Scora", "Azarine", 
    "Glowsophy", "Implora", "Hanasui", "Gloow&Be", "Skintific", "Kahf", 
    "Scarlett", "YOU", "EIEM Beauty", "Glowies Beauty", "Glow & Lovely", 
    "Kormesic", "Acnaway", "Zienvi", "Pigeon", "Purbasari", "Marina", 
    "The Originote", "Torriden", "Hada Labo", "Pipiqiu", "Feali", "Shinzui", 
    "ELFORMULA", "Glamazing", "Skin Aqua", "Amaterasun", "Suniora", "Junny", 
    "Skingenius", "SKIN1004", "Madame Gie", "Facerinna", "Guanjing", "Unitary", 
    "Carasun", "Dorskin", "NRW Shine", "Seger Snow", "Lightplus", "Cetaphil", 
    "Skin Game", "Sonik Scents", "Bioaqua", "NYYO Cosmetics", "Glow FX", 
    "Nuface", "Skin Nice"
]

# Trik Data Engineering: Urutkan dari yang TERPANJANG ke TERPENDEK
# Ini mencegah "Skin" tertangkap sebelum "Skin Aqua"
KNOWN_BRANDS_SORTED = sorted(KNOWN_BRANDS, key=len, reverse=True)

# ==========================================
# 2. FUNGSI-FUNGSI PEMBERSIHAN (CLEANING FUNCTIONS)
# ==========================================
def clean_product_name(name):
    """Menghapus karakter aneh (Mojibake) dan mempertahankan hanya huruf, angka, dan tanda baca dasar."""
    if pd.isna(name): return ""
    # Mengizinkan &, ., /, -, (, ) untuk nama brand seperti "Gloow & Be" atau "Y.O.U"
    cleaned = re.sub(r'[^\w\s\-\(\)/+&.]', '', str(name), flags=re.UNICODE)
    return re.sub(r'\s+', ' ', cleaned).strip()

def extract_brand(name):
    """Mencocokkan nama produk dengan daftar brand known (diurutkan panjang). Fallback ke kata pertama."""
    if pd.isna(name): return "Unknown"
    name_upper = str(name).upper()
    
    for brand in KNOWN_BRANDS_SORTED:
        if brand.upper() in name_upper:
            return brand 
            
    # Fallback: Ambil kata pertama, hapus karakter aneh di awal
    first_word = str(name).split()[0]
    return re.sub(r'[^\w]', '', first_word).capitalize()

def clean_price(val):
    """Mengubah string harga 'Rp96.580' menjadi float 96580.0."""
    if pd.isna(val) or str(val).strip() == '':
        return np.nan
    cleaned = str(val).replace('Rp', '').replace('.', '').replace(',', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return np.nan

def parse_sold_count(val):
    """Mengubah '100rb+ terjual' menjadi 100000.0."""
    if pd.isna(val) or str(val).strip() == '':
        return 0.0
    val_lower = str(val).lower()
    
    num_str = re.sub(r'[^\d.]', '', val_lower)
    if not num_str: return 0.0
    num = float(num_str)
    
    if 'jt' in val_lower or 'juta' in val_lower:
        return num * 1000000
    elif 'rb' in val_lower or 'ribu' in val_lower:
        return num * 1000
    else:
        return num

# ==========================================
# 3. FUNGSI UTAMA TRANSFORMASI
# ==========================================
def main():
    print("🧹 Memulai Data Transformation (Final Version)...")
    
    try:
        # Tambahkan dtype={'product_id': str} agar ID tidak dianggap angka oleh Pandas/Excel
        df = pd.read_csv(
            config.RAW_DATA_PATH, 
            sep=None, 
            engine='python', 
            on_bad_lines='skip', 
            encoding='utf-8', 
            encoding_errors='ignore',
            dtype={'product_id': str} 
        )
        print(f"✅ Berhasil membaca {len(df)} baris data mentah.")
    except FileNotFoundError:
        print("❌ File raw_skincare.csv tidak ditemukan. Jalankan scraper.py terlebih dahulu.")
        return

    # 1. Bersihkan Nama Produk & Ekstraksi Brand
    df['product_name'] = df['product_name'].apply(clean_product_name)
    df['brand'] = df['product_name'].apply(extract_brand)

    # 2. Bersihkan Harga (Fokus hanya ke original_price -> list_price)
    # Kita buang final_price karena bias diskon pengguna baru
    df['list_price'] = df['raw_original_price'].apply(clean_price)

    # Safety Net: Jika list_price < 5000, anggap error (misal harga sampel/ongkir), ganti NaN
    df.loc[df['list_price'] < 5000, 'list_price'] = np.nan

    # Imputasi: Jika list_price kosong, isi dengan MEDIAN harga brand tersebut
    median_prices = df.groupby('brand')['list_price'].transform('median')
    df['list_price'] = df['list_price'].fillna(median_prices)

    # 3. Parsing Jumlah Terjual
    df['estimated_sold'] = df['raw_sold_count'].apply(parse_sold_count)

    # 4. Handling Rating (Valid Absence)
    # Ubah ke numeric, jika kosong/error biarkan NaN (jangan diimputasi!)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    
    # FITUR BARU: Tandai apakah produk punya rating atau tidak (Sangat berguna untuk analisis)
    df['has_rating'] = df['rating'].notna()

    # 5. Hitung Metrik Turunan (Proksi Ukuran Pasar)
    df['estimated_revenue'] = df['list_price'] * df['estimated_sold']

    # 6. Hapus Baris yang Masih Tidak Valid
    initial_rows = len(df)
    df = df.dropna(subset=['list_price', 'product_id'])
    print(f"🗑️ Menghapus {initial_rows - len(df)} baris yang tidak valid (harga/ID kosong).")

    # 7. Hapus Kolom Mentah yang Tidak Diperlukan
    cols_to_drop = ['product_id', 'raw_original_price', 'raw_final_price']
    '''
        product_id rusak karena semua angka belakang id berubah menjadi 0 dan memang tidak diperlukan
        raW_original_price sudah digantikan menjadi list_price
        raw_final_price karena mengandung angka setelah diskon yang tidak masuk akal, disebabkan proses
        scrap data tanpa melakukan login akun terlebih dahulu
    '''
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # 8. Simpan ke Clean CSV
    df.to_csv(config.CLEAN_DATA_PATH, index=False, encoding='utf-8')
    print(f"✨ Transformasi Selesai! Data bersih disimpan di: {config.CLEAN_DATA_PATH}")
    print(f"📊 Total baris bersih: {len(df)}")
    
    # Validasi Cepat
    print(f"\n📈 Statistik Rating:")
    print(f"Produk dengan rating: {df['has_rating'].sum()}")
    print(f"Produk tanpa rating (Silent Buyers): {(~df['has_rating']).sum()}")

if __name__ == "__main__":
    main()