from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import Qt, Signal

class ProgressCardWidget(QFrame):
    cancelRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            ProgressCardWidget {
                background: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 16px;
            }
        """)

        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        self.title_label = QLabel("Translation & Streaming Status")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1E88E5;")
        self.mode_badge = QLabel("🛡️ Safe Low-Memory Streaming (Zero-OOM)")
        self.mode_badge.setStyleSheet("font-size: 11px; background: #E8F5E9; color: #2E7D32; padding: 4px 8px; border-radius: 6px;")
        top_row.addWidget(self.title_label)
        top_row.addStretch()
        top_row.addWidget(self.mode_badge)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        bottom_row = QHBoxLayout()
        self.status_label = QLabel("Ready to translate")
        self.status_label.setStyleSheet("color: #495057; font-size: 12px;")
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedWidth(80)
        self.btn_cancel.setStyleSheet("background: #E53935; color: white; padding: 6px 12px; font-weight: bold;")
        self.btn_cancel.clicked.connect(self.cancelRequested.emit)
        self.btn_cancel.setVisible(False)

        bottom_row.addWidget(self.status_label)
        bottom_row.addStretch()
        bottom_row.addWidget(self.btn_cancel)

        layout.addLayout(top_row)
        layout.addWidget(self.progress_bar)
        layout.addLayout(bottom_row)

    def set_progress(self, current: int, total: int, status_msg: str):
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(min(100, pct))
            self.status_label.setText(f"{status_msg} ({pct}%)")
        else:
            self.status_label.setText(status_msg)

    def set_running(self, running: bool):
        self.btn_cancel.setVisible(running)
        if not running:
            self.progress_bar.setValue(100)

