package com.doctranslate.app

import com.doctranslate.app.domain.translation.TokenMasker
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class TokenMaskerTest {

    @Test
    fun testTokenMaskingAndUnmasking_URLs() {
        val input = "Visit our website at https://example.com/doc for more info."
        val maskResult = TokenMasker.mask(input)

        assertTrue(maskResult.maskedText.contains("___TOKEN_URL_0___"))
        assertFalse(maskResult.maskedText.contains("https://example.com/doc"))
        assertEquals(1, maskResult.tokenMap.size)

        val restored = TokenMasker.unmask(maskResult.maskedText, maskResult.tokenMap)
        assertEquals(input, restored)
    }

    @Test
    fun testTokenMaskingAndUnmasking_EmailsAndNumbers() {
        val input = "Contact support@doctranslate.com or call 12345 with formula =SUM(A1:A10)."
        val maskResult = TokenMasker.mask(input)

        assertTrue(maskResult.maskedText.contains("___TOKEN_EMAIL_"))
        assertTrue(maskResult.maskedText.contains("___TOKEN_NUM_"))

        val restored = TokenMasker.unmask(maskResult.maskedText, maskResult.tokenMap)
        assertEquals(input, restored)
    }
}
