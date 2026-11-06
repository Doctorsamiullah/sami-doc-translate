import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal

from src.config import APP_NAME, APP_VERSION, SUPPORTED_EXTENSIONS
from src.db.sqlite_db import DatabaseManager
from src.core.nmt.offline_engine import OfflineTranslationEngine
from src.core.parsers.docx_parser import DocxParser
from src.core.parsers.pdf_parser import PdfParser
from src.core.parsers.text_parser import TextParser
from src.core.converter.format_converter import FormatConverter
from src.core.fonts.font_manager import FontManager

from src.gui.themes import ThemeManager
from src.gui.widgets.drop_zone import DropZoneWidget
from src.gui.widgets.progress_card import ProgressCardWidget
from src.gui.widgets.compressor_panel import CompressorPanel
from src.gui.widgets.preview_panel import PreviewPanel
from src.gui.widgets.docx_styler_panel import DocxStylerPanel

class TranslationWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal(bool, str)

    def __init__(self, parser, input_path, output_path, engine, src_lang, tgt_lang, font_name="Noto Sans Devanagari"):
        super().__init__()
        self.parser = parser
        self.input_path = input_path
        self.output_path = output_path
        self.engine = engine
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.font_name = font_name

    def run(self):
        try:
            kwargs = {
                "progress_callback": lambda c, t, m: self.progress.emit(c, t, m)
            }
            if hasattr(self.parser, "translate_document") and "font_name" in self.parser.translate_document.__code__.co_varnames:
                kwargs["font_name"] = self.font_name

            success = self.parser.translate_document(
                self.input_path,
                self.output_path,
                self.engine,
                self.src_lang,
                self.tgt_lang,
                **kwargs
            )
            self.finished.emit(success, self.output_path)
        except Exception as e:
            self.finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - English ↔ Hindi Offline Suite")
        self.resize(1060, 760)

        # Core Services
        self.db = DatabaseManager()
        self.engine = OfflineTranslationEngine(self.db)
        self.parsers = {
            ".docx": DocxParser(),
            ".pdf": PdfParser(),
            ".txt": TextParser(),
            ".md": TextParser(),
            ".csv": TextParser()
        }

        self.selected_file = ""
        self.src_lang = "en"
        self.tgt_lang = "hi"

        self._init_ui()
        self._apply_theme("Vibrant Rainbow Light")

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(12)

        # Top Header Bar (Title + Language Swap + Theme Switcher)
        header_bar = QHBoxLayout()
        title_label = QLabel(f"🌐 {APP_NAME}")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E88E5;")
        subtitle = QLabel("English ↔ Hindi Document Suite")
        subtitle.setStyleSheet("color: #6C757D; font-size: 12px; margin-left: 8px;")

        # Theme Switcher
        lbl_theme = QLabel("Rainbow Light Theme:")
        lbl_theme.setStyleSheet("font-weight: 600; margin-left: 16px;")
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(ThemeManager.get_theme_names())
        self.combo_theme.currentTextChanged.connect(self._apply_theme)

        header_bar.addWidget(title_label)
        header_bar.addWidget(subtitle)
        header_bar.addStretch()
        header_bar.addWidget(lbl_theme)
        header_bar.addWidget(self.combo_theme)
        main_layout.addLayout(header_bar)

        # Navigation Tabs
        self.tabs = QTabWidget()
        self.tab_translator = self._create_translator_tab()
        self.tab_styler = DocxStylerPanel()
        self.tab_converter = self._create_converter_tab()
        self.tab_compressor = CompressorPanel()
        self.tab_preview = PreviewPanel()
        self.tab_preview.set_engine(self.engine)

        self.tabs.addTab(self.tab_translator, "📄 Document Translator")
        self.tabs.addTab(self.tab_styler, "🖋️ DOCX Headings & Fonts")
        self.tabs.addTab(self.tab_converter, "🔄 Format Converter")
        self.tabs.addTab(self.tab_compressor, "🗜️ File Compressor")
        self.tabs.addTab(self.tab_preview, "🔍 Side-by-Side Editor")
        main_layout.addWidget(self.tabs)

    def _apply_theme(self, theme_name: str):
        stylesheet = ThemeManager.get_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)

    def _create_translator_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)

        # Direction Switcher Row
        dir_layout = QHBoxLayout()
        self.lbl_src = QLabel("English (EN)")
        self.lbl_src.setStyleSheet("font-weight: bold; font-size: 14px; color: #1E88E5; padding: 6px 12px; background: #E3F2FD; border-radius: 6px;")
        
        self.btn_swap = QPushButton("⇄ Swap Direction")
        self.btn_swap.setFixedWidth(150)
        self.btn_swap.clicked.connect(self._swap_languages)

        self.lbl_tgt = QLabel("Hindi (HI - Devanagari)")
        self.lbl_tgt.setStyleSheet("font-weight: bold; font-size: 14px; color: #8E24AA; padding: 6px 12px; background: #F3E5F5; border-radius: 6px;")

        dir_layout.addStretch()
        dir_layout.addWidget(self.lbl_src)
        dir_layout.addWidget(self.btn_swap)
        dir_layout.addWidget(self.lbl_tgt)
        dir_layout.addStretch()
        layout.addLayout(dir_layout)

        # Drop Zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.fileSelected.connect(self._on_file_selected)
        layout.addWidget(self.drop_zone)

        # Target Format & Font selection row
        opts_row = QHBoxLayout()
        lbl_fmt = QLabel("Target Format:")
        lbl_fmt.setStyleSheet("font-weight: 600;")
        self.combo_format = QComboBox()
        self.combo_format.addItems(["Same as Source", "Word Document (.docx)", "PDF Document (.pdf)", "Plain Text (.txt)"])

        lbl_font = QLabel("Devanagari Font:")
        lbl_font.setStyleSheet("font-weight: 600; margin-left: 14px;")
        self.combo_font = QComboBox()
        self.combo_font.addItems(FontManager.get_all_font_names())

        opts_row.addWidget(lbl_fmt)
        opts_row.addWidget(self.combo_format)
        opts_row.addWidget(lbl_font)
        opts_row.addWidget(self.combo_font)
        opts_row.addStretch()
        layout.addLayout(opts_row)

        # Action Button
        self.btn_translate = QPushButton("Translate Document (Unlimited Streaming)")
        self.btn_translate.setFixedHeight(44)
        self.btn_translate.clicked.connect(self._start_translation)
        layout.addWidget(self.btn_translate)

        # Progress Card
        self.progress_card = ProgressCardWidget()
        layout.addWidget(self.progress_card)

        return widget

    def _create_converter_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)

        header = QLabel("Standalone Format Converter")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E88E5;")
        sub = QLabel("Convert between PDF, DOCX, TXT, and Markdown without translation.")
        sub.setStyleSheet("color: #6C757D; font-size: 12px;")
        layout.addWidget(header)
        layout.addWidget(sub)

        row1 = QHBoxLayout()
        self.lbl_conv_file = QLabel("No document selected")
        self.lbl_conv_file.setStyleSheet("padding: 8px; background: #FFFFFF; border: 1px solid #CED4DA; border-radius: 6px;")
        btn_sel = QPushButton("Select File")
        btn_sel.clicked.connect(self._select_convert_file)
        row1.addWidget(self.lbl_conv_file, stretch=1)
        row1.addWidget(btn_sel)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        lbl_to = QLabel("Convert To:")
        lbl_to.setStyleSheet("font-weight: 600;")
        self.combo_conv_target = QComboBox()
        self.combo_conv_target.addItems([".pdf", ".docx", ".txt"])
        row2.addWidget(lbl_to)
        row2.addWidget(self.combo_conv_target)
        row2.addStretch()
        layout.addLayout(row2)

        self.btn_run_convert = QPushButton("Convert File Format")
        self.btn_run_convert.setFixedHeight(42)
        self.btn_run_convert.clicked.connect(self._run_conversion)
        layout.addWidget(self.btn_run_convert)

        layout.addStretch()
        return widget

    def _swap_languages(self):
        self.src_lang, self.tgt_lang = self.tgt_lang, self.src_lang
        if self.src_lang == "en":
            self.lbl_src.setText("English (EN)")
            self.lbl_tgt.setText("Hindi (HI - Devanagari)")
        else:
            self.lbl_src.setText("Hindi (HI - Devanagari)")
            self.lbl_tgt.setText("English (EN)")
        self.tab_preview.src_lang = self.src_lang
        self.tab_preview.tgt_lang = self.tgt_lang
        self.tab_preview.lbl_src_title.setText(f"Source ({'English' if self.src_lang == 'en' else 'Hindi'})")
        self.tab_preview.lbl_tgt_title.setText(f"Translated ({'Hindi - Devanagari' if self.tgt_lang == 'hi' else 'English'})")

    def _on_file_selected(self, path: str):
        self.selected_file = path

    def _select_convert_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Document to Convert", "", "Documents (*.pdf *.docx *.txt *.md)")
        if f:
            self.conv_file = f
            self.lbl_conv_file.setText(Path(f).name)

    def _run_conversion(self):
        if not hasattr(self, 'conv_file') or not self.conv_file:
            QMessageBox.warning(self, "No File", "Please select a file to convert.")
            return

        target_ext = self.combo_conv_target.currentText()
        p = Path(self.conv_file)
        out_p = p.with_name(f"{p.stem}_converted{target_ext}")

        try:
            success = FormatConverter.convert(self.conv_file, str(out_p))
            if success:
                QMessageBox.information(self, "Success", f"File converted successfully:\n{out_p.name}")
        except Exception as e:
            QMessageBox.critical(self, "Conversion Failed", str(e))

    def _start_translation(self):
        if not self.selected_file or not os.path.exists(self.selected_file):
            QMessageBox.warning(self, "Select Document", "Please select or drop a valid document first.")
            return

        p = Path(self.selected_file)
        ext = p.suffix.lower()
        if ext not in self.parsers:
            QMessageBox.critical(self, "Unsupported", f"Extension {ext} is not supported.")
            return

        out_name = f"{p.stem}_{self.tgt_lang}{ext}"
        out_path = str(p.with_name(out_name))

        selected_font = self.combo_font.currentText()

        self.btn_translate.setEnabled(False)
        self.progress_card.set_running(True)

        parser = self.parsers[ext]
        self.worker = TranslationWorker(
            parser, self.selected_file, out_path, self.engine, self.src_lang, self.tgt_lang, font_name=selected_font
        )
        self.worker.progress.connect(self.progress_card.set_progress)
        self.worker.finished.connect(self._on_translation_finished)
        self.worker.start()

    def _on_translation_finished(self, success: bool, result: str):
        self.btn_translate.setEnabled(True)
        self.progress_card.set_running(False)
        if success:
            try:
                self.tab_preview.load_document_pair(self.selected_file, result, self.src_lang, self.tgt_lang)
            except Exception as e:
                print(f"Error loading preview: {e}")

            reply = QMessageBox.question(
                self,
                "Translation Complete",
                f"Document translated successfully into Devanagari Hindi!\nSaved to:\n{result}\n\nWould you like to open it in the Side-by-Side Editor now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.tabs.setCurrentWidget(self.tab_preview)
        else:
            QMessageBox.critical(self, "Translation Error", f"An error occurred:\n{result}")
