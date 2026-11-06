package com.doctranslate.app.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "history")
data class HistoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val fileName: String,
    val fileType: String,
    val operationType: String, // "TRANSLATION", "CONVERSION", "COMPRESSION"
    val sourceLang: String? = null,
    val targetLang: String? = null,
    val originalSize: Long = 0L,
    val processedSize: Long = 0L,
    val outputUri: String,
    val translatedTextSample: String? = null,
    val timestamp: Long = System.currentTimeMillis()
)
