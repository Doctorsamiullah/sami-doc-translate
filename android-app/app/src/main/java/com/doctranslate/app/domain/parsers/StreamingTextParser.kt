package com.doctranslate.app.domain.parsers

import java.io.BufferedReader
import java.io.BufferedWriter
import java.io.InputStream
import java.io.InputStreamReader
import java.io.OutputStream
import java.io.OutputStreamWriter

object StreamingTextParser {

    suspend fun translateTextStream(
        inputStream: InputStream,
        outputStream: OutputStream,
        translateBlock: suspend (String) -> String,
        onProgress: suspend (ParseProgress) -> Unit
    ) {
        val reader = BufferedReader(InputStreamReader(inputStream, Charsets.UTF_8))
        val writer = BufferedWriter(OutputStreamWriter(outputStream, Charsets.UTF_8))

        try {
            var lineCount = 0
            var line: String? = reader.readLine()

            while (line != null) {
                lineCount++
                val translated = if (line.isNotBlank()) {
                    translateBlock(line)
                } else {
                    line
                }

                writer.write(translated)
                writer.newLine()

                if (lineCount % 10 == 0) {
                    writer.flush()
                    onProgress(
                        ParseProgress(
                            currentItem = lineCount,
                            totalItems = -1, // Unknown total
                            statusMessage = "Processed $lineCount lines (Zero-OOM Streaming)"
                        )
                    )
                }

                line = reader.readLine()
            }
            writer.flush()
            onProgress(
                ParseProgress(
                    currentItem = lineCount,
                    totalItems = lineCount,
                    statusMessage = "Completed $lineCount lines"
                )
            )
        } finally {
            reader.close()
            writer.close()
        }
    }
}
