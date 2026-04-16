import { useState } from 'react'
import './HelpModal.css'

interface Props {
  onClose: () => void
}

type Tab = 'start' | 'formats' | 'playlist' | 'network' | 'dashboard' | 'settings' | 'errors'

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'start',     label: 'Démarrage rapide',   icon: '🚀' },
  { id: 'formats',   label: 'Formats & Qualités',  icon: '🎬' },
  { id: 'playlist',  label: 'Playlists & File',    icon: '📋' },
  { id: 'network',   label: 'Réseau & Sécurité',   icon: '🌐' },
  { id: 'dashboard', label: 'Tableau de bord',     icon: '📊' },
  { id: 'settings',  label: 'Paramètres',          icon: '⚙' },
  { id: 'errors',    label: 'Erreurs & Conseils',  icon: '🔧' },
]

export default function HelpModal({ onClose }: Props) {
  const [tab, setTab] = useState<Tab>('start')

  return (
    <div className="help-page" role="dialog" aria-modal="true" aria-label="Aide Tubor">

      <div className="help-page-header">
        <h2 className="help-page-title">❓ Aide — Tubor v0.3</h2>
        <button className="icon-btn" onClick={onClose} aria-label="Fermer">✕</button>
      </div>

      {/* Onglets */}
      <div className="help-page-tabs">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`help-tab-btn ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      <div className="help-page-body">

        {/* ── Démarrage rapide ───────────────────────────────────── */}
        {tab === 'start' && (
          <div className="help-section">
            <h3>Télécharger une vidéo ou de l'audio</h3>
            <ol className="help-steps">
              <li>
                <strong>Copiez l'URL</strong> de la vidéo depuis votre navigateur
                (YouTube, Vimeo, Twitch, Dailymotion, et 1000+ sites supportés).
              </li>
              <li>
                <strong>Collez l'URL</strong> dans le champ texte, ou cliquez sur
                <span className="kbd">📋</span> pour coller depuis le presse-papiers.
                Vous pouvez coller <strong>plusieurs URLs</strong> d'un coup — une par ligne.
              </li>
              <li>
                <strong>Prévisualisez</strong> (optionnel) avec le bouton <span className="kbd">🔍</span>
                pour voir le titre, la durée et choisir le format exact avant de lancer.
              </li>
              <li>
                <strong>Choisissez</strong> format (<span className="badge badge-video">🎬 Vidéo</span> ou
                <span className="badge badge-audio">🎵 Audio</span>), qualité, et dossier de destination.
              </li>
              <li>
                Cliquez sur <span className="kbd">⬇ TÉLÉCHARGER</span> — la progression apparaît
                en temps réel dans la liste ci-dessous.
              </li>
            </ol>

            <h3>Multi-URLs — télécharger plusieurs vidéos d'un coup</h3>
            <p>
              La zone de saisie accepte autant d'URLs que vous voulez. Collez-les toutes en une fois
              (une par ligne) : un badge <strong>N URLs</strong> confirme la détection.
              Chaque URL est ajoutée individuellement à la file et traitée dans l'ordre.
            </p>

            <h3>Prévisualisation avant téléchargement</h3>
            <p>
              Le bouton <span className="kbd">🔍</span> interroge yt-dlp pour récupérer le titre,
              la durée, la miniature et les formats disponibles. Une fenêtre s'affiche pour
              vous permettre de confirmer ou d'ajuster le format/qualité avant de lancer.
            </p>

            <h3>Suivi en temps réel</h3>
            <p>Chaque téléchargement affiche :</p>
            <ul>
              <li>Une <strong>barre de progression</strong> animée avec pourcentage</li>
              <li>La <strong>vitesse</strong> de téléchargement et l'<strong>ETA</strong></li>
              <li>Le <strong>titre</strong> de la vidéo une fois détecté</li>
              <li>Le <strong>drapeau du pays</strong> d'où part le téléchargement (proxy/VPN actif)</li>
              <li>Le <strong>statut</strong> en couleur : bleu = en cours, orange = traitement, vert = terminé, rouge = erreur</li>
            </ul>

            <h3>Réordonner la file d'attente</h3>
            <p>
              Les téléchargements en statut <strong>En attente</strong> peuvent être réordonnés
              par <strong>glisser-déposer</strong>. Faites glisser une carte vers le haut ou le
              bas pour changer sa priorité dans la file.
            </p>

            <h3>Toggles rapides Proxy / VPN</h3>
            <p>
              Sous le formulaire, deux boutons permettent d'activer ou désactiver instantanément
              le proxy et le VPN <strong>sans quitter la page</strong> et sans perdre la configuration :
            </p>
            <ul>
              <li><span className="kbd">🌐 Proxy ON/OFF</span> — visible uniquement si un proxy est configuré dans les Paramètres</li>
              <li><span className="kbd">🛡 VPN ON/OFF</span> — visible uniquement si des pays VPN sont configurés</li>
            </ul>

            <h3>Journal des logs</h3>
            <p>
              Le panneau <strong>Journal</strong> en bas de page affiche les messages bruts de yt-dlp
              en temps réel via WebSocket. Cliquez dessus pour l'ouvrir/fermer.
              Les lignes sont colorées : rouge = erreur, vert = succès, cyan = commande VPN.
            </p>

            <h3>Ouvrir un fichier téléchargé</h3>
            <p>
              Après un téléchargement réussi, le bouton <span className="kbd">📂 Ouvrir</span> lance
              le fichier directement avec le lecteur par défaut de votre système (VLC, mpv, etc.)
              sans quitter l'interface.
            </p>
          </div>
        )}

        {/* ── Formats & Qualités ──────────────────────────────────── */}
        {tab === 'formats' && (
          <div className="help-section">
            <h3>Mode Vidéo (MP4)</h3>
            <p>Télécharge la vidéo complète avec le son. Le fichier final est en <strong>MP4</strong>.</p>
            <table className="help-table">
              <thead>
                <tr><th>Qualité</th><th>Résolution</th><th>Usage recommandé</th></tr>
              </thead>
              <tbody>
                <tr><td><strong>Meilleure qualité</strong></td><td>Maximale disponible</td><td>Archive, montage</td></tr>
                <tr><td>1080p (Full HD)</td><td>1920×1080</td><td>Visionnage TV/écran</td></tr>
                <tr><td>720p (HD)</td><td>1280×720</td><td>Bon compromis taille/qualité</td></tr>
                <tr><td>480p (SD)</td><td>854×480</td><td>Connexion lente</td></tr>
                <tr><td>360p (Basse)</td><td>640×360</td><td>Aperçu, économie d'espace</td></tr>
              </tbody>
            </table>
            <div className="help-note">
              Si la résolution demandée n'est pas disponible, yt-dlp sélectionne automatiquement
              la meilleure qualité inférieure disponible.
            </div>

            <h3>Mode Audio (MP3)</h3>
            <p>Extrait uniquement la piste audio et la convertit en <strong>MP3</strong> via ffmpeg.</p>
            <table className="help-table">
              <thead>
                <tr><th>Qualité</th><th>Débit</th><th>Usage recommandé</th></tr>
              </thead>
              <tbody>
                <tr><td><strong>Meilleure qualité</strong></td><td>320 kbps</td><td>Musique, archive</td></tr>
                <tr><td>MP3 320 kbps</td><td>320 kbps</td><td>Qualité maximale</td></tr>
                <tr><td>MP3 192 kbps</td><td>192 kbps</td><td>Bon équilibre</td></tr>
                <tr><td>MP3 128 kbps</td><td>128 kbps</td><td>Podcasts, voix</td></tr>
              </tbody>
            </table>

            <h3>Prévisualisation des formats disponibles</h3>
            <p>
              Le bouton <span className="kbd">🔍</span> permet de voir tous les formats et résolutions
              réellement disponibles pour une URL avant de télécharger. Utile pour choisir
              précisément la qualité ou vérifier qu'une piste audio séparée existe.
            </p>

            <h3>Options post-traitement (ffmpeg)</h3>
            <p>
              Tubor utilise <strong>ffmpeg</strong> pour :
            </p>
            <ul>
              <li>Fusionner les flux vidéo et audio séparés (nécessaire pour les formats HD sur YouTube)</li>
              <li>Convertir l'audio en MP3</li>
              <li>Intégrer les <strong>métadonnées</strong> (titre, artiste, album, date)</li>
              <li>Intégrer la <strong>miniature</strong> (pochette d'album ou vignette YouTube)</li>
            </ul>
            <div className="help-note warn">
              Si ffmpeg n'est pas installé, les téléchargements HD et la conversion MP3 ne
              fonctionneront pas. Installez-le avec : <code>sudo apt install ffmpeg</code>
            </div>
          </div>
        )}

        {/* ── Playlists & File ────────────────────────────────────── */}
        {tab === 'playlist' && (
          <div className="help-section">
            <h3>Modes de téléchargement de playlist</h3>

            <div className="help-card">
              <div className="help-card-title">🎬 Vidéo seule (par défaut)</div>
              <p>
                Télécharge uniquement la vidéo correspondant à l'URL, même si elle fait
                partie d'une playlist. Idéal quand vous voulez un contenu précis.
              </p>
            </div>

            <div className="help-card">
              <div className="help-card-title">📋 Playlist entière</div>
              <p>
                Télécharge toutes les vidéos de la playlist. Chaque vidéo est ajoutée
                individuellement à la file d'attente et traitée séquentiellement.
              </p>
              <p>
                <strong>Limite de playlist</strong> — Indiquez un nombre pour ne télécharger
                que les N premières vidéos (ex : <em>10</em>).
                Laissez <em>0</em> pour tout télécharger.
              </p>
            </div>

            <h3>Gestion de la file d'attente</h3>
            <ul>
              <li>Les téléchargements sont traités <strong>un par un</strong> dans l'ordre d'ajout</li>
              <li><strong>Glissez-déposez</strong> les cartes en statut "En attente" pour changer leur ordre de priorité</li>
              <li>Le bouton <span className="kbd">⊘ Tout arrêter</span> annule tous les téléchargements actifs</li>
              <li>Le bouton <span className="kbd">🗑 Effacer terminés</span> nettoie la liste des éléments finis/annulés</li>
            </ul>

            <h3>Planification à une heure précise</h3>
            <p>
              Cochez <span className="kbd">⏱ Planifier</span> dans le formulaire pour choisir une
              date et heure de démarrage. Le téléchargement reste en file et démarre automatiquement
              à l'heure programmée.
            </p>

            <div className="help-note">
              Pour planifier tous les téléchargements uniquement la nuit, utilisez le
              <strong> Mode Nuit tranquille</strong> dans <em>Paramètres → Planification</em>.
            </div>

            <h3>Compatibilité</h3>
            <p>Les playlists sont supportées pour :</p>
            <ul>
              <li>YouTube (playlists publiques et privées avec cookies)</li>
              <li>Twitch (VOD clips)</li>
              <li>SoundCloud (albums, sets)</li>
              <li>Et tout site supporté par yt-dlp avec une notion de playlist</li>
            </ul>
          </div>
        )}

        {/* ── Réseau & Sécurité ────────────────────────────────────── */}
        {tab === 'network' && (
          <div className="help-section">
            <h3>Toggles rapides sur la page de téléchargement</h3>
            <p>
              Les boutons <span className="kbd">🌐 Proxy ON/OFF</span> et <span className="kbd">🛡 VPN ON/OFF</span>
              permettent d'activer/désactiver proxy et VPN en un clic <strong>sans perdre la configuration</strong>.
              Ils n'apparaissent que si un proxy ou des pays VPN sont configurés dans les Paramètres.
            </p>

            <h3>Proxies (Paramètres → Réseau & Proxies)</h3>
            <p>
              Un proxy achemine votre trafic via une autre IP — utile quand YouTube bloque votre
              IP pour téléchargements répétés (HTTP 429/403).
            </p>
            <dl className="help-dl">
              <dt>Proxy unique</dt>
              <dd>
                Un seul proxy pour tous les téléchargements.<br />
                Formats : <code>http://host:port</code>, <code>http://host:port:user:pass</code>, <code>socks5://host:port</code><br />
                Le format court <code>http://IP:PORT:USER:PASS</code> est automatiquement normalisé.
              </dd>
              <dt>Liste de proxies</dt>
              <dd>
                Un proxy par ligne. Avec la <strong>rotation automatique</strong> activée,
                Tubor change de proxy à chaque nouveau téléchargement (round-robin).
                En cas d'erreur, le proxy suivant est utilisé pour le retry.
              </dd>
              <dt>Tentatives max</dt>
              <dd>Nombre de retries en cas d'échec. Backoff exponentiel : 10s, 20s, 40s… (0 = pas de retry)</dd>
              <dt>Pause entre requêtes</dt>
              <dd>Délai entre deux téléchargements (recommandé : 3-5s pour éviter la détection).</dd>
              <dt>Limite de bande passante</dt>
              <dd>Ex : <code>2M</code> ou <code>500K</code>. Vide = illimité.</dd>
            </dl>

            <h3>VPN Auto (Paramètres → VPN Auto)</h3>
            <div className="help-note">
              Quand YouTube détecte un bot (<em>"Sign in to confirm you're not a bot"</em>),
              Tubor peut automatiquement <strong>changer de pays VPN</strong> et relancer le téléchargement
              depuis une nouvelle IP.
            </div>
            <p style={{ marginTop: '0.5rem' }}>Clients VPN supportés :</p>
            <ul>
              <li><strong>ProtonVPN</strong> — <code>/usr/bin/protonvpn connect --country {'{COUNTRY}'}</code></li>
              <li><strong>Mullvad</strong> — <code>mullvad relay set location {'{country}'}</code></li>
              <li><strong>NordVPN</strong> — <code>nordvpn connect {'{country}'}</code></li>
              <li><strong>ExpressVPN</strong> — <code>expressvpn connect {'{country}'}</code></li>
              <li><strong>Script personnalisé</strong> — n'importe quelle commande avec <code>{'{country}'}</code> ou <code>{'{COUNTRY}'}</code></li>
            </ul>
            <p>Les pays de rotation sont sélectionnables en chips (<em>US, GB, DE, FR, NL…</em>) ou en saisissant les codes ISO.</p>

            <div className="help-card">
              <div className="help-card-title">🔄 Flux de retry automatique</div>
              <p>
                1. YouTube détecte un bot → Tubor marque l'erreur<br />
                2. Commande VPN exécutée avec le prochain pays de la rotation<br />
                3. Attente du délai de reconnexion (5s par défaut)<br />
                4. Relance du téléchargement depuis la nouvelle IP<br />
                5. Répété jusqu'au nombre max de tentatives (réglable dans <em>Réseau</em>)
              </p>
            </div>

            <h3>Drapeau pays dans la liste</h3>
            <p>
              Pendant le téléchargement, le drapeau du pays de l'IP utilisée s'affiche sur la carte.
              Tubor géolocalise l'IP via <code>ip-api.com</code> (résultat mis en cache pour éviter
              les appels répétés).
            </p>
          </div>
        )}

        {/* ── Tableau de bord ─────────────────────────────────────── */}
        {tab === 'dashboard' && (
          <div className="help-section">
            <h3>Vue d'ensemble</h3>
            <p>
              La page <strong>📊 Tableau de bord</strong> centralise toutes vos statistiques de téléchargement.
              Les données sont <strong>rafraîchies automatiquement toutes les 30 secondes</strong>.
              Utilisez le bouton <span className="kbd">🔄</span> pour actualiser manuellement.
            </p>

            <h3>Cartes de statistiques</h3>
            <p>Six indicateurs clés sont affichés et certains sont <strong>cliquables</strong> :</p>
            <table className="help-table">
              <thead>
                <tr><th>Carte</th><th>Description</th><th>Clic</th></tr>
              </thead>
              <tbody>
                <tr><td><strong>Total</strong></td><td>Nombre total de téléchargements</td><td>→ Historique</td></tr>
                <tr><td><strong>Réussis ↗</strong></td><td>Téléchargements terminés avec succès</td><td>→ Onglet Réussis</td></tr>
                <tr><td><strong>Échoués ↗</strong></td><td>Téléchargements en erreur</td><td>→ Onglet Échoués</td></tr>
                <tr><td><strong>Aujourd'hui</strong></td><td>Téléchargements du jour</td><td>—</td></tr>
                <tr><td><strong>Téléchargé</strong></td><td>Volume total (Ko, Mo, Go)</td><td>—</td></tr>
                <tr><td><strong>Taux de succès</strong></td><td>% de réussite global</td><td>—</td></tr>
              </tbody>
            </table>

            <h3>Graphique — 14 derniers jours</h3>
            <p>
              Barres empilées CSS : <span style={{ color: 'var(--color-success)' }}>■ vert</span> = réussis,
              <span style={{ color: 'var(--color-error)', marginLeft: '0.3rem' }}>■ rouge</span> = échoués.
              Survolez une barre pour voir le détail du jour.
            </p>

            <h3>Top plateformes</h3>
            <p>
              Barres horizontales montrant les plateformes les plus utilisées
              (YouTube, Vimeo, SoundCloud…) avec le nombre de téléchargements par plateforme.
            </p>

            <h3>Onglet Réussis</h3>
            <p>
              Liste des 100 derniers téléchargements réussis avec titre, plateforme,
              format (🎵 MP3 / 🎬 MP4), taille du fichier et date de fin.
            </p>

            <h3>Onglet Échoués</h3>
            <p>
              Liste des 100 derniers téléchargements en erreur avec le message d'erreur complet.
              Le bouton <span className="kbd">📋 Copier URL</span> copie l'URL dans le presse-papiers
              pour la recoller facilement dans le formulaire et réessayer.
              La colonne <strong>Pays</strong> indique l'IP utilisée lors de la tentative échouée.
            </p>

            <h3>Onglet Historique</h3>
            <p>
              Historique complet avec filtres par <strong>statut</strong> (terminé, erreur, annulé)
              et par <strong>format</strong> (vidéo, audio). Tableau avec colonnes :
              Statut, Titre, Plateforme, <strong>Pays</strong> (drapeau emoji), Format, Taille, Date.
            </p>
          </div>
        )}

        {/* ── Paramètres ──────────────────────────────────────────── */}
        {tab === 'settings' && (
          <div className="help-section">
            <p>
              Les Paramètres sont organisés en <strong>6 onglets</strong> dans une barre latérale gauche.
              Cliquez sur <span className="kbd">💾 Enregistrer</span> en bas pour valider chaque modification.
            </p>

            <h3>📥 Téléchargement</h3>
            <dl className="help-dl">
              <dt>Dossier de destination</dt>
              <dd>Répertoire par défaut où tous les fichiers sont enregistrés. Modifiable aussi pour chaque téléchargement individuellement.</dd>
              <dt>Format préféré</dt>
              <dd>Pré-sélectionne Vidéo (MP4) ou Audio (MP3) à l'ouverture de l'application.</dd>
              <dt>Qualité préférée</dt>
              <dd>Qualité sélectionnée par défaut lors d'un nouveau téléchargement.</dd>
              <dt>Intégrer les métadonnées</dt>
              <dd>Ajoute titre, artiste, date, description dans les balises du fichier (requiert ffmpeg).</dd>
              <dt>Intégrer la miniature</dt>
              <dd>Intègre la vignette/pochette dans le fichier audio ou vidéo (requiert ffmpeg).</dd>
            </dl>

            <h3>🌐 Réseau & Proxies</h3>
            <dl className="help-dl">
              <dt>Proxy unique</dt>
              <dd>Un proxy pour tous les téléchargements. Formats acceptés : <code>http://host:port</code>, <code>http://IP:PORT:USER:PASS</code>, <code>socks5://host:port</code>.</dd>
              <dt>Liste de proxies + rotation</dt>
              <dd>Un proxy par ligne. La rotation round-robin change de proxy à chaque téléchargement. En cas d'erreur, le suivant est utilisé automatiquement.</dd>
              <dt>Tentatives max</dt>
              <dd>Retries en cas d'échec avec backoff exponentiel (10s, 20s, 40s…). 0 = aucun retry.</dd>
              <dt>Pause entre requêtes</dt>
              <dd>Délai en secondes entre chaque téléchargement (3-5s recommandé).</dd>
              <dt>Limite de bande passante</dt>
              <dd><code>2M</code>, <code>500K</code>, etc. Vide = illimité.</dd>
            </dl>

            <h3>🛡 VPN Auto</h3>
            <dl className="help-dl">
              <dt>Activer la rotation VPN</dt>
              <dd>Sur détection de bot YouTube, change de pays et relance automatiquement.</dd>
              <dt>Client VPN</dt>
              <dd>ProtonVPN, Mullvad, NordVPN, ExpressVPN, ou script personnalisé. La commande est pré-remplie selon le choix.</dd>
              <dt>Pays de rotation</dt>
              <dd>Sélectionnables en chips (US, GB, DE, FR, NL, CA, JP…) ou en saisissant les codes ISO dans la zone texte. Rotation round-robin.</dd>
              <dt>Délai de reconnexion</dt>
              <dd>Secondes d'attente après le changement de pays (5s recommandé).</dd>
            </dl>

            <h3>🌙 Planification</h3>
            <dl className="help-dl">
              <dt>Mode Nuit tranquille</dt>
              <dd>Les téléchargements en file démarrent uniquement dans la fenêtre horaire configurée (ex : 22h → 6h). Fonctionne sur les plages qui enjambent minuit.</dd>
              <dt>Planification par téléchargement</dt>
              <dd>Via le formulaire principal (cocher <em>⏱ Planifier</em>), chaque téléchargement peut avoir sa propre heure de départ indépendante du mode nuit.</dd>
            </dl>

            <h3>🔐 Authentification</h3>
            <dl className="help-dl">
              <dt>Fichier cookies (.txt)</dt>
              <dd>
                Chemin absolu vers un fichier cookies au format Netscape.
                Nécessaire pour les vidéos privées, membres, ou restreintes par l'âge.
                Utilisez l'extension <strong>Get cookies.txt LOCALLY</strong> (Chrome/Firefox),
                connectez-vous à YouTube, puis exportez le fichier.
              </dd>
            </dl>

            <h3>⚙ Moteur yt-dlp</h3>
            <dl className="help-dl">
              <dt>Version yt-dlp</dt>
              <dd>Version actuellement installée du moteur de téléchargement.</dd>
              <dt>ffmpeg disponible</dt>
              <dd>Indique si ffmpeg est détecté. Requis pour MP3 et fusion des flux HD.</dd>
              <dt>Mettre à jour yt-dlp</dt>
              <dd>Lance <code>pip install --upgrade yt-dlp</code>. À faire si des sites ne fonctionnent plus.</dd>
              <dt>Robustesse automatique</dt>
              <dd>Chaque téléchargement utilise <code>--retries 5 --fragment-retries 5 --socket-timeout 30 --extractor-retries 3</code>.</dd>
            </dl>
          </div>
        )}

        {/* ── Erreurs & Conseils ───────────────────────────────────── */}
        {tab === 'errors' && (
          <div className="help-section">
            <h3>Messages d'erreur courants</h3>

            <div className="error-entry">
              <div className="error-title">🔴 HTTP 403 Forbidden</div>
              <div className="error-desc">
                Accès refusé. La vidéo est protégée ou votre IP est bloquée.
                <br /><strong>Solutions :</strong>
                <ul>
                  <li>Réessayez plus tard (limitation temporaire)</li>
                  <li>Mettez à jour yt-dlp (Paramètres → Moteur)</li>
                  <li>Configurez un proxy ou activez le VPN</li>
                  <li>Ajoutez vos cookies pour les sites nécessitant une connexion</li>
                </ul>
              </div>
            </div>

            <div className="error-entry">
              <div className="error-title">🔴 Sign in to confirm you're not a bot</div>
              <div className="error-desc">
                YouTube a détecté un comportement automatisé depuis votre IP.
                <br /><strong>Solutions :</strong>
                <ul>
                  <li>Activez le <strong>VPN Auto</strong> (Paramètres → VPN Auto) pour changer de pays automatiquement</li>
                  <li>Exportez vos cookies YouTube et configurez le fichier cookies (Paramètres → Authentification)</li>
                  <li>Activez un proxy résidentiel</li>
                </ul>
              </div>
            </div>

            <div className="error-entry">
              <div className="error-title">🔴 HTTP 429 Too Many Requests</div>
              <div className="error-desc">
                Trop de requêtes depuis votre IP. YouTube a temporairement bloqué votre connexion.
                <br /><strong>Solutions :</strong>
                <ul>
                  <li>Attendez 15-30 minutes</li>
                  <li>Activez la <strong>rotation de proxies</strong> (Paramètres → Réseau)</li>
                  <li>Augmentez la <strong>pause entre requêtes</strong> (3-5s minimum)</li>
                </ul>
              </div>
            </div>

            <div className="error-entry">
              <div className="error-title">🔴 Vidéo privée / Video unavailable</div>
              <div className="error-desc">
                La vidéo est privée, non listée, ou supprimée.
                <br /><strong>Solution :</strong> Configurez votre fichier cookies si vous avez accès à cette vidéo depuis votre compte YouTube.
              </div>
            </div>

            <div className="error-entry">
              <div className="error-title">🔴 URL non reconnue / Unsupported URL</div>
              <div className="error-desc">
                Le site n'est pas supporté ou l'URL est incorrecte.
                <br /><strong>Solution :</strong> Vérifiez que l'URL commence par <code>https://</code>
                et consultez la liste des sites supportés sur <em>github.com/yt-dlp/yt-dlp</em>.
              </div>
            </div>

            <div className="error-entry">
              <div className="error-title">🟡 ffmpeg non disponible</div>
              <div className="error-desc">
                ffmpeg n'est pas installé. Conversion MP3 et vidéos HD non fonctionnelles.
                <br /><strong>Solution :</strong> <code>sudo apt install ffmpeg</code>
              </div>
            </div>

            <h3>Conseils d'utilisation</h3>

            <div className="tip-card">
              <div className="tip-icon">🔄</div>
              <div>
                <strong>Maintenir yt-dlp à jour</strong><br />
                YouTube modifie régulièrement sa structure. Si un site ne fonctionne plus,
                mettez à jour via <strong>Paramètres → Moteur → Mettre à jour yt-dlp</strong>.
              </div>
            </div>

            <div className="tip-card">
              <div className="tip-icon">🛡</div>
              <div>
                <strong>Combo proxy + VPN</strong><br />
                Pour une robustesse maximale : configurez une liste de proxies avec rotation
                <em>et</em> activez le VPN Auto. En cas de blocage bot, le VPN change de pays ;
                en cas d'erreur normale, le proxy rotatif change d'IP.
              </div>
            </div>

            <div className="tip-card">
              <div className="tip-icon">🍪</div>
              <div>
                <strong>Cookies pour le contenu premium</strong><br />
                Pour YouTube Music, contenus membres Patreon/Twitch, ou vidéos privées,
                configurez un fichier cookies via l'extension <em>Get cookies.txt LOCALLY</em>
                (Chrome/Firefox).
              </div>
            </div>

            <div className="tip-card">
              <div className="tip-icon">🌙</div>
              <div>
                <strong>Télécharger la nuit automatiquement</strong><br />
                Ajoutez vos URLs en journée, puis activez le <strong>Mode Nuit tranquille</strong>
                (Paramètres → Planification). Les téléchargements démarreront dans la fenêtre
                horaire configurée sans intervention de votre part.
              </div>
            </div>

            <div className="tip-card">
              <div className="tip-icon">📋</div>
              <div>
                <strong>Récupérer une URL échouée</strong><br />
                Dans le <strong>Tableau de bord → Échoués</strong>, le bouton
                <span className="kbd">📋 Copier URL</span> copie l'URL pour la recoller
                directement dans le formulaire et réessayer avec des paramètres différents.
              </div>
            </div>

            <div className="tip-card">
              <div className="tip-icon">🔍</div>
              <div>
                <strong>1000+ sites supportés</strong><br />
                yt-dlp supporte YouTube, Vimeo, Twitch, Dailymotion, SoundCloud, Bandcamp,
                Arte, France.tv, TikTok, Twitter/X, Instagram, Reddit, et bien d'autres.
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="help-page-footer">
        <span className="help-footer-text">
          Tubor v0.3 — Propulsé par <strong>yt-dlp</strong> &amp; <strong>ffmpeg</strong>
        </span>
        <button className="btn btn-primary" onClick={onClose}>Fermer</button>
      </div>
    </div>
  )
}
