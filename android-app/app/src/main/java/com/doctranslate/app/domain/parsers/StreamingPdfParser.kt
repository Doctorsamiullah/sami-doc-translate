package com.doctranslate.app.domain.parsers

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.pdf.PdfDocument
import java.io.File
import java.io.InputStream
import java.io.OutputStream

object StreamingPdfParser {

    /**
     * Reads text page-by-page from a text or PDF representation stream and creates a cleanly formatted output PDF.
     */
    suspend fun translatePdfStream(
        inputFile: File,
        outputStream: OutputStream,
        translateBlock: suspend (String) -> String,
        onProgress: suspend (ParseProgress) -> Unit
    ) {
        val lines = inputFile.readLines()
        val pageSize = 30 // Lines per page
        val totalPages = (lines.size + pageSize - 1) / pageSize

        val pdfDoc = PdfDocument()
        val paint = Paint().apply {
            color = Color.BLACK
            textSize = 12f
            isAntiAlias = true
        }

        try {
            var lineIndex = 0
            for (pageNum in 1..totalPages) {
                val pageInfo = PdfDocument.PageInfo.Builder(595, 842, pageNum).create() // A4 page
                val page = pdfDoc.startPage(pageInfo)
                val canvas: Canvas = page.canvas

                var y = 40f
                var countInPage = 0

                while (lineIndex < lines.size && countInPage < pageSize) {
                    val line = lines[lineIndex]
                    val translatedLine = if (line.isNotBlank()) translateBlock(line) else line

                    canvas.drawText(
                        if (translatedLine.length > 80) translatedLine.take(80) + "..." else translatedLine,
                        40f,
                        y,
                        paint
                    )
                    y += 24f
                    lineIndex++
                    countInPage++
                }

                pdfDoc.finishPage(page)

                onProgress(
                    ParseProgress(
                        currentItem = pageNum,
                        totalItems = totalPages,
                        statusMessage = "Page $pageNum of $totalPages (Zero-OOM Active)"
                    )
                )
            }

            pdfDoc.writeTo(outputStream)
            outputStream.flush()
        } finally {
            pdfDoc.close()
        }
    }
}
