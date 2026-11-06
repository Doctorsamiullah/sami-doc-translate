import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QComboBox, QSpinBox, QCheckBox, QMessageBox, QProgressBar, QGroupBox
)
from PySide6.QtCore import Qt
from src.core.fonts.font_manager import FontManager
from src.core.parsers.docx_formatter import DocxStyleFormatter

class DocxStylerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file: str = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Header
        header = QLabel("DOCX Heading, Subheading & Numbering Formatter")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E88E5;")
        sub = QLabel("Customize typography hierarchy, auto-number subheadings, and apply Devanagari/Unicode fonts to your Word document.")
        sub.setStyleSheet("color: #6C757D; font-size: 12px;")
        layout.addWidget(header)
        layout.addWidget(sub)

        # File Picker Row
        file_box = QGroupBox("Select Word Document (.docx)")
        file_layout = QHBoxLayout(file_box)
        self.lbl_file = QLabel("No document selected")
        self.lbl_file.setStyleSheet("padding: 8px; background: #FFFFFF; border: 1px solid #CED4DA; border-radius: 6px;")
        btn_browse = QPushButton("Browse DOCX")
        btn_browse.clicked.connect(self._select_file)
        file_layout.addWidget(self.lbl_file, stretch=1)
        file_layout.addWidget(btn_browse)
        layout.addWidget(file_box)

        # Font Selection Group
        font_box = QGroupBox("Devanagari Font Family")
        font_layout = QVBoxLayout(font_box)
        
        row_font = QHBoxLayout()
        lbl_font = QLabel("Choose Font:")
        lbl_font.setStyleSheet("font-weight: 600;")
        self.combo_fonts = QComboBox()
        self.combo_fonts.addItems(FontManager.get_all_font_names())
        self.combo_fonts.currentTextChanged.connect(self._on_font_changed)
        row_font.addWidget(lbl_font)
        row_font.addWidget(self.combo_fonts, stretch=1)
        font_layout.addLayout(row_font)

        self.lbl_font_desc = QLabel(FontManager.FONT_DESCRIPTIONS.get(FontManager.get_default_font(), ""))
        self.lbl_font_desc.setStyleSheet("color: #495057; font-style: italic; font-size: 11px; padding: 4px;")
        font_layout.addWidget(self.lbl_font_desc)
        layout.addWidget(font_box)

        # Styling & Numbering Controls Group
        style_box = QGroupBox("Headings & Subheadings Configuration")
        style_layout = QVBoxLayout(style_box)

        # Heading 1 & Subheading sizes
        sizes_row = QHBoxLayout()
        lbl_h1 = QLabel("Heading 1 Size:")
        lbl_h1.setStyleSheet("font-weight: 600;")
        self.spin_h1 = QSpinBox()
        self.spin_h1.setRange(12, 32)
        self.spin_h1.setValue(16)

        lbl_h2 = QLabel("Subheading Size:")
        lbl_h2.setStyleSheet("font-weight: 600; margin-left: 12px;")
        self.spin_h2 = QSpinBox()
        self.spin_h2.setRange(10, 24)
        self.spin_h2.setValue(13)

        sizes_row.addWidget(lbl_h1)
        sizes_row.addWidget(self.spin_h1)
        sizes_row.addWidget(lbl_h2)
        sizes_row.addWidget(self.spin_h2)
        sizes_row.addStretch()
        style_layout.addLayout(sizes_row)

        # Numbering scheme
        num_row = QHBoxLayout()
        lbl_num = QLabel("Subheading Numbering:")
        lbl_num.setStyleSheet("font-weight: 600;")
        self.combo_num = QComboBox()
        self.combo_num.addItems([
            "1.1, 1.2 (Arabic)",
            "१.१, १.२ (Devanagari)",
            "A., B., C. (Capital Alpha)",
            "a., b., c. (Small Alpha)",
            "Keep Original Text"
        ])
        num_row.addWidget(lbl_num)
        num_row.addWidget(self.combo_num, stretch=1)
        style_layout.addLayout(num_row)

        self.chk_bold = QCheckBox("Bold all Headings and Subheadings")
        self.chk_bold.setChecked(True)
        style_layout.addWidget(self.chk_bold)

        layout.addWidget(style_box)

        # Action Button
        self.btn_apply = QPushButton("Apply Typography & Numbering to Document")
        self.btn_apply.setFixedHeight(44)
        self.btn_apply.clicked.connect(self._apply_styling)
        layout.addWidget(self.btn_apply)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("font-weight: 600; color: #495057;")
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.lbl_status)

        layout.addStretch()

    def _select_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select DOCX Document", "", "Word Documents (*.docx)")
        if f:
            self.selected_file = f
            self.lbl_file.setText(f"{Path(f).name} ({os.path.getsize(f) / 1024:.1f} KB)")

    def _on_font_changed(self, font_name: str):
        desc = FontManager.FONT_DESCRIPTIONS.get(font_name, "")
        self.lbl_font_desc.setText(desc)

    def _apply_styling(self):
        if not self.selected_file or not os.path.exists(self.selected_file):
            QMessageBox.warning(self, "No Document", "Please select a .docx file first.")
            return

        font_name = self.combo_fonts.currentText()
        h1_size = self.spin_h1.value()
        h2_size = self.spin_h2.value()
        numbering = self.combo_num.currentText()
        bold = self.chk_bold.isChecked()

        orig_p = Path(self.selected_file)
        out_p = orig_p.with_name(f"{orig_p.stem}_styled{orig_p.suffix}")

        self.btn_apply.setEnabled(False)
        self.progress_bar.setValue(20)
        self.lbl_status.setText("Formatting headings and applying font...")

        try:
            def on_progress(curr, tot, msg):
                pct = int((curr / tot) * 100)
                self.progress_bar.setValue(pct)
                self.lbl_status.setText(msg)

            success = DocxStyleFormatter.format_document(
                input_path=self.selected_file,
                output_path=str(out_p),
                font_name=font_name,
                heading1_size=h1_size,
                subheading_size=h2_size,
                numbering_style=numbering,
                apply_bold_headings=bold,
                progress_callback=on_progress
            )

            if success:
                self.progress_bar.setValue(100)
                msg = f"Done! Document styled with {font_name} and saved as:\n{out_p.name}"
                self.lbl_status.setText(msg)
                QMessageBox.information(self, "Success", msg)
        except Exception as e:
            QMessageBox.critical(self, "Formatting Error", str(e))
            self.lbl_status.setText(f"Error: {e}")
        finally:
            self.btn_apply.setEnabled(True)

