package com.doctranslate.app.domain.parsers

import org.apache.poi.xwpf.usermodel.XWPFDocument
import java.io.InputStream
import java.io.OutputStream

data class ParseProgress(
    val currentItem: Int,
    val totalItems: Int,
    val statusMessage: String
)

object StreamingDocxParser {

    suspend fun translateDocxStream(
        inputStream: InputStream,
        outputStream: OutputStream,
        translateBlock: suspend (String) -> String,
        onProgress: suspend (ParseProgress) -> Unit
    ) {
        val doc = XWPFDocument(inputStream)
        try {
            val paragraphs = doc.paragraphs
            val totalParagraphs = paragraphs.size
            val tables = doc.tables
            var currentCount = 0

            // Process paragraphs
            for ((index, paragraph) in paragraphs.withIndex()) {
                val text = paragraph.paragraphText
                if (text.isNotBlank()) {
                    val translated = translateBlock(text)
                    // Clear existing runs and replace with translated text
                    while (paragraph.runs.size > 0) {
                        paragraph.removeRun(0)
                    }
                    val newRun = paragraph.createRun()
                    newRun.setText(translated)
                }
                currentCount++
                onProgress(
                    ParseProgress(
                        currentItem = currentCount,
                        totalItems = totalParagraphs + tables.size,
                        statusMessage = "Processing paragraph $currentCount of $totalParagraphs"
                    )
                )
            }

            // Process tables
            for (table in tables) {
                for (row in table.rows) {
                    for (cell in row.tableCells) {
                        val cellText = cell.text
                        if (cellText.isNotBlank()) {
                            val translated = translateBlock(cellText)
                            cell.removeParagraph(0)
                            val p = cell.addParagraph()
                            val r = p.createRun()
                            r.setText(translated)
                        }
                    }
                }
                currentCount++
                onProgress(
                    ParseProgress(
                        currentItem = currentCount,
                        totalItems = totalParagraphs + tables.size,
                        statusMessage = "Processing tables..."
                    )
                )
            }

            doc.write(outputStream)
            outputStream.flush()
        } finally {
            doc.close()
        }
    }
}
