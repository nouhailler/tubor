#!/usr/bin/env python3
"""
Tubor — Interface graphique pour yt-dlp
Licence : GPL v3
"""

import sys
import os

# Ajoute le répertoire courant au PYTHONPATH (pour les imports relatifs)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from core.config import Config
from ui.main_window import MainWindow


def main():
    # Activer le support des écrans haute résolution (HiDPI)
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Tubor")
    app.setApplicationDisplayName("Tubor")
    app.setOrganizationName("Tubor")

    # Chargement de la configuration
    config = Config()

    # Fenêtre principale
    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
