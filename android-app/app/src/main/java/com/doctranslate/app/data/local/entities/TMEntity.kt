package com.doctranslate.app.data.local.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "translation_memory",
    indices = [Index(value = ["hash", "sourceLang", "targetLang"])]
)
data class TMEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sourceText: String,
    val targetText: String,
    val sourceLang: String,
    val targetLang: String,
    val hash: String,
    val createdAt: Long = System.currentTimeMillis()
)
