package com.doctranslate.app.data.saf

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream

data class FileMetadata(
    val name: String,
    val size: Long,
    val mimeType: String?
)

object SAFHelper {

    fun getFileMetadata(context: Context, uri: Uri): FileMetadata {
        var name = "unknown_document"
        var size = 0L
        val mimeType = context.contentResolver.getType(uri)

        context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            val sizeIndex = cursor.getColumnIndex(OpenableColumns.SIZE)
            if (cursor.moveToFirst()) {
                if (nameIndex != -1) name = cursor.getString(nameIndex) ?: name
                if (sizeIndex != -1) size = cursor.getLong(sizeIndex)
            }
        }

        return FileMetadata(name, size, mimeType)
    }

    fun copyToTempFile(context: Context, uri: Uri, prefix: String = "input_"): File {
        val metadata = getFileMetadata(context, uri)
        val ext = metadata.name.substringAfterLast('.', "tmp")
        val tempFile = File.createTempFile(prefix, ".$ext", context.cacheDir)
        tempFile.deleteOnExit()

        context.contentResolver.openInputStream(uri)?.use { input ->
            FileOutputStream(tempFile).use { output ->
                input.copyTo(output)
            }
        }
        return tempFile
    }

    fun openInputStream(context: Context, uri: Uri): InputStream? {
        return context.contentResolver.openInputStream(uri)
    }

    fun createTempOutputFile(context: Context, originalName: String, suffixTag: String, extension: String): File {
        val baseName = originalName.substringBeforeLast('.')
        val fileName = "${baseName}_${suffixTag}.$extension"
        val outFile = File(context.cacheDir, fileName)
        if (outFile.exists()) outFile.delete()
        return outFile
    }

    fun clearCache(context: Context) {
        runCatching {
            context.cacheDir.listFiles()?.forEach { file ->
                if (file.isFile) file.delete()
            }
        }
    }
}
