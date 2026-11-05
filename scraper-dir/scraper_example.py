"""
Scraper skala kecil untuk proyek pembelajaran.

Semua nilai yang spesifik terhadap situs target (URL, CSS selector, aturan
badge, pola ID produk) dibaca dari config.py dan TIDAK ditulis di file ini.
Salin config.example.py menjadi config.py lalu isi sendiri nilainya.
"""

import csv
import random
import re
import time
from datetime import datetime
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeout

import config


# ---------------------------------------------------------------------------
# 0. VALIDASI KONFIGURASI
# ---------------------------------------------------------------------------
REQUIRED_CONFIG = [
    "BASE_URL",
    "SEL_NAME",
    "SEL_CARD",
    "SEL_FINAL_PRICE",
    "SEL_ORIGINAL_PRICE",
    "SEL_SHOP_INFO",
    "SEL_BADGE_IMG",
    "PRODUCT_ID_PATTERN",
]


def check_config():
    """Hentikan program dengan pesan jelas jika ada nilai config yang kosong."""
    missing = [name for name in REQUIRED_CONFIG if not getattr(config, name, "")]
    if missing:
        raise SystemExit(
            "Config belum lengkap. Isi nilai berikut di config.py:\n  - "
            + "\n  - ".join(missing)
        )


# ---------------------------------------------------------------------------
# 1. FUNGSI BANTU (FAULT TOLERANCE)
# ---------------------------------------------------------------------------
def safe_extract_text(card, selector):
    """Ambil teks elemen. Jika tidak ada, kembalikan string kosong."""
    try:
        element = card.query_selector(selector)
        return element.inner_text().strip() if element else ""
    except Exception:
        return ""


def extract_rating(card):
    """Cari angka desimal 0.0 - 5.0 di dalam kartu produk."""
    try:
        for span in card.query_selector_all("span"):
            text = span.inner_text().strip()
            try:
                value = float(text)
            except ValueError:
                continue
            if 0.0 <= value <= 5.0:
                return text
    except Exception:
        pass
    return ""


def extract_sold_count(card):
    """Cari teks yang memuat kata 'terjual' di dalam kartu."""
    try:
        for span in card.query_selector_all("span"):
            text = span.inner_text().strip()
            if "terjual" in text.lower():
                return text
    except Exception:
        pass
    return ""


def extract_product_id(card):
    """Ambil ID produk dari link di dalam kartu memakai pola dari config."""
    try:
        link_element = card.query_selector("a")
        link = link_element.get_attribute("href") if link_element else ""
    except Exception:
        return ""

    if not link:
        return ""

    match = re.search(config.PRODUCT_ID_PATTERN, link)
    if match and match.lastindex:
        return match.group(match.lastindex)

    # Cadangan jika pola tidak cocok
    return link.split("?")[0].rstrip("/").split("-")[-1]


def extract_shop_info(card):
    """Ambil nama dan lokasi toko berdasarkan urutan span."""
    try:
        container = card.query_selector(config.SEL_SHOP_INFO)
        if not container:
            return "", ""
        spans = container.query_selector_all("span")
        name = spans[0].inner_text().strip() if len(spans) > 0 else ""
        location = spans[1].inner_text().strip() if len(spans) > 1 else ""
        return name, location
    except Exception:
        return "", ""


def extract_shop_badge(card):
    """Tentukan jenis badge toko memakai aturan pemetaan dari config."""
    badge = "Reguler"
    try:
        badge_img = card.query_selector(config.SEL_BADGE_IMG)
        if not badge_img:
            return badge

        src_url = (badge_img.get_attribute("src") or "").lower()
        for fragment, label in getattr(config, "BADGE_RULES", {}).items():
            if fragment.lower() in src_url:
                return label
    except Exception:
        pass
    return badge


# ---------------------------------------------------------------------------
# 2. HEADER CSV
# ---------------------------------------------------------------------------
CSV_HEADERS = [
    "product_id", "search_keyword", "scraped_at", "product_name", "brand",
    "raw_final_price", "raw_original_price", "rating", "raw_sold_count",
    "shop_name", "shop_location", "shop_badge",
]


