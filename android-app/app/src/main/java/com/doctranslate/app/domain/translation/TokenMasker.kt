package com.doctranslate.app.domain.translation

import java.util.regex.Pattern

data class MaskResult(
    val maskedText: String,
    val tokenMap: Map<String, String>
)

object TokenMasker {

    private val EMAIL_PATTERN = Pattern.compile("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
    private val URL_PATTERN = Pattern.compile("https?://[^\\s]+|www\\.[^\\s]+")
    private val FORMULA_NUM_PATTERN = Pattern.compile("=[A-Z0-9()+/*.-]+|\\b\\d+(?:[.,]\\d+)*%?\\b")

    fun mask(text: String): MaskResult {
        if (text.isBlank()) return MaskResult(text, emptyMap())

        val tokenMap = mutableMapOf<String, String>()
        var counter = 0
        var currentText = text

        // 1. Mask URLs
        var matcher = URL_PATTERN.matcher(currentText)
        val urlBuffer = StringBuffer()
        while (matcher.find()) {
            val original = matcher.group()
            val token = "___TOKEN_URL_${counter++}___"
            tokenMap[token] = original
            matcher.appendReplacement(urlBuffer, token)
        }
        matcher.appendTail(urlBuffer)
        currentText = urlBuffer.toString()

        // 2. Mask Emails
        matcher = EMAIL_PATTERN.matcher(currentText)
        val emailBuffer = StringBuffer()
        while (matcher.find()) {
            val original = matcher.group()
            val token = "___TOKEN_EMAIL_${counter++}___"
            tokenMap[token] = original
            matcher.appendReplacement(emailBuffer, token)
        }
        matcher.appendTail(emailBuffer)
        currentText = emailBuffer.toString()

        // 3. Mask Formulas & Numbers
        matcher = FORMULA_NUM_PATTERN.matcher(currentText)
        val numBuffer = StringBuffer()
        while (matcher.find()) {
            val original = matcher.group()
            val token = "___TOKEN_NUM_${counter++}___"
            tokenMap[token] = original
            matcher.appendReplacement(numBuffer, token)
        }
        matcher.appendTail(numBuffer)
        currentText = numBuffer.toString()

        return MaskResult(currentText, tokenMap)
    }

    fun unmask(maskedText: String, tokenMap: Map<String, String>): String {
        if (tokenMap.isEmpty() || maskedText.isBlank()) return maskedText

        var result = maskedText
        for ((token, original) in tokenMap) {
            // Replace exact token or token with slight spaces that ML Kit might introduce
            result = result.replace(token, original)
            val regex = Regex(Regex.escape(token).replace("_", "\\s*_\\s*"), RegexOption.IGNORE_CASE)
            result = result.replace(regex, original)
        }
        return result
    }
}
