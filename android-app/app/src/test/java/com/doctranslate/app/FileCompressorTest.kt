package com.doctranslate.app

import com.doctranslate.app.domain.compressor.SmartFileCompressor
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class FileCompressorTest {

    @get:Rule
    val tempFolder = TemporaryFolder()

    @Test
    fun testScratchBufferAndDpiFloorConstant() {
        assertEquals(150, SmartFileCompressor.MIN_DPI_FLOOR)

        val dummyCacheDir = tempFolder.newFolder("cacheDir")
        val scratchFile = File(dummyCacheDir, "input_scratch_123.tmp")
        scratchFile.writeText("Dummy scratch content")

        assertTrue(scratchFile.exists())

        // Simulate scratch cleanup logic
        dummyCacheDir.listFiles()?.forEach { file ->
            if (file.name.startsWith("input_")) {
                file.delete()
            }
        }

        assertTrue(!scratchFile.exists())
    }
}
