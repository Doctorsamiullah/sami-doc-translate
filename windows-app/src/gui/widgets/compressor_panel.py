import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QDoubleSpinBox, QComboBox, QCheckBox, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt
from src.core.compressor.file_compressor import FileCompressor

class CompressorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file: str = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Header
        header = QLabel("Intelligent Document Compressor")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #8E24AA;")
        sub = QLabel("Reduce file sizes down to an exact target while strictly preserving text readability, vectors, and font crispness.")
        sub.setStyleSheet("color: #6C757D; font-size: 12px;")
        layout.addWidget(header)
        layout.addWidget(sub)

        # File selection row
        file_row = QHBoxLayout()
        self.lbl_file = QLabel("No document selected")
        self.lbl_file.setStyleSheet("padding: 8px; background: #FFFFFF; border: 1px solid #CED4DA; border-radius: 6px;")
        btn_browse = QPushButton("Select Document")
        btn_browse.clicked.connect(self._select_file)
        file_row.addWidget(self.lbl_file, stretch=1)
        file_row.addWidget(btn_browse)
        layout.addLayout(file_row)

        # Target Size controls
        target_group = QHBoxLayout()
        lbl_target = QLabel("Target File Size:")
        lbl_target.setStyleSheet("font-weight: 600;")
        
        self.spin_size = QDoubleSpinBox()
        self.spin_size.setRange(0.1, 500.0)
        self.spin_size.setValue(2.0)
        self.spin_size.setSingleStep(0.5)

        self.combo_unit = QComboBox()
        self.combo_unit.addItems(["MB", "KB"])

        target_group.addWidget(lbl_target)
        target_group.addWidget(self.spin_size)
        target_group.addWidget(self.combo_unit)
        target_group.addStretch()
        layout.addLayout(target_group)

        # Preservation checkboxes
        self.chk_readability = QCheckBox("Preserve Text Readability & Vector Quality (>= 150 DPI floor)")
        self.chk_readability.setChecked(True)
        self.chk_cleanup = QCheckBox("Auto-Clear Temporary Scratch Cache immediately after compression")
        self.chk_cleanup.setChecked(True)
        layout.addWidget(self.chk_readability)
        layout.addWidget(self.chk_cleanup)

        # Action button
        self.btn_compress = QPushButton("Compress Document Now")
        self.btn_compress.setFixedHeight(42)
        self.btn_compress.clicked.connect(self._start_compression)
        layout.addWidget(self.btn_compress)

        # Progress bar & Result
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("font-weight: 600; color: #495057;")
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.lbl_status)

        layout.addStretch()

    def _select_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select File to Compress", "", "Documents (*.pdf *.docx *.pptx *.xlsx)")
        if f:
            self.selected_file = f
            size_mb = os.path.getsize(f) / (1024 * 1024)
            self.lbl_file.setText(f"{Path(f).name} ({size_mb:.2f} MB)")

    def _start_compression(self):
        if not self.selected_file or not os.path.exists(self.selected_file):
            QMessageBox.warning(self, "No File", "Please select a document first.")
            return

        unit = self.combo_unit.currentText()
        val = self.spin_size.value()
        target_bytes = int(val * 1024 * 1024 if unit == "MB" else val * 1024)

        orig_p = Path(self.selected_file)
        out_p = orig_p.with_name(f"{orig_p.stem}_compressed{orig_p.suffix}")

        self.btn_compress.setEnabled(False)
        self.progress_bar.setValue(30)
        self.lbl_status.setText("Compressing...")

        try:
            def on_progress(pct: float, msg: str):
                self.progress_bar.setValue(int(pct * 100))
                self.lbl_status.setText(msg)

            success = FileCompressor.compress_file(
                self.selected_file,
                str(out_p),
                target_size_bytes=target_bytes,
                preserve_readability=self.chk_readability.isChecked(),
                progress_callback=on_progress
            )

            if success:
                new_mb = os.path.getsize(out_p) / (1024 * 1024)
                orig_mb = os.path.getsize(self.selected_file) / (1024 * 1024)
                reduction = ((orig_mb - new_mb) / orig_mb) * 100
                self.progress_bar.setValue(100)
                msg = f"Done! Size reduced from {orig_mb:.2f} MB to {new_mb:.2f} MB ({reduction:.1f}% reduction).\nSaved as: {out_p.name}"
                self.lbl_status.setText(msg)
                QMessageBox.information(self, "Compression Success", msg)
        except Exception as e:
            QMessageBox.critical(self, "Compression Error", str(e))
            self.lbl_status.setText(f"Error: {e}")
        finally:
            self.btn_compress.setEnabled(True)

