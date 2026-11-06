package com.doctranslate.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.doctranslate.app.data.local.entities.CheckpointEntity

@Dao
interface CheckpointDao {
    @Query("SELECT * FROM checkpoints WHERE docUri = :uri")
    suspend fun getCheckpoint(uri: String): CheckpointEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveCheckpoint(entity: CheckpointEntity)

    @Query("DELETE FROM checkpoints WHERE docUri = :uri")
    suspend fun deleteCheckpoint(uri: String)
}
