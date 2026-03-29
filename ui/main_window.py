"""
Tubor - Fenêtre principale de l'application
Architecture MVC : cette classe est la Vue + Contrôleur.
"""

import shutil
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QFileDialog, QFrame, QScrollArea, QSplitter,
    QPlainTextEdit, QCheckBox, QApplication,
    QMessageBox, QSizePolicy, QSpacerItem, QDialog,
)

from core.config import Config
from core.downloader import (
    DownloadTask, DownloadProgress, DownloadWorker, DownloadQueue,
    is_ffmpeg_available,
)
from core.utils import is_valid_url, send_desktop_notification
from ui.download_item import DownloadItemWidget
from ui.settings_dialog import SettingsDialog
from ui.help_dialog import HelpDialog
from ui.styles import get_stylesheet


# ─── Constantes d'affichage ────────────────────────────────────────────────

QUALITY_OPTIONS_VIDEO = [
    ("Meilleure qualité", "best"),
    ("1080p (Full HD)", "1080p"),
    ("720p (HD)", "720p"),
    ("480p (SD)", "480p"),
    ("360p", "360p"),
]

QUALITY_OPTIONS_AUDIO = [
    ("MP3 320 kbps", "mp3_320"),
    ("MP3 192 kbps", "mp3_192"),
    ("MP3 128 kbps", "mp3_128"),
]

# Style pour les boutons toggle Format (actif / inactif)
_TOGGLE_ACTIVE_VIDEO = (
    "QPushButton {"
    "  background-color: #89b4fa;"
    "  color: #1e1e2e;"
    "  border: none;"
    "  border-radius: 6px;"
    "  padding: 8px 18px;"
    "  font-size: 13px;"
    "  font-weight: 700;"
    "}"
)
_TOGGLE_INACTIVE = (
    "QPushButton {"
    "  background-color: transparent;"
    "  color: #a6adc8;"
    "  border: 1px solid #45475a;"
    "  border-radius: 6px;"
    "  padding: 8px 18px;"
    "  font-size: 13px;"
    "  font-weight: 500;"
    "}"
    "QPushButton:hover {"
    "  background-color: #313244;"
    "  color: #cdd6f4;"
    "}"
)
_TOGGLE_ACTIVE_AUDIO = (
    "QPushButton {"
    "  background-color: #a6e3a1;"
    "  color: #1e1e2e;"
    "  border: none;"
    "  border-radius: 6px;"
    "  padding: 8px 18px;"
    "  font-size: 13px;"
    "  font-weight: 700;"
    "}"
)


