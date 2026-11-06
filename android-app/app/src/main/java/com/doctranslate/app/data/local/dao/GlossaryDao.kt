package com.doctranslate.app.data.local.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.doctranslate.app.data.local.entities.GlossaryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface GlossaryDao {
    @Query("SELECT * FROM glossary ORDER BY sourceTerm ASC")
    fun getAllTerms(): Flow<List<GlossaryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entity: GlossaryEntity)

    @Delete
    suspend fun delete(entity: GlossaryEntity)
}
