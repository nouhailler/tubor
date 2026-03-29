"""
Tubor - Boîte de dialogue d'aide
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QWidget, QScrollArea,
    QFrame,
)


def _section(title: str, body: str) -> QWidget:
    """Crée un bloc titre + texte pour une section d'aide."""
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 8, 0, 4)
    layout.setSpacing(4)

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet(
        "font-size: 13px; font-weight: 700; color: #89b4fa;"
    )
    layout.addWidget(lbl_title)

    lbl_body = QLabel(body)
    lbl_body.setWordWrap(True)
    lbl_body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    lbl_body.setStyleSheet("color: #cdd6f4; font-size: 12px; line-height: 1.5;")
    layout.addWidget(lbl_body)
    return w


def _separator() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setStyleSheet("background-color: #313244; border: none; max-height: 1px; margin: 4px 0;")
    return sep


def _tab_content(sections: list) -> QWidget:
    """Crée un onglet scrollable avec une liste de sections."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(8, 4, 16, 12)
    layout.setSpacing(2)

    for i, item in enumerate(sections):
        if item == "---":
            layout.addWidget(_separator())
        else:
            layout.addWidget(item)

    layout.addStretch()
    scroll.setWidget(container)
    return scroll


class HelpDialog(QDialog):
    """Fenêtre d'aide de Tubor — organisée en onglets thématiques."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aide — Tubor")
        self.setMinimumSize(620, 520)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(12)

        # ── En-tête ───────────────────────────────────────────────
        header = QHBoxLayout()
        lbl_icon = QLabel("❓")
        lbl_icon.setStyleSheet("font-size: 28px;")
        header.addWidget(lbl_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        lbl_title = QLabel("Aide — Tubor")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #cdd6f4;")
        lbl_sub = QLabel("Téléchargeur vidéo & audio — propulsé par yt-dlp")
        lbl_sub.setStyleSheet("font-size: 11px; color: #a6adc8;")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        header.addLayout(title_col)
        header.addStretch()
        layout.addLayout(header)

        # ── Onglets ───────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.addTab(self._tab_demarrage(),    "🚀  Démarrage rapide")
        tabs.addTab(self._tab_formats(),      "🎬  Formats & Qualité")
        tabs.addTab(self._tab_file(),         "📋  File d'attente")
        tabs.addTab(self._tab_arret(),        "⏹  Arrêt & Erreurs")
        tabs.addTab(self._tab_parametres(),   "⚙  Paramètres")
        tabs.addTab(self._tab_faq(),          "❔  FAQ")
        layout.addWidget(tabs, 1)

        # ── Bouton fermer ─────────────────────────────────────────
        btn_close = QPushButton("Fermer")
        btn_close.setFixedWidth(100)
        btn_close.setDefault(True)
        btn_close.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(btn_close)
        layout.addLayout(row)

    # ── Contenu des onglets ───────────────────────────────────────

    def _tab_demarrage(self) -> QWidget:
        return _tab_content([
            _section(
                "1.  Collez l'URL",
                "Copiez l'adresse d'une vidéo YouTube, Vimeo, Twitter/X, SoundCloud, "
                "Dailymotion ou tout autre site supporté par yt-dlp, "
                "puis collez-la dans le champ en haut de la fenêtre.\n\n"
                "💡 Le bouton 📋 Coller insère automatiquement le contenu de votre presse-papier."
            ),
            "---",
            _section(
                "2.  Choisissez le format",
                "Deux boutons vous permettent de basculer entre :\n"
                "  • 🎬 Vidéo (MP4)         — télécharge la vidéo complète\n"
                "  • 🎵 Audio seulement (MP3) — extrait uniquement l'audio\n\n"
                "Le format sélectionné s'applique à tous les téléchargements de la session."
            ),
            "---",
            _section(
                "3.  Sélectionnez la qualité",
                "Vidéo : Meilleure qualité, 1080p, 720p, 480p ou 360p\n"
                "Audio : MP3 320 kbps (haute fidélité), 192 kbps ou 128 kbps\n\n"
                "⚠ La qualité dépend de ce que la source propose. "
                "Si la qualité demandée n'est pas disponible, yt-dlp choisit "
                "automatiquement la meilleure alternative."
            ),
            "---",
            _section(
                "4.  Choisissez le dossier de destination",
                "Par défaut, les fichiers sont enregistrés dans ~/Downloads.\n"
                "Cliquez sur 📁 Parcourir pour choisir un autre dossier.\n\n"
                "Si le dossier n'existe pas, Tubor vous proposera de le créer."
            ),
            "---",
            _section(
                "5.  Lancez le téléchargement",
                "Appuyez sur ⬇ TÉLÉCHARGER pour démarrer immédiatement.\n"
                "Vous pouvez aussi appuyer sur Entrée dans le champ URL.\n\n"
                "Une barre bleue apparaît en haut avec la progression, la vitesse "
                "et le temps estimé restant."
            ),
        ])

    def _tab_formats(self) -> QWidget:
        return _tab_content([
            _section(
                "Sites supportés",
                "Tubor utilise yt-dlp en moteur, qui supporte plus de 1 000 sites :\n"
                "YouTube · Vimeo · Twitter/X · Instagram · TikTok · SoundCloud · "
                "Dailymotion · Twitch · Reddit · PeerTube · Arte · France TV…\n\n"
                "Si un site n'est pas supporté, une erreur s'affiche dans le journal."
            ),
            "---",
            _section(
                "Format Vidéo (MP4)",
                "Télécharge la vidéo et l'audio séparément puis les fusionne en MP4 "
                "via ffmpeg.\n\n"
                "Qualités disponibles :\n"
                "  • Meilleure qualité  — choisit automatiquement la résolution maximale\n"
                "  • 1080p (Full HD)    — recommandé pour la plupart des usages\n"
                "  • 720p (HD)          — bon compromis taille/qualité\n"
                "  • 480p / 360p        — pour les connexions lentes ou le stockage limité"
            ),
            "---",
            _section(
                "Format Audio seulement (MP3)",
                "Extrait l'audio de la vidéo et le convertit en MP3 via ffmpeg.\n\n"
                "Qualités disponibles :\n"
                "  • 320 kbps — qualité maximale, recommandé pour la musique\n"
                "  • 192 kbps — bonne qualité, taille réduite\n"
                "  • 128 kbps — qualité suffisante pour les podcasts"
            ),
            "---",
            _section(
                "Métadonnées & Miniature",
                "Si ffmpeg est installé, Tubor peut automatiquement :\n"
                "  • Intégrer les métadonnées (titre, artiste, année) dans le fichier\n"
                "  • Intégrer la miniature (pochette) dans le fichier MP3 ou MP4\n\n"
                "Ces options s'activent dans ⚙ Paramètres → Téléchargement."
            ),
            "---",
            _section(
                "Playlists",
                "Si l'URL pointe vers une playlist, le menu PLAYLIST vous permet de :\n"
                "  • Vidéo actuelle seulement — télécharge uniquement la vidéo de l'URL\n"
                "  • Toute la playlist         — télécharge chaque vidéo de la playlist\n\n"
                "💡 Les vidéos d'une playlist sont ajoutées une par une à la file d'attente."
            ),
        ])

    def _tab_file(self) -> QWidget:
        return _tab_content([
            _section(
                "Comment fonctionne la file d'attente",
                "Tubor télécharge les vidéos une par une dans l'ordre où elles ont "
                "été ajoutées. La file permet de préparer plusieurs téléchargements "
                "à l'avance sans attendre la fin du précédent."
            ),
            "---",
            _section(
                "Ajouter à la file",
                "Deux façons d'ajouter un téléchargement :\n\n"
                "  • ⬇ TÉLÉCHARGER       — ajoute et lance immédiatement si rien n'est en cours\n"
                "  • + Ajouter à la file  — ajoute en attente sans interrompre le téléchargement actif\n\n"
                "Vous pouvez ajouter autant d'URLs que vous le souhaitez "
                "pendant qu'un téléchargement est en cours."
            ),
            "---",
            _section(
                "Suivre l'avancement",
                "Chaque téléchargement apparaît comme une carte dans la liste :\n"
                "  • Badge 🎬 VIDÉO ou 🎵 AUDIO selon le format\n"
                "  • Titre de la vidéo (affiché dès que yt-dlp le connaît)\n"
                "  • Barre de progression\n"
                "  • Pourcentage · Vitesse de téléchargement · Temps restant\n"
                "  • Bouton ⏹ Arrêter individuel"
            ),
            "---",
            _section(
                "Nettoyer la liste",
                "Cliquez sur Effacer terminés pour supprimer de la liste "
                "les téléchargements déjà complétés, annulés ou en erreur.\n\n"
                "Les fichiers sur le disque ne sont pas supprimés."
            ),
        ])

    def _tab_arret(self) -> QWidget:
        return _tab_content([
            _section(
                "Arrêter un téléchargement",
                "Trois façons d'arrêter un téléchargement en cours :\n\n"
                "  1. Bouton ⏹ Arrêter sur la carte du téléchargement\n"
                "  2. Bouton ⏹ ARRÊTER dans la barre bleue en haut\n"
                "  3. Touche Échap (Escape) du clavier\n\n"
                "L'arrêt est immédiat et garanti : Tubor envoie un signal "
                "d'arrêt au processus yt-dlp sous-jacent."
            ),
            "---",
            _section(
                "Que se passe-t-il quand on arrête ?",
                "Quand vous arrêtez manuellement :\n"
                "  • Le téléchargement actif est stoppé\n"
                "  • La file d'attente est vidée\n"
                "  • Les éventuels fichiers partiels restent sur le disque\n\n"
                "Tubor ne tente pas de reprendre automatiquement."
            ),
            "---",
            _section(
                "Erreurs et fenêtre de notification",
                "Quand une erreur survient (403 Forbidden, vidéo privée, etc.), "
                "une fenêtre s'affiche avec :\n"
                "  • Le message d'erreur en clair\n"
                "  • L'URL concernée\n"
                "  • Deux choix :\n"
                "      ▶ Continuer avec le suivant — passe au prochain de la file\n"
                "      ⏹ Tout arrêter             — vide la file et s'arrête"
            ),
            "---",
            _section(
                "Erreur HTTP 403 Forbidden",
                "Cette erreur signifie que le serveur a refusé l'accès.\n\n"
                "Causes fréquentes :\n"
                "  • Vidéo restreinte géographiquement\n"
                "  • YouTube a changé son format de streaming (HLS)\n"
                "  • Votre IP est temporairement bloquée\n\n"
                "Solutions :\n"
                "  • Attendez quelques minutes et réessayez\n"
                "  • Mettez à jour yt-dlp dans ⚙ Paramètres → Moteur yt-dlp\n"
                "  • Essayez une autre qualité (720p au lieu de Meilleure qualité)\n"
                "  • Utilisez des cookies si vous êtes connecté au site (⚙ Paramètres → Authentification)"
            ),
            "---",
            _section(
                "Notifications bureau",
                "Tubor envoie une notification système quand un téléchargement se "
                "termine (succès ou erreur). Assurez-vous que notify-send est "
                "installé sur votre système :\n\n"
                "    sudo apt install libnotify-bin"
            ),
        ])

    def _tab_parametres(self) -> QWidget:
        return _tab_content([
            _section(
                "Accéder aux paramètres",
                "Cliquez sur l'icône ⚙ en haut à droite de la fenêtre."
            ),
            "---",
            _section(
                "Téléchargement",
                "  • Dossier par défaut    — dossier de destination si aucun n'est saisi\n"
                "  • Format préféré        — Video ou Audio, mémorisé entre les sessions\n"
                "  • Qualité préférée      — pré-sélectionnée à l'ouverture\n"
                "  • Métadonnées           — intègre titre, artiste… dans le fichier\n"
                "  • Miniature             — intègre la vignette dans MP3/MP4"
            ),
            "---",
            _section(
                "Apparence",
                "Choisissez entre :\n"
                "  • Thème sombre — fond foncé (Catppuccin Mocha), recommandé la nuit\n"
                "  • Thème clair  — fond blanc (Catppuccin Latte)\n\n"
                "Le thème est appliqué immédiatement après avoir cliqué sur Enregistrer."
            ),
            "---",
            _section(
                "Authentification (Cookies)",
                "Certaines vidéos nécessitent d'être connecté (vidéos membres, "
                "contenu adulte vérifié…).\n\n"
                "Pour les télécharger :\n"
                "  1. Installez l'extension navigateur 'Get cookies.txt LOCALLY'\n"
                "  2. Connectez-vous sur le site concerné dans votre navigateur\n"
                "  3. Exportez les cookies au format cookies.txt\n"
                "  4. Dans Paramètres → Authentification, pointez vers ce fichier\n\n"
                "⚠ Ne partagez jamais votre fichier cookies.txt — il donne accès à votre compte."
            ),
            "---",
            _section(
                "Mise à jour du moteur yt-dlp",
                "YouTube et les autres plateformes changent régulièrement leur code. "
                "Si des téléchargements échouent soudainement, c'est souvent parce "
                "que yt-dlp a besoin d'être mis à jour.\n\n"
                "Dans ⚙ Paramètres → Moteur yt-dlp, cliquez sur ⟳ Vérifier les mises à jour.\n\n"
                "Cette opération nécessite une connexion Internet et peut prendre "
                "quelques dizaines de secondes."
            ),
        ])

    def _tab_faq(self) -> QWidget:
        return _tab_content([
            _section(
                "Le téléchargement est très lent, est-ce normal ?",
                "La vitesse dépend de votre connexion Internet et du serveur source. "
                "YouTube limite parfois intentionnellement la vitesse. "
                "Choisir une qualité moindre (720p au lieu de 1080p) peut accélérer le téléchargement."
            ),
            "---",
            _section(
                "Le fichier MP3 n'a pas de pochette / pas de titre",
                "Vérifiez que :\n"
                "  • ffmpeg est installé (sudo apt install ffmpeg)\n"
                "  • Les options Métadonnées et Miniature sont cochées dans ⚙ Paramètres\n\n"
                "Si ffmpeg est absent, Tubor affiche un avertissement en haut de la fenêtre."
            ),
            "---",
            _section(
                "Puis-je fermer Tubor pendant un téléchargement ?",
                "Oui, mais Tubor vous demandera confirmation. Si vous confirmez, "
                "le téléchargement en cours sera interrompu. "
                "Les fichiers partiels resteront sur le disque."
            ),
            "---",
            _section(
                "Tubor peut-il télécharger des vidéos privées ou membres ?",
                "Uniquement si vous fournissez un fichier cookies.txt issu d'un "
                "navigateur où vous êtes connecté au compte qui a accès à ces vidéos.\n"
                "Voir ⚙ Paramètres → Authentification."
            ),
            "---",
            _section(
                "L'erreur 'URL non supportée' apparaît",
                "Tous les sites ne sont pas supportés par yt-dlp. "
                "Consultez la liste complète sur https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md\n\n"
                "Si le site est normalement supporté, essayez de mettre à jour yt-dlp "
                "(⚙ Paramètres → Moteur yt-dlp)."
            ),
            "---",
            _section(
                "Comment mettre à jour Tubor lui-même ?",
                "Consultez la page GitHub du projet pour les nouvelles versions. "
                "Le moteur yt-dlp (la partie qui change le plus souvent) se met à "
                "jour depuis l'application via ⚙ Paramètres → Moteur yt-dlp."
            ),
            "---",
            _section(
                "Raccourcis clavier",
                "  • Entrée     — lance le téléchargement (depuis le champ URL)\n"
                "  • Échap      — arrête le téléchargement en cours\n"
                "  • Ctrl+V     — coller une URL dans le champ (standard système)"
            ),
        ])
