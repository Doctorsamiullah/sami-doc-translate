import sqlite3
import hashlib
import threading
from typing import Optional, Dict, List
from pathlib import Path
from src.config import DB_PATH

class DatabaseManager:
    """
    Thread-safe SQLite Database Manager.
    Uses check_same_thread=False with threading.RLock and Write-Ahead Logging (WAL)
    so the connection can be safely accessed across the Qt GUI thread and QThread workers.
    """
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self.db_path), timeout=20.0, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode = WAL;")
        self._conn.execute("PRAGMA synchronous = NORMAL;")
        self._init_db()

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None

    def _init_db(self) -> None:
        with self._lock:
            cursor = self._conn.cursor()
            # Translation Memory
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS translation_memory (
                    source_hash TEXT PRIMARY KEY,
                    src_lang TEXT NOT NULL,
                    tgt_lang TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tm_hash ON translation_memory(source_hash, src_lang, tgt_lang);")

            # Custom Glossary
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS glossary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT DEFAULT 'general',
                    term_en TEXT NOT NULL,
                    term_hi TEXT NOT NULL,
                    case_sensitive INTEGER DEFAULT 0,
                    UNIQUE(term_en, term_hi)
                );
            """)

            # Job Checkpoints for Unlimited Pages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_checkpoints (
                    job_id TEXT PRIMARY KEY,
                    source_path TEXT NOT NULL,
                    target_path TEXT NOT NULL,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    total_pages INTEGER NOT NULL,
                    completed_pages INTEGER DEFAULT 0,
                    status TEXT CHECK(status IN ('pending', 'running', 'paused', 'completed', 'failed')),
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self._conn.commit()

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def get_translation(self, text: str, src_lang: str, tgt_lang: str) -> Optional[str]:
        thash = self.hash_text(text)
        with self._lock:
            if self._conn is None:
                return None
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT translated_text FROM translation_memory 
                WHERE source_hash = ? AND src_lang = ? AND tgt_lang = ?
            """, (thash, src_lang, tgt_lang))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    UPDATE translation_memory 
                    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP 
                    WHERE source_hash = ?
                """, (thash,))
                self._conn.commit()
                return row[0]
        return None

    def store_translation(self, source_text: str, translated_text: str, src_lang: str, tgt_lang: str) -> None:
        thash = self.hash_text(source_text)
        with self._lock:
            if self._conn is None:
                return
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO translation_memory (source_hash, src_lang, tgt_lang, source_text, translated_text)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_hash) DO UPDATE SET
                    translated_text = excluded.translated_text,
                    usage_count = usage_count + 1,
                    last_used = CURRENT_TIMESTAMP;
            """, (thash, src_lang, tgt_lang, source_text.strip(), translated_text.strip()))
            self._conn.commit()

    def get_glossary(self) -> Dict[str, str]:
        with self._lock:
            if self._conn is None:
                return {}
            cursor = self._conn.cursor()
            cursor.execute("SELECT term_en, term_hi FROM glossary;")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def add_glossary_term(self, term_en: str, term_hi: str, category: str = "general") -> None:
        with self._lock:
            if self._conn is None:
                return
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO glossary (category, term_en, term_hi)
                VALUES (?, ?, ?);
            """, (category, term_en.strip(), term_hi.strip()))
            self._conn.commit()

    def save_checkpoint(self, job_id: str, src_path: str, tgt_path: str, src_lang: str, tgt_lang: str, total_pages: int, completed_pages: int, status: str = "running") -> None:
        with self._lock:
            if self._conn is None:
                return
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO job_checkpoints (job_id, source_path, target_path, source_lang, target_lang, total_pages, completed_pages, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    completed_pages = excluded.completed_pages,
                    status = excluded.status,
                    updated_at = CURRENT_TIMESTAMP;
            """, (job_id, src_path, tgt_path, src_lang, tgt_lang, total_pages, completed_pages, status))
            self._conn.commit()
