import os
from pathlib import Path
from typing import Optional, List, Tuple
import docx  # type: ignore[import-untyped,import-not-found]
from docx.shared import Pt  # type: ignore[import-untyped,import-not-found]
from docx.oxml import OxmlElement  # type: ignore[import-untyped,import-not-found]
from docx.oxml.ns import qn  # type: ignore[import-untyped,import-not-found]
try:
    import pymupdf as fitz  # type: ignore[import-untyped,import-not-found]
except ImportError:
    import fitz  # type: ignore[import-untyped,import-not-found]

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QFileDialog, QComboBox, QSpinBox, QCheckBox, QMessageBox, QProgressBar,
    QSplitter, QGroupBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QStyledItemDelegate, QTabWidget, QToolButton
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

from src.core.fonts.font_manager import FontManager


class MultiLineDelegate(QStyledItemDelegate):
    """Custom item delegate allowing multiline QTextEdit in table cells."""
    def __init__(self, font_name="Noto Sans Devanagari", font_size=12, parent=None):
        super().__init__(parent)
        self.font_name = font_name
        self.font_size = font_size

    def createEditor(self, parent, option, index):
        editor = QTextEdit(parent)
        editor.setFont(QFont(self.font_name, self.font_size))
        editor.setAcceptRichText(False)
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.ItemDataRole.EditRole) or ""
        editor.setPlainText(text)

    def setModelData(self, editor, model, index):
        text = editor.toPlainText()
        model.setData(index, text, Qt.ItemDataRole.EditRole)


