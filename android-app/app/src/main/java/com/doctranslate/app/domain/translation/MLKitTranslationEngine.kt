package com.doctranslate.app.domain.translation

import com.doctranslate.app.data.local.dao.TMDao
import com.doctranslate.app.data.local.entities.TMEntity
import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.common.model.RemoteModelManager
import com.google.mlkit.nl.translate.TranslateLanguage
import com.google.mlkit.nl.translate.TranslateRemoteModel
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.Translator
import com.google.mlkit.nl.translate.TranslatorOptions
import kotlinx.coroutines.tasks.await
import java.security.MessageDigest

class MLKitTranslationEngine(private val tmDao: TMDao? = null) {

    private val modelManager = RemoteModelManager.getInstance()

    private var enHiTranslator: Translator? = null
    private var hiEnTranslator: Translator? = null

    init {
        val enHiOptions = TranslatorOptions.Builder()
            .setSourceLanguage(TranslateLanguage.ENGLISH)
            .setTargetLanguage(TranslateLanguage.HINDI)
            .build()
        enHiTranslator = Translation.getClient(enHiOptions)

        val hiEnOptions = TranslatorOptions.Builder()
            .setSourceLanguage(TranslateLanguage.HINDI)
            .setTargetLanguage(TranslateLanguage.ENGLISH)
            .build()
        hiEnTranslator = Translation.getClient(hiEnOptions)
    }

    suspend fun isModelDownloaded(langCode: String): Boolean {
        val translateLang = if (langCode.equals("hi", ignoreCase = true)) TranslateLanguage.HINDI else TranslateLanguage.ENGLISH
        val model = TranslateRemoteModel.Builder(translateLang).build()
        return try {
            modelManager.isModelDownloaded(model).await()
        } catch (e: Exception) {
            false
        }
    }

    suspend fun downloadModel(langCode: String): Boolean {
        val translateLang = if (langCode.equals("hi", ignoreCase = true)) TranslateLanguage.HINDI else TranslateLanguage.ENGLISH
        val model = TranslateRemoteModel.Builder(translateLang).build()
        val conditions = DownloadConditions.Builder().build()
        return try {
            modelManager.download(model, conditions).await()
            true
        } catch (e: Exception) {
            false
        }
    }

    suspend fun translateText(
        text: String,
        sourceLang: String, // "en" or "hi"
        targetLang: String  // "hi" or "en"
    ): String {
        if (text.isBlank()) return text

        val normalizedSrc = sourceLang.lowercase()
        val normalizedTgt = targetLang.lowercase()

        // 1. Translation Memory Lookup
        val hash = computeHash(text)
        tmDao?.findTranslation(hash, normalizedSrc, normalizedTgt)?.let { cached ->
            return cached.targetText
        }

        // 2. Token Masking (URLs, emails, numbers)
        val maskResult = TokenMasker.mask(text)

        // 3. Select ML Kit Translator Client
        val translator: Translator = (when {
            normalizedSrc == "en" && normalizedTgt == "hi" -> enHiTranslator
            normalizedSrc == "hi" && normalizedTgt == "en" -> hiEnTranslator
            else -> null
        }) ?: throw IllegalArgumentException("Unsupported language pair: $sourceLang -> $targetLang")

        // 4. Translate masked text
        val rawTranslation = try {
            translator.translate(maskResult.maskedText).await()
        } catch (e: Exception) {
            throw e
        }

        // 5. Unmask
        val finalTranslation = TokenMasker.unmask(rawTranslation, maskResult.tokenMap)

        // 6. Save to TM
        tmDao?.insert(
            TMEntity(
                sourceText = text,
                targetText = finalTranslation,
                sourceLang = normalizedSrc,
                targetLang = normalizedTgt,
                hash = hash
            )
        )

        return finalTranslation
    }

    private fun computeHash(text: String): String {
        val md = MessageDigest.getInstance("SHA-256")
        val digest = md.digest(text.trim().toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02x".format(it) }
    }

    fun close() {
        enHiTranslator?.close()
        hiEnTranslator?.close()
    }
}
