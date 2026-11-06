package com.doctranslate.app.presentation.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

@Composable
fun DocTranslateTheme(
    rainbowTheme: RainbowTheme = RainbowTheme.VIBRANT,
    content: @Composable () -> Unit
) {
    val primary = RainbowGradients.getPrimaryColor(rainbowTheme)
    val background = RainbowGradients.getBackgroundColor(rainbowTheme)
    val surface = RainbowGradients.getSurfaceColor(rainbowTheme)

    val colorScheme = lightColorScheme(
        primary = primary,
        secondary = primary,
        background = background,
        surface = surface,
        onPrimary = Color.White,
        onBackground = Color(0xFF212121),
        onSurface = Color(0xFF212121)
    )

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
