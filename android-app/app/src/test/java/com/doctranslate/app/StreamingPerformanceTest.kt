package com.doctranslate.app

import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.BufferedReader
import java.io.BufferedWriter
import java.io.File

class StreamingPerformanceTest {

    @get:Rule
    val tempFolder = TemporaryFolder()

    @Test
    fun testSimulated100PageStreamingZeroOOM() = runBlocking {
        // Generate a 100-page document (~10,000 paragraphs / lines)
        val largeFile = tempFolder.newFile("large_100_page_doc.txt")
        largeFile.bufferedWriter().use { writer ->
            for (i in 1..10000) {
                writer.write("Page ${(i / 100) + 1} Paragraph $i: This is a sample text line to be processed line-by-line with streaming iterators.")
                writer.newLine()
            }
        }

        val runtime = Runtime.getRuntime()
        runtime.gc()
        val initialMemory = runtime.totalMemory() - runtime.freeMemory()

        val outputFile = tempFolder.newFile("translated_output.txt")

        // Streaming process: line by line
        val reader = BufferedReader(largeFile.reader())
        val writer = BufferedWriter(outputFile.writer())

        var lineCount = 0
        reader.forEachLine { line ->
            lineCount++
            val translated = " [HI] $line"
            writer.write(translated)
            writer.newLine()
            if (lineCount % 500 == 0) {
                writer.flush()
            }
        }
        reader.close()
        writer.close()

        runtime.gc()
        val finalMemory = runtime.totalMemory() - runtime.freeMemory()
        val memoryDeltaMB = (finalMemory - initialMemory) / (1024 * 1024)

        assertEquals(10000, lineCount)
        assertTrue(outputFile.length() > 0)
        // Verify heap memory delta during streaming is well under 250 MB
        assertTrue("Memory delta was $memoryDeltaMB MB, expected < 250 MB", memoryDeltaMB < 250)
    }
}
