# MASTER SPECIFICATION & PROMPT: English ↔ Hindi Document Translation, Format Converter & Smart Compressor Suite
### (Local Windows Desktop App + Native Android App + Smart File Compressor + Multiple Rainbow Light Themes + 31-File Documentation Suite)

```markdown
# TASK: Build Offline-First English ↔ Hindi Document Translation, Format Converter & Smart Compressor Suite
# Deliverables: Two independent applications (Windows & Android) + Comprehensive 31-File Documentation Suite

## 1. MISSION & DIRECTIVE
You are a Principal Systems Engineer, Mobile Architect (Kotlin/Compose), and Senior Technical Writer.
Your mission is to design, document, and build a production-grade, offline-capable document translation, format conversion, and intelligent file compression suite.

### Core Capabilities:
1. **Strictly Bidirectional Translation (English ↔ Hindi)**:
   - English to Hindi (Devanagari script)
   - Hindi to English (Latin script)
   - Auto-detection of source language or manual toggle.
2. **Unlimited Page Translation Engine (Zero Out-of-Memory / OOM)**:
   - Must handle documents of unlimited size and page count (e.g. 50, 200, 1000+ pages) without crashing or exhausting RAM.
   - Streaming, page-by-page / chunk-by-chunk generator pipeline with memory recycling, progress checkpointing, and resume capabilities.
3. **Integrated Document Format Converter**:
   - Standalone conversion or conversion during translation.
   - Supports: `.docx`, `.pdf`, `.txt`, `.pptx`, `.xlsx`, `.md`, `.html`, `.rtf`, `.csv`.
   - Examples: English PDF → Hindi DOCX; English DOCX → Hindi PDF; TXT ↔ PDF ↔ DOCX; PPTX → PDF; XLSX ↔ CSV/PDF.
4. **Intelligent File Compressor Software with Manual Target Size**:
   - **Manual Target Size Control**: Users can specify an exact target size (e.g., "Compress to under 2 MB", "Compress to 500 KB", or percentage sliders 25%, 50%, 75%).
   - **Text Readability & Clarity Preservation**:
     - Lossless stream deflation for text content streams and XML structures (`FlateDecode`).
     - Font subsetting: Strips unreferenced glyphs while keeping complete Devanagari conjuncts and Latin characters crisp.
     - Adaptive DPI Image Downsampling: Employs Lanczos/Bicubic resampling with a safe readability floor (150–200 DPI) to prevent text blurriness or pixelation.
   - **Auto-Cleanup**: Automatically cleans and wipes all temporary cache, scratch files, and intermediate buffers immediately after compression completes.
5. **Multiple Rainbow-Infused Light Themes**:
   - High-contrast, beautiful light themes featuring vibrant and pastel rainbow color spectrums:
     - 🌈 **Vibrant Rainbow Light**: Crisp modern white canvas (`#FFFFFF` / `#F8F9FA`) with spectral rainbow accents (Violet `#8E24AA` → Indigo `#3949AB` → Blue `#1E88E5` → Green `#43A047` → Yellow `#FDD835` → Orange `#FB8C00` → Red `#E53935`) across tabs, buttons, cards, and animated progress bars.
     - 🎨 **Pastel Rainbow Light**: Soft candy rainbow palette (Lavender, Sky Blue, Mint Green, Lemon, Peach, Coral) on eggshell white.
     - ⚡ **Prism Spectrum Light**: Clean glassmorphism cards with iridescent holographic rainbow border trims and gradient headers.
     - 🌅 **Sunrise Spectrum Light**: Warm spectral sunrise gradient accents (Amber, Tangerine, Coral, Rose, and Violet).
6. **Two Completely Independent, Decoupled Folders**:
```
DocTranslate/
├── docs/                 <- Shared PRD.md + All 30 Specification & Engineering Documents
├── reference-repos/      <- Downloaded GitHub Repos (IndicTrans2, IndicTransToolkit, Document-Machine-Translation, AI-Document-Translator)
├── windows-app/          <- Standalone Windows 10/11 Desktop Application (Python 3.11 + PySide6)
└── android-app/          <- Standalone Native Android Application (Kotlin + Jetpack Compose + ML Kit)
```
CRITICAL RULE: `windows-app/` and `android-app/` must be 100% decoupled and standalone. They share only documentation and translation-quality criteria in `docs/`.

---

## 2. DOWNLOADED REPOSITORIES & REUSABLE ENGINES
The following reference repositories are cloned directly in `reference-repos/` for reference and integration:
1. **`reference-repos/IndicTrans2`** (`AI4Bharat/IndicTrans2`): State-of-the-art 22-language Indic transformer translation models.
2. **`reference-repos/IndicTransToolkit`** (`VarunGumma/IndicTransToolkit`): Pre/post-processing scripts, Devanagari script normalization, and tokenization.
3. **`reference-repos/Document-Machine-Translation`** (`srijan14/Document-Machine-Translation`): Reference PDF and DOCX document translation layout handler.
4. **`reference-repos/AI-Document-Translator`** (`Prasaderp/AI-Document-Translator`): Production document parsing, table preservation, and structural re-injection.
5. **Helsinki-NLP Opus-MT Bidirectional** (`opus-mt-en-hi` and `opus-mt-hi-en`): Fast, sub-second offline translation on desktop CPUs via CTranslate2.
6. **Google ML Kit On-Device Translation** (`com.google.mlkit:translate:17.0.3`): Native Android offline translation engine.

