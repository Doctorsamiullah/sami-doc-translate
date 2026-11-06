package com.doctranslate.app.domain.worker

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.pm.ServiceInfo
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.CoroutineWorker
import androidx.work.ForegroundInfo
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import com.doctranslate.app.data.local.AppDatabase
import com.doctranslate.app.data.local.entities.HistoryEntity
import com.doctranslate.app.data.saf.SAFHelper
import com.doctranslate.app.domain.parsers.StreamingDocxParser
import com.doctranslate.app.domain.parsers.StreamingPdfParser
import com.doctranslate.app.domain.parsers.StreamingTextParser
import com.doctranslate.app.domain.translation.MLKitTranslationEngine
import java.io.File
import java.io.FileOutputStream

class TranslationWorker(
    private val appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    companion object {
        const val CHANNEL_ID = "doc_translate_channel"
        const val NOTIFICATION_ID = 1001
        const val KEY_INPUT_URI = "key_input_uri"
        const val KEY_SOURCE_LANG = "key_source_lang"
        const val KEY_TARGET_LANG = "key_target_lang"
        const val KEY_PROGRESS = "key_progress"
        const val KEY_STATUS = "key_status"
        const val KEY_OUTPUT_PATH = "key_output_path"
    }

    private val db = AppDatabase.getInstance(appContext)
    private val translationEngine = MLKitTranslationEngine(db.tmDao())

    override suspend fun doWork(): Result {
        val uriString = inputData.getString(KEY_INPUT_URI) ?: return Result.failure()
        val sourceLang = inputData.getString(KEY_SOURCE_LANG) ?: "en"
        val targetLang = inputData.getString(KEY_TARGET_LANG) ?: "hi"

        val uri = Uri.parse(uriString)
        val metadata = SAFHelper.getFileMetadata(appContext, uri)
        val tempInputFile = SAFHelper.copyToTempFile(appContext, uri)

        createNotificationChannel()
        val initialNotification = createForegroundInfo("Starting translation for ${metadata.name}...")
        setForeground(initialNotification)

        val extension = metadata.name.substringAfterLast('.', "txt").lowercase()
        val outputFile = SAFHelper.createTempOutputFile(appContext, metadata.name, "translated", extension)

        return try {
            when (extension) {
                "docx" -> {
                    tempInputFile.inputStream().use { input ->
                        FileOutputStream(outputFile).use { output ->
                            StreamingDocxParser.translateDocxStream(
                                inputStream = input,
                                outputStream = output,
                                translateBlock = { text ->
                                    translationEngine.translateText(text, sourceLang, targetLang)
                                },
                                onProgress = { progress ->
                                    updateNotificationAndProgress(
                                        metadata.name,
                                        progress.currentItem,
                                        progress.totalItems,
                                        progress.statusMessage
                                    )
                                }
                            )
                        }
                    }
                }
                "pdf" -> {
                    FileOutputStream(outputFile).use { output ->
                        StreamingPdfParser.translatePdfStream(
                            inputFile = tempInputFile,
                            outputStream = output,
                            translateBlock = { text ->
                                translationEngine.translateText(text, sourceLang, targetLang)
                            },
                            onProgress = { progress ->
                                updateNotificationAndProgress(
                                    metadata.name,
                                    progress.currentItem,
                                    progress.totalItems,
                                    progress.statusMessage
                                )
                            }
                        )
                    }
                }
                else -> {
                    tempInputFile.inputStream().use { input ->
                        FileOutputStream(outputFile).use { output ->
                            StreamingTextParser.translateTextStream(
                                inputStream = input,
                                outputStream = output,
                                translateBlock = { text ->
                                    translationEngine.translateText(text, sourceLang, targetLang)
                                },
                                onProgress = { progress ->
                                    updateNotificationAndProgress(
                                        metadata.name,
                                        progress.currentItem,
                                        progress.totalItems,
                                        progress.statusMessage
                                    )
                                }
                            )
                        }
                    }
                }
            }

            // Save History Entry
            db.historyDao().insert(
                HistoryEntity(
                    fileName = metadata.name,
                    fileType = extension.uppercase(),
                    operationType = "TRANSLATION",
                    sourceLang = sourceLang,
                    targetLang = targetLang,
                    originalSize = metadata.size,
                    processedSize = outputFile.length(),
                    outputUri = outputFile.absolutePath,
                    translatedTextSample = "Translated ${metadata.name} to $targetLang"
                )
            )

            // Auto-clear temporary scratch cache
            SAFHelper.clearCache(appContext)

            Result.success(workDataOf(KEY_OUTPUT_PATH to outputFile.absolutePath))
        } catch (e: Exception) {
            e.printStackTrace()
            Result.failure(workDataOf(KEY_STATUS to "Error: ${e.localizedMessage}"))
        } finally {
            translationEngine.close()
        }
    }

    private suspend fun updateNotificationAndProgress(
        fileName: String,
        current: Int,
        total: Int,
        statusText: String
    ) {
        val totalDisplay = if (total > 0) total.toString() else "∞"
        val message = "Translating $fileName: Page $current of $totalDisplay (Zero-OOM Active)"
        setProgress(workDataOf(KEY_PROGRESS to current, KEY_STATUS to message))

        val notificationManager = appContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val notification = NotificationCompat.Builder(appContext, CHANNEL_ID)
            .setContentTitle("DocTranslate Active")
            .setContentText(message)
            .setSmallIcon(android.R.drawable.ic_menu_upload)
            .setOngoing(true)
            .setProgress(if (total > 0) total else 100, if (total > 0) current else 50, total <= 0)
            .build()

        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    private fun createForegroundInfo(statusMessage: String): ForegroundInfo {
        val notification = NotificationCompat.Builder(appContext, CHANNEL_ID)
            .setContentTitle("DocTranslate Active")
            .setContentText(statusMessage)
            .setSmallIcon(android.R.drawable.ic_menu_upload)
            .setOngoing(true)
            .build()

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ForegroundInfo(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
        } else {
            ForegroundInfo(NOTIFICATION_ID, notification)
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "DocTranslate Work Channel",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = appContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }
}
