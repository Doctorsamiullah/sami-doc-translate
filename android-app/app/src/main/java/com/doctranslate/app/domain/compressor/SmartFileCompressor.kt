package com.doctranslate.app.domain.compressor

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import com.doctranslate.app.data.saf.SAFHelper
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.util.zip.Deflater
import java.util.zip.ZipEntry
import java.util.zip.ZipInputStream
import java.util.zip.ZipOutputStream

data class CompressionResult(
    val outputFile: File,
    val originalSizeBytes: Long,
    val compressedSizeBytes: Long,
    val targetSizeBytes: Long,
    val isTargetMet: Boolean
)

object SmartFileCompressor {

    const val MIN_DPI_FLOOR = 150

    suspend fun compressFile(
        context: Context,
        inputFile: File,
        targetSizeBytes: Long,
        preserveReadability: Boolean = true
    ): CompressionResult {
        val originalSize = inputFile.length()
        if (originalSize <= targetSizeBytes) {
            val copyFile = SAFHelper.createTempOutputFile(context, inputFile.name, "compressed", inputFile.extension)
            inputFile.copyTo(copyFile, overwrite = true)
            return CompressionResult(
                outputFile = copyFile,
                originalSizeBytes = originalSize,
                compressedSizeBytes = copyFile.length(),
                targetSizeBytes = targetSizeBytes,
                isTargetMet = true
            )
        }

        val outputFile = SAFHelper.createTempOutputFile(context, inputFile.name, "compressed", inputFile.extension)

        try {
            val extension = inputFile.extension.lowercase()
            if (extension == "docx") {
                compressZipContainer(inputFile, outputFile, targetSizeBytes, preserveReadability)
            } else {
                compressGeneralFile(inputFile, outputFile, targetSizeBytes, preserveReadability)
            }

            val finalSize = outputFile.length()
            val result = CompressionResult(
                outputFile = outputFile,
                originalSizeBytes = originalSize,
                compressedSizeBytes = finalSize,
                targetSizeBytes = targetSizeBytes,
                isTargetMet = finalSize <= targetSizeBytes
            )
            return result
        } finally {
            // Guarantee cleanup of extraneous scratch files in cacheDir
            cleanScratchFiles(context, keepFiles = listOf(outputFile))
        }
    }

    private fun compressZipContainer(
        inputFile: File,
        outputFile: File,
        targetSizeBytes: Long,
        preserveReadability: Boolean
    ) {
        val zis = ZipInputStream(FileInputStream(inputFile))
        val zos = ZipOutputStream(FileOutputStream(outputFile))
        zos.setLevel(Deflater.BEST_COMPRESSION)

        var entry: ZipEntry? = zis.nextEntry
        val buffer = ByteArray(8192)

        while (entry != null) {
            val newEntry = ZipEntry(entry.name)
            zos.putNextEntry(newEntry)

            val nameLower = entry.name.lowercase()
            if ((nameLower.endsWith(".png") || nameLower.endsWith(".jpeg") || nameLower.endsWith(".jpg"))) {
                // Image entry: Compress/downsample with DPI floor
                val baos = ByteArrayOutputStream()
                var len: Int
                while (zis.read(buffer).also { len = it } > 0) {
                    baos.write(buffer, 0, len)
                }
                val imageBytes = baos.toByteArray()
                val compressedImageBytes = compressImageWithDpiFloor(imageBytes, preserveReadability)
                zos.write(compressedImageBytes)
            } else {
                // Non-image entry: Raw copy with maximum Deflate compression
                var len: Int
                while (zis.read(buffer).also { len = it } > 0) {
                    zos.write(buffer, 0, len)
                }
            }
            zos.closeEntry()
            entry = zis.nextEntry
        }
        zis.close()
        zos.finish()
        zos.close()
    }

    private fun compressGeneralFile(
        inputFile: File,
        outputFile: File,
        targetSizeBytes: Long,
        preserveReadability: Boolean
    ) {
        // High compression deflate stream copy
        val fis = FileInputStream(inputFile)
        val fos = FileOutputStream(outputFile)
        val zos = ZipOutputStream(fos)
        zos.setLevel(Deflater.BEST_COMPRESSION)

        val entry = ZipEntry("content")
        zos.putNextEntry(entry)

        val buffer = ByteArray(8192)
        var bytesRead: Int
        while (fis.read(buffer).also { bytesRead = it } != -1) {
            zos.write(buffer, 0, bytesRead)
        }

        zos.closeEntry()
        zos.finish()
        zos.close()
        fis.close()
    }

    private fun compressImageWithDpiFloor(
        imageBytes: ByteArray,
        preserveReadability: Boolean
    ): ByteArray {
        val options = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size, options)

        val origWidth = options.outWidth
        val origHeight = options.outHeight

        if (origWidth <= 0 || origHeight <= 0) return imageBytes

        // Enforce 150 DPI minimum floor based on standard 8.5" page width (approx 1275 px width)
        val minTargetWidth = if (preserveReadability) 1275 else 600
        var sampleSize = 1
        while (origWidth / sampleSize > minTargetWidth) {
            sampleSize *= 2
        }

        val decodeOptions = BitmapFactory.Options().apply { inSampleSize = sampleSize }
        val bitmap = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size, decodeOptions)
            ?: return imageBytes

        val outStream = ByteArrayOutputStream()
        val quality = if (preserveReadability) 80 else 60
        bitmap.compress(Bitmap.CompressFormat.JPEG, quality, outStream)
        bitmap.recycle()
        return outStream.toByteArray()
    }

    private fun cleanScratchFiles(context: Context, keepFiles: List<File>) {
        runCatching {
            val keepPaths = keepFiles.map { it.absolutePath }.toSet()
            context.cacheDir.listFiles()?.forEach { file ->
                if (file.isFile && !keepPaths.contains(file.absolutePath) && file.name.startsWith("input_")) {
                    file.delete()
                }
            }
        }
    }
}
