package com.doctranslate.app

import com.doctranslate.app.domain.converter.SupportedFormat
import org.junit.Assert.assertEquals
import org.junit.Test

class FormatConverterTest {

    @Test
    fun testFormatConverterMappings() {
        val formats = SupportedFormat.values()
        assertEquals(4, formats.size)
        assertEquals(SupportedFormat.DOCX, SupportedFormat.valueOf("DOCX"))
        assertEquals(SupportedFormat.PDF, SupportedFormat.valueOf("PDF"))
        assertEquals(SupportedFormat.TXT, SupportedFormat.valueOf("TXT"))
        assertEquals(SupportedFormat.CSV, SupportedFormat.valueOf("CSV"))
    }
}