class MainWindow(QMainWindow):
    """Fenêtre principale de Tubor."""

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.queue = DownloadQueue()
        self._active_worker: DownloadWorker | None = None
        self._item_widgets: dict[int, DownloadItemWidget] = {}
        self._is_downloading = False
        self._current_format = config.format  # "video" | "audio"

        self.setWindowTitle("Tubor")
        self.setMinimumSize(700, 580)

        self._apply_theme()
        self._build_ui()
        self._check_ffmpeg()
        self._restore_geometry()
        self._sync_format_from_config()

    # ─── Construction de l'UI ─────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        root.addWidget(self._build_header())

        # Barre de statut "En cours..." (masquée par défaut)
        root.addWidget(self._build_status_bar())

        # Splitter : zone principale + log
        self._splitter = QSplitter(Qt.Orientation.Vertical)
        self._splitter.setHandleWidth(4)

        top_panel = self._build_top_panel()
        self._splitter.addWidget(top_panel)

        bottom_panel = self._build_bottom_panel()
        self._splitter.addWidget(bottom_panel)
        self._splitter.setSizes([420, 160])

        root.addWidget(self._splitter, 1)

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("card")
        header.setMaximumHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)

        lbl_icon = QLabel("⬇")
        lbl_icon.setStyleSheet("font-size: 22px;")
        header_layout.addWidget(lbl_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        lbl_title = QLabel("Tubor")
        lbl_title.setObjectName("lbl_title")
        lbl_sub = QLabel("Téléchargeur vidéo & audio")
        lbl_sub.setObjectName("lbl_subtitle")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        header_layout.addLayout(title_col)
        header_layout.addStretch()

        self.btn_help = QPushButton("❓")
        self.btn_help.setObjectName("btn_settings")
        self.btn_help.setToolTip("Aide")
        self.btn_help.setFixedSize(38, 38)
        self.btn_help.clicked.connect(self._open_help)
        header_layout.addWidget(self.btn_help)

        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.setToolTip("Paramètres")
        self.btn_settings.setFixedSize(38, 38)
        self.btn_settings.clicked.connect(self._open_settings)
        header_layout.addWidget(self.btn_settings)

        return header

    def _build_status_bar(self) -> QWidget:
        """Barre de statut visible uniquement pendant un téléchargement actif."""
        self._status_bar = QFrame()
        self._status_bar.setObjectName("card")
        self._status_bar.setMaximumHeight(48)
        self._status_bar.setStyleSheet(
            "QFrame { background-color: #313244; border-radius: 0px; border: none; "
            "border-bottom: 1px solid #45475a; }"
        )
        bar_layout = QHBoxLayout(self._status_bar)
        bar_layout.setContentsMargins(20, 6, 20, 6)
        bar_layout.setSpacing(12)

        # Indicateur animé
        self._lbl_status_active = QLabel("⬇  Téléchargement en cours…")
        self._lbl_status_active.setStyleSheet(
            "color: #89b4fa; font-size: 12px; font-weight: 600; background: transparent;"
        )
        bar_layout.addWidget(self._lbl_status_active, 1)

        # Mini-barre de progression globale
        self._global_progress = QLabel("")
        self._global_progress.setStyleSheet(
            "color: #a6adc8; font-size: 11px; background: transparent;"
        )
        bar_layout.addWidget(self._global_progress)

        # Bouton STOP — grand, rouge, impossible à manquer
        self._btn_global_stop = QPushButton("⏹  ARRÊTER")
        self._btn_global_stop.setFixedHeight(32)
        self._btn_global_stop.setMinimumWidth(110)
        self._btn_global_stop.setStyleSheet(
            "QPushButton {"
            "  background-color: #f38ba8;"
            "  color: #1e1e2e;"
            "  border: none;"
            "  border-radius: 6px;"
            "  font-size: 13px;"
            "  font-weight: 700;"
            "  padding: 0 16px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #eba0ac;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #d20f39;"
            "}"
        )
        self._btn_global_stop.setToolTip("Arrêter le téléchargement en cours (Échap)")
        self._btn_global_stop.clicked.connect(self._cancel_download)
        bar_layout.addWidget(self._btn_global_stop)

        self._status_bar.hide()
        return self._status_bar

    def _build_top_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 8)
        layout.setSpacing(12)

        # ── Avertissement ffmpeg ──────────────────────────────
        self.lbl_ffmpeg_warn = QLabel(
            "⚠  ffmpeg introuvable. Certaines fonctionnalités sont désactivées "
            "(conversion audio, intégration des métadonnées)."
        )
        self.lbl_ffmpeg_warn.setObjectName("lbl_warning")
        self.lbl_ffmpeg_warn.setWordWrap(True)
        self.lbl_ffmpeg_warn.hide()
        layout.addWidget(self.lbl_ffmpeg_warn)

        # ── URL ───────────────────────────────────────────────
        lbl_url = QLabel("URL DE LA VIDÉO / AUDIO")
        lbl_url.setObjectName("lbl_section")
        layout.addWidget(lbl_url)

        url_row = QHBoxLayout()
        url_row.setSpacing(8)
        self.edit_url = QLineEdit()
        self.edit_url.setPlaceholderText("Collez l'URL ici (YouTube, Vimeo, Twitter…)")
        self.edit_url.setClearButtonEnabled(True)
        self.edit_url.returnPressed.connect(self._add_to_queue_or_download)
        url_row.addWidget(self.edit_url)

        btn_paste = QPushButton("📋 Coller")
        btn_paste.setFixedWidth(90)
        btn_paste.setToolTip("Coller depuis le presse-papier")
        btn_paste.clicked.connect(self._paste_url)
        url_row.addWidget(btn_paste)
        layout.addLayout(url_row)

        # ── Toggle FORMAT — Vidéo / Audio ─────────────────────
        fmt_section = QVBoxLayout()
        fmt_section.setSpacing(6)
        lbl_fmt = QLabel("FORMAT")
        lbl_fmt.setObjectName("lbl_section")
        fmt_section.addWidget(lbl_fmt)

        fmt_toggle_row = QHBoxLayout()
        fmt_toggle_row.setSpacing(8)

        self.btn_fmt_video = QPushButton("🎬  Vidéo (MP4)")
        self.btn_fmt_video.setFixedHeight(36)
        self.btn_fmt_video.clicked.connect(lambda: self._select_format("video"))
        fmt_toggle_row.addWidget(self.btn_fmt_video)

        self.btn_fmt_audio = QPushButton("🎵  Audio seulement (MP3)")
        self.btn_fmt_audio.setFixedHeight(36)
        self.btn_fmt_audio.clicked.connect(lambda: self._select_format("audio"))
        fmt_toggle_row.addWidget(self.btn_fmt_audio)

        fmt_toggle_row.addStretch()
        fmt_section.addLayout(fmt_toggle_row)
        layout.addLayout(fmt_section)

        # ── Qualité ──────────────────────────────────────────
        qual_row = QHBoxLayout()
        qual_row.setSpacing(12)

        qual_col = QVBoxLayout()
        lbl_qual = QLabel("QUALITÉ")
        lbl_qual.setObjectName("lbl_section")
        qual_col.addWidget(lbl_qual)
        self.combo_quality = QComboBox()
        self.combo_quality.setMinimumWidth(200)
        self._populate_quality("video")
        qual_col.addWidget(self.combo_quality)
        qual_row.addLayout(qual_col)

        # Playlist
        playlist_col = QVBoxLayout()
        lbl_playlist = QLabel("PLAYLIST")
        lbl_playlist.setObjectName("lbl_section")
        playlist_col.addWidget(lbl_playlist)
        self.combo_playlist = QComboBox()
        self.combo_playlist.addItems([
            "Vidéo actuelle seulement",
            "Toute la playlist",
        ])
        playlist_col.addWidget(self.combo_playlist)
        qual_row.addLayout(playlist_col)
        qual_row.addStretch()
        layout.addLayout(qual_row)

        # ── Dossier de destination ────────────────────────────
        folder_section = QVBoxLayout()
        folder_section.setSpacing(6)
        lbl_dest = QLabel("DOSSIER DE DESTINATION")
        lbl_dest.setObjectName("lbl_section")
        folder_section.addWidget(lbl_dest)

        folder_input_row = QHBoxLayout()
        folder_input_row.setSpacing(6)
        self.edit_folder = QLineEdit()
        self.edit_folder.setText(self.config.download_folder)
        self.edit_folder.setPlaceholderText("Dossier de téléchargement…")
        folder_input_row.addWidget(self.edit_folder)
        btn_browse = QPushButton("📁 Parcourir")
        btn_browse.setFixedWidth(105)
        btn_browse.setToolTip("Choisir un dossier")
        btn_browse.clicked.connect(self._browse_folder)
        folder_input_row.addWidget(btn_browse)
        folder_section.addLayout(folder_input_row)
        layout.addLayout(folder_section)

        # ── Boutons d'action ──────────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_add_queue = QPushButton("+ Ajouter à la file")
        self.btn_add_queue.setToolTip("Ajoute l'URL à la file sans lancer immédiatement")
        self.btn_add_queue.clicked.connect(self._add_to_queue)
        action_row.addWidget(self.btn_add_queue)

        action_row.addStretch()

        self.btn_download = QPushButton("⬇  TÉLÉCHARGER")
        self.btn_download.setObjectName("btn_download")
        self.btn_download.setMinimumWidth(170)
        self.btn_download.setMinimumHeight(40)
        self.btn_download.clicked.connect(self._add_to_queue_or_download)
        action_row.addWidget(self.btn_download)

        layout.addLayout(action_row)

        # ── Séparateur ────────────────────────────────────────
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # ── Liste des téléchargements ─────────────────────────
        dl_header = QHBoxLayout()
        lbl_list = QLabel("TÉLÉCHARGEMENTS")
        lbl_list.setObjectName("lbl_section")
        dl_header.addWidget(lbl_list)
        dl_header.addStretch()
        btn_clear_all = QPushButton("Effacer terminés")
        btn_clear_all.setFixedWidth(120)
        btn_clear_all.setStyleSheet("font-size: 11px;")
        btn_clear_all.clicked.connect(self._clear_finished)
        dl_header.addWidget(btn_clear_all)
        layout.addLayout(dl_header)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 4, 0, 4)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch()

        self._lbl_empty = QLabel(
            "Aucun téléchargement en cours.\n"
            "Collez une URL ci-dessus et appuyez sur ⬇ TÉLÉCHARGER !"
        )
        self._lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_empty.setStyleSheet("color: #585b70; font-size: 13px;")
        self._list_layout.insertWidget(0, self._lbl_empty)

        self._scroll_area.setWidget(self._list_container)
        layout.addWidget(self._scroll_area, 1)

        return panel

    def _build_bottom_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 4, 20, 12)
        layout.setSpacing(4)

        log_header = QHBoxLayout()
        lbl_log = QLabel("JOURNAL")
        lbl_log.setObjectName("lbl_section")
        log_header.addWidget(lbl_log)
        log_header.addStretch()
        btn_clear_log = QPushButton("Effacer")
        btn_clear_log.setFixedWidth(70)
        btn_clear_log.clicked.connect(lambda: self._log_view.clear())
        log_header.addWidget(btn_clear_log)
        layout.addLayout(log_header)

        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setMaximumBlockCount(500)
        self._log_view.setStyleSheet(
            "QPlainTextEdit { background-color: #11111b; color: #a6adc8; "
            "font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 11px; "
            "border: 1px solid #313244; border-radius: 6px; }"
        )
        layout.addWidget(self._log_view)
        return panel

    # ─── Format toggle ────────────────────────────────────────────────────

    def _select_format(self, fmt: str):
        """Sélectionne le format (video | audio) et met à jour les boutons toggle."""
        self._current_format = fmt
        if fmt == "video":
            self.btn_fmt_video.setStyleSheet(_TOGGLE_ACTIVE_VIDEO)
            self.btn_fmt_audio.setStyleSheet(_TOGGLE_INACTIVE)
        else:
            self.btn_fmt_video.setStyleSheet(_TOGGLE_INACTIVE)
            self.btn_fmt_audio.setStyleSheet(_TOGGLE_ACTIVE_AUDIO)
        self._populate_quality(fmt)

    def _sync_format_from_config(self):
        """Applique le format sauvegardé dans la config."""
        self._select_format(self.config.format)
        # Qualité
        quality = self.config.quality
        options = QUALITY_OPTIONS_VIDEO if self._current_format == "video" else QUALITY_OPTIONS_AUDIO
        for i, (_, val) in enumerate(options):
            if val == quality:
                self.combo_quality.setCurrentIndex(i)
                break

    # ─── Helpers ─────────────────────────────────────────────────────────

    def _apply_theme(self):
        self.setStyleSheet(get_stylesheet(self.config.theme))

    def _check_ffmpeg(self):
        if not is_ffmpeg_available():
            self.lbl_ffmpeg_warn.show()
            self._log("⚠  ffmpeg non trouvé. Installez-le : sudo apt install ffmpeg")
        else:
            self._log(f"✔  ffmpeg détecté : {shutil.which('ffmpeg')}")

    def _populate_quality(self, fmt: str):
        self.combo_quality.clear()
        options = QUALITY_OPTIONS_VIDEO if fmt == "video" else QUALITY_OPTIONS_AUDIO
        for label, _ in options:
            self.combo_quality.addItem(label)

    def _get_quality(self) -> str:
        idx = self.combo_quality.currentIndex()
        options = (QUALITY_OPTIONS_VIDEO if self._current_format == "video"
                   else QUALITY_OPTIONS_AUDIO)
        if 0 <= idx < len(options):
            return options[idx][1]
        return "best"

    def _log(self, msg: str):
        self._log_view.appendPlainText(msg)
        self._log_view.verticalScrollBar().setValue(
            self._log_view.verticalScrollBar().maximum()
        )

    def _add_item_widget(self, task_id: int, url: str, fmt: str) -> DownloadItemWidget:
        """Crée et ajoute un widget de téléchargement dans la liste."""
        if self._lbl_empty.isVisible():
            self._lbl_empty.hide()

        widget = DownloadItemWidget(task_id, url, format_type=fmt)
        widget.cancel_requested.connect(self._on_item_cancel)
        self._list_layout.insertWidget(self._list_layout.count() - 1, widget)
        self._item_widgets[task_id] = widget

        QTimer.singleShot(50, lambda: self._scroll_area.verticalScrollBar().setValue(
            self._scroll_area.verticalScrollBar().maximum()
        ))
        return widget

    def _build_task_from_ui(self) -> DownloadTask | None:
        """Construit une DownloadTask depuis l'état actuel de l'UI."""
        url = self.edit_url.text().strip()
        if not url:
            self.edit_url.setFocus()
            return None
        if not is_valid_url(url):
            QMessageBox.warning(self, "URL invalide",
                                f"L'URL « {url[:80]} » ne semble pas valide.\n"
                                "Vérifiez qu'elle commence par http:// ou https://")
            return None

        folder = self.edit_folder.text().strip() or self.config.download_folder
        if not Path(folder).exists():
            reply = QMessageBox.question(
                self, "Dossier inexistant",
                f"Le dossier « {folder} » n'existe pas. Voulez-vous le créer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    Path(folder).mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    QMessageBox.critical(self, "Erreur", f"Impossible de créer le dossier :\n{e}")
                    return None
            else:
                return None

        playlist_mode = "all" if self.combo_playlist.currentIndex() == 1 else "single"

        return DownloadTask(
            url=url,
            format_type=self._current_format,
            quality=self._get_quality(),
            output_folder=folder,
            playlist_mode=playlist_mode,
            embed_metadata=self.config.embed_metadata,
            embed_thumbnail=self.config.embed_thumbnail,
            cookies_file=self.config.get("cookies_file", ""),
        )

    def _start_next_download(self):
        """Lance le prochain téléchargement de la file."""
        if self._is_downloading:
            return
        task = self.queue.next()
        if task is None:
            self._set_downloading(False)
            return

        self._set_downloading(True)
        widget = self._item_widgets.get(task.task_id)
        if widget is None:
            widget = self._add_item_widget(task.task_id, task.url, task.format_type)

        worker = DownloadWorker(task)
        worker.progress_updated.connect(self._on_progress_updated)
        worker.log_message.connect(self._log)
        worker.finished_task.connect(self._on_task_finished)
        self._active_worker = worker
        worker.start()

        fmt_label = "Audio" if task.format_type == "audio" else "Vidéo"
        self._log(f"[START] {fmt_label} : {task.url}")

    def _set_downloading(self, active: bool):
        self._is_downloading = active
        self.btn_download.setEnabled(not active)
        self.btn_add_queue.setEnabled(not active or len(self.queue) < 20)

        if active:
            self._status_bar.show()
        else:
            self._status_bar.hide()
            self._active_worker = None

    def _clear_finished(self):
        """Supprime les widgets terminés / annulés / en erreur de la liste."""
        to_remove = []
        for tid, widget in self._item_widgets.items():
            status_text = widget.lbl_status.text()
            if any(s in status_text for s in ["Terminé", "Arrêté", "✗", "⊘"]):
                to_remove.append(tid)
        for tid in to_remove:
            w = self._item_widgets.pop(tid)
            self._list_layout.removeWidget(w)
            w.deleteLater()
        if not self._item_widgets:
            self._lbl_empty.show()

    # ─── Raccourci clavier ────────────────────────────────────────────────

    def keyPressEvent(self, event):
        from PyQt6.QtCore import Qt as QtCore_Qt
        if event.key() == QtCore_Qt.Key.Key_Escape and self._is_downloading:
            self._cancel_download()
        else:
            super().keyPressEvent(event)

    # ─── Slots ───────────────────────────────────────────────────────────

    @pyqtSlot()
    def _paste_url(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.edit_url.setText(text)
            self.edit_url.setFocus()

    @pyqtSlot()
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Choisir le dossier de destination",
            self.edit_folder.text() or str(Path.home() / "Downloads"),
        )
        if folder:
            self.edit_folder.setText(folder)

    @pyqtSlot()
    def _add_to_queue(self):
        task = self._build_task_from_ui()
        if task is None:
            return
        task_id = self.queue.add(task)
        self._add_item_widget(task_id, task.url, task.format_type)
        fmt_label = "Audio" if task.format_type == "audio" else "Vidéo"
        self._log(f"[QUEUE] {fmt_label} ajouté : {task.url}")
        self.edit_url.clear()
        if not self._is_downloading:
            self._start_next_download()

    @pyqtSlot()
    def _add_to_queue_or_download(self):
        task = self._build_task_from_ui()
        if task is None:
            return
        task_id = self.queue.add(task)
        self._add_item_widget(task_id, task.url, task.format_type)
        self.edit_url.clear()
        self._start_next_download()

    @pyqtSlot()
    def _cancel_download(self):
        """Annule le téléchargement actif."""
        if self._active_worker:
            self._active_worker.cancel()
            self._lbl_status_active.setText("⏹  Arrêt en cours…")
            self._btn_global_stop.setEnabled(False)
            self._log("[CANCEL] Arrêt demandé…")

    @pyqtSlot(int)
    def _on_item_cancel(self, task_id: int):
        """Arrêt depuis le bouton d'un item."""
        if (self._active_worker and
                self._active_worker.task.task_id == task_id):
            self._cancel_download()
        else:
            self.queue.remove(task_id)
            widget = self._item_widgets.get(task_id)
            if widget:
                progress = DownloadProgress(task_id=task_id, status="cancelled")
                widget.update_progress(progress)
            self._log(f"[QUEUE] Tâche {task_id} retirée de la file.")

    @pyqtSlot(object)
    def _on_progress_updated(self, progress: DownloadProgress):
        widget = self._item_widgets.get(progress.task_id)
        if widget:
            widget.update_progress(progress)
        # Mise à jour de la barre de statut globale
        if progress.status == "downloading" and progress.speed:
            self._global_progress.setText(
                f"{progress.percent:.0f}%  ·  {progress.speed}"
            )

    @pyqtSlot(object)
    def _on_task_finished(self, progress: DownloadProgress):
        widget = self._item_widgets.get(progress.task_id)
        if widget:
            widget.update_progress(progress)

        # Sauvegarde l'URL AVANT de réinitialiser _active_worker
        # (car _set_downloading(False) le met à None)
        failed_url = ""
        if self._active_worker:
            failed_url = self._active_worker.task.url
        if not failed_url and progress.task_id in self._item_widgets:
            failed_url = self._item_widgets[progress.task_id].url

        # Réinitialise la barre de statut
        self._set_downloading(False)
        self._btn_global_stop.setEnabled(True)
        self._lbl_status_active.setText("⬇  Téléchargement en cours…")
        self._global_progress.setText("")

        if progress.status == "finished":
            title = progress.title or "Téléchargement"
            self._log(f"[OK] Terminé : {title}")
            send_desktop_notification("Tubor — Terminé", f"✔  {title}")
            QTimer.singleShot(200, self._start_next_download)

        elif progress.status == "cancelled":
            self._log("[ARRÊT] Téléchargement arrêté par l'utilisateur.")
            self.queue.clear()
            self._log("[ARRÊT] File d'attente vidée.")

        elif progress.status == "error":
            self._log(f"[ERREUR] {progress.error_message}")
            send_desktop_notification(
                "Tubor — Erreur de téléchargement",
                f"✗  {progress.error_message}",
                urgency="critical",
            )
            self._show_error_dialog(progress, failed_url)

    def _show_error_dialog(self, progress: DownloadProgress, failed_url: str = ""):
        """
        Affiche une fenêtre de notification d'erreur.
        Propose à l'utilisateur de continuer avec le suivant ou tout arrêter.
        """
        if not failed_url and progress.task_id in self._item_widgets:
            failed_url = self._item_widgets[progress.task_id].url

        dlg = _ErrorDialog(
            error_message=progress.error_message,
            url=failed_url,
            queue_size=len(self.queue),
            parent=self,
        )
        choice = dlg.exec()

        if choice == _ErrorDialog.CONTINUE:
            # Lance le prochain téléchargement de la file
            self._log("[INFO] Passage au suivant…")
            QTimer.singleShot(200, self._start_next_download)
        else:
            # Arrêt : vide la file
            remaining = len(self.queue)
            self.queue.clear()
            if remaining > 0:
                self._log(f"[ARRÊT] File vidée ({remaining} téléchargement(s) annulé(s)).")

    @pyqtSlot()
    def _open_help(self):
        dlg = HelpDialog(parent=self)
        dlg.exec()

    def _open_settings(self):
        dlg = SettingsDialog(self.config, parent=self)
        dlg.settings_changed.connect(self._on_settings_changed)
        dlg.exec()

    @pyqtSlot()
    def _on_settings_changed(self):
        self._apply_theme()
        self.edit_folder.setText(self.config.download_folder)
        self._sync_format_from_config()
        self._log("[INFO] Paramètres mis à jour.")

    # ─── Cycle de vie ────────────────────────────────────────────────────

    def _restore_geometry(self):
        geom = self.config.get("window_geometry")
        if geom:
            try:
                from PyQt6.QtCore import QByteArray
                import base64
                self.restoreGeometry(QByteArray(base64.b64decode(geom)))
            except Exception:
                pass

    def closeEvent(self, event):
        if self._is_downloading:
            reply = QMessageBox.question(
                self, "Quitter Tubor",
                "Un téléchargement est en cours. Voulez-vous vraiment quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            if self._active_worker:
                self._active_worker.cancel()
                self._active_worker.wait(2000)

        import base64
        geom_b64 = base64.b64encode(bytes(self.saveGeometry())).decode()
        self.config.set("window_geometry", geom_b64)
        self.config.save()
        event.accept()


# ─────────────────────────────────────────────────────────────────────────────
#  Dialogue d'erreur de téléchargement
# ─────────────────────────────────────────────────────────────────────────────

class _ErrorDialog(QDialog):
    """
    Fenêtre modale affichée quand un téléchargement échoue.
    Propose deux choix :
      • Continuer : passer au téléchargement suivant dans la file
      • Arrêter   : vider la file et ne rien lancer de plus
    """

    CONTINUE = 1
    STOP     = 0

    def __init__(self, error_message: str, url: str, queue_size: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Erreur de téléchargement")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setMaximumWidth(640)
        self._result_choice = self.STOP
        self._build_ui(error_message, url, queue_size)

    def _build_ui(self, error_message: str, url: str, queue_size: int):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Icône + Titre ──────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        lbl_icon = QLabel("⚠")
        lbl_icon.setStyleSheet(
            "font-size: 36px; color: #f38ba8; background: transparent;"
        )
        lbl_icon.setFixedWidth(44)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        header_row.addWidget(lbl_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        lbl_title = QLabel("Échec du téléchargement")
        lbl_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #f38ba8; background: transparent;"
        )
        title_col.addWidget(lbl_title)

        # URL tronquée
        if url:
            short_url = url if len(url) <= 60 else url[:57] + "…"
            lbl_url = QLabel(short_url)
            lbl_url.setStyleSheet(
                "font-size: 11px; color: #a6adc8; background: transparent;"
            )
            lbl_url.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            lbl_url.setWordWrap(True)
            title_col.addWidget(lbl_url)

        header_row.addLayout(title_col)
        layout.addLayout(header_row)

        # ── Message d'erreur ───────────────────────────────────
        err_frame = QFrame()
        err_frame.setObjectName("card")
        err_frame.setStyleSheet(
            "QFrame { background-color: #3d1f2a; border: 1px solid #f38ba8; "
            "border-radius: 8px; }"
        )
        err_layout = QVBoxLayout(err_frame)
        err_layout.setContentsMargins(14, 10, 14, 10)

        lbl_err_label = QLabel("Détail de l'erreur :")
        lbl_err_label.setStyleSheet(
            "color: #f38ba8; font-size: 11px; font-weight: 600; background: transparent;"
        )
        err_layout.addWidget(lbl_err_label)

        lbl_err_msg = QLabel(error_message or "Erreur inconnue.")
        lbl_err_msg.setStyleSheet(
            "color: #cdd6f4; font-size: 12px; background: transparent;"
        )
        lbl_err_msg.setWordWrap(True)
        lbl_err_msg.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        err_layout.addWidget(lbl_err_msg)
        layout.addWidget(err_frame)

        # ── Info file d'attente ────────────────────────────────
        if queue_size > 0:
            lbl_queue = QLabel(
                f"ℹ  Il reste {queue_size} téléchargement(s) en attente dans la file."
            )
            lbl_queue.setStyleSheet(
                "color: #89b4fa; font-size: 12px; background: transparent;"
            )
            lbl_queue.setWordWrap(True)
            layout.addWidget(lbl_queue)
        else:
            lbl_queue = QLabel("ℹ  La file d'attente est vide.")
            lbl_queue.setStyleSheet(
                "color: #a6adc8; font-size: 12px; background: transparent;"
            )
            layout.addWidget(lbl_queue)

        # ── Séparateur ─────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #313244; border: none; max-height: 1px;")
        layout.addWidget(sep)

        # ── Boutons ────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        btn_stop = QPushButton("⏹  Tout arrêter")
        btn_stop.setMinimumWidth(130)
        btn_stop.setMinimumHeight(36)
        btn_stop.setStyleSheet(
            "QPushButton {"
            "  background-color: #313244;"
            "  color: #f38ba8;"
            "  border: 1px solid #f38ba8;"
            "  border-radius: 6px;"
            "  padding: 6px 16px;"
            "  font-weight: 600;"
            "}"
            "QPushButton:hover { background-color: #3d2030; }"
        )
        btn_stop.clicked.connect(self._on_stop)
        btn_row.addWidget(btn_stop)

        if queue_size > 0:
            btn_continue = QPushButton("▶  Continuer avec le suivant")
        else:
            btn_continue = QPushButton("✕  Fermer")
        btn_continue.setMinimumWidth(180)
        btn_continue.setMinimumHeight(36)
        btn_continue.setDefault(True)
        btn_continue.setStyleSheet(
            "QPushButton {"
            "  background-color: #89b4fa;"
            "  color: #1e1e2e;"
            "  border: none;"
            "  border-radius: 6px;"
            "  padding: 6px 16px;"
            "  font-weight: 700;"
            "}"
            "QPushButton:hover { background-color: #b4befe; }"
        )
        btn_continue.clicked.connect(self._on_continue)
        btn_row.addWidget(btn_continue)

        layout.addLayout(btn_row)

    def _on_continue(self):
        self._result_choice = self.CONTINUE
        self.accept()

    def _on_stop(self):
        self._result_choice = self.STOP
        self.reject()

    def exec(self) -> int:
        """Retourne CONTINUE ou STOP selon le choix de l'utilisateur."""
        super().exec()
        return self._result_choice
