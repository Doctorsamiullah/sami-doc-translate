# TASK: Build an English → Hindi Document Translation Suite
# (Local Windows App + Android App, in two separate folders)

## 0. Role
You are a senior full-stack engineer, mobile engineer, and technical writer.
Plan first, then write docs, then build, then test. Do not skip steps.

## 1. Goal
Build a document translation product that translates documents from
English to Hindi (Devanagari) while PRESERVING layout and formatting.
Two separate deliverables, two separate folders:

```
C:\DocTranslate\
├── windows-app\      <- local desktop app (Windows 10/11), works offline
├── android-app\      <- native Android app, works offline (on-device)
└── docs\             <- shared PRD.md + all 30 .md files (see section 5)
```

The two apps must not depend on each other's code. Share only the docs
and the same translation-quality goals.

## 2. Research step (do this first)
Search GitHub and the web for open-source repos for document translation
English → Hindi, for example: "repo for doc translation from english to hindi".
Evaluate at least these candidates and any better ones you find:
- AI4Bharat IndicTrans2 (best quality for English → Indian languages)
- Helsinki-NLP opus-mt-en-hi (small, fast, offline)
- Meta NLLB-200 (distilled, 600M)
- Argos Translate / LibreTranslate (offline, Python)
- BabelDOC or similar PDF-layout-preserving translators
- Google ML Kit On-Device Translation (Android, supports Hindi)
- Libraries for reading/writing documents: python-docx, PyMuPDF,
  python-pptx, openpyxl

For each: license, last commit date, model size, Hindi quality, offline
support, Windows/Android feasibility. Write the result into
docs\RESEARCH.md with a comparison table and a clear recommendation.
Only use repos whose license allows our use. Do not invent repos or
links. Verify every repo exists before using it.

## 3. Functional requirements

### Windows app (windows-app\)
- Stack: Python 3.11 + PySide6 (or Tkinter if simpler) UI; packaged to
  a single installer with PyInstaller + Inno Setup.
- Input formats: .docx, .pdf (text-based), .txt, .pptx, .xlsx, .md
- Optional OCR for scanned PDFs/images (Tesseract) as a later phase.
- Output: translated file in the SAME format, same layout, fonts replaced
  with a Devanagari font (Noto Sans Devanagari / Mangal) so Hindi
  displays correctly.
- Translation engine options in Settings:
  1. Offline model (IndicTrans2 or opus-mt-en-hi), default
  2. Online API (optional, user supplies own key, stored securely)
- Features: drag-and-drop, batch folder translation, progress bar,
  side-by-side preview (English | Hindi), edit translation before
  export, glossary / custom dictionary (e.g. medical terms), translation
  memory (SQLite) so repeated sentences are not re-translated, history.
- Works fully offline after first model download; show model download
  manager with size and progress.
- UI language: English and Hindi.

### Android app (android-app\)
- Stack: Kotlin + Jetpack Compose, minSdk 26, targetSdk latest stable.
- Input: pick files with the system file picker; support .docx, .pdf
  (text-based), .txt; share-sheet "Translate with DocTranslate" intent;
  camera scan with ML Kit text recognition (phase 2).
- Translation: on-device (ML Kit Translation for Hindi, or an ONNX /
  TFLite converted model if research shows it is better). Offline after
  language pack download.
- Output: translated .docx / .pdf / .txt saved to Downloads or shared.
- Features: history (Room DB), glossary, dark mode, Hindi/English UI,
  text-to-speech of the Hindi output (Android TTS), copy / share.
- Keep APK size reasonable; explain trade-offs in ARCHITECTURE.md.

## 4. Non-functional requirements
- Privacy first: documents never leave the device in offline mode.
- Translation quality: sentence-level segmentation, keep numbers, dates,
  URLs, email addresses, code, and proper nouns untouched unless in the
  glossary. Keep tables, bullets, headings, bold/italic, and images.
- Performance: a 20-page docx should translate in a reasonable time on a
  mid-range PC (no GPU) and show progress; document the benchmark.
- Error handling for corrupt files, password-protected PDFs, huge files.
- Accessibility, readable Devanagari fonts, proper line-breaking.
- Include unit tests, an end-to-end test with sample documents, and a
  quality check (compare a few sentences against a reference).

## 5. Documentation set (create BEFORE writing code)
Create docs\PRD.md first (problem, users, goals, non-goals, user
stories, features for both apps, success metrics, risks, milestones).
Then create each file below in docs\, filled with real, project-specific
content (no placeholder text), cross-linking each other:

1. DESIGN.md
2. ARCHITECTURE.md
3. DATABASE.md
4. API.md
5. AGENTS.md
6. README.md
7. IMPLEMENTATION.md
8. SETUP.md
9. FEATURE-DEVELOPMENT.md
10. AUTH-SECURITY.md
11. MCP-CONNECTION.md
12. INTEGRATIONS.md
13. TESTING-QA.md
14. DEBUGGING.md
15. TASKS.md
16. ROADMAP.md
17. CHANGELOG.md
18. DEPLOYMENT.md
19. ENVIRONMENT.md
20. CODING-STANDARDS.md
21. CLAUDE.md (and GEMINI.md, same content)
22. PROMPTS.md
23. ERROR-HANDLING.md
24. PERFORMANCE.md
25. SECURITY.md
26. PRIVACY-POLICY.md
27. TERMS.md
28. UI-COMPONENTS.md
29. MIGRATIONS.md
30. CONTRIBUTING.md

Guidance per file (keep each focused and useful):
- DESIGN: UI wireframes in text, color palette, Devanagari typography.
- ARCHITECTURE: both apps' module diagrams (Mermaid), data flow from
  file → segmentation → translation → reconstruction.
- DATABASE: SQLite (Windows) and Room (Android) schemas for history,
  glossary, translation memory, settings.
- API: internal module interfaces; optional online translation provider
  interface; no public server required.
- AGENTS / CLAUDE / GEMINI: rules for AI coding agents working on this
  repo (folder layout, commands, do/don't).
- AUTH-SECURITY / SECURITY: local-only data, secure API key storage
  (Windows Credential Manager, Android Keystore), file validation.
- MCP-CONNECTION: optional MCP server exposing "translate_document" as a
  tool, plus how to connect it.
- INTEGRATIONS: model sources, OCR, TTS, optional online providers.
- TASKS: checklist broken into small tasks per app, with status boxes.
- PROMPTS: the prompts used for any LLM-based post-editing of Hindi.
- PRIVACY-POLICY / TERMS: plain-language drafts; mark them as drafts
  that need legal review before publishing.
- Other files: follow their standard purpose.

## 6. Build order
1. Research -> RESEARCH.md
2. PRD.md and all 30 docs
3. STOP and show me a short summary + the chosen stack for approval
4. Windows app MVP (docx + txt, offline model) -> test -> add pdf, pptx,
   xlsx, glossary, translation memory
5. Android app MVP (txt + docx, on-device) -> test -> add pdf, history,
   TTS
6. Packaging: Windows installer (.exe), Android debug + release APK/AAB
7. Update CHANGELOG.md, TASKS.md, README.md

## 7. Rules
- Keep the two folders fully separate and self-contained.
- Never hardcode API keys; use .env.example and secure storage.
- Do not claim a feature works unless you ran and tested it. Report
  honestly what passed and what failed.
- Ask me before downloading very large models (>1 GB) or buying/using
  paid APIs.
- Prefer simple, maintainable code with comments; follow CODING-STANDARDS.md.
