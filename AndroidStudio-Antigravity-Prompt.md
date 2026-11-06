# 🤖 MASTER PROMPT FOR ANDROID STUDIO (ANTIGRAVITY AGENT)

Copy and paste the exact prompt below into Antigravity when you open this project in Android Studio:

---

```markdown
# TASK: Build Native Android App for Offline English ↔ Hindi Document Translation, Conversion & Compression
# Execution Environment: Android Studio (Antigravity Agent)
# Target Directory: android-app/

## 1. YOUR ROLE & MISSION
You are a Principal Android Architect and Senior Kotlin Engineer.
Your task is to build a production-ready, 100% offline, native Android application in `android-app/` that performs:
1. **Strictly Bidirectional English ↔ Hindi Document Translation**:
   - English to Hindi (Devanagari script)
   - Hindi to English (Latin script)
   - Powered by Google ML Kit On-Device Translation (`com.google.mlkit:translate:17.0.3`). Zero cloud leakage.
2. **Unlimited-Page Streaming (Zero-OOM)**:
   - Handle 50, 100, 500+ page documents with bounded memory (< 250 MB RAM) using page-by-page streaming iterators and Android `WorkManager` Foreground Service.
3. **Integrated Format Converter**:
   - Convert between `.docx`, `.pdf`, `.txt`, `.csv` with or without translation.
4. **Smart File Compressor**:
   - Manual target size specification (e.g., compress to under 2 MB or 500 KB).
   - Preserves text clarity and vector shapes with a minimum 150 DPI readability floor.
   - Auto-clears all temporary scratch cache immediately upon completion.
5. **Multiple Rainbow Light Themes**:
   - 4 high-contrast light themes with vibrant and pastel rainbow gradients (`Brush.horizontalGradient` across TopAppBar, active tab indicators, and progress bars).

IMPORTANT: This Android app must be completely self-contained in `android-app/` and have zero dependencies on Python or the desktop app. Shared documentation is in `../docs/`.

---

## 2. TECHNICAL SPECIFICATIONS & GRADLE SETUP

### A. Core Stack:
- **Language**: Kotlin 1.9+
- **Min SDK**: 26 (Android 8.0 Oreo) | **Target SDK**: 34 (Android 14)
- **UI Framework**: Jetpack Compose + Material Design 3 (M3)
- **Concurrency**: Kotlin Coroutines + StateFlow
- **Database**: Android Jetpack Room Persistence Library
- **Background Tasks**: Android Jetpack `WorkManager` (Foreground Service with ongoing progress notification)
- **Translation Engine**: Google ML Kit On-Device Translation SDK
- **Speech**: Android Native Text-to-Speech (`android.speech.tts.TextToSpeech`) with `Locale("hi", "IN")`

### B. Required Dependencies (`app/build.gradle.kts`):
```kotlin
dependencies {
    // Jetpack Compose & Material 3
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.navigation:navigation-compose:2.7.7")
    implementation("androidx.activity:activity-compose:1.8.2")

    // Google ML Kit On-Device Translation (English <-> Hindi)
    implementation("com.google.mlkit:translate:17.0.3")

    // Room Database (Translation Memory, History, Glossaries)
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // WorkManager for Unlimited Page Processing
    implementation("androidx.work:work-runtime-ktx:2.9.0")

    // Apache POI Android for DOCX Parsing
    implementation("org.apache.poi:poi-ooxml:5.2.3")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
}
```

---

## 3. PROJECT DIRECTORY STRUCTURE TO BUILD

Create the complete structure inside `android-app/`:
```
android-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/doctranslate/app/
│   │   │   ├── MainActivity.kt
│   │   │   ├── data/
│   │   │   │   ├── local/
│   │   │   │   │   ├── AppDatabase.kt
│   │   │   │   │   ├── entities/ (TMEntity, HistoryEntity, GlossaryEntity)
│   │   │   │   │   └── dao/ (TMDao, HistoryDao, GlossaryDao)
│   │   │   │   └── saf/ (SAFHelper.kt)
│   │   │   ├── domain/
│   │   │   │   ├── translation/ (MLKitTranslationEngine.kt, TokenMasker.kt)
│   │   │   │   ├── parsers/ (StreamingDocxParser.kt, StreamingPdfParser.kt, StreamingTextParser.kt)
│   │   │   │   ├── compressor/ (SmartFileCompressor.kt)
│   │   │   │   ├── converter/ (FormatConverter.kt)
│   │   │   │   └── tts/ (TTSManager.kt)
│   │   │   └── presentation/
│   │   │       ├── theme/ (Color.kt, Theme.kt, RainbowGradients.kt)
│   │   │       ├── components/ (RainbowHeader.kt, LanguageSwapCard.kt, ProgressCard.kt, FilePickerCard.kt)
│   │   │       ├── screens/
│   │   │       │   ├── TranslateScreen.kt
│   │   │       │   ├── ConvertScreen.kt
│   │   │       │   ├── CompressScreen.kt
│   │   │       │   └── HistoryScreen.kt
│   │   │       └── viewmodel/ (MainViewModel.kt)
│   │   ├── res/
│   │   │   ├── values/ (strings.xml, colors.xml)
│   │   │   └── values-hi/ (strings.xml - Hindi localization)
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
├── build.gradle.kts
├── settings.gradle.kts
└── gradle.properties
```

---

## 4. DETAILED IMPLEMENTATION REQUIREMENTS

### [1] ML Kit Translation Engine (`domain/translation/MLKitTranslationEngine.kt`):
- Implement dynamic download of English & Hindi model packs via `RemoteModelManager`:
  ```kotlin
  val options = TranslatorOptions.Builder()
      .setSourceLanguage(TranslateLanguage.ENGLISH)
      .setTargetLanguage(TranslateLanguage.HINDI)
      .build()
  val englishHindiTranslator = Translation.getClient(options)
  ```
- Bidirectional support: Instantly switch between `EN -> HI` and `HI -> EN`.
- Wrap translation in Translation Memory (Room DB) check to reuse previous translations.
- Mask URLs, emails, and numeric formulas before sending to ML Kit.

### [2] Unlimited-Page Streaming Engine:
- Read files via Android Storage Access Framework (`contentResolver.openInputStream(uri)`).
- Process paragraphs/pages sequentially without loading entire byte buffers into memory.
- Use `WorkManager` with `setForegroundAsync()` showing live notification:
  *"Translating Document.pdf: Page 42 of 180 (Zero-OOM Active)"*.

### [3] Smart File Compressor (`domain/compressor/SmartFileCompressor.kt`):
- Accept manual target size (in MB or KB).
- Recompress streams losslessly (`Deflate`).
- Downsample embedded images enforcing a strict **150 DPI minimum floor** to maintain crystal clear text.
- Guarantee auto-cleanup: Delete all temporary scratch files in `context.cacheDir` upon completion.

### [4] Format Converter (`domain/converter/FormatConverter.kt`):
- Standalone conversion between `.docx`, `.pdf`, `.txt`, `.csv`.

### [5] Rainbow Light Themes in Jetpack Compose (`presentation/theme/RainbowGradients.kt`):
- Provide 4 selectable light themes:
  1. **Vibrant Rainbow Light**: Spectral gradient `listOf(Color(0xFF8E24AA), Color(0xFF1E88E5), Color(0xFF43A047), Color(0xFFFDD835), Color(0xFFFB8C00), Color(0xFFE53935))` on crisp white.
  2. **Pastel Rainbow Light**: Lavender, Sky Blue, Mint, Lemon, Peach, Coral on eggshell.
  3. **Prism Spectrum Light**: Holo rainbow border trims and high-contrast dark text.
  4. **Sunrise Spectrum Light**: Amber, Tangerine, Coral, Rose, and Violet.
- Apply to `RainbowHeader`, active tab indicator underlines, and `LinearProgressIndicator`.

### [6] Text-to-Speech (TTS):
- Support native Hindi audio playback via `TextToSpeech` with `Locale("hi", "IN")` directly from the History tab.

---

## 5. BUILD & VERIFICATION GATES
1. Implement unit tests in `app/src/test/java/` verifying:
   - Translation Memory deduplication logic.
   - Token masking (URLs, emails, and numbers).
   - Format converter mappings.
   - File compressor scratch buffer cleanup.
2. Execute Gradle verification:
   ```bash
   ./gradlew testDebugUnitTest
   ./gradlew assembleDebug
   ```
3. Verify zero memory leaks during 100-page simulated streaming.

Start by creating the Gradle configuration files and directory structure in `android-app/`, then implement the data, domain, and Compose presentation layers.
```

