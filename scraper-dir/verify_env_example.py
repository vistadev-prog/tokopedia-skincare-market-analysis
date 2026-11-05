"""
Skrip verifikasi lingkungan: memastikan Python, pandas, dan Playwright
berjalan di komputer ini. Skrip ini TIDAK mengakses situs target apa pun.
"""

import sys
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright


def check_environment():
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Pandas Version: {pd.__version__}")

    try:
        # Folder profil browser terpisah. Isinya cookie dan sesi, jadi
        # JANGAN di-upload (sudah ada di .gitignore).
        user_data_dir = Path(__file__).resolve().parent / ".browser_profile"
        user_data_dir.mkdir(exist_ok=True)

        print("Membuka browser...")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,  # tampilkan jendela agar mudah dipantau
                args=["--disable-gpu"],  # mencegah layar hitam di beberapa GPU Windows
                viewport={"width": 1920, "height": 1080},
                locale="id-ID",
                timezone_id="Asia/Jakarta",
            )

            page = context.new_page()

            # Halaman kosong bawaan browser, cukup untuk memastikan browser jalan
            page.goto("about:blank")
            page.wait_for_timeout(2000)

            print("Playwright berhasil: browser dapat dibuka dan ditutup.")
            context.close()

    except Exception as e:
        print(f"Playwright gagal: {e}")
        print("Jika browser belum terpasang, jalankan: playwright install chromium")


if __name__ == "__main__":
    check_environment()
