class ThemeManager:
    """Provides high-contrast light themes featuring dynamic rainbow color accents."""

    THEMES = {
        "Vibrant Rainbow Light": """
            QMainWindow, QWidget {
                background-color: #F8F9FA;
                color: #212529;
                font-family: 'Segoe UI', 'Noto Sans Devanagari', sans-serif;
                font-size: 13px;
            }
            QTabBar::tab {
                background: #FFFFFF;
                border: 1px solid #E0E0E0;
                padding: 10px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                color: #495057;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                border-bottom: 3px solid #8E24AA;
                color: #1E88E5;
            }
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                margin-top: 18px;
                font-weight: 600;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #3949AB;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8E24AA, stop:0.2 #1E88E5, stop:0.4 #43A047, stop:0.6 #FDD835, stop:0.8 #FB8C00, stop:1 #E53935);
                color: #FFFFFF;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:disabled {
                background: #CED4DA;
                color: #6C757D;
            }
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                text-align: center;
                background-color: #E9ECEF;
                color: #212529;
                font-weight: bold;
                height: 22px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8E24AA, stop:0.25 #1E88E5, stop:0.5 #43A047, stop:0.75 #FB8C00, stop:1 #E53935);
                border-radius: 5px;
            }
            QComboBox, QSpinBox, QLineEdit {
                background: #FFFFFF;
                border: 1px solid #CED4DA;
                border-radius: 6px;
                padding: 6px 12px;
                color: #212529;
            }
            QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
                border: 2px solid #1E88E5;
            }
        """,

        "Pastel Rainbow Light": """
            QMainWindow, QWidget {
                background-color: #FAFAFC;
                color: #263238;
                font-family: 'Segoe UI', 'Noto Sans Devanagari', sans-serif;
                font-size: 13px;
            }
            QTabBar::tab {
                background: #FFFFFF;
                border: 1px solid #ECEFF1;
                padding: 9px 20px;
                border-radius: 8px;
                margin-right: 4px;
                font-weight: 600;
                color: #546E7A;
            }
            QTabBar::tab:selected {
                background: #EDE7F6;
                border: 1px solid #D1C4E9;
                color: #5E35B1;
            }
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #ECEFF1;
                border-radius: 12px;
                margin-top: 18px;
                font-weight: bold;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #B39DDB, stop:0.25 #90CAF9, stop:0.5 #A5D6A7, stop:0.75 #FFE082, stop:1 #FFAB91);
                color: #212121;
                font-weight: bold;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px 18px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #CE93D8, stop:0.33 #80DEEA, stop:0.66 #C5E1A5, stop:1 #FFCC80);
                border-radius: 4px;
            }
        """,

        "Prism Spectrum Light": """
            QMainWindow, QWidget {
                background-color: #FFFFFF;
                color: #1A1A1A;
                font-family: 'Segoe UI', 'Noto Sans Devanagari', sans-serif;
                font-size: 13px;
            }
            QGroupBox {
                border: 2px solid #E1BEE7;
                border-radius: 10px;
                margin-top: 18px;
                background-color: #FFFFFF;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7B1FA2, stop:0.3 #0288D1, stop:0.6 #388E3C, stop:1 #F57C00);
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #AB47BC, stop:0.25 #26A69A, stop:0.5 #FFEE58, stop:0.75 #FFA726, stop:1 #EF5350);
            }
        """,

        "Sunrise Spectrum Light": """
            QMainWindow, QWidget {
                background-color: #FFFDF9;
                color: #2D241E;
                font-family: 'Segoe UI', 'Noto Sans Devanagari', sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6F00, stop:0.3 #FF8F00, stop:0.6 #F4511E, stop:1 #AD1457);
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFE082, stop:0.33 #FFB74D, stop:0.66 #FF8A65, stop:1 #F06292);
            }
        """
    }

    @classmethod
    def get_theme_names(cls) -> list[str]:
        return list(cls.THEMES.keys())

    @classmethod
    def get_stylesheet(cls, name: str) -> str:
        return cls.THEMES.get(name, cls.THEMES["Vibrant Rainbow Light"])

