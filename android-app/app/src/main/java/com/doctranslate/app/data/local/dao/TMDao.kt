package com.doctranslate.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.doctranslate.app.data.local.entities.TMEntity

@Dao
interface TMDao {
    @Query("SELECT * FROM translation_memory WHERE hash = :hash AND sourceLang = :srcLang AND targetLang = :tgtLang LIMIT 1")
    suspend fun findTranslation(hash: String, srcLang: String, tgtLang: String): TMEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entity: TMEntity)

    @Query("SELECT COUNT(*) FROM translation_memory")
    suspend fun getCount(): Int

    @Query("DELETE FROM translation_memory")
    suspend fun clearAll()
}
