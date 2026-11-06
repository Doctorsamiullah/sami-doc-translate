package com.doctranslate.app.domain.converter

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.pdf.PdfDocument
import org.apache.poi.xwpf.usermodel.XWPFDocument
import java.io.BufferedReader
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.InputStreamReader

enum class SupportedFormat {
    DOCX, PDF, TXT, CSV
}

object FormatConverter {

    suspend fun convert(
        inputFile: File,
        outputFile: File,
        targetFormat: SupportedFormat,
        translateBlock: (suspend (String) -> String)? = null
    ) {
        val ext = inputFile.extension.lowercase()
        val sourceFormat = when (ext) {
            "docx" -> SupportedFormat.DOCX
            "pdf" -> SupportedFormat.PDF
            "csv" -> SupportedFormat.CSV
            else -> SupportedFormat.TXT
        }

        if (sourceFormat == targetFormat && translateBlock == null) {
            inputFile.copyTo(outputFile, overwrite = true)
            return
        }

        when (sourceFormat) {
            SupportedFormat.TXT, SupportedFormat.CSV -> {
                convertTextSource(inputFile, outputFile, sourceFormat, targetFormat, translateBlock)
            }
            SupportedFormat.DOCX -> {
                convertDocxSource(inputFile, outputFile, targetFormat, translateBlock)
            }
            SupportedFormat.PDF -> {
                convertPdfSource(inputFile, outputFile, targetFormat, translateBlock)
            }
        }
    }

    private suspend fun convertTextSource(
        inputFile: File,
        outputFile: File,
        sourceFormat: SupportedFormat,
        targetFormat: SupportedFormat,
        translateBlock: (suspend (String) -> String)?
    ) {
        val lines = inputFile.readLines()

        when (targetFormat) {
            SupportedFormat.TXT, SupportedFormat.CSV -> {
                outputFile.bufferedWriter().use { writer ->
                    for (line in lines) {
                        val processed = if (translateBlock != null && line.isNotBlank()) {
                            translateBlock(line)
                        } else line
                        writer.write(processed)
                        writer.newLine()
                    }
                }
            }
            SupportedFormat.DOCX -> {
                val doc = XWPFDocument()
                for (line in lines) {
                    val processed = if (translateBlock != null && line.isNotBlank()) {
                        translateBlock(line)
                    } else line
                    val p = doc.createParagraph()
                    val r = p.createRun()
                    r.setText(processed)
                }
                FileOutputStream(outputFile).use { out -> doc.write(out) }
                doc.close()
            }
            SupportedFormat.PDF -> {
                writeLinesToPdf(lines, outputFile, translateBlock)
            }
        }
    }

    private suspend fun convertDocxSource(
        inputFile: File,
        outputFile: File,
        targetFormat: SupportedFormat,
        translateBlock: (suspend (String) -> String)?
    ) {
        val extractedLines = mutableListOf<String>()
        FileInputStream(inputFile).use { fis ->
            val doc = XWPFDocument(fis)
            for (p in doc.paragraphs) {
                extractedLines.add(p.paragraphText)
            }
            doc.close()
        }

        when (targetFormat) {
            SupportedFormat.TXT, SupportedFormat.CSV -> {
                outputFile.bufferedWriter().use { writer ->
                    for (line in extractedLines) {
                        val processed = if (translateBlock != null && line.isNotBlank()) {
                            translateBlock(line)
                        } else line
                        writer.write(processed)
                        writer.newLine()
                    }
                }
            }
            SupportedFormat.DOCX -> {
                val doc = XWPFDocument()
                for (line in extractedLines) {
                    val processed = if (translateBlock != null && line.isNotBlank()) {
                        translateBlock(line)
                    } else line
                    val p = doc.createParagraph()
                    val r = p.createRun()
                    r.setText(processed)
                }
                FileOutputStream(outputFile).use { out -> doc.write(out) }
                doc.close()
            }
            SupportedFormat.PDF -> {
                writeLinesToPdf(extractedLines, outputFile, translateBlock)
            }
        }
    }

    private suspend fun convertPdfSource(
        inputFile: File,
        outputFile: File,
        targetFormat: SupportedFormat,
        translateBlock: (suspend (String) -> String)?
    ) {
        // Simple PDF plain text extraction or representation
        val lines = runCatching { inputFile.readLines() }.getOrDefault(listOf("PDF Content"))
        when (targetFormat) {
            SupportedFormat.TXT, SupportedFormat.CSV -> {
                outputFile.bufferedWriter().use { writer ->
                    for (line in lines) {
                        val processed = if (translateBlock != null && line.isNotBlank()) {
                            translateBlock(line)
                        } else line
                        writer.write(processed)
                        writer.newLine()
                    }
                }
            }
            SupportedFormat.DOCX -> {
                val doc = XWPFDocument()
                for (line in lines) {
                    val processed = if (translateBlock != null && line.isNotBlank()) {
                        translateBlock(line)
                    } else line
                    val p = doc.createParagraph()
                    val r = p.createRun()
                    r.setText(processed)
                }
                FileOutputStream(outputFile).use { out -> doc.write(out) }
                doc.close()
            }
            SupportedFormat.PDF -> {
                writeLinesToPdf(lines, outputFile, translateBlock)
            }
        }
    }

    private suspend fun writeLinesToPdf(
        lines: List<String>,
        outputFile: File,
        translateBlock: (suspend (String) -> String)?
    ) {
        val pdfDoc = PdfDocument()
        val paint = Paint().apply {
            color = Color.BLACK
            textSize = 12f
            isAntiAlias = true
        }
        val linesPerPage = 30
        val totalPages = (lines.size + linesPerPage - 1).coerceAtLeast(1) / linesPerPage

        var lineIdx = 0
        for (pNum in 1..totalPages.coerceAtLeast(1)) {
            val pageInfo = PdfDocument.PageInfo.Builder(595, 842, pNum).create()
            val page = pdfDoc.startPage(pageInfo)
            val canvas: Canvas = page.canvas
            var y = 40f
            var count = 0

            while (lineIdx < lines.size && count < linesPerPage) {
                val line = lines[lineIdx]
                val processed = if (translateBlock != null && line.isNotBlank()) {
                    translateBlock(line)
                } else line

                canvas.drawText(
                    if (processed.length > 80) processed.take(80) + "..." else processed,
                    40f,
                    y,
                    paint
                )
                y += 24f
                lineIdx++
                count++
            }
            pdfDoc.finishPage(page)
        }

        FileOutputStream(outputFile).use { out ->
            pdfDoc.writeTo(out)
        }
        pdfDoc.close()
    }
}
