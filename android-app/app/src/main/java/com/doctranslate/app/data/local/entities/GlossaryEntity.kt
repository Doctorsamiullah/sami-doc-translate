package com.doctranslate.app.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "glossary")
data class GlossaryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sourceTerm: String,
    val targetTerm: String,
    val domain: String = "General"
)
