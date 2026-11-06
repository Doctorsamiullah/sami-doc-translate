import pytest
import os
import tempfile
from pathlib import Path

from src.db.sqlite_db import DatabaseManager
from src.core.nmt.offline_engine import OfflineTranslationEngine
from src.core.parsers.docx_parser import DocxParser
from src.core.parsers.text_parser import TextParser
from src.core.converter.format_converter import FormatConverter
from src.core.compressor.file_compressor import FileCompressor
import docx

@pytest.fixture
def temp_env():
    d = tempfile.mkdtemp()
    temp_path = Path(d)
    db = DatabaseManager(db_path=temp_path / "test.db")
    engine = OfflineTranslationEngine(db)
    yield temp_path, db, engine
    db.close()
    import shutil
    shutil.rmtree(d, ignore_errors=True)

def test_offline_engine_bidirectional(temp_env):
    _, _, engine = temp_env
    # English -> Hindi
    en_text = "The annual financial report is approved."
    hi_trans = engine.translate(en_text, src="en", tgt="hi")
    assert "रिपोर्ट" in hi_trans or "वार्षिक" in hi_trans

    # Hindi -> English
    hi_text = "यह वार्षिक रिपोर्ट है।"
    en_trans = engine.translate(hi_text, src="hi", tgt="en")
    assert "annual" in en_trans.lower() or "report" in en_trans.lower()

def test_token_masking(temp_env):
    _, _, engine = temp_env
    text = "Visit https://example.com or email test@corp.gov for report."
    trans = engine.translate(text, src="en", tgt="hi")
    # Verify URL and Email are preserved untouched
    assert "https://example.com" in trans
    assert "test@corp.gov" in trans

def test_translation_memory_caching(temp_env):
    _, db, engine = temp_env
    text = "Confidential agreement statement"
    first = engine.translate(text, src="en", tgt="hi")
    cached = db.get_translation(text, "en", "hi")
    assert cached == first

def test_docx_parser(temp_env):
    temp_dir, _, engine = temp_env
    sample_p = temp_dir / "sample.docx"
    doc = docx.Document()
    p = doc.add_paragraph()
    run = p.add_run("Annual report statement.")
    run.bold = True
    doc.save(str(sample_p))

    out_p = temp_dir / "sample_hi.docx"
    parser = DocxParser()
    success = parser.translate_document(str(sample_p), str(out_p), engine, "en", "hi")
    assert success is True
    assert out_p.exists()

    # Verify run retained bold and has content
    res_doc = docx.Document(str(out_p))
    assert len(res_doc.paragraphs) == 1
    assert res_doc.paragraphs[0].runs[0].bold is True

def test_format_converter(temp_env):
    temp_dir, _, _ = temp_env
    txt_p = temp_dir / "test.txt"
    txt_p.write_text("Line 1\nLine 2\nLine 3", encoding="utf-8")
    
    docx_p = temp_dir / "test.docx"
    success = FormatConverter.convert(str(txt_p), str(docx_p))
    assert success is True
    assert docx_p.exists()

def test_file_compressor(temp_env):
    temp_dir, _, _ = temp_env
    doc_p = temp_dir / "large.docx"
    doc = docx.Document()
    for i in range(100):
        doc.add_paragraph(f"This is repetitive test line {i} with financial statement report data.")
    doc.save(str(doc_p))

    out_p = temp_dir / "compressed.docx"
    success = FileCompressor.compress_file(str(doc_p), str(out_p), target_size_bytes=10000)
    assert success is True
    assert out_p.exists()
