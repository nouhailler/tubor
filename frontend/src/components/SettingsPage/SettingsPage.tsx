import { useState, useEffect } from 'react'
import type { Config, SystemInfo } from '../../types'
import { getSystemInfo, updateYtdlp } from '../../api/system'
import './SettingsPage.css'

interface Props {
  config: Config
  onSave: (patch: Partial<Config>) => void
}

type Tab = 'download' | 'network' | 'vpn' | 'schedule' | 'auth' | 'engine'

const TABS: { id: Tab; icon: string; label: string }[] = [
  { id: 'download', icon: '📥', label: 'Téléchargement' },
  { id: 'network',  icon: '🌐', label: 'Réseau & Proxies' },
  { id: 'vpn',      icon: '🛡',  label: 'VPN Auto' },
  { id: 'schedule', icon: '🌙', label: 'Planification' },
  { id: 'auth',     icon: '🔐', label: 'Authentification' },
  { id: 'engine',   icon: '⚙',  label: 'Moteur' },
]

const VPN_TYPES = [
  { value: 'mullvad',    label: 'Mullvad VPN' },
  { value: 'nordvpn',    label: 'NordVPN' },
  { value: 'protonvpn',  label: 'ProtonVPN' },
  { value: 'expressvpn', label: 'ExpressVPN' },
  { value: 'custom',     label: 'Script personnalisé' },
]

const VPN_CMD_TEMPLATES: Record<string, string> = {
  mullvad:    'mullvad relay set location {country} && mullvad reconnect',
  nordvpn:    'nordvpn disconnect && nordvpn connect {country}',
  protonvpn:  '/usr/bin/protonvpn disconnect && /usr/bin/protonvpn connect --country {COUNTRY}',
  expressvpn: 'expressvpn disconnect && expressvpn connect {country}',
  custom:     '',
}

const POPULAR_COUNTRIES = [
  'US','GB','DE','FR','NL','CA','JP','AU','SE','CH','SG','NO','FI','DK',
]

