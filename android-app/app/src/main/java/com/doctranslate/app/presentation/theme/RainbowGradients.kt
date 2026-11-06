package com.doctranslate.app.presentation.theme

import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

enum class RainbowTheme(val displayName: String) {
    VIBRANT("Vibrant Rainbow Light"),
    PASTEL("Pastel Rainbow Light"),
    PRISM("Prism Spectrum Light"),
    SUNRISE("Sunrise Spectrum Light")
}

object RainbowGradients {

    // 1. Vibrant Rainbow Light
    val vibrantGradientColors = listOf(
        Color(0xFF8E24AA), // Purple
        Color(0xFF1E88E5), // Blue
        Color(0xFF43A047), // Green
        Color(0xFFFDD835), // Yellow
        Color(0xFFFB8C00), // Orange
        Color(0xFFE53935)  // Red
    )

    // 2. Pastel Rainbow Light
    val pastelGradientColors = listOf(
        Color(0xFFE1BEE7), // Lavender
        Color(0xFFBBDEFB), // Sky Blue
        Color(0xFFC8E6C9), // Mint
        Color(0xFFFFF9C4), // Lemon
        Color(0xFFFFE0B2), // Peach
        Color(0xFFFFCDD2)  // Coral
    )

    // 3. Prism Spectrum Light
    val prismGradientColors = listOf(
        Color(0xFF7B1FA2), // Deep Violet
        Color(0xFF0288D1), // Cyan Blue
        Color(0xFF388E3C), // Forest Green
        Color(0xFFFBC02D), // Gold
        Color(0xFFF57C00), // Deep Amber
        Color(0xFFD32F2F)  // Crimson
    )

    // 4. Sunrise Spectrum Light
    val sunriseGradientColors = listOf(
        Color(0xFFFFB300), // Amber
        Color(0xFFFB8C00), // Tangerine
        Color(0xFFF4511E), // Coral
        Color(0xFFE91E63), // Rose
        Color(0xFF8E24AA)  // Violet
    )

    fun getGradientBrush(theme: RainbowTheme): Brush {
        val colors = when (theme) {
            RainbowTheme.VIBRANT -> vibrantGradientColors
            RainbowTheme.PASTEL -> pastelGradientColors
            RainbowTheme.PRISM -> prismGradientColors
            RainbowTheme.SUNRISE -> sunriseGradientColors
        }
        return Brush.horizontalGradient(colors)
    }

    fun getBackgroundColor(theme: RainbowTheme): Color {
        return when (theme) {
            RainbowTheme.VIBRANT -> Color(0xFFFAFAFA)
            RainbowTheme.PASTEL -> Color(0xFFFBF9F5)
            RainbowTheme.PRISM -> Color(0xFFF8F9FA)
            RainbowTheme.SUNRISE -> Color(0xFFFFFDF9)
        }
    }

    fun getSurfaceColor(theme: RainbowTheme): Color {
        return when (theme) {
            RainbowTheme.VIBRANT -> Color(0xFFFFFFFF)
            RainbowTheme.PASTEL -> Color(0xFFFFFFFF)
            RainbowTheme.PRISM -> Color(0xFFFFFFFF)
            RainbowTheme.SUNRISE -> Color(0xFFFFFFFF)
        }
    }

    fun getPrimaryColor(theme: RainbowTheme): Color {
        return when (theme) {
            RainbowTheme.VIBRANT -> Color(0xFF1E88E5)
            RainbowTheme.PASTEL -> Color(0xFF7E57C2)
            RainbowTheme.PRISM -> Color(0xFF7B1FA2)
            RainbowTheme.SUNRISE -> Color(0xFFF4511E)
        }
    }
}
