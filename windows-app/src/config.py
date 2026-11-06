import os
from pathlib import Path

APP_NAME = "DocTranslate"
APP_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# User Data & Cache directories
APPDATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = APPDATA_DIR / "doctranslate.db"
TEMP_DIR = APPDATA_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Supported extensions
SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".txt", ".md", ".xlsx", ".pptx", ".csv"}
CONVERTIBLE_EXTENSIONS = {".docx", ".pdf", ".txt", ".md", ".html"}

# Fallback Devanagari Fonts
DEVANAGARI_FONTS = ["Noto Sans Devanagari", "Mangal", "Aparajita", "Nirmala UI", "Arial Unicode MS"]

