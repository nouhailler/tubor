"""
Tubor - Boîte de dialogue des paramètres
"""

import threading
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QCheckBox, QFileDialog, QGroupBox, QFrame,
    QWidget, QMessageBox, QSizePolicy,
)

from core.config import Config
from core.utils import get_yt_dlp_version, update_yt_dlp


class SettingsDialog(QDialog):
    """Fenêtre de paramètres persistants."""

    settings_changed = pyqtSignal()

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Paramètres — Tubor")
        self.setMinimumWidth(520)
        self.setModal(True)
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Téléchargement ──────────────────────────────
        grp_dl = QGroupBox("TÉLÉCHARGEMENT")
        form_dl = QFormLayout(grp_dl)
        form_dl.setSpacing(10)
        form_dl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Dossier par défaut
        folder_row = QWidget()
        folder_layout = QHBoxLayout(folder_row)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        folder_layout.setSpacing(6)
        self.edit_folder = QLineEdit()
        self.edit_folder.setPlaceholderText("Dossier de téléchargement...")
        btn_browse = QPushButton("Parcourir")
        btn_browse.setFixedWidth(90)
        btn_browse.clicked.connect(self._browse_folder)
        folder_layout.addWidget(self.edit_folder)
        folder_layout.addWidget(btn_browse)
        form_dl.addRow("Dossier par défaut :", folder_row)

        # Format préféré
        self.combo_format = QComboBox()
        self.combo_format.addItems(["Vidéo (MP4)", "Audio seulement (MP3)"])
        form_dl.addRow("Format préféré :", self.combo_format)

        # Qualité préférée
        self.combo_quality = QComboBox()
        self._populate_quality(self.combo_format.currentIndex())
        self.combo_format.currentIndexChanged.connect(self._populate_quality)
        form_dl.addRow("Qualité préférée :", self.combo_quality)

        # Métadonnées
        self.chk_metadata = QCheckBox("Intégrer les métadonnées (titre, artiste…)")
        form_dl.addRow("", self.chk_metadata)

        self.chk_thumbnail = QCheckBox("Intégrer la miniature dans le fichier")
        form_dl.addRow("", self.chk_thumbnail)

        layout.addWidget(grp_dl)

        # ── Apparence ──────────────────────────────────
        grp_ui = QGroupBox("APPARENCE")
        form_ui = QFormLayout(grp_ui)
        form_ui.setSpacing(10)
        form_ui.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Thème sombre", "Thème clair"])
        form_ui.addRow("Thème :", self.combo_theme)

        layout.addWidget(grp_ui)

        # ── Authentification ───────────────────────────
        grp_auth = QGroupBox("AUTHENTIFICATION")
        form_auth = QFormLayout(grp_auth)
        form_auth.setSpacing(10)
        form_auth.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Fichier cookies
        cookies_row = QWidget()
        cookies_layout = QHBoxLayout(cookies_row)
        cookies_layout.setContentsMargins(0, 0, 0, 0)
        cookies_layout.setSpacing(6)
        self.edit_cookies = QLineEdit()
        self.edit_cookies.setPlaceholderText("Chemin vers le fichier cookies.txt (optionnel)")
        btn_cookies = QPushButton("Parcourir")
        btn_cookies.setFixedWidth(90)
        btn_cookies.clicked.connect(self._browse_cookies)
        cookies_layout.addWidget(self.edit_cookies)
        cookies_layout.addWidget(btn_cookies)
        form_auth.addRow("Cookies :", cookies_row)

        lbl_cookies_hint = QLabel(
            "Exportez vos cookies via l'extension « Get cookies.txt LOCALLY »"
        )
        lbl_cookies_hint.setObjectName("lbl_subtitle")
        lbl_cookies_hint.setWordWrap(True)
        form_auth.addRow("", lbl_cookies_hint)

        layout.addWidget(grp_auth)

        # ── Moteur ────────────────────────────────────
        grp_engine = QGroupBox("MOTEUR YT-DLP")
        form_engine = QFormLayout(grp_engine)
        form_engine.setSpacing(10)
        form_engine.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        engine_row = QWidget()
        engine_layout = QHBoxLayout(engine_row)
        engine_layout.setContentsMargins(0, 0, 0, 0)
        engine_layout.setSpacing(10)
        self.lbl_version = QLabel(f"Version : {get_yt_dlp_version()}")
        self.btn_update = QPushButton("⟳  Vérifier les mises à jour")
        self.btn_update.clicked.connect(self._update_ytdlp)
        engine_layout.addWidget(self.lbl_version)
        engine_layout.addWidget(self.btn_update)
        engine_layout.addStretch()
        form_engine.addRow("", engine_row)

        self.lbl_update_status = QLabel("")
        self.lbl_update_status.setObjectName("lbl_status")
        self.lbl_update_status.hide()
        form_engine.addRow("", self.lbl_update_status)

        layout.addWidget(grp_engine)

        # ── Boutons OK / Annuler ───────────────────────
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Enregistrer")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._save_and_close)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def _populate_quality(self, format_index: int = 0):
        self.combo_quality.clear()
        if format_index == 0:  # Vidéo
            self.combo_quality.addItems([
                "Meilleure qualité",
                "1080p (Full HD)",
                "720p (HD)",
                "480p (SD)",
                "360p",
            ])
        else:  # Audio
            self.combo_quality.addItems([
                "MP3 320 kbps",
                "MP3 192 kbps",
                "MP3 128 kbps",
            ])

    def _load_values(self):
        """Remplit les widgets avec les valeurs actuelles de la config."""
        self.edit_folder.setText(self.config.download_folder)

        fmt_idx = 0 if self.config.format == "video" else 1
        self.combo_format.setCurrentIndex(fmt_idx)
        self._populate_quality(fmt_idx)

        quality_map_video = {
            "best": 0, "1080p": 1, "720p": 2, "480p": 3, "360p": 4
        }
        quality_map_audio = {
            "mp3_320": 0, "mp3_192": 1, "mp3_128": 2, "best": 0
        }
        if self.config.format == "video":
            self.combo_quality.setCurrentIndex(quality_map_video.get(self.config.quality, 0))
        else:
            self.combo_quality.setCurrentIndex(quality_map_audio.get(self.config.quality, 0))

        self.chk_metadata.setChecked(self.config.embed_metadata)
        self.chk_thumbnail.setChecked(self.config.embed_thumbnail)

        theme_idx = 1 if self.config.theme == "light" else 0
        self.combo_theme.setCurrentIndex(theme_idx)

        self.edit_cookies.setText(self.config.get("cookies_file", ""))

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Choisir le dossier de téléchargement",
            self.edit_folder.text() or str(Path.home() / "Downloads"),
        )
        if folder:
            self.edit_folder.setText(folder)

    def _browse_cookies(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir le fichier cookies",
            str(Path.home()),
            "Fichiers texte (*.txt);;Tous les fichiers (*)",
        )
        if path:
            self.edit_cookies.setText(path)

    def _update_ytdlp(self):
        """Lance la mise à jour de yt-dlp dans un thread séparé."""
        self.btn_update.setEnabled(False)
        self.lbl_update_status.setText("Mise à jour en cours…")
        self.lbl_update_status.setObjectName("lbl_subtitle")
        self.lbl_update_status.show()

        def _do_update():
            success, msg = update_yt_dlp()
            # Retour dans le thread GUI
            from PyQt6.QtCore import QMetaObject, Q_ARG
            if success:
                self.lbl_update_status.setObjectName("lbl_status")
                new_ver = get_yt_dlp_version()
                self.lbl_version.setText(f"Version : {new_ver}")
            else:
                self.lbl_update_status.setObjectName("lbl_status_error")
            self.lbl_update_status.setText(msg)
            self.lbl_update_status.style().unpolish(self.lbl_update_status)
            self.lbl_update_status.style().polish(self.lbl_update_status)
            self.btn_update.setEnabled(True)

        t = threading.Thread(target=_do_update, daemon=True)
        t.start()

    def _save_and_close(self):
        """Sauvegarde les paramètres et ferme la boîte de dialogue."""
        folder = self.edit_folder.text().strip()
        if folder and not Path(folder).exists():
            QMessageBox.warning(self, "Dossier invalide",
                                f"Le dossier « {folder} » n'existe pas.")
            return

        fmt_index = self.combo_format.currentIndex()
        fmt = "video" if fmt_index == 0 else "audio"

        quality_map_video = {0: "best", 1: "1080p", 2: "720p", 3: "480p", 4: "360p"}
        quality_map_audio = {0: "mp3_320", 1: "mp3_192", 2: "mp3_128"}
        if fmt == "video":
            quality = quality_map_video.get(self.combo_quality.currentIndex(), "best")
        else:
            quality = quality_map_audio.get(self.combo_quality.currentIndex(), "mp3_192")

        theme = "light" if self.combo_theme.currentIndex() == 1 else "dark"

        self.config.update({
            "download_folder": folder,
            "format": fmt,
            "quality": quality,
            "theme": theme,
            "embed_metadata": self.chk_metadata.isChecked(),
            "embed_thumbnail": self.chk_thumbnail.isChecked(),
            "cookies_file": self.edit_cookies.text().strip(),
        })
        self.config.save()
        self.settings_changed.emit()
        self.accept()
