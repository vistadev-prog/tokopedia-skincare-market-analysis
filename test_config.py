import config

print("---Pengujian Config---")
print(f"Root Proyek: {config.PROJECT_ROOT}")
print(f"Folder Data ada? {config.DATA_DIR.exists()}")
print(f"Jalur Raw Data: {config.RAW_DATA_PATH}")
print(f"Kata Kunci: {config.SEARCH_KEYWORDS}")