export default function SettingsPage({ config, onSave }: Props) {
  const [tab, setTab] = useState<Tab>('download')
  const [saved, setSaved] = useState(false)

  // Téléchargement
  const [downloadFolder, setFolder]     = useState(config.download_folder)
  const [format,         setFormat]     = useState(config.format)
  const [quality,        setQuality]    = useState(config.quality)
  const [embedMeta,      setEmbedMeta]  = useState(config.embed_metadata)
  const [embedThumb,     setEmbedThumb] = useState(config.embed_thumbnail)

  // Réseau
  const [proxy,        setProxy]     = useState(config.proxy)
  const [proxyList,    setProxyList] = useState((config.proxy_list ?? []).join('\n'))
  const [proxyRot,     setProxyRot]  = useState(config.proxy_rotation)
  const [maxRetries,   setRetries]   = useState(config.max_retries)
  const [sleepInt,     setSleep]     = useState(config.sleep_interval)
  const [bwLimit,      setBw]        = useState(config.bandwidth_limit)

  // Planification
  const [nightMode,  setNightMode]  = useState(config.night_mode)
  const [nightStart, setNightStart] = useState(config.night_start)
  const [nightEnd,   setNightEnd]   = useState(config.night_end)

  // VPN
  const [vpnEnabled,  setVpnEnabled]  = useState(config.vpn_enabled ?? false)
  const [vpnType,     setVpnType]     = useState(config.vpn_type ?? 'mullvad')
  const [vpnCountries,setVpnCountries]= useState((config.vpn_countries ?? []).join('\n'))
  const [vpnCustomCmd,setVpnCustomCmd]= useState(config.vpn_custom_cmd ?? '')
  const [vpnDelay,    setVpnDelay]    = useState(config.vpn_reconnect_delay ?? 5)

  // Auth
  const [cookiesFile, setCookies] = useState(config.cookies_file)

  // Moteur
  const [sysInfo,    setSysInfo]   = useState<SystemInfo | null>(null)
  const [updateMsg,  setUpdateMsg] = useState('')
  const [updating,   setUpdating]  = useState(false)

  useEffect(() => {
    getSystemInfo().then(setSysInfo).catch(() => {})
  }, [])

  const handleSave = () => {
    onSave({
      download_folder:  downloadFolder,
      format, quality,
      embed_metadata:   embedMeta,
      embed_thumbnail:  embedThumb,
      proxy,
      proxy_list:       proxyList.split('\n').map((p: string) => p.trim()).filter(Boolean),
      proxy_rotation:   proxyRot,
      max_retries:      maxRetries,
      sleep_interval:   sleepInt,
      bandwidth_limit:  bwLimit,
      night_mode:       nightMode,
      night_start:      nightStart,
      night_end:        nightEnd,
      cookies_file:     cookiesFile,
      vpn_enabled:      vpnEnabled,
      vpn_type:         vpnType,
      vpn_countries:    vpnCountries.split('\n').map((c: string) => c.trim().toUpperCase()).filter(Boolean),
      vpn_custom_cmd:   vpnCustomCmd,
      vpn_reconnect_delay: vpnDelay,
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleUpdate = async () => {
    setUpdating(true); setUpdateMsg('')
    try {
      const r = await updateYtdlp()
      setUpdateMsg(r.message)
      if (r.success) setSysInfo(await getSystemInfo())
    } catch (e) {
      setUpdateMsg(e instanceof Error ? e.message : 'Erreur')
    } finally {
      setUpdating(false)
    }
  }

  return (
    <div className="settings-page">
      {/* ── Sidebar ───────────────────────────────────────────────────────── */}
      <nav className="settings-sidebar">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`settings-nav-btn ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            <span className="snav-icon">{t.icon}</span>
            <span className="snav-label">{t.label}</span>
          </button>
        ))}
      </nav>

      {/* ── Contenu ───────────────────────────────────────────────────────── */}
      <div className="settings-body">
        <div className="settings-content">

          {/* ── Téléchargement ────────────────────────────────────────────── */}
          {tab === 'download' && (
            <>
              <h2 className="settings-section-title">📥 Téléchargement</h2>

              <div className="settings-field">
                <label className="settings-label">Dossier de destination</label>
                <input
                  type="text"
                  className="input"
                  value={downloadFolder}
                  onChange={e => setFolder(e.target.value)}
                  placeholder="~/Downloads"
                />
                <p className="settings-hint">Dossier où seront enregistrés tous les fichiers téléchargés.</p>
              </div>

              <div className="settings-row-2">
                <div className="settings-field">
                  <label className="settings-label">Format préféré</label>
                  <select className="input select" value={format} onChange={e => setFormat(e.target.value)}>
                    <option value="video">🎬 Vidéo (MP4)</option>
                    <option value="audio">🎵 Audio (MP3)</option>
                  </select>
                </div>
                <div className="settings-field">
                  <label className="settings-label">Qualité préférée</label>
                  <select className="input select" value={quality} onChange={e => setQuality(e.target.value)}>
                    {(format === 'video'
                      ? ['best', '1080p', '720p', '480p', '360p']
                      : ['best', 'mp3_320', 'mp3_192', 'mp3_128']
                    ).map(q => <option key={q} value={q}>{q}</option>)}
                  </select>
                </div>
              </div>

              <div className="settings-field">
                <label className="settings-label">Options post-traitement <span className="settings-badge">ffmpeg</span></label>
                <div className="settings-checks">
                  <label className="checkbox-label">
                    <input type="checkbox" checked={embedMeta} onChange={e => setEmbedMeta(e.target.checked)} />
                    Intégrer les métadonnées (titre, artiste, album…)
                  </label>
                  <label className="checkbox-label">
                    <input type="checkbox" checked={embedThumb} onChange={e => setEmbedThumb(e.target.checked)} />
                    Intégrer la miniature dans le fichier
                  </label>
                </div>
              </div>
            </>
          )}

          {/* ── Réseau & Proxies ──────────────────────────────────────────── */}
          {tab === 'network' && (
            <>
              <h2 className="settings-section-title">🌐 Réseau & Proxies</h2>

              <div className="settings-info-box">
                <strong>Pourquoi utiliser un proxy ?</strong>
                <p>
                  YouTube détecte les téléchargements répétés depuis la même IP et peut bloquer
                  votre connexion (HTTP 429/403). Un proxy résidentiel rotatif contourne ces limitations
                  et évite les interruptions.
                </p>
              </div>

              <div className="settings-field">
                <label className="settings-label">Proxy unique</label>
                <input
                  type="text"
                  className="input"
                  value={proxy}
                  placeholder="http://user:pass@host:8080 ou socks5://host:1080"
                  onChange={e => setProxy(e.target.value)}
                />
                <p className="settings-hint">
                  Formats acceptés : <code>http://host:port</code>, <code>http://host:port:user:pass</code>,
                  <code> socks5://host:port</code>
                </p>
              </div>

              <div className="settings-field">
                <label className="settings-label">
                  Liste de proxies
                  <span className="settings-badge">rotation</span>
                </label>
                <textarea
                  className="input proxy-textarea"
                  value={proxyList}
                  placeholder={
                    'http://31.50.28.176:8754:username:password\n' +
                    'socks5://45.12.33.100:1080:user2:pass2\n' +
                    'http://proxy3:8080'
                  }
                  onChange={e => setProxyList(e.target.value)}
                  rows={6}
                />
                <p className="settings-hint">
                  Un proxy par ligne. Format court accepté : <code>http://IP:PORT:USER:PASS</code><br />
                  Le backend convertit automatiquement en <code>http://USER:PASS@IP:PORT</code> pour yt-dlp.
                </p>
              </div>

              <div className="settings-field">
                <label className="checkbox-label large">
                  <input type="checkbox" checked={proxyRot} onChange={e => setProxyRot(e.target.checked)} />
                  <span>
                    <strong>Rotation automatique</strong>
                    <small>Change de proxy à chaque nouveau téléchargement (round-robin)</small>
                  </span>
                </label>
              </div>

              <div className="settings-row-3">
                <div className="settings-field">
                  <label className="settings-label">Tentatives max</label>
                  <input
                    type="number"
                    className="input"
                    min={0} max={10}
                    value={maxRetries}
                    onChange={e => setRetries(Number(e.target.value))}
                  />
                  <p className="settings-hint">0 = aucun retry. Backoff exponentiel : 10s, 20s, 40s…</p>
                </div>
                <div className="settings-field">
                  <label className="settings-label">Pause entre requêtes (s)</label>
                  <input
                    type="number"
                    className="input"
                    min={0} max={60}
                    value={sleepInt}
                    onChange={e => setSleep(Number(e.target.value))}
                  />
                  <p className="settings-hint">0 = désactivé. Recommandé : 3-5s.</p>
                </div>
                <div className="settings-field">
                  <label className="settings-label">Limite de bande passante</label>
                  <input
                    type="text"
                    className="input"
                    value={bwLimit}
                    placeholder="ex: 2M ou 500K"
                    onChange={e => setBw(e.target.value)}
                  />
                  <p className="settings-hint">Vide = illimité. Unités : K, M, G.</p>
                </div>
              </div>
            </>
          )}

          {/* ── VPN Auto ─────────────────────────────────────────────────── */}
          {tab === 'vpn' && (
            <>
              <h2 className="settings-section-title">🛡 VPN — Rotation automatique de pays</h2>

              <div className="settings-info-box">
                <strong>Pourquoi c'est efficace contre les blocages YouTube</strong>
                <p>
                  Lorsque YouTube détecte un bot (<em>"Sign in to confirm you're not a bot"</em>),
                  Tubor peut automatiquement changer de pays VPN et relancer le téléchargement.
                  Chaque pays donne une nouvelle IP, contournant le blocage.
                </p>
              </div>

              <div className="settings-field">
                <label className="checkbox-label large">
                  <input type="checkbox" checked={vpnEnabled} onChange={e => setVpnEnabled(e.target.checked)} />
                  <span>
                    <strong>Activer la rotation VPN automatique</strong>
                    <small>Sur détection de bot, Tubor change de pays et réessaie automatiquement</small>
                  </span>
                </label>
              </div>

              {vpnEnabled && (
                <>
                  <div className="settings-row-2">
                    <div className="settings-field">
                      <label className="settings-label">Client VPN installé</label>
                      <select
                        className="input select"
                        value={vpnType}
                        onChange={e => setVpnType(e.target.value)}
                      >
                        {VPN_TYPES.map(v => (
                          <option key={v.value} value={v.value}>{v.label}</option>
                        ))}
                      </select>
                      <p className="settings-hint">
                        Le client VPN doit être installé et accessible en ligne de commande.
                      </p>
                    </div>
                    <div className="settings-field">
                      <label className="settings-label">Délai de reconnexion (s)</label>
                      <input
                        type="number"
                        className="input"
                        min={2} max={30}
                        value={vpnDelay}
                        onChange={e => setVpnDelay(Number(e.target.value))}
                      />
                      <p className="settings-hint">Temps d'attente après le changement de pays (5s recommandé).</p>
                    </div>
                  </div>

                  <div className="settings-field">
                    <label className="settings-label">
                      Commande de changement de pays
                      {vpnType !== 'custom' && (
                        <span className="settings-badge">auto-rempli</span>
                      )}
                    </label>
                    <input
                      type="text"
                      className="input"
                      value={vpnType === 'custom' ? vpnCustomCmd : (VPN_CMD_TEMPLATES[vpnType] || '')}
                      onChange={e => setVpnCustomCmd(e.target.value)}
                      placeholder="ex: /usr/bin/protonvpn disconnect && /usr/bin/protonvpn connect --country {COUNTRY}"
                      readOnly={vpnType !== 'custom'}
                    />
                    <p className="settings-hint">
                      <code>{'{country}'}</code> = code ISO minuscule (us, gb…) ·{' '}
                      <code>{'{COUNTRY}'}</code> = majuscule (US, GB…)
                    </p>
                  </div>

                  <div className="settings-field">
                    <label className="settings-label">
                      Pays de rotation
                      <span className="settings-badge">{vpnCountries.split('\n').filter(c => c.trim()).length} pays</span>
                    </label>
                    <div className="vpn-countries-quick">
                      {POPULAR_COUNTRIES.map(cc => {
                        const active = vpnCountries.toUpperCase().split('\n').map(c => c.trim()).includes(cc)
                        return (
                          <button
                            key={cc}
                            type="button"
                            className={`country-chip ${active ? 'active' : ''}`}
                            onClick={() => {
                              const list = vpnCountries.split('\n').map(c => c.trim().toUpperCase()).filter(Boolean)
                              const next = active
                                ? list.filter(c => c !== cc)
                                : [...list, cc]
                              setVpnCountries(next.join('\n'))
                            }}
                            title={cc}
                          >
                            {String.fromCodePoint(0x1F1E6 - 65 + cc.charCodeAt(0)) +
                             String.fromCodePoint(0x1F1E6 - 65 + cc.charCodeAt(1))} {cc}
                          </button>
                        )
                      })}
                    </div>
                    <textarea
                      className="input proxy-textarea"
                      value={vpnCountries}
                      placeholder={'US\nGB\nDE\nFR\nNL'}
                      onChange={e => setVpnCountries(e.target.value)}
                      rows={4}
                    />
                    <p className="settings-hint">Un code pays ISO par ligne. Rotation round-robin à chaque détection de bot.</p>
                  </div>

                  <div className="settings-info-box">
                    <strong>Flux de retry automatique</strong>
                    <p>
                      1. YouTube détecte un bot → Tubor marque l'erreur<br />
                      2. Appel de la commande VPN avec le prochain pays<br />
                      3. Attente {vpnDelay}s (reconnexion VPN)<br />
                      4. Relance du téléchargement depuis la nouvelle IP<br />
                      5. Répété jusqu'à {'{max_retries}'} tentatives (réglable dans <em>Réseau</em>)
                    </p>
                  </div>
                </>
              )}
            </>
          )}

          {/* ── Planification ─────────────────────────────────────────────── */}
          {tab === 'schedule' && (
            <>
              <h2 className="settings-section-title">🌙 Planification</h2>

              <div className="settings-field">
                <label className="checkbox-label large">
                  <input type="checkbox" checked={nightMode} onChange={e => setNightMode(e.target.checked)} />
                  <span>
                    <strong>Mode Nuit tranquille</strong>
                    <small>
                      Les téléchargements en file démarrent uniquement dans la fenêtre horaire ci-dessous.
                      Utile pour ne pas saturer la connexion en journée.
                    </small>
                  </span>
                </label>
              </div>

              {nightMode && (
                <div className="settings-field">
                  <label className="settings-label">Fenêtre horaire</label>
                  <div className="night-window">
                    <div className="night-part">
                      <label className="settings-label small">Début</label>
                      <div className="night-time-row">
                        <input
                          type="number"
                          className="input time-input"
                          min={0} max={23}
                          value={nightStart}
                          onChange={e => setNightStart(Number(e.target.value))}
                        />
                        <span className="time-unit">h</span>
                      </div>
                    </div>
                    <span className="night-arrow">→</span>
                    <div className="night-part">
                      <label className="settings-label small">Fin</label>
                      <div className="night-time-row">
                        <input
                          type="number"
                          className="input time-input"
                          min={0} max={23}
                          value={nightEnd}
                          onChange={e => setNightEnd(Number(e.target.value))}
                        />
                        <span className="time-unit">h</span>
                      </div>
                    </div>
                  </div>
                  <p className="settings-hint">
                    Actuellement configuré : {nightStart}h00 → {nightEnd}h00.
                    Fonctionne aussi en fenêtre qui enjambe minuit (ex: 22h → 6h).
                  </p>
                </div>
              )}

              <div className="settings-info-box">
                <strong>Planification par téléchargement</strong>
                <p>
                  Vous pouvez aussi programmer un téléchargement à une heure précise directement
                  depuis le formulaire en cochant <em>⏱ Planifier</em> avant de cliquer Télécharger.
                </p>
              </div>
            </>
          )}

          {/* ── Auth ──────────────────────────────────────────────────────── */}
          {tab === 'auth' && (
            <>
              <h2 className="settings-section-title">🔐 Authentification</h2>

              <div className="settings-field">
                <label className="settings-label">Fichier cookies (.txt)</label>
                <input
                  type="text"
                  className="input"
                  value={cookiesFile}
                  placeholder="~/.config/tubor/cookies.txt"
                  onChange={e => setCookies(e.target.value)}
                />
                <p className="settings-hint">
                  Chemin absolu vers un fichier cookies au format Netscape.<br />
                  Nécessaire pour les vidéos privées, membres, ou restreintes par l'âge.
                </p>
              </div>

              <div className="settings-info-box">
                <strong>Comment exporter vos cookies ?</strong>
                <p>
                  Installez l'extension <em>Get cookies.txt LOCALLY</em> (Chrome/Firefox),
                  connectez-vous à YouTube, puis exportez le fichier. Enregistrez-le dans
                  <code> ~/.config/tubor/cookies.txt</code> et renseignez ce chemin ci-dessus.
                </p>
              </div>
            </>
          )}

          {/* ── Moteur ────────────────────────────────────────────────────── */}
          {tab === 'engine' && (
            <>
              <h2 className="settings-section-title">⚙ Moteur yt-dlp</h2>

              <div className="settings-engine-card">
                <div className="engine-row">
                  <span className="engine-key">Version yt-dlp</span>
                  <strong className="engine-val">{sysInfo?.ytdlp_version ?? '…'}</strong>
                </div>
                <div className="engine-row">
                  <span className="engine-key">ffmpeg disponible</span>
                  <strong className={`engine-val ${sysInfo?.ffmpeg_available ? 'ok' : 'nok'}`}>
                    {sysInfo === null ? '…' : sysInfo.ffmpeg_available ? '✔ Oui' : '✗ Non'}
                  </strong>
                </div>
              </div>

              <button
                className="btn btn-secondary"
                onClick={handleUpdate}
                disabled={updating}
                style={{ alignSelf: 'flex-start' }}
              >
                {updating ? '⏳ Mise à jour en cours…' : '⬆ Mettre à jour yt-dlp'}
              </button>
              {updateMsg && <p className="update-msg">{updateMsg}</p>}

              <div className="settings-info-box">
                <strong>Options de robustesse actives</strong>
                <p>
                  Chaque téléchargement utilise automatiquement :<br />
                  <code>--retries 5 --fragment-retries 5 --socket-timeout 30 --extractor-retries 3</code>
                </p>
              </div>
            </>
          )}
        </div>

        {/* ── Footer sauvegarde ─────────────────────────────────────────────── */}
        <div className="settings-footer">
          <button className="btn btn-primary save-btn" onClick={handleSave}>
            {saved ? '✔ Enregistré !' : '💾 Enregistrer les paramètres'}
          </button>
        </div>
      </div>
    </div>
  )
}
