package com.doctranslate.app.presentation.viewmodel

import android.app.Application
import android.content.Context
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.doctranslate.app.data.local.AppDatabase
import com.doctranslate.app.data.local.entities.HistoryEntity
import com.doctranslate.app.data.saf.SAFHelper
import com.doctranslate.app.domain.compressor.CompressionResult
import com.doctranslate.app.domain.compressor.SmartFileCompressor
import com.doctranslate.app.domain.converter.FormatConverter
import com.doctranslate.app.domain.converter.SupportedFormat
import com.doctranslate.app.domain.parsers.StreamingDocxParser
import com.doctranslate.app.domain.parsers.StreamingPdfParser
import com.doctranslate.app.domain.parsers.StreamingTextParser
import com.doctranslate.app.domain.translation.MLKitTranslationEngine
import com.doctranslate.app.domain.tts.TTSManager
import com.doctranslate.app.presentation.theme.RainbowTheme
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File
import java.io.FileOutputStream

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val db = AppDatabase.getInstance(application)
    private val translationEngine = MLKitTranslationEngine(db.tmDao())
    val ttsManager = TTSManager(application)

    val historyList = db.historyDao().getAllHistory()

    private val _currentTheme = MutableStateFlow(RainbowTheme.VIBRANT)
    val currentTheme: StateFlow<RainbowTheme> = _currentTheme.asStateFlow()

    private val _selectedUri = MutableStateFlow<Uri?>(null)
    val selectedUri: StateFlow<Uri?> = _selectedUri.asStateFlow()

    private val _selectedFileName = MutableStateFlow<String?>(null)
    val selectedFileName: StateFlow<String?> = _selectedFileName.asStateFlow()

    private val _selectedFileSize = MutableStateFlow<Long>(0L)
    val selectedFileSize: StateFlow<Long> = _selectedFileSize.asStateFlow()

    private val _sourceLang = MutableStateFlow("en")
    val sourceLang: StateFlow<String> = _sourceLang.asStateFlow()

    private val _targetLang = MutableStateFlow("hi")
    val targetLang: StateFlow<String> = _targetLang.asStateFlow()

    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()

    private val _progressFraction = MutableStateFlow(0f)
    val progressFraction: StateFlow<Float> = _progressFraction.asStateFlow()

    private val _statusMessage = MutableStateFlow("")
    val statusMessage: StateFlow<String> = _statusMessage.asStateFlow()

    private val _enModelDownloaded = MutableStateFlow(false)
    val enModelDownloaded: StateFlow<Boolean> = _enModelDownloaded.asStateFlow()

    private val _hiModelDownloaded = MutableStateFlow(false)
    val hiModelDownloaded: StateFlow<Boolean> = _hiModelDownloaded.asStateFlow()

    private val _tmCount = MutableStateFlow(0)
    val tmCount: StateFlow<Int> = _tmCount.asStateFlow()

    // Conversion state
    private val _targetConvertFormat = MutableStateFlow(SupportedFormat.PDF)
    val targetConvertFormat: StateFlow<SupportedFormat> = _targetConvertFormat.asStateFlow()

    private val _translateOnConvert = MutableStateFlow(false)
    val translateOnConvert: StateFlow<Boolean> = _translateOnConvert.asStateFlow()

    // Compression state
    private val _targetCompressMB = MutableStateFlow(2.0f)
    val targetCompressMB: StateFlow<Float> = _targetCompressMB.asStateFlow()

    private val _preserveReadability = MutableStateFlow(true)
    val preserveReadability: StateFlow<Boolean> = _preserveReadability.asStateFlow()

    private val _lastCompressedResult = MutableStateFlow<CompressionResult?>(null)
    val lastCompressedResult: StateFlow<CompressionResult?> = _lastCompressedResult.asStateFlow()

    init {
        checkModelsAndTM()
    }

    fun setTheme(theme: RainbowTheme) {
        _currentTheme.value = theme
    }

    fun setSelectedFile(context: Context, uri: Uri?) {
        _selectedUri.value = uri
        if (uri != null) {
            val metadata = SAFHelper.getFileMetadata(context, uri)
            _selectedFileName.value = metadata.name
            _selectedFileSize.value = metadata.size
        } else {
            _selectedFileName.value = null
            _selectedFileSize.value = 0L
        }
    }

    fun swapLanguages() {
        val temp = _sourceLang.value
        _sourceLang.value = _targetLang.value
        _targetLang.value = temp
    }

    fun checkModelsAndTM() {
        viewModelScope.launch(Dispatchers.IO) {
            _enModelDownloaded.value = translationEngine.isModelDownloaded("en")
            _hiModelDownloaded.value = translationEngine.isModelDownloaded("hi")
            _tmCount.value = db.tmDao().getCount()
        }
    }

    fun downloadModels() {
        viewModelScope.launch(Dispatchers.IO) {
            _statusMessage.value = "Downloading ML Kit language packs..."
            val enSuccess = translationEngine.downloadModel("en")
            val hiSuccess = translationEngine.downloadModel("hi")
            _enModelDownloaded.value = enSuccess
            _hiModelDownloaded.value = hiSuccess
            _statusMessage.value = if (enSuccess && hiSuccess) "Models ready offline!" else "Failed to download models"
        }
    }

    fun setTargetConvertFormat(format: SupportedFormat) {
        _targetConvertFormat.value = format
    }

    fun setTranslateOnConvert(enable: Boolean) {
        _translateOnConvert.value = enable
    }

    fun setTargetCompressMB(mb: Float) {
        _targetCompressMB.value = mb
    }

    fun setPreserveReadability(preserve: Boolean) {
        _preserveReadability.value = preserve
    }

    fun startTranslation(context: Context) {
        val uri = _selectedUri.value ?: return
        val fileName = _selectedFileName.value ?: "document"

        viewModelScope.launch(Dispatchers.IO) {
            _isProcessing.value = true
            _progressFraction.value = 0.05f
            _statusMessage.value = "Starting translation for $fileName..."

            try {
                val tempInput = SAFHelper.copyToTempFile(context, uri)
                val ext = fileName.substringAfterLast('.', "txt").lowercase()
                val outputFile = SAFHelper.createTempOutputFile(context, fileName, "translated", ext)

                val src = _sourceLang.value
                val tgt = _targetLang.value

                when (ext) {
                    "docx" -> {
                        tempInput.inputStream().use { input ->
                            FileOutputStream(outputFile).use { output ->
                                StreamingDocxParser.translateDocxStream(
                                    inputStream = input,
                                    outputStream = output,
                                    translateBlock = { text -> translationEngine.translateText(text, src, tgt) },
                                    onProgress = { p ->
                                        val total = if (p.totalItems > 0) p.totalItems else 100
                                        _progressFraction.value = (p.currentItem.toFloat() / total).coerceIn(0f, 1f)
                                        _statusMessage.value = "Translating $fileName: ${p.currentItem}/$total (Zero-OOM Active)"
                                    }
                                )
                            }
                        }
                    }
                    "pdf" -> {
                        FileOutputStream(outputFile).use { output ->
                            StreamingPdfParser.translatePdfStream(
                                inputFile = tempInput,
                                outputStream = output,
                                translateBlock = { text -> translationEngine.translateText(text, src, tgt) },
                                onProgress = { p ->
                                    val total = if (p.totalItems > 0) p.totalItems else 100
                                    _progressFraction.value = (p.currentItem.toFloat() / total).coerceIn(0f, 1f)
                                    _statusMessage.value = "Translating $fileName: Page ${p.currentItem}/$total (Zero-OOM Active)"
                                }
                            )
                        }
                    }
                    else -> {
                        tempInput.inputStream().use { input ->
                            FileOutputStream(outputFile).use { output ->
                                StreamingTextParser.translateTextStream(
                                    inputStream = input,
                                    outputStream = output,
                                    translateBlock = { text -> translationEngine.translateText(text, src, tgt) },
                                    onProgress = { p ->
                                        _statusMessage.value = p.statusMessage
                                        _progressFraction.value = 0.5f
                                    }
                                )
                            }
                        }
                    }
                }

                db.historyDao().insert(
                    HistoryEntity(
                        fileName = fileName,
                        fileType = ext.uppercase(),
                        operationType = "TRANSLATION",
                        sourceLang = src,
                        targetLang = tgt,
                        originalSize = _selectedFileSize.value,
                        processedSize = outputFile.length(),
                        outputUri = outputFile.absolutePath,
                        translatedTextSample = "Translated $fileName ($src -> $tgt)"
                    )
                )

                _progressFraction.value = 1.0f
                _statusMessage.value = "Translation completed successfully!"
                _tmCount.value = db.tmDao().getCount()
                SAFHelper.clearCache(context)
            } catch (e: Exception) {
                e.printStackTrace()
                _statusMessage.value = "Error: ${e.localizedMessage}"
            } finally {
                _isProcessing.value = false
            }
        }
    }

    fun startConversion(context: Context) {
        val uri = _selectedUri.value ?: return
        val fileName = _selectedFileName.value ?: "document"

        viewModelScope.launch(Dispatchers.IO) {
            _isProcessing.value = true
            _progressFraction.value = 0.1f
            _statusMessage.value = "Converting $fileName..."

            try {
                val tempInput = SAFHelper.copyToTempFile(context, uri)
                val targetFormat = _targetConvertFormat.value
                val targetExt = targetFormat.name.lowercase()
                val outputFile = SAFHelper.createTempOutputFile(context, fileName, "converted", targetExt)

                val shouldTranslate = _translateOnConvert.value
                val src = _sourceLang.value
                val tgt = _targetLang.value

                val translateBlock: (suspend (String) -> String)? = if (shouldTranslate) {
                    { text -> translationEngine.translateText(text, src, tgt) }
                } else null

                FormatConverter.convert(
                    inputFile = tempInput,
                    outputFile = outputFile,
                    targetFormat = targetFormat,
                    translateBlock = translateBlock
                )

                db.historyDao().insert(
                    HistoryEntity(
                        fileName = fileName,
                        fileType = targetFormat.name,
                        operationType = if (shouldTranslate) "CONVERT & TRANSLATE" else "CONVERSION",
                        sourceLang = if (shouldTranslate) src else null,
                        targetLang = if (shouldTranslate) tgt else null,
                        originalSize = _selectedFileSize.value,
                        processedSize = outputFile.length(),
                        outputUri = outputFile.absolutePath,
                        translatedTextSample = "Converted $fileName to $targetFormat"
                    )
                )

                _progressFraction.value = 1.0f
                _statusMessage.value = "Conversion completed successfully!"
                SAFHelper.clearCache(context)
            } catch (e: Exception) {
                e.printStackTrace()
                _statusMessage.value = "Error: ${e.localizedMessage}"
            } finally {
                _isProcessing.value = false
            }
        }
    }

    fun startCompression(context: Context) {
        val uri = _selectedUri.value ?: return
        val fileName = _selectedFileName.value ?: "document"

        viewModelScope.launch(Dispatchers.IO) {
            _isProcessing.value = true
            _progressFraction.value = 0.2f
            _statusMessage.value = "Compressing $fileName..."

            try {
                val tempInput = SAFHelper.copyToTempFile(context, uri)
                val targetBytes = (_targetCompressMB.value * 1024 * 1024).toLong()

                val result = SmartFileCompressor.compressFile(
                    context = context,
                    inputFile = tempInput,
                    targetSizeBytes = targetBytes,
                    preserveReadability = _preserveReadability.value
                )

                _lastCompressedResult.value = result

                db.historyDao().insert(
                    HistoryEntity(
                        fileName = fileName,
                        fileType = fileName.substringAfterLast('.').uppercase(),
                        operationType = "COMPRESSION",
                        originalSize = result.originalSizeBytes,
                        processedSize = result.compressedSizeBytes,
                        outputUri = result.outputFile.absolutePath,
                        translatedTextSample = "Compressed to %.2f MB".format(result.compressedSizeBytes / (1024f * 1024f))
                    )
                )

                _progressFraction.value = 1.0f
                _statusMessage.value = "Compression complete! (Target Met: ${result.isTargetMet})"
            } catch (e: Exception) {
                e.printStackTrace()
                _statusMessage.value = "Error: ${e.localizedMessage}"
            } finally {
                _isProcessing.value = false
            }
        }
    }

    fun speakHindiText(text: String) {
        ttsManager.speak(text, "hi")
    }

    fun stopTTS() {
        ttsManager.stop()
    }

    fun clearHistory() {
        viewModelScope.launch(Dispatchers.IO) {
            db.historyDao().clearAll()
        }
    }

    override fun onCleared() {
        super.onCleared()
        translationEngine.close()
        ttsManager.shutdown()
    }
}
