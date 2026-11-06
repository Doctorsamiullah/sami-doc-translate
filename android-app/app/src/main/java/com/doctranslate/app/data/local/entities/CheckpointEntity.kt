package com.doctranslate.app.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "checkpoints")
data class CheckpointEntity(
    @PrimaryKey val docUri: String,
    val processedPages: Int,
    val totalPages: Int,
    val lastPosition: Long = 0L,
    val updatedAt: Long = System.currentTimeMillis()
)
