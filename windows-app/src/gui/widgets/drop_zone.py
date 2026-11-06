from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtCore import Qt, Signal
from pathlib import Path
from src.config import SUPPORTED_EXTENSIONS

class DropZoneWidget(QFrame):
    fileSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.selected_file: str = ""

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel("📄")
        self.icon_label.setStyleSheet("font-size: 44px;")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel("Drag & Drop your document here\n- or -")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #495057;")

        self.btn_browse = QPushButton("Browse Files")
        self.btn_browse.setFixedWidth(160)
        self.btn_browse.clicked.connect(self._browse_file)

        self.info_label = QLabel(f"Supports: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
        self.info_label.setStyleSheet("font-size: 11px; color: #6C757D;")
        self.info_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.btn_browse, alignment=Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self._set_idle_style()

    def _set_idle_style(self):
        self.setStyleSheet("""
            DropZoneWidget {
                border: 2px dashed #BDBDBD;
                border-radius: 12px;
                background-color: #FFFFFF;
                padding: 24px;
            }
        """)

    def _set_hover_style(self):
        self.setStyleSheet("""
            DropZoneWidget {
                border: 2px dashed #1E88E5;
                border-radius: 12px;
                background-color: #E3F2FD;
                padding: 24px;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_hover_style()

    def dragLeaveEvent(self, event):
        self._set_idle_style()

    def dropEvent(self, event):
        self._set_idle_style()
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            ext = Path(path).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                self.set_file(path)

    def _browse_file(self):
        filter_str = f"All Supported Documents ({' '.join(['*' + e for e in SUPPORTED_EXTENSIONS])});;All Files (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document to Translate", "", filter_str)
        if file_path:
            self.set_file(file_path)

    def set_file(self, path: str):
        self.selected_file = path
        name = Path(path).name
        size_kb = Path(path).stat().st_size / 1024
        self.text_label.setText(f"Selected: {name}\n({size_kb:.1f} KB)")
        self.icon_label.setText("✅")
        self.fileSelected.emit(path)

