package com.doctranslate.app.presentation.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CloudDownload
import androidx.compose.material.icons.filled.OfflinePin
import androidx.compose.material.icons.filled.Translate
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.doctranslate.app.presentation.components.FilePickerCard
import com.doctranslate.app.presentation.components.LanguageSwapCard
import com.doctranslate.app.presentation.components.ProgressCard
import com.doctranslate.app.presentation.theme.RainbowGradients
import com.doctranslate.app.presentation.viewmodel.MainViewModel

@Composable
fun TranslateScreen(viewModel: MainViewModel) {
    val context = LocalContext.current
    val currentTheme by viewModel.currentTheme.collectAsState()
    val sourceLang by viewModel.sourceLang.collectAsState()
    val targetLang by viewModel.targetLang.collectAsState()
    val selectedFileName by viewModel.selectedFileName.collectAsState()
    val selectedFileSize by viewModel.selectedFileSize.collectAsState()
    val isProcessing by viewModel.isProcessing.collectAsState()
    val progressFraction by viewModel.progressFraction.collectAsState()
    val statusMessage by viewModel.statusMessage.collectAsState()
    val enModelDownloaded by viewModel.enModelDownloaded.collectAsState()
    val hiModelDownloaded by viewModel.hiModelDownloaded.collectAsState()
    val tmCount by viewModel.tmCount.collectAsState()

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
        // Offline Model Status & TM Status Banner
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.OfflinePin,
                            contentDescription = "Offline",
                            tint = Color(0xFF43A047),
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "ML Kit Models: " + if (enModelDownloaded && hiModelDownloaded) "Ready Offline" else "Download Required",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }

                    Surface(
                        modifier = Modifier.clip(RoundedCornerShape(8.dp)),
                        color = MaterialTheme.colorScheme.primaryContainer
                    ) {
                        Text(
                            text = "TM Cached: $tmCount",
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                }

                if (!enModelDownloaded || !hiModelDownloaded) {
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedButton(
                        onClick = { viewModel.downloadModels() },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(
                            imageVector = Icons.Default.CloudDownload,
                            contentDescription = "Download",
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(text = "Download English & Hindi Models (1-Time Setup)", fontSize = 12.sp)
                    }
                }
            }
        }

        // Language Swap Selector
        LanguageSwapCard(
            sourceLang = sourceLang,
            targetLang = targetLang,
            currentTheme = currentTheme,
            onSwap = { viewModel.swapLanguages() }
        )

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

        // Translate Button
        Button(
            onClick = { viewModel.startTranslation(context) },
            enabled = selectedFileName != null && !isProcessing,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = RainbowGradients.getPrimaryColor(currentTheme)
            )
        ) {
            Icon(imageVector = Icons.Default.Translate, contentDescription = "Translate")
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = if (isProcessing) "Translating Document..." else "Translate Document",
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
