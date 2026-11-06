package com.doctranslate.app.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.doctranslate.app.data.local.dao.CheckpointDao
import com.doctranslate.app.data.local.dao.GlossaryDao
import com.doctranslate.app.data.local.dao.HistoryDao
import com.doctranslate.app.data.local.dao.TMDao
import com.doctranslate.app.data.local.entities.CheckpointEntity
import com.doctranslate.app.data.local.entities.GlossaryEntity
import com.doctranslate.app.data.local.entities.HistoryEntity
import com.doctranslate.app.data.local.entities.TMEntity

@Database(
    entities = [
        TMEntity::class,
        HistoryEntity::class,
        GlossaryEntity::class,
        CheckpointEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {

    abstract fun tmDao(): TMDao
    abstract fun historyDao(): HistoryDao
    abstract fun glossaryDao(): GlossaryDao
    abstract fun checkpointDao(): CheckpointDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "doc_translate_db"
                ).fallbackToDestructiveMigration(true).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
