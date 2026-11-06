package com.doctranslate.app

import com.doctranslate.app.data.local.entities.TMEntity
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Test
import java.security.MessageDigest

class TranslationMemoryTest {

    private fun computeHash(text: String): String {
        val md = MessageDigest.getInstance("SHA-256")
        val digest = md.digest(text.trim().toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02x".format(it) }
    }

    @Test
    fun testTMDeduplicationHash() {
        val text1 = "Hello World"
        val text2 = "  Hello World  "
        val text3 = "Different Text"

        val hash1 = computeHash(text1)
        val hash2 = computeHash(text2)
        val hash3 = computeHash(text3)

        assertEquals(hash1, hash2) // Deduplicated hash
        assertNotEquals(hash1, hash3)

        val tmEntity = TMEntity(
            sourceText = text1,
            targetText = "नमस्ते दुनिया",
            sourceLang = "en",
            targetLang = "hi",
            hash = hash1
        )

        assertEquals("en", tmEntity.sourceLang)
        assertEquals("hi", tmEntity.targetLang)
        assertEquals("नमस्ते दुनिया", tmEntity.targetText)
    }
}