# ---------------------------------------------------------------------------
# 3. FUNGSI UTAMA
# ---------------------------------------------------------------------------
def main():
    check_config()
    print("Memulai scraper...")

    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_exists = (
        config.RAW_DATA_PATH.exists() and config.RAW_DATA_PATH.stat().st_size > 0
    )

    with sync_playwright() as p:
        print("Membuka browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(config.BROWSER_PROFILE_PATH),
            headless=False,  # ubah ke True jika sudah yakin skrip berjalan baik
            viewport={"width": 1920, "height": 1080},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
        )
        page = context.new_page()

        # newline='' penting di Windows agar tidak ada baris kosong ganda
        with open(config.RAW_DATA_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)

            if not file_exists:
                writer.writeheader()
                print(f"Header CSV baru dibuat di {config.RAW_DATA_PATH}")
            else:
                print(f"Menambahkan data ke file yang sudah ada: {config.RAW_DATA_PATH}")

            for keyword in config.SEARCH_KEYWORDS:
                print(f"\nMemulai pencarian untuk: '{keyword}'")

                url = config.BASE_URL.format(keyword=quote_plus(keyword))

                print("  Membuka halaman pencarian...")
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=20000)
                except PlaywrightTimeout:
                    print("  Timeout saat membuka halaman. Lanjut ke keyword berikutnya.")
                    continue

                # Lacak product_id yang sudah diambil untuk mencegah duplikasi
                seen_product_ids = set()

                for page_num in range(1, config.MAX_PAGES + 1):
                    print(f"Memproses batch ke-{page_num}...")

                    try:
                        # Tunggu nama produk muncul (tanda data asli sudah termuat)
                        page.wait_for_selector(config.SEL_NAME, timeout=15000)

                        # Hanya ambil kartu yang sudah memuat nama produk
                        card_selector = f"{config.SEL_CARD}:has({config.SEL_NAME})"
                        cards = page.query_selector_all(card_selector)
                        print(f"  Ditemukan {len(cards)} produk valid di layar")

                        new_products_count = 0

                        for card in cards:
                            product_id = extract_product_id(card)

                            # Lewati jika ID kosong atau sudah pernah diambil
                            if not product_id or product_id in seen_product_ids:
                                continue

                            seen_product_ids.add(product_id)
                            new_products_count += 1

                            shop_name, shop_location = extract_shop_info(card)

                            row_data = {
                                "product_id": product_id,
                                "search_keyword": keyword,
                                "scraped_at": datetime.now().isoformat(),
                                "product_name": safe_extract_text(
                                    card, f"{config.SEL_NAME} span"
                                ),
                                "brand": "",  # diisi lewat parsing di transform.py
                                "raw_final_price": safe_extract_text(
                                    card, f"{config.SEL_FINAL_PRICE} span"
                                ),
                                "raw_original_price": safe_extract_text(
                                    card, f"{config.SEL_ORIGINAL_PRICE} span"
                                ),
                                "rating": extract_rating(card),
                                "raw_sold_count": extract_sold_count(card),
                                "shop_name": shop_name,
                                "shop_location": shop_location,
                                "shop_badge": extract_shop_badge(card),
                            }

                            writer.writerow(row_data)

                        print(f"  Ditambahkan {new_products_count} produk baru ke CSV.")

                        if new_products_count == 0:
                            print("  Tidak ada produk baru. Berhenti untuk keyword ini.")
                            break

                    except PlaywrightTimeout:
                        print("  Timeout. Melewati keyword ini...")
                        break
                    except Exception as e:
                        # Pesan error bisa memuat selector, jangan simpan ke repo
                        print(f"  Error: {e}")
                        break

                    # Scroll untuk memuat produk berikutnya, lalu beri jeda
                    if page_num < config.MAX_PAGES:
                        print("  Scroll ke bawah untuk memuat produk baru...")
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(4000)

                        print("  Menunggu jeda waktu acak...")
                        time.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))

        print(f"\nScraping selesai! Cek file {config.RAW_DATA_PATH.name}")
        context.close()


if __name__ == "__main__":
    main()
