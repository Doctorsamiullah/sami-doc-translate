package com.doctranslate.app.presentation.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Transform
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.doctranslate.app.domain.converter.SupportedFormat
import com.doctranslate.app.presentation.components.FilePickerCard
import com.doctranslate.app.presentation.components.LanguageSwapCard
import com.doctranslate.app.presentation.components.ProgressCard
import com.doctranslate.app.presentation.theme.RainbowGradients
import com.doctranslate.app.presentation.viewmodel.MainViewModel

@Composable
fun ConvertScreen(viewModel: MainViewModel) {
    val context = LocalContext.current
    val currentTheme by viewModel.currentTheme.collectAsState()
    val selectedFileName by viewModel.selectedFileName.collectAsState()
    val selectedFileSize by viewModel.selectedFileSize.collectAsState()
    val targetFormat by viewModel.targetConvertFormat.collectAsState()
    val translateOnConvert by viewModel.translateOnConvert.collectAsState()
    val sourceLang by viewModel.sourceLang.collectAsState()
    val targetLang by viewModel.targetLang.collectAsState()
    val isProcessing by viewModel.isProcessing.collectAsState()
    val progressFraction by viewModel.progressFraction.collectAsState()
    val statusMessage by viewModel.statusMessage.collectAsState()

    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument(),
        onResult = { uri: Uri? ->
            if (uri != null) {
                viewModel.setSelectedFile(context, uri)
            }
        }
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // File Picker Card
        FilePickerCard(
            selectedFileName = selectedFileName,
            selectedFileSize = selectedFileSize,
            currentTheme = currentTheme,
            onPickFile = {
                filePickerLauncher.launch(
                    arrayOf(
                        "application/pdf",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "text/plain",
                        "text/csv"
                    )
                )
            }
        )

        // Target Format Selector Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Convert Target Format:",
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    SupportedFormat.values().forEach { fmt ->
                        FilterChip(
                            selected = fmt == targetFormat,
                            onClick = { viewModel.setTargetConvertFormat(fmt) },
                            label = { Text(fmt.name) }
                        )
                    }
                }
            }
        }

        // Optional Translation Switch
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Translate during conversion",
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                    Text(
                        text = "English ↔ Hindi auto-translation",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = translateOnConvert,
                    onCheckedChange = { viewModel.setTranslateOnConvert(it) }
                )
            }
        }

        if (translateOnConvert) {
            LanguageSwapCard(
                sourceLang = sourceLang,
                targetLang = targetLang,
                currentTheme = currentTheme,
                onSwap = { viewModel.swapLanguages() }
            )
        }

        // Convert Button
        Button(
            onClick = { viewModel.startConversion(context) },
            enabled = selectedFileName != null && !isProcessing,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = RainbowGradients.getPrimaryColor(currentTheme)
            )
        ) {
            Icon(imageVector = Icons.Default.Transform, contentDescription = "Convert")
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = if (isProcessing) "Converting Document..." else "Convert Document to ${targetFormat.name}",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold
            )
        }

        // Progress Display
        ProgressCard(
            statusMessage = statusMessage,
            progressFraction = progressFraction,
            isProcessing = isProcessing,
            currentTheme = currentTheme
        )
    }
}
