import sys
import os
import pandas as pd
from playwright.sync_api import sync_playwright

def check_environment():
    print(f"✅ Python Version: {sys.version.split()[0]}")
    print(f"✅ Pandas Version: {pd.__version__}")

    try:
        # 1. Tentukan path ke folder profil KHUSUS yang terisolasi (AMAN untuk di-upload strukturnya)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        user_data_dir = os.path.join(current_dir, "scraping_profile")
        
        # Buat folder profil jika belum ada
        os.makedirs(user_data_dir, exist_ok=True)

        print(f"📂 Menggunakan profil terisolasi di: {user_data_dir}")
        print("🔄 Membuka browser... (Perhatikan jendela browser yang muncul)")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False, # Tampilkan visual agar BISA dipantau prosesnya (debugging)
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-gpu', # Mencegah crash layar hitam pada beberapa GPU Windows
                    '--no-sandbox'
                ],
                viewport={'width': 1920, 'height': 1080},
                locale='id-ID',
                timezone_id='Asia/Jakarta'
            )

            # 3. Buat halaman baru di dalam context ini
            page = context.new_page()

            # 4. Navigasi ke halaman umum HANYA untuk verifikasi browser berjalan
            # CATATAN PENTING: URL target scraping sebenarnya TIDAK ADA DI SINI.
            # URL dan selector spesifik disimpan di config.py (yang tidak diunggah).
            page.goto(
                "",
                wait_until='domcontentloaded',
                timeout=30000
            )

            # Beri waktu 3 detik agar bisa melihat hasilnya
            page.wait_for_timeout(3000)
            
            title = page.title()
            print(f"✅ Playwright Berhasil! Browser terbuka dengan judul: {title}")
            print("ℹ️  Script ini hanya verifikasi lingkungan. Logika scraping (selector, URL spesifik) disamarkan sesuai etika data.")

            context.close()

    except Exception as e:
        print(f"❌ Playwright Gagal: {e}")

if __name__ == "__main__":
    check_environment()