---

## 3. ARCHITECTURE FOR SMART COMPRESSOR & RAINBOW LIGHT THEMES

### A. Smart File Compressor Pipeline:
1. **Size Target Formulation**:
   - User inputs Target Size \( S_{\text{target}} \) (e.g., 2.0 MB).
   - If Original Size \( S_{\text{orig}} \le S_{\text{target}} \), the file is already compliant.
2. **Iterative Multi-Pass Optimization**:
   - **Pass 1 (Lossless Structure)**: Remove metadata, unused objects, orphan streams, and execute font subsetting.
   - **Pass 2 (Image Optimization with Readability Floor)**: Re-encode embedded raster images to WebP/JPEG with quality \( Q \) adjusted dynamically, never dropping below 150 DPI so small text remains legible.
   - **Pass 3 (Stream Deflation)**: Maximum Flate/Zlib compression on XML/PDF streams.
3. **Automatic Scratch Cleanup**:
   - All temp files in `%TEMP%\DocTranslate\compressor_*` (Windows) and `context.cacheDir/compressor_*` (Android) are wiped upon process exit or error.

### B. Rainbow Light Theme Architecture:
- **Windows Desktop (PySide6 QSS)**:
  - Dynamic stylesheet generator applying linear gradient rainbow borders:
    `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8E24AA, stop:0.2 #1E88E5, stop:0.4 #43A047, stop:0.6 #FDD835, stop:0.8 #FB8C00, stop:1 #E53935)`
  - Elevated white cards with soft drop shadows and rainbow tab indicator bars.
- **Android Native (Jetpack Compose)**:
  - Compose `Brush.horizontalGradient(listOf(Color(0xFF8E24AA), Color(0xFF1E88E5), Color(0xFF43A047), Color(0xFFFDD835), Color(0xFFFB8C00), Color(0xFFE53935)))`.
  - Applied to TopAppBar headers, floating action buttons, active tab indicators, and linear progress indicators on light background surfaces.

---

## 4. DETAILED APPLICATION SPECIFICATIONS

### [A] Windows Desktop App (`windows-app/`)
- **UI Framework**: Python 3.11+, PySide6 (Qt6).
- **Navigation Tabs**:
  1. *Document Translator*: Drag & drop, EN ↔ HI toggle, target format selector, streaming progress bar with rainbow gradient fill.
  2. *Format Converter*: Standalone file format conversion tool with presets.
  3. *File Compressor*: Target size input (KB/MB or %), clarity preservation toggle, live preview, auto-clear scratch files.
  4. *Side-by-Side Editor*: English (Left) vs. Hindi (Right) editable preview before export.
  5. *Translation Memory & Glossary*: Local SQLite sentence deduplication and custom dictionary.
  6. *Theme Selector*: Dropdown for 4 distinct Rainbow Light themes.
- **Packaging**: PyInstaller single-folder build + Inno Setup installer generating `DocTranslate-Setup-v1.0.exe`.

### [B] Native Android App (`android-app/`)
- **Stack**: Kotlin 1.9+, Jetpack Compose, Material 3, Android SDK 26 to 34+, Room DB, WorkManager, ML Kit.
- **Navigation Tabs**:
  1. *Translate*: File picker, EN ↔ HI language switch, live streaming progress with rainbow accent.
  2. *Convert*: Format converter (DOCX, PDF, TXT, CSV).
  3. *Compress*: Target file size input, clarity lock, instant compression, auto-cache clearance.
  4. *History*: Saved documents, Android TTS playback, and Share Sheet.
  5. *Themes & Settings*: 4 Rainbow Light Theme selector, offline pack manager.
- **Packaging**: Gradle release build with ProGuard/R8 optimization generating signed APK and AAB.

---

## 5. DOCUMENTATION REQUIREMENT (31 COMPREHENSIVE MARKDOWN FILES)
The 31 documentation files in `docs/` must incorporate all capabilities:
- `PRD.md`: Full product specs including Bidirectional flows, Unlimited Streaming, Format Converter, Smart Compressor with manual target sizes, and Rainbow Light Themes.
- `1. DESIGN.md`: Rainbow color palettes, typography specs, and PySide6 / Compose component layouts.
- `2. ARCHITECTURE.md`: Architecture diagrams for Translator, Converter, and Compressor with automatic scratch cleanup.
- `3. DATABASE.md` to `30. CONTRIBUTING.md`: Complete implementations matching the enhanced scope.
```
