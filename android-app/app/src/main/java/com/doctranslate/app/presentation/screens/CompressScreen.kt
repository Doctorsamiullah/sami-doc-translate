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
import androidx.compose.material.icons.filled.Compress
import androidx.compose.material.icons.filled.HighQuality
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
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
import com.doctranslate.app.presentation.components.FilePickerCard
import com.doctranslate.app.presentation.components.ProgressCard
import com.doctranslate.app.presentation.theme.RainbowGradients
import com.doctranslate.app.presentation.viewmodel.MainViewModel

@Composable
fun CompressScreen(viewModel: MainViewModel) {
    val context = LocalContext.current
    val currentTheme by viewModel.currentTheme.collectAsState()
    val selectedFileName by viewModel.selectedFileName.collectAsState()
    val selectedFileSize by viewModel.selectedFileSize.collectAsState()
    val targetMB by viewModel.targetCompressMB.collectAsState()
    val preserveReadability by viewModel.preserveReadability.collectAsState()
    val lastResult by viewModel.lastCompressedResult.collectAsState()
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
                        "text/plain"
                    )
                )
            }
        )

        // Target Size Slider Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Target Maximum Size:",
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                    Text(
                        text = "%.1f MB".format(targetMB),
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        color = MaterialTheme.colorScheme.primary
                    )
                }

                Slider(
                    value = targetMB,
                    onValueChange = { viewModel.setTargetCompressMB(it) },
                    valueRange = 0.2f..10.0f,
                    steps = 98
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("200 KB", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("5 MB", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("10 MB", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }

        // Quality Floor Option Card
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
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.HighQuality,
                            contentDescription = "Readability",
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Preserve Text Readability",
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                    }
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = "Enforces strict 150 DPI minimum floor for vector shapes & document text clarity",
                        fontSize = 11.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = preserveReadability,
                    onCheckedChange = { viewModel.setPreserveReadability(it) }
                )
            }
        }

        // Compress Button
        Button(
            onClick = { viewModel.startCompression(context) },
            enabled = selectedFileName != null && !isProcessing,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = RainbowGradients.getPrimaryColor(currentTheme)
            )
        ) {
            Icon(imageVector = Icons.Default.Compress, contentDescription = "Compress")
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = if (isProcessing) "Compressing File..." else "Compress File to < %.1f MB".format(targetMB),
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold
            )
        }

        // Compression Results Card if available
        lastResult?.let { res ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = "Compression Result Summary", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("Original Size: %.2f MB".format(res.originalSizeBytes / (1024f * 1024f)), fontSize = 13.sp)
                    Text("Compressed Size: %.2f MB".format(res.compressedSizeBytes / (1024f * 1024f)), fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                    Text("Target Met: ${if (res.isTargetMet) "YES ✓" else "NO"}", fontSize = 13.sp, color = if (res.isTargetMet) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error)
                }
            }
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
