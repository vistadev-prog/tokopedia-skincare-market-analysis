'''
    Ini adalah PROSES KEDUA dari explore_brand setelah mengetahui seluruh kata yang paling banyak
    muncul dari PROSES PERTAMA dengan STOPWORDS yang hanya berisikan:
    'sunscreen', 'moisturizer', 'spf', 'pa', 'original', 'bpom', 'flash', 'sale',
    'terlaris', 'terbaik', 'murah', 'promo', 'diskon', 'gratis', 'ongkir', 'wajah',
    'badan', 'kulit', 'berminyak', 'kering', 'sensitif', 'jerawat', 'glowing', 'putih',
    'cerah', 'lembab', 'halal', 'import', 'lokal', 'new', 'baru', 'paket', 'bundle',
    'buy', 'get', 'free', 'gift', 'set', 'travel', 'size', 'mini', 'full',
    'untuk', 'dan', 'dengan', 'atau', 'yang', 'di', 'ke', 'dari', 'the', 'a', 'an',
    'tabir', 'surya', 'uv', 'filter', 'gel', 'cream', 'serum', 'lotion', 'spray'
'''

import pandas as pd
import re
from collections import Counter
import config

# ==========================================
# 1. DAFTAR KATA UMUM (STOPWORDS) - DIPERLUAS
# ==========================================
# Kita tambahkan bahan, kata sifat, dan kata umum yang ditemukan dari hasil sebelumnya
STOPWORDS = {
    # Kata Umum E-commerce
    'original', 'bpom', 'flash', 'sale', 'terlaris', 'terbaik', 'murah', 'promo', 'diskon', 
    'gratis', 'ongkir', 'import', 'lokal', 'new', 'baru', 'paket', 'bundle', 'buy', 'get', 
    'free', 'gift', 'set', 'travel', 'size', 'mini', 'full', 'untuk', 'dan', 'dengan', 'atau', 
    'yang', 'di', 'ke', 'dari', 'the', 'a', 'an', 'of', 'and', 'in', 'to', 'for',
    
    # Kategori & Jenis Produk
    'sunscreen', 'moisturizer', 'spf', 'pa', 'tabir', 'surya', 'uv', 'filter', 'gel', 'cream', 
    'serum', 'lotion', 'spray', 'wajah', 'badan', 'kulit', 'berminyak', 'kering', 'sensitif', 
    'jerawat', 'glowing', 'putih', 'cerah', 'lembab', 'halal', 'pria', 'wanita', 'anak', 'ibu',
    'daily', 'top', 'creator', 'seller', 'store', 'shop', 'official', 'kosmetik', 'beauty',
    
    # Bahan & Ingredient (Ditemukan dari data)
    'panthenol', 'ceramide', 'centella', 'collagen', 'aqua', 'allantoin', 'mulberry', 'blueberry', 
    'peach', 'pomegranate', 'niacinamide', 'retinol', 'calendula', 'hyaluronic', 'aloe', 'tea tree',
    'cica', 'glow', 'skin', 'barrier', 'bright', 'brightening', 'acne', 'calm', 'calming', 'moist',
    'moisturizing', 'hydrashot', 'hydrasoothe', 'whitening', 'anti', 'aging', 'spot', 'pore',
    
    # Kata Sifat & SEO Spam (Ditemukan dari data)
    'perfect', 'triple', 'exclusive', 'special', 'best', 'viral', 'ready', 'stock', 'stok', 'termurah',
    'terpercaya', 'aman', 'nyaman', 'cepat', 'lengkap', 'murah', 'promo', 'diskon', 'bonus', 'extra',
    'upgrade', 'new', 'latest', 'hot', 'top', 'best', 'favorite', 'recommended', 'popular', 'viral',
    'fyp', 'tiktok', 'instagram', 'tiktokmade', 'beli', 'jual', 'harga', 'promo', 'cashback', 'voucher',
    'shield', 'hero', 'launch', 'water', 'watermelon', 'battle', 'glass', 'series', 'madagascar',
    'spf50', 'packaging', 'all', 'cicamide', 'real', 'coming', 'protection', 'product', 'tone', 'teens',
    'lovely', 'day', 'varian', 'jumbo', 'dreamy', 'big', 'expert', 'produk', 'certified', 'rumus',
    'pilih', 'find', 'awards', 'royal', 'chemical', 'siap', 'aster', 'livestream', 'oktober', 'formula',
    'everyday', 'pack', 'picks', 'toneup', 'deal', 'edition', 'langsung', 'goat', 'perlindungan', 'vip',
    'auction', 'pcs', 'smooth', 'dapat', 'gather', 'madame', 'active', 'lightplus', 'whitessentials',
    'seger', 'snow', 'gurls', '3in1', 'ori', 'hydra', 'glad', 'light', 'game', 'kind', 'biru', 'sonik',
    'scents', 'msh', 'pelembab', 'nrw', 'shine', 'cosmetics', 'cooling', 'exlusive', 'creatornew', 'nuface',
    'essential', 'white', 'refill', 'kiwi', 'facelogy', 'waterbarrier', 'glowbi', 'eiembeauty', 'cerahydro',
    '100gglad2glow', 'promoscarlett', 'skintipiik', 'sellingtorriden', 'exclusivescarlett', 'carendelanos',
    'favoritescarlett', 'glowsophywatermelon', 'upgradeglad2glow', 'approvedfacerinna', 'varianazarine',
    'salefacetolog', 'bpombuy', 'eiem', 'backmadame', 'cloudberry', 'elformula', 'gloowbe', 'sunbrella',
    'amaterasun', 'skin1004', 'labo', 'gokujyun', 'vivo', 'mts', 'suniora', 'vicci', 'fyb', 'skingenius',
    'codrose', 'saleskingenius', 'dorskin', 'shinzui', 'cetaphil', 'bioaqua', 'nyyo', 'purbasari', 'ceramella',
    'envio', 'junny', 'animate', 'tasya', 'farasya', 'facerinna', 'unitary', 'hada'
}

# ==========================================
# 2. FUNGSI UTAMA (DIPERBAIKI)
# ==========================================
def main():
    print("🔍 Memulai Brand Discovery (Versi 2.0 - Anti Merged Words)...")
    
    try:
        df = pd.read_csv(config.RAW_DATA_PATH, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8')
        print(f"✅ Berhasil membaca {len(df)} baris data mentah.")
    except FileNotFoundError:
        print("❌ File raw_skincare.csv tidak ditemukan.")
        return

    word_counts = Counter()

    for name in df['product_name'].dropna():
        # PERBAIKAN UTAMA: Ganti SEMUA simbol non-alfanumerik dengan SPASI
        # Sehingga "[BPOM]BUY" menjadi " BPOM BUY " (terpisah)
        cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(name))
        
        # Pecah menjadi kata-kata
        words = cleaned_name.split()
        
        # Ambil maksimal 3 kata pertama
        for word in words[:3]:
            clean_word = word.lower()
            
            # Filter: panjang > 2, bukan angka murni, dan bukan stopwords
            if len(clean_word) > 2 and not clean_word.isdigit() and clean_word not in STOPWORDS:
                word_counts[clean_word] += 1

    result_df = pd.DataFrame(word_counts.most_common(), columns=['Candidate_Brand', 'Frequency'])
    output_path = config.DATA_DIR / "candidate_brands_v2.csv"
    result_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"✨ Selesai! {len(result_df)} kandidat kata ditemukan.")
    print(f"📂 Silakan buka dan review file: {output_path}")

if __name__ == "__main__":
    main()