class TableTranslateWorker(QThread):
    """Background worker for translating table rows or text asynchronously."""
    progress = Signal(int, int)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, engine, items: List[str], src_lang: str, tgt_lang: str):
        super().__init__()
        self.engine = engine
        self.items = items
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def run(self):
        try:
            if not self.engine:
                self.error.emit("Translation engine is not initialized.")
                return

            results = []
            total = len(self.items)

            for i, item in enumerate(self.items):
                if not item.strip():
                    results.append("")
                else:
                    trans = self.engine.translate(item.strip(), self.src_lang, self.tgt_lang)
                    results.append(trans)
                self.progress.emit(i + 1, total)

            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class PreviewPanel(QWidget):
    """
    Advanced Side-by-Side Dual-Mode Document Editor & Aligned Comparator.
    Supports:
    - Bidirectional English ↔ Hindi & Hindi ↔ English translation and comparison
    - Mode 1: Aligned Line-by-Line / Paragraph-by-Paragraph Table View (exact horizontal lock)
    - Mode 2: Continuous Side-by-Side Text Document View
    - Dynamic row height auto-expansion (when more space is needed, shifts next line in same line)
    - Real-time in-cell multiline editing
    - Export to DOCX (with Devanagari fonts) or TXT
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = None
        self.src_lang = "en"
        self.tgt_lang = "hi"
        self._syncing_scroll = False
        self._updating_table = False
        self.current_source_path: Optional[str] = None
        self.current_target_path: Optional[str] = None

        self._init_ui()

    def set_engine(self, engine):
        self.engine = engine

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 10, 14, 10)
        root_layout.setSpacing(10)

        # 1. Top Header & Direction Switcher Bar
        top_bar = QHBoxLayout()
        v_title = QVBoxLayout()
        header = QLabel("🔍 Side-by-Side Live Document Editor & Aligned Comparator")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E88E5;")
        sub = QLabel("Compare English ↔ Hindi line-by-line or paragraph-by-paragraph with strict horizontal row alignment.")
        sub.setStyleSheet("font-size: 12px; color: #6C757D;")
        v_title.addWidget(header)
        v_title.addWidget(sub)
        top_bar.addLayout(v_title)
        top_bar.addStretch()

        # Bidirectional Swap Button in Header
        self.btn_swap_dir = QPushButton("⇄ Swap Direction (EN ↔ HI)")
        self.btn_swap_dir.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E88E5, stop:1 #8E24AA); color: white; font-weight: bold; border-radius: 6px; padding: 7px 14px;")
        self.btn_swap_dir.clicked.connect(self.swap_direction)
        top_bar.addWidget(self.btn_swap_dir)

        root_layout.addLayout(top_bar)

        # 2. Main Controls & Actions Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background: #F8F9FA; border: 1px solid #E0E0E0; border-radius: 8px; padding: 6px;")
        tool_layout = QHBoxLayout(toolbar)
        tool_layout.setContentsMargins(8, 4, 8, 4)
        tool_layout.setSpacing(10)

        # Language Direction Display Badges
        self.lbl_src_badge = QLabel("Source: English (EN)")
        self.lbl_src_badge.setStyleSheet("font-weight: bold; color: #1565C0; background: #E3F2FD; padding: 4px 10px; border-radius: 4px;")
        tool_layout.addWidget(self.lbl_src_badge)

        arrow_lbl = QLabel("➔")
        arrow_lbl.setStyleSheet("font-weight: bold; color: #757575;")
        tool_layout.addWidget(arrow_lbl)

        self.lbl_tgt_badge = QLabel("Target: Hindi (HI - Devanagari)")
        self.lbl_tgt_badge.setStyleSheet("font-weight: bold; color: #6A1B9A; background: #F3E5F5; padding: 4px 10px; border-radius: 4px;")
        tool_layout.addWidget(self.lbl_tgt_badge)

        tool_layout.addSpacing(8)

        # Alignment Mode Selector
        lbl_split = QLabel("Alignment Unit:")
        lbl_split.setStyleSheet("font-weight: 600; font-size: 11px;")
        tool_layout.addWidget(lbl_split)

        self.combo_alignment = QComboBox()
        self.combo_alignment.addItems(["Paragraph by Paragraph", "Line by Line"])
        self.combo_alignment.currentIndexChanged.connect(self._realign_from_text)
        tool_layout.addWidget(self.combo_alignment)

        tool_layout.addSpacing(8)

        # Font Family & Size
        lbl_font = QLabel("Hindi Font:")
        lbl_font.setStyleSheet("font-weight: 600; font-size: 11px;")
        tool_layout.addWidget(lbl_font)

        self.combo_fonts = QComboBox()
        self.combo_fonts.addItems(FontManager.get_all_font_names())
        self.combo_fonts.currentTextChanged.connect(self._on_font_changed)
        tool_layout.addWidget(self.combo_fonts)

        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(10, 32)
        self.spin_font_size.setValue(12)
        self.spin_font_size.valueChanged.connect(self._on_font_size_changed)
        tool_layout.addWidget(self.spin_font_size)

        tool_layout.addSpacing(8)

        # Action: Translate All Rows
        self.btn_live_translate = QPushButton("⚡ Translate All Rows")
        self.btn_live_translate.setStyleSheet("background: #E8F5E9; color: #2E7D32; font-weight: bold; border: 1px solid #81C784; border-radius: 5px; padding: 5px 12px;")
        self.btn_live_translate.clicked.connect(self._on_translate_all)
        tool_layout.addWidget(self.btn_live_translate)

        tool_layout.addStretch()

        # Action: Export Buttons
        self.btn_export_docx = QPushButton("💾 Export DOCX")
        self.btn_export_docx.setStyleSheet("background: #E3F2FD; color: #1565C0; font-weight: bold; border: 1px solid #90CAF9; border-radius: 5px; padding: 5px 12px;")
        self.btn_export_docx.clicked.connect(self._export_to_docx)
        tool_layout.addWidget(self.btn_export_docx)

        self.btn_export_txt = QPushButton("💾 Export TXT")
        self.btn_export_txt.setStyleSheet("background: #EDE7F6; color: #4527A0; font-weight: bold; border: 1px solid #B39DDB; border-radius: 5px; padding: 5px 12px;")
        self.btn_export_txt.clicked.connect(self._export_to_txt)
        tool_layout.addWidget(self.btn_export_txt)

        root_layout.addWidget(toolbar)

        # Progress bar for translations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        root_layout.addWidget(self.progress_bar)

        # 3. View Switcher Tabs (Aligned Table vs Continuous Text)
        self.view_tabs = QTabWidget()

        # TAB 1: Aligned Line-by-Line Table View (PRIMARY & DEFAULT)
        self.tab_table_view = self._create_table_view()
        self.view_tabs.addTab(self.tab_table_view, "📊 Aligned Line-by-Line Grid (Exact Row Matching)")

        # TAB 2: Continuous Split View
        self.tab_text_view = self._create_text_view()
        self.view_tabs.addTab(self.tab_text_view, "📝 Free-Form Side-by-Side Text")

        self.view_tabs.currentChanged.connect(self._on_view_tab_changed)
        root_layout.addWidget(self.view_tabs, stretch=1)

    def _create_table_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 6, 4, 4)
        layout.setSpacing(6)

        # Table Control Bar
        row_tools = QHBoxLayout()
        self.lbl_table_status = QLabel("Showing 0 aligned rows. Both languages stay strictly on the same line.")
        self.lbl_table_status.setStyleSheet("color: #495057; font-weight: 500; font-size: 12px;")
        row_tools.addWidget(self.lbl_table_status)
        row_tools.addStretch()

        btn_add_row = QPushButton("➕ Add Row")
        btn_add_row.clicked.connect(self._add_row)
        btn_del_row = QPushButton("➖ Delete Row")
        btn_del_row.clicked.connect(self._delete_selected_row)
        btn_trans_row = QPushButton("⚡ Translate Selected Row")
        btn_trans_row.clicked.connect(self._translate_selected_row)
        btn_open_src_tab = QPushButton("📂 Open Source Doc")
        btn_open_src_tab.clicked.connect(self._open_source_file)
        btn_open_tgt_tab = QPushButton("📂 Open Translated Doc")
        btn_open_tgt_tab.clicked.connect(self._open_target_file)

        row_tools.addWidget(btn_open_src_tab)
        row_tools.addWidget(btn_open_tgt_tab)
        row_tools.addWidget(btn_trans_row)
        row_tools.addWidget(btn_add_row)
        row_tools.addWidget(btn_del_row)
        layout.addLayout(row_tools)

        # The Aligned Grid Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["#", "Source (English)", "Translated (Hindi - Devanagari)"])
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                background-color: #FFFFFF;
                alternate-background-color: #F8F9FA;
                selection-background-color: #E3F2FD;
                selection-color: #000000;
                border: 1px solid #CED4DA;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #ECEFF1;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #CFD8DC;
            }
        """)

        # Set custom multi-line delegate
        self.delegate = MultiLineDelegate(self.combo_fonts.currentText(), self.spin_font_size.value(), self.table)
        self.table.setItemDelegateForColumn(1, self.delegate)
        self.table.setItemDelegateForColumn(2, self.delegate)
        self.table.itemChanged.connect(self._on_table_item_changed)

        layout.addWidget(self.table, stretch=1)
        return widget

    def _create_text_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 6, 4, 4)
        layout.setSpacing(6)

        # Sync Scroll Checkbox in text view
        text_top = QHBoxLayout()
        lbl_hint = QLabel("Continuous document comparison mode.")
        lbl_hint.setStyleSheet("color: #757575; font-size: 11px;")
        text_top.addWidget(lbl_hint)
        text_top.addStretch()

        self.chk_sync_scroll = QCheckBox("🔗 Synchronize Scrolling")
        self.chk_sync_scroll.setChecked(True)
        self.chk_sync_scroll.setStyleSheet("font-weight: 600; color: #2E7D32;")
        text_top.addWidget(self.chk_sync_scroll)
        layout.addLayout(text_top)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left (Source)
        src_w = QWidget()
        l_src = QVBoxLayout(src_w)
        l_src.setContentsMargins(2, 2, 2, 2)
        row_src = QHBoxLayout()
        self.lbl_src_title = QLabel("Source (English)")
        self.lbl_src_title.setStyleSheet("font-weight: bold; color: #1565C0;")
        btn_clr_src = QPushButton("Clear")
        btn_clr_src.clicked.connect(lambda: self.txt_src.clear())
        row_src.addWidget(self.lbl_src_title)
        row_src.addStretch()
        row_src.addWidget(btn_clr_src)
        l_src.addLayout(row_src)

        self.lbl_src_file = QLabel("No document opened")
        self.lbl_src_file.setStyleSheet("color: #757575; font-size: 11px; font-style: italic;")
        l_src.addWidget(self.lbl_src_file)

        self.txt_src = QTextEdit()
        self.txt_src.setPlaceholderText("Source text appears here...")
        self.txt_src.textChanged.connect(self._update_stats)
        l_src.addWidget(self.txt_src)

        self.lbl_src_stats = QLabel("Paragraphs: 0 | Words: 0 | Characters: 0")
        self.lbl_src_stats.setStyleSheet("color: #757575; font-size: 11px;")
        l_src.addWidget(self.lbl_src_stats)
        splitter.addWidget(src_w)

        # Right (Target)
        tgt_w = QWidget()
        l_tgt = QVBoxLayout(tgt_w)
        l_tgt.setContentsMargins(2, 2, 2, 2)
        row_tgt = QHBoxLayout()
        self.lbl_tgt_title = QLabel("Translated (Hindi - Devanagari)")
        self.lbl_tgt_title.setStyleSheet("font-weight: bold; color: #6A1B9A;")
        btn_clr_tgt = QPushButton("Clear")
        btn_clr_tgt.clicked.connect(lambda: self.txt_tgt.clear())
        row_tgt.addWidget(self.lbl_tgt_title)
        row_tgt.addStretch()
        row_tgt.addWidget(btn_clr_tgt)
        l_tgt.addLayout(row_tgt)

        self.lbl_tgt_file = QLabel("No document opened")
        self.lbl_tgt_file.setStyleSheet("color: #757575; font-size: 11px; font-style: italic;")
        l_tgt.addWidget(self.lbl_tgt_file)

        self.txt_tgt = QTextEdit()
        self.txt_tgt.setPlaceholderText("Translated text appears here...")
        self.txt_tgt.textChanged.connect(self._update_stats)
        l_tgt.addWidget(self.txt_tgt)

        self.lbl_tgt_stats = QLabel("Paragraphs: 0 | Words: 0 | Characters: 0")
        self.lbl_tgt_stats.setStyleSheet("color: #757575; font-size: 11px;")
        l_tgt.addWidget(self.lbl_tgt_stats)
        splitter.addWidget(tgt_w)

        splitter.setSizes([500, 500])
        layout.addWidget(splitter, stretch=1)

        # Synchronize text scrolling
        self.txt_src.verticalScrollBar().valueChanged.connect(self._sync_scroll_src_to_tgt)
        self.txt_tgt.verticalScrollBar().valueChanged.connect(self._sync_scroll_tgt_to_src)

        return widget

    def swap_direction(self):
        """Swaps translation direction between English -> Hindi and Hindi -> English."""
        self.src_lang, self.tgt_lang = self.tgt_lang, self.src_lang

        # Swap Badges & Labels
        if self.src_lang == "en":
            src_name = "English (EN)"
            tgt_name = "Hindi (HI - Devanagari)"
        else:
            src_name = "Hindi (HI - Devanagari)"
            tgt_name = "English (EN)"

        self.lbl_src_badge.setText(f"Source: {src_name}")
        self.lbl_tgt_badge.setText(f"Target: {tgt_name}")
        self.lbl_src_title.setText(f"Source ({src_name})")
        self.lbl_tgt_title.setText(f"Translated ({tgt_name})")
        self.table.setHorizontalHeaderLabels(["#", f"Source ({src_name})", f"Translated ({tgt_name})"])

        # Swap columns in the table
        self._updating_table = True
        for row in range(self.table.rowCount()):
            item1 = self.table.item(row, 1)
            item2 = self.table.item(row, 2)
            t1 = item1.text() if item1 else ""
            t2 = item2.text() if item2 else ""
            if item1:
                item1.setText(t2)
            if item2:
                item2.setText(t1)
        self._updating_table = False

        # Swap contents in the text edits
        src_text = self.txt_src.toPlainText()
        tgt_text = self.txt_tgt.toPlainText()
        self.txt_src.setPlainText(tgt_text)
        self.txt_tgt.setPlainText(src_text)

        self._on_font_changed()
        self.table.resizeRowsToContents()
        self._update_stats()

    def _on_font_changed(self):
        font_name = self.combo_fonts.currentText()
        font_size = self.spin_font_size.value()
        qfont = QFont(font_name, font_size)

        # Apply to target editor if target is Hindi, else to source
        if self.tgt_lang == "hi":
            self.txt_tgt.setFont(qfont)
            self.delegate.font_name = font_name
            self.delegate.font_size = font_size
            self.table.setItemDelegateForColumn(2, self.delegate)
        else:
            self.txt_src.setFont(qfont)
            self.delegate.font_name = font_name
            self.delegate.font_size = font_size
            self.table.setItemDelegateForColumn(1, self.delegate)

        self.table.resizeRowsToContents()

    def _on_font_size_changed(self, size: int):
        self._on_font_changed()

    def _sync_scroll_src_to_tgt(self, val: int):
        if not self.chk_sync_scroll.isChecked() or self._syncing_scroll:
            return
        self._syncing_scroll = True
        max_src = self.txt_src.verticalScrollBar().maximum()
        max_tgt = self.txt_tgt.verticalScrollBar().maximum()
        if max_src > 0 and max_tgt > 0:
            ratio = val / max_src
            self.txt_tgt.verticalScrollBar().setValue(int(ratio * max_tgt))
        self._syncing_scroll = False

    def _sync_scroll_tgt_to_src(self, val: int):
        if not self.chk_sync_scroll.isChecked() or self._syncing_scroll:
            return
        self._syncing_scroll = True
        max_src = self.txt_src.verticalScrollBar().maximum()
        max_tgt = self.txt_tgt.verticalScrollBar().maximum()
        if max_src > 0 and max_tgt > 0:
            ratio = val / max_tgt
            self.txt_src.verticalScrollBar().setValue(int(ratio * max_src))
        self._syncing_scroll = False

    def _extract_text_from_file(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == ".docx":
            doc = docx.Document(file_path)
            paragraphs = []
            for p in doc.paragraphs:
                if p.text.strip():
                    paragraphs.append(p.text.strip())
            for t in doc.tables:
                for row in t.rows:
                    row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_texts:
                        paragraphs.append(" | ".join(row_texts))
            return "\n\n".join(paragraphs)
        elif ext == ".pdf":
            doc = fitz.open(file_path)
            paragraphs = []
            for page in doc:
                raw_text = page.get_text()
                text = str(raw_text) if raw_text is not None else ""
                if text.strip():
                    paragraphs.append(text.strip())
            return "\n\n".join(paragraphs)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def _split_text(self, text: str) -> List[str]:
        mode = self.combo_alignment.currentText()
        if "Line by Line" in mode:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            return lines
        else:
            paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            return paras

    def populate_table_from_texts(self, src_text: str, tgt_text: str):
        """Populates the aligned table row-by-row with automatic height fitting."""
        self._updating_table = True
        src_items = self._split_text(src_text)
        tgt_items = self._split_text(tgt_text)

        max_rows = max(len(src_items), len(tgt_items))
        self.table.setRowCount(max_rows)

        for row in range(max_rows):
            # Row index
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, num_item)

            # Source text
            s_val = src_items[row] if row < len(src_items) else ""
            s_item = QTableWidgetItem(s_val)
            self.table.setItem(row, 1, s_item)

            # Target text
            t_val = tgt_items[row] if row < len(tgt_items) else ""
            t_item = QTableWidgetItem(t_val)
            self.table.setItem(row, 2, t_item)

        self._updating_table = False
        self.table.resizeRowsToContents()
        self.lbl_table_status.setText(f"Showing {max_rows} aligned rows locked side-by-side on the same line.")

    def _realign_from_text(self):
        src_text = self.txt_src.toPlainText()
        tgt_text = self.txt_tgt.toPlainText()
        if src_text or tgt_text:
            self.populate_table_from_texts(src_text, tgt_text)

    def _on_table_item_changed(self, item: QTableWidgetItem):
        if self._updating_table:
            return
        row = item.row()
        # Recalculate row height when text changes
        self.table.resizeRowToContents(row)

    def _on_view_tab_changed(self, index: int):
        if index == 0:
            # Switched to Table View: sync from text edits
            src_text = self.txt_src.toPlainText()
            tgt_text = self.txt_tgt.toPlainText()
            self.populate_table_from_texts(src_text, tgt_text)
        else:
            # Switched to Text View: sync from table items
            src_list = []
            tgt_list = []
            sep = "\n" if "Line by Line" in self.combo_alignment.currentText() else "\n\n"
            for row in range(self.table.rowCount()):
                item1 = self.table.item(row, 1)
                item2 = self.table.item(row, 2)
                src_list.append(item1.text() if item1 else "")
                tgt_list.append(item2.text() if item2 else "")
            self.txt_src.setPlainText(sep.join(src_list))
            self.txt_tgt.setPlainText(sep.join(tgt_list))
            self._update_stats()

    def _add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        num_item = QTableWidgetItem(str(row + 1))
        num_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, num_item)
        self.table.setItem(row, 1, QTableWidgetItem(""))
        self.table.setItem(row, 2, QTableWidgetItem(""))
        self.table.resizeRowToContents(row)
        self.lbl_table_status.setText(f"Showing {self.table.rowCount()} aligned rows.")

    def _delete_selected_row(self):
        selected_rows = sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)
        if not selected_rows:
            QMessageBox.information(self, "Select Row", "Please select a row in the table to delete.")
            return
        for r in selected_rows:
            self.table.removeRow(r)
        # Renumber
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item:
                item.setText(str(r + 1))
        self.lbl_table_status.setText(f"Showing {self.table.rowCount()} aligned rows.")

    def _translate_selected_row(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Row", "Please select a row to translate.")
            return

        src_item = self.table.item(row, 1)
        src_text = src_item.text().strip() if src_item else ""
        if not src_text:
            QMessageBox.warning(self, "Empty Text", "Selected row has no source text.")
            return

        if not self.engine:
            QMessageBox.critical(self, "Error", "Translation engine is not initialized.")
            return

        try:
            trans = self.engine.translate(src_text, self.src_lang, self.tgt_lang)
            self._updating_table = True
            tgt_item = self.table.item(row, 2)
            if not tgt_item:
                tgt_item = QTableWidgetItem("")
                self.table.setItem(row, 2, tgt_item)
            tgt_item.setText(trans)
            self._updating_table = False
            self.table.resizeRowToContents(row)
        except Exception as e:
            QMessageBox.critical(self, "Translation Error", str(e))

    def _on_translate_all(self):
        # Collect source items from table
        items = []
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 1)
            items.append(it.text() if it else "")

        if not items or all(not it.strip() for it in items):
            # If table is empty, check text edit
            src_text = self.txt_src.toPlainText().strip()
            if not src_text:
                QMessageBox.warning(self, "Empty Content", "Please load or enter source text to translate.")
                return
            self.populate_table_from_texts(src_text, "")
            items = []
            for r in range(self.table.rowCount()):
                it = self.table.item(r, 1)
                items.append(it.text() if it is not None else "")

        self.btn_live_translate.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.worker = TableTranslateWorker(self.engine, items, self.src_lang, self.tgt_lang)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_table_translate_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, current: int, total: int):
        if total > 0:
            self.progress_bar.setValue(int((current / total) * 100))

    def _on_table_translate_finished(self, results: List[str]):
        self.btn_live_translate.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._updating_table = True

        for r, trans in enumerate(results):
            if r < self.table.rowCount():
                tgt_item = self.table.item(r, 2)
                if not tgt_item:
                    tgt_item = QTableWidgetItem("")
                    self.table.setItem(r, 2, tgt_item)
                tgt_item.setText(trans)

        self._updating_table = False
        self.table.resizeRowsToContents()

        # Also sync back to txt_tgt
        sep = "\n" if "Line by Line" in self.combo_alignment.currentText() else "\n\n"
        self.txt_tgt.setPlainText(sep.join(results))
        self._update_stats()

        QMessageBox.information(self, "Complete", "All lines translated and aligned side-by-side on the same line!")

    def _on_error(self, err_msg: str):
        self.btn_live_translate.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Translation Error", f"Translation failed:\n{err_msg}")

    def _open_source_file(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Select Source Document", "", "Documents (*.docx *.pdf *.txt *.md *.csv)"
        )
        if f:
            try:
                text = self._extract_text_from_file(f)
                self.current_source_path = f
                self.lbl_src_file.setText(f"File: {Path(f).name}")
                self.txt_src.setPlainText(text)
                self.populate_table_from_texts(text, self.txt_tgt.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Read Error", f"Could not read file:\n{str(e)}")

    def _open_target_file(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Select Translated Document", "", "Documents (*.docx *.pdf *.txt *.md)"
        )
        if f:
            try:
                text = self._extract_text_from_file(f)
                self.current_target_path = f
                self.lbl_tgt_file.setText(f"File: {Path(f).name}")
                self.txt_tgt.setPlainText(text)
                self.populate_table_from_texts(self.txt_src.toPlainText(), text)
            except Exception as e:
                QMessageBox.critical(self, "Read Error", f"Could not read file:\n{str(e)}")

    def load_document_pair(self, src_path: str, tgt_path: str, src_lang: str = "en", tgt_lang: str = "hi"):
        """Called automatically by MainWindow when a translation finishes."""
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

        if src_lang == "en":
            self.lbl_src_badge.setText("Source: English (EN)")
            self.lbl_tgt_badge.setText("Target: Hindi (HI - Devanagari)")
            self.lbl_src_title.setText("Source (English)")
            self.lbl_tgt_title.setText("Translated (Hindi - Devanagari)")
            self.table.setHorizontalHeaderLabels(["#", "Source (English)", "Translated (Hindi - Devanagari)"])
        else:
            self.lbl_src_badge.setText("Source: Hindi (HI - Devanagari)")
            self.lbl_tgt_badge.setText("Target: English (EN)")
            self.lbl_src_title.setText("Source (Hindi - Devanagari)")
            self.lbl_tgt_title.setText("Translated (English)")
            self.table.setHorizontalHeaderLabels(["#", "Source (Hindi - Devanagari)", "Translated (English)"])

        src_text = ""
        tgt_text = ""
        if os.path.exists(src_path):
            self.current_source_path = src_path
            self.lbl_src_file.setText(f"File: {Path(src_path).name}")
            try:
                src_text = self._extract_text_from_file(src_path)
                self.txt_src.setPlainText(src_text)
            except Exception:
                pass

        if os.path.exists(tgt_path):
            self.current_target_path = tgt_path
            self.lbl_tgt_file.setText(f"File: {Path(tgt_path).name}")
            try:
                tgt_text = self._extract_text_from_file(tgt_path)
                self.txt_tgt.setPlainText(tgt_text)
            except Exception:
                pass

        self.populate_table_from_texts(src_text, tgt_text)
        self._update_stats()

    def set_content(self, src_text: str, tgt_text: str, src_lang: str = "en", tgt_lang: str = "hi"):
        """Legacy helper maintained for backward compatibility."""
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.txt_src.setPlainText(src_text)
        self.txt_tgt.setPlainText(tgt_text)
        self.populate_table_from_texts(src_text, tgt_text)
        self._update_stats()

    def get_edited_target_text(self) -> str:
        tgt_list = []
        sep = "\n" if "Line by Line" in self.combo_alignment.currentText() else "\n\n"
        for row in range(self.table.rowCount()):
            it = self.table.item(row, 2)
            if it and it.text().strip():
                tgt_list.append(it.text().strip())
        return sep.join(tgt_list)

    def _update_stats(self):
        src_text = self.txt_src.toPlainText()
        src_paras = len([p for p in src_text.split("\n\n") if p.strip()])
        src_words = len(src_text.split())
        src_chars = len(src_text)
        self.lbl_src_stats.setText(f"Paragraphs: {src_paras} | Words: {src_words} | Characters: {src_chars}")

        tgt_text = self.txt_tgt.toPlainText()
        tgt_paras = len([p for p in tgt_text.split("\n\n") if p.strip()])
        tgt_words = len(tgt_text.split())
        tgt_chars = len(tgt_text)
        self.lbl_tgt_stats.setText(f"Paragraphs: {tgt_paras} | Words: {tgt_words} | Characters: {tgt_chars}")

    def _export_to_docx(self):
        tgt_text = self.get_edited_target_text()
        if not tgt_text.strip():
            QMessageBox.warning(self, "No Content", "There is no translated text in the table to export.")
            return

        default_name = "edited_translated.docx"
        if self.current_target_path:
            p = Path(self.current_target_path)
            default_name = f"{p.stem}_edited.docx"

        f, _ = QFileDialog.getSaveFileName(self, "Export Word Document", default_name, "Word Document (*.docx)")
        if not f:
            return

        try:
            doc = docx.Document()
            font_name = self.combo_fonts.currentText()
            font_size = self.spin_font_size.value()

            paragraphs = tgt_text.split("\n\n" if "Paragraph by Paragraph" in self.combo_alignment.currentText() else "\n")
            for para_str in paragraphs:
                if not para_str.strip():
                    continue
                p = doc.add_paragraph()
                run = p.add_run(para_str.strip())
                run.font.name = font_name
                run.font.size = Pt(font_size)

                # Set Word XML font elements for Devanagari Unicode
                rPr = run._r.get_or_add_rPr()
                rFonts = OxmlElement('w:rFonts')
                rFonts.set(qn('w:ascii'), font_name)
                rFonts.set(qn('w:hAnsi'), font_name)
                rFonts.set(qn('w:cs'), font_name)
                rPr.append(rFonts)

            doc.save(f)
            QMessageBox.information(self, "Saved", f"Aligned document exported successfully:\n{Path(f).name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Could not export DOCX:\n{str(e)}")

    def _export_to_txt(self):
        tgt_text = self.get_edited_target_text()
        if not tgt_text.strip():
            QMessageBox.warning(self, "No Content", "There is no translated text to export.")
            return

        default_name = "edited_translated.txt"
        if self.current_target_path:
            p = Path(self.current_target_path)
            default_name = f"{p.stem}_edited.txt"

        f, _ = QFileDialog.getSaveFileName(self, "Export Plain Text", default_name, "Plain Text (*.txt)")
        if not f:
            return

        try:
            with open(f, "w", encoding="utf-8") as out:
                out.write(tgt_text)
            QMessageBox.information(self, "Saved", f"Plain text saved successfully:\n{Path(f).name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Could not export TXT:\n{str(e)}")
