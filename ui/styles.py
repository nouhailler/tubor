"""
Tubor - Feuilles de style QSS (dark / light)
"""

DARK_THEME = """
/* ──────────────── Base ──────────────── */
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #1e1e2e;
}

/* ──────────────── Inputs ──────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}

QLineEdit:disabled, QComboBox:disabled {
    background-color: #181825;
    color: #585b70;
}

/* ──────────────── ComboBox ──────────────── */
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #cdd6f4;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
    padding: 4px;
}

/* ──────────────── Buttons ──────────────── */
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 7px 16px;
    color: #cdd6f4;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton:disabled {
    background-color: #181825;
    color: #585b70;
    border-color: #313244;
}

/* Bouton principal d'action */
QPushButton#btn_download {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QPushButton#btn_download:hover {
    background-color: #b4befe;
}

QPushButton#btn_download:pressed {
    background-color: #74c7ec;
}

QPushButton#btn_download:disabled {
    background-color: #313244;
    color: #585b70;
}

/* Bouton annuler */
QPushButton#btn_cancel {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#btn_cancel:hover {
    background-color: #eba0ac;
}

/* Bouton paramètres */
QPushButton#btn_settings {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 18px;
}

QPushButton#btn_settings:hover {
    background-color: #313244;
}

/* ──────────────── Progress Bar ──────────────── */
QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 5px;
    height: 10px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 5px;
}

QProgressBar[error="true"]::chunk {
    background-color: #f38ba8;
}

/* ──────────────── Labels ──────────────── */
QLabel {
    color: #cdd6f4;
    background-color: transparent;
}

QLabel#lbl_title {
    font-size: 20px;
    font-weight: 700;
    color: #cdd6f4;
    letter-spacing: 1px;
}

QLabel#lbl_subtitle {
    color: #a6adc8;
    font-size: 11px;
}

QLabel#lbl_section {
    color: #a6adc8;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

QLabel#lbl_status {
    color: #a6e3a1;
    font-size: 12px;
}

QLabel#lbl_status_error {
    color: #f38ba8;
    font-size: 12px;
}

QLabel#lbl_warning {
    color: #fab387;
    background-color: #3d2b1f;
    border: 1px solid #fab387;
    border-radius: 6px;
    padding: 6px 10px;
}

/* ──────────────── Scroll / List ──────────────── */
QScrollBar:vertical {
    background: #1e1e2e;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #585b70;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

/* ──────────────── Separator / Frame ──────────────── */
QFrame#separator {
    background-color: #313244;
    border: none;
    max-height: 1px;
}

QFrame#card {
    background-color: #313244;
    border-radius: 10px;
    border: 1px solid #45475a;
}

/* ──────────────── TabWidget ──────────────── */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 6px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 8px 16px;
    border-radius: 4px 4px 0 0;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #45475a;
    color: #cdd6f4;
}

/* ──────────────── CheckBox ──────────────── */
QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #45475a;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

/* ──────────────── GroupBox ──────────────── */
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    padding: 10px;
    color: #a6adc8;
    font-weight: 600;
    font-size: 11px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #89b4fa;
}

/* ──────────────── Tooltip ──────────────── */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}

/* ──────────────── Splitter ──────────────── */
QSplitter::handle {
    background-color: #313244;
    height: 2px;
}
"""

LIGHT_THEME = """
/* ──────────────── Base ──────────────── */
QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #eff1f5;
}

/* ──────────────── Inputs ──────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    padding: 6px 10px;
    color: #4c4f69;
    selection-background-color: #1e66f5;
    selection-color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #1e66f5;
}

QLineEdit:disabled, QComboBox:disabled {
    background-color: #e6e9ef;
    color: #acb0be;
}

/* ──────────────── ComboBox ──────────────── */
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #4c4f69;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    selection-background-color: #1e66f5;
    selection-color: #ffffff;
    padding: 4px;
}

/* ──────────────── Buttons ──────────────── */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    padding: 7px 16px;
    color: #4c4f69;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #e6e9ef;
    border-color: #9ca0b0;
}

QPushButton:pressed {
    background-color: #dce0e8;
}

QPushButton:disabled {
    background-color: #e6e9ef;
    color: #acb0be;
    border-color: #bcc0cc;
}

QPushButton#btn_download {
    background-color: #1e66f5;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#btn_download:hover {
    background-color: #04a5e5;
}

QPushButton#btn_download:disabled {
    background-color: #e6e9ef;
    color: #acb0be;
}

QPushButton#btn_cancel {
    background-color: #d20f39;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#btn_settings {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 18px;
}

QPushButton#btn_settings:hover {
    background-color: #dce0e8;
}

/* ──────────────── Progress Bar ──────────────── */
QProgressBar {
    background-color: #dce0e8;
    border: none;
    border-radius: 5px;
    height: 10px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #1e66f5;
    border-radius: 5px;
}

/* ──────────────── Labels ──────────────── */
QLabel {
    color: #4c4f69;
    background-color: transparent;
}

QLabel#lbl_title {
    font-size: 20px;
    font-weight: 700;
    color: #4c4f69;
}

QLabel#lbl_subtitle {
    color: #6c6f85;
    font-size: 11px;
}

QLabel#lbl_section {
    color: #6c6f85;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
}

QLabel#lbl_status {
    color: #40a02b;
    font-size: 12px;
}

QLabel#lbl_warning {
    color: #fe640b;
    background-color: #fef2e4;
    border: 1px solid #fe640b;
    border-radius: 6px;
    padding: 6px 10px;
}

/* ──────────────── Scroll ──────────────── */
QScrollBar:vertical {
    background: #eff1f5;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #bcc0cc;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #9ca0b0;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

/* ──────────────── Frame ──────────────── */
QFrame#separator {
    background-color: #bcc0cc;
    border: none;
    max-height: 1px;
}

QFrame#card {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #bcc0cc;
}

/* ──────────────── CheckBox ──────────────── */
QCheckBox {
    color: #4c4f69;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #bcc0cc;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #1e66f5;
    border-color: #1e66f5;
}

/* ──────────────── GroupBox ──────────────── */
QGroupBox {
    border: 1px solid #bcc0cc;
    border-radius: 8px;
    margin-top: 12px;
    padding: 10px;
    color: #6c6f85;
    font-weight: 600;
    font-size: 11px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #1e66f5;
}

/* ──────────────── Tooltip ──────────────── */
QToolTip {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    padding: 4px 8px;
}
"""


def get_stylesheet(theme: str) -> str:
    """Retourne la feuille de style selon le thème."""
    if theme == "light":
        return LIGHT_THEME
    return DARK_THEME
