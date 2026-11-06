# Product Requirements Document (PRD)
## DocTranslate: Offline English ↔ Hindi Document Translation & Format Conversion Suite

---

### 1. Executive Summary & Problem Statement
Translating multi-page documents between English and Hindi (Devanagari) presents three severe engineering bottlenecks in standard tools:
1. **Layout & Typography Rupture**: Translating `.docx`, `.pdf`, `.pptx`, or `.xlsx` files usually strips formatting, misaligns tables, or produces empty Unicode boxes ("tofu") because Hindi Devanagari requires specific font metrics, conjunct rendering, and higher line-heights for Matras.
2. **Memory Exhaustion (OOM) on Large Documents**: Traditional translators load entire documents into memory. Documents exceeding 50 or 100 pages frequently crash desktop and mobile applications due to memory spikes.
3. **Data Privacy & Network Latency**: Cloud-based translation APIs send sensitive corporate, legal, or personal documents to remote third-party servers, posing compliance risks and requiring persistent internet.

**DocTranslate** solves this by providing:
- Two dedicated, standalone offline applications:
  - **Windows Desktop App** (`windows-app/`): Built with Python 3.11 + PySide6, powered by offline CTranslate2 / Opus-MT / IndicTrans2.
  - **Android Native App** (`android-app/`): Built with Kotlin + Jetpack Compose, powered by Google ML Kit On-Device Translation.
- **Strictly Bidirectional Translation (English ↔ Hindi)**:
  - English to Hindi (Devanagari)
  - Hindi to English (Latin)
- **Unlimited-Page Streaming Architecture**: Page-by-page generator pipeline with constant bounded RAM consumption (<250MB on Android, <600MB on Windows), supporting documents of 1,000+ pages without crashing.
- **Integrated Document Format Converter**: Standalone file converter or simultaneous "translate-and-convert" (e.g., English PDF → Hindi DOCX).
- **Intelligent File Compressor Software with Manual Target Size**: Compress documents to a user-specified target size (e.g. "under 2 MB", "500 KB", or % reduction) while preserving vector crispness, font legibility, and automatically purging scratch files immediately after compression.
- **Multiple Rainbow Light Themes**: Gorgeous, accessible light theme combinations (Vibrant Rainbow Light, Pastel Rainbow Light, Prism Spectrum Light, Sunrise Spectrum Light) featuring spectrum gradients across tabs, cards, and progress bars.
- **Downloaded Open-Source Core Repositories**: Cloned in `reference-repos/` for reference and model pipelines (`IndicTrans2`, `IndicTransToolkit`, `Document-Machine-Translation`, `AI-Document-Translator`).

---

### 2. User Personas
1. **Legal & Government Officers**: Need to translate large court affidavits, gazettes, and official notifications between English and Hindi offline without leaking sensitive data.
2. **Academics & Researchers**: Translating 200+ page textbooks, research papers, and lecture slides (`.pptx`, `.pdf`, `.docx`) while preserving equations, citations, and image placements.
3. **Field Agents & Mobile Professionals**: On-site Android users receiving official PDF/DOCX contracts via WhatsApp/Email, needing instant on-device translation to Hindi with offline TTS playback.

---

### 3. Scope & Key Functional Requirements

| Category | Requirement | Windows Desktop App | Android Native App |
| :--- | :--- | :--- | :--- |
| **Translation Direction** | English → Hindi & Hindi → English | Supported (Toggle / Auto) | Supported (Toggle / Auto) |
| **Offline Operation** | 100% On-Device Inference | Supported (Opus-MT / IndicTrans2) | Supported (ML Kit Translation) |
| **Page Volume** | Unlimited Pages (Streaming) | Bounded RAM (<600 MB) | Bounded RAM (<250 MB) |
| **Supported Formats** | Ingestion & Generation | `.docx`, `.pdf`, `.pptx`, `.xlsx`, `.txt`, `.md`, `.html`, `.csv`, `.rtf` | `.docx`, `.pdf`, `.txt`, `.csv`, `.md` |
| **Built-in Converter** | Format-to-Format Translation | e.g., PDF → DOCX, PPTX → PDF | e.g., PDF → DOCX, TXT → PDF |
| **Layout Preservation** | Tables, Bold/Italic, Hierarchy | Supported (Run-level XML) | Supported (Run-level DOM) |
| **Devanagari Fonts** | Noto Sans Devanagari / Mangal | Embedded TTF Fallback | Downloadable / System Font |
| **Translation Memory** | Deduplication Cache (SQLite/Room) | Local SQLite | Local Room DB |
| **Custom Glossary** | User Terminology Dictionary | SQLite CRUD | Room DB CRUD |
| **Audio Playback** | Text-to-Speech (Hindi & English) | SAPI / pyttsx3 | Native Android TTS |

---

### 4. Non-Functional Requirements (NFR)
1. **Privacy & Security**: Zero telemetry. Zero document bytes uploaded to external clouds in offline mode.
2. **Reliability & Crash Resilience**: Any interrupted translation job (battery drop, crash) must recover from the last page checkpoint without data loss.
3. **Performance SLA**:
   - Short text / 1-page document: < 2.5 seconds on desktop CPU, < 4 seconds on mobile.
   - 100-page document: Smooth background processing with progress callbacks and constant memory usage.
4. **Devanagari Typography Fidelity**: Proper rendering of half-letters (*halant*), conjuncts (*samyuktakshar*), and vowel diacritics (*matras*).

---

### 5. Release Milestones
- **M1 (Docs & Foundation)**: Complete 31-file specification suite, directory setup.
- **M2 (Windows App MVP)**: Streaming DOCX/PDF translation with PySide6 UI and offline CTranslate2 engine.
- **M3 (Android App MVP)**: Kotlin + Jetpack Compose app with ML Kit on-device translation, SAF picker, and Room DB history.
- **M4 (Format Converter Suite)**: Ingestion matrix, PDF ↔ DOCX converter, and batch queues for both platforms.
- **M5 (Production Packaging)**: Windows PyInstaller + Inno Setup installer; Android signed release APK/AAB.
