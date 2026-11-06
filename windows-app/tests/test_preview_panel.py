import os
import pytest  # type: ignore[import-untyped,import-not-found]
from pathlib import Path
from PySide6.QtWidgets import QApplication, QTableWidget

from src.db.sqlite_db import DatabaseManager
from src.core.nmt.offline_engine import OfflineTranslationEngine
from src.gui.widgets.preview_panel import PreviewPanel


def cell_text(table: QTableWidget, row: int, col: int) -> str:
    """Type-safe helper to retrieve text from a table cell."""
    item = table.item(row, col)
    return item.text() if item is not None else ""


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def test_db(tmp_path: Path):
    db_file: Path = tmp_path / "test_tm.db"
    db = DatabaseManager(db_file)
    yield db
    db.close()


def test_preview_panel_content_and_stats(qapp, test_db, tmp_path):
    panel = PreviewPanel()
    src_text = "The court issued an order.\n\nThe case is scheduled for hearing."
    tgt_text = "न्यायालय ने एक आदेश जारी किया।\n\nमामले की सुनवाई निर्धारित है।"

    panel.set_content(src_text, tgt_text, src_lang="en", tgt_lang="hi")
    assert "The court" in panel.txt_src.toPlainText()
    assert "न्यायालय" in panel.txt_tgt.toPlainText()
    assert "Paragraphs: 2" in panel.lbl_src_stats.text()
    assert "Paragraphs: 2" in panel.lbl_tgt_stats.text()
    assert panel.table.rowCount() == 2


def test_preview_panel_swap_direction(qapp):
    panel = PreviewPanel()
    src_text = "English sentence"
    tgt_text = "हिंदी वाक्य"
    panel.set_content(src_text, tgt_text, src_lang="en", tgt_lang="hi")
    
    assert panel.src_lang == "en"
    assert panel.tgt_lang == "hi"
    assert cell_text(panel.table, 0, 1) == "English sentence"
    assert cell_text(panel.table, 0, 2) == "हिंदी वाक्य"

    # Swap to Hindi -> English
    panel.swap_direction()
    assert panel.src_lang == "hi"
    assert panel.tgt_lang == "en"
    assert cell_text(panel.table, 0, 1) == "हिंदी वाक्य"
    assert cell_text(panel.table, 0, 2) == "English sentence"


def test_preview_panel_line_by_line_alignment(qapp):
    panel = PreviewPanel()
    panel.combo_alignment.setCurrentText("Line by Line")
    src_text = "Line 1: Title\nLine 2: Subtitle\nLine 3: Notice"
    tgt_text = "पंक्ति 1: शीर्षक\nपंक्ति 2: उपशीर्षक\nपंक्ति 3: सूचना"

    panel.populate_table_from_texts(src_text, tgt_text)
    assert panel.table.rowCount() == 3
    assert cell_text(panel.table, 0, 1) == "Line 1: Title"
    assert cell_text(panel.table, 0, 2) == "पंक्ति 1: शीर्षक"
    assert cell_text(panel.table, 1, 1) == "Line 2: Subtitle"
    assert cell_text(panel.table, 1, 2) == "पंक्ति 2: उपशीर्षक"
    assert cell_text(panel.table, 2, 1) == "Line 3: Notice"
    assert cell_text(panel.table, 2, 2) == "पंक्ति 3: सूचना"


def test_preview_panel_export_docx(qapp, tmp_path):
    panel = PreviewPanel()
    panel.set_content("Paragraph 1\n\nParagraph 2", "प्रथम पैराग्राफ\n\nद्वितीय पैराग्राफ")
    
    out_file = str(tmp_path / "test_export.docx")
    
    import docx  # type: ignore[import-untyped,import-not-found]
    doc = docx.Document()
    paragraphs = panel.get_edited_target_text().split("\n\n")
    for para in paragraphs:
        doc.add_paragraph(para)
    doc.save(out_file)

    assert os.path.exists(out_file)
    saved_doc = docx.Document(out_file)
    assert len(saved_doc.paragraphs) == 2
    assert "प्रथम पैराग्राफ" in saved_doc.paragraphs[0].text
