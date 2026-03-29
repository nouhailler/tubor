"""
Tubor - Widget représentant un téléchargement dans la liste
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QProgressBar, QPushButton, QFrame,
)

from core.downloader import DownloadProgress


class DownloadItemWidget(QWidget):
    """Carte d'un téléchargement dans la liste."""

    cancel_requested = pyqtSignal(int)  # task_id

    def __init__(self, task_id: int, url: str, format_type: str = "video", parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.url = url
        self.format_type = format_type
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("card")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(6)

        # ── Ligne 1 : badge type + titre ──────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        # Badge format
        badge_text = "🎵 AUDIO" if self.format_type == "audio" else "🎬 VIDÉO"
        badge_color = "#a6e3a1" if self.format_type == "audio" else "#89b4fa"
        lbl_badge = QLabel(badge_text)
        lbl_badge.setStyleSheet(
            f"background-color: transparent; color: {badge_color}; "
            f"font-size: 10px; font-weight: 700; border: 1px solid {badge_color}; "
            f"border-radius: 3px; padding: 1px 5px;"
        )
        lbl_badge.setFixedHeight(18)
        top_row.addWidget(lbl_badge)

        self.lbl_title = QLabel(self._short_url())
        self.lbl_title.setStyleSheet("font-weight: 600;")
        self.lbl_title.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        top_row.addWidget(self.lbl_title, 1)

        outer.addLayout(top_row)

        # ── Barre de progression ───────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        outer.addWidget(self.progress_bar)

        # ── Ligne 2 : statut + vitesse + ETA + bouton ARRÊTER ─
        info_row = QHBoxLayout()
        info_row.setSpacing(10)

        self.lbl_status = QLabel("En attente…")
        self.lbl_status.setStyleSheet("color: #a6adc8; font-size: 11px;")
        info_row.addWidget(self.lbl_status, 1)

        self.lbl_speed = QLabel("")
        self.lbl_speed.setStyleSheet("color: #a6adc8; font-size: 11px;")
        info_row.addWidget(self.lbl_speed)

        self.lbl_eta = QLabel("")
        self.lbl_eta.setStyleSheet("color: #a6adc8; font-size: 11px;")
        info_row.addWidget(self.lbl_eta)

        # ── Bouton ARRÊTER — toujours visible et rouge ────────
        self.btn_stop = QPushButton("⏹ Arrêter")
        self.btn_stop.setFixedSize(80, 24)
        self.btn_stop.setToolTip("Arrêter ce téléchargement")
        self.btn_stop.setStyleSheet(
            "QPushButton {"
            "  background-color: #f38ba8;"
            "  color: #1e1e2e;"
            "  border: none;"
            "  border-radius: 4px;"
            "  font-size: 11px;"
            "  font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "  background-color: #eba0ac;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #d20f39;"
            "}"
        )
        self.btn_stop.clicked.connect(lambda: self.cancel_requested.emit(self.task_id))
        info_row.addWidget(self.btn_stop)
        outer.addLayout(info_row)

    def _short_url(self) -> str:
        """Affiche une version courte de l'URL."""
        u = self.url
        if len(u) > 60:
            return u[:57] + "…"
        return u

    def update_progress(self, progress: DownloadProgress):
        """Met à jour l'affichage depuis un objet DownloadProgress."""
        if progress.title:
            title = progress.title
            if len(title) > 60:
                title = title[:57] + "…"
            self.lbl_title.setText(title)

        status = progress.status

        if status == "downloading":
            self.progress_bar.setValue(int(progress.percent))
            self.lbl_status.setText(f"{progress.percent:.1f}%")
            self.lbl_speed.setText(progress.speed)
            self.lbl_eta.setText(f"⏱ {progress.eta}" if progress.eta else "")
            self.btn_stop.setEnabled(True)

        elif status == "processing":
            self.progress_bar.setValue(99)
            self.lbl_status.setText("⚙ Post-traitement…")
            self.lbl_speed.setText("")
            self.lbl_eta.setText("")
            self.btn_stop.setEnabled(False)

        elif status == "finished":
            self.progress_bar.setValue(100)
            self.lbl_status.setText("✔ Terminé")
            self.lbl_status.setStyleSheet("color: #a6e3a1; font-size: 11px; font-weight: 600;")
            self.lbl_speed.setText("")
            self.lbl_eta.setText("")
            self.btn_stop.hide()

        elif status == "error":
            self.progress_bar.setProperty("error", "true")
            self.progress_bar.style().unpolish(self.progress_bar)
            self.progress_bar.style().polish(self.progress_bar)
            msg = progress.error_message or "Erreur inconnue"
            self.lbl_status.setText(f"✗ {msg}")
            self.lbl_status.setStyleSheet("color: #f38ba8; font-size: 11px;")
            self.lbl_speed.setText("")
            self.lbl_eta.setText("")
            self.btn_stop.hide()

        elif status == "cancelled":
            self.lbl_status.setText("⊘ Arrêté")
            self.lbl_status.setStyleSheet("color: #fab387; font-size: 11px;")
            self.lbl_speed.setText("")
            self.lbl_eta.setText("")
            self.btn_stop.hide()

        elif status == "waiting":
            self.lbl_status.setText("⏸ En attente…")
            self.btn_stop.setEnabled(True)
