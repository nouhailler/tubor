import { useState, useEffect } from 'react'
import type { Config, SystemInfo } from '../../types'
import { getSystemInfo, updateYtdlp } from '../../api/system'
import './SettingsModal.css'

interface Props {
  config: Config
  onSave: (patch: Partial<Config>) => void
  onClose: () => void
}

type Tab = 'download' | 'network' | 'schedule' | 'auth' | 'engine'

export default function SettingsModal({ config, onSave, onClose }: Props) {
  const [tab, setTab] = useState<Tab>('download')

  // Téléchargement
  const [downloadFolder,  setFolder]     = useState(config.download_folder)
  const [format,          setFormat]     = useState(config.format)
  const [quality,         setQuality]    = useState(config.quality)
  const [embedMeta,       setEmbedMeta]  = useState(config.embed_metadata)
  const [embedThumb,      setEmbedThumb] = useState(config.embed_thumbnail)

  // Réseau
  const [proxy,           setProxy]      = useState(config.proxy)
  const [proxyList,       setProxyList]  = useState((config.proxy_list ?? []).join('\n'))
  const [proxyRot,        setProxyRot]   = useState(config.proxy_rotation)
  const [maxRetries,      setMaxRetries] = useState(config.max_retries)
  const [sleepInterval,   setSleep]      = useState(config.sleep_interval)
  const [bwLimit,         setBw]         = useState(config.bandwidth_limit)

  // Planification
  const [nightMode,       setNightMode]  = useState(config.night_mode)
  const [nightStart,      setNightStart] = useState(config.night_start)
  const [nightEnd,        setNightEnd]   = useState(config.night_end)

  // Auth
  const [cookiesFile,     setCookies]    = useState(config.cookies_file)

  // Moteur
  const [sysInfo,         setSysInfo]    = useState<SystemInfo | null>(null)
  const [updateMsg,       setUpdateMsg]  = useState('')
  const [updating,        setUpdating]   = useState(false)

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
      proxy_list:       proxyList.split('\n').map(p => p.trim()).filter(Boolean),
      proxy_rotation:   proxyRot,
      max_retries:      maxRetries,
      sleep_interval:   sleepInterval,
      bandwidth_limit:  bwLimit,
      night_mode:       nightMode,
      night_start:      nightStart,
      night_end:        nightEnd,
      cookies_file:     cookiesFile,
    })
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

  const TABS: { id: Tab; label: string }[] = [
    { id: 'download', label: '📥 Téléchargement' },
    { id: 'network',  label: '🌐 Réseau & Proxies' },
    { id: 'schedule', label: '🌙 Planification' },
    { id: 'auth',     label: '🔐 Auth' },
    { id: 'engine',   label: '⚙ Moteur' },
  ]

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Paramètres</h2>
          <button className="icon-btn" onClick={onClose}>✕</button>
        </div>

        <div className="modal-tabs">
          {TABS.map(t => (
            <button key={t.id} className={`tab-btn ${tab === t.id ? 'active' : ''}`}
              onClick={() => setTab(t.id)}>{t.label}</button>
          ))}
        </div>

        <div className="modal-body">

          {/* ── Téléchargement ─────────────────────────────────────── */}
          {tab === 'download' && (
            <div className="tab-content">
              <label className="field-label">Dossier par défaut</label>
              <input type="text" className="input" value={downloadFolder} onChange={e => setFolder(e.target.value)} />

              <label className="field-label">Format préféré</label>
              <select className="input select" value={format} onChange={e => setFormat(e.target.value)}>
                <option value="video">Vidéo (MP4)</option>
                <option value="audio">Audio (MP3)</option>
              </select>

              <label className="field-label">Qualité préférée</label>
              <select className="input select" value={quality} onChange={e => setQuality(e.target.value)}>
                {(format === 'video'
                  ? ['best','1080p','720p','480p','360p']
                  : ['best','mp3_320','mp3_192','mp3_128']
                ).map(q => <option key={q} value={q}>{q}</option>)}
              </select>

              <label className="checkbox-label">
                <input type="checkbox" checked={embedMeta} onChange={e => setEmbedMeta(e.target.checked)} />
                Intégrer les métadonnées (requiert ffmpeg)
              </label>
              <label className="checkbox-label">
                <input type="checkbox" checked={embedThumb} onChange={e => setEmbedThumb(e.target.checked)} />
                Intégrer la miniature (requiert ffmpeg)
              </label>
            </div>
          )}

          {/* ── Réseau & Proxies ───────────────────────────────────── */}
          {tab === 'network' && (
            <div className="tab-content">
              <div className="settings-info">
                <strong>Pourquoi utiliser un proxy ?</strong><br />
                YouTube détecte les téléchargements répétés depuis la même IP et peut bloquer
                votre connexion (HTTP 403/429) ou corrompre les réponses, ce qui provoque des
                plantages. Un proxy résidentiel rotatif contourne ces limitations.
              </div>

              <label className="field-label">Proxy unique</label>
              <input type="text" className="input" value={proxy}
                placeholder="http://user:pass@host:8080 ou socks5://host:1080"
                onChange={e => setProxy(e.target.value)} />
              <p className="hint">Formats supportés : http://, https://, socks5://, socks4://</p>

              <label className="field-label">Liste de proxies (un par ligne)</label>
              <textarea className="input proxy-textarea" value={proxyList}
                placeholder={"http://proxy1:8080\nhttp://proxy2:8080\nsocks5://proxy3:1080"}
                onChange={e => setProxyList(e.target.value)} rows={4}
              />

              <label className="checkbox-label">
                <input type="checkbox" checked={proxyRot} onChange={e => setProxyRot(e.target.checked)} />
                Rotation automatique (change de proxy à chaque téléchargement)
              </label>

              <div className="field-row">
                <div>
                  <label className="field-label">Tentatives max</label>
                  <input type="number" className="input short-input" min={0} max={10}
                    value={maxRetries} onChange={e => setMaxRetries(Number(e.target.value))} />
                  <p className="hint">0 = aucun retry. Retry exponentiel : 10s, 20s, 40s…</p>
                </div>
                <div>
                  <label className="field-label">Pause entre requêtes (s)</label>
                  <input type="number" className="input short-input" min={0} max={60}
                    value={sleepInterval} onChange={e => setSleep(Number(e.target.value))} />
                  <p className="hint">0 = désactivé. Recommandé : 3-5s pour éviter les bans.</p>
                </div>
              </div>

              <label className="field-label">Limite de bande passante</label>
              <input type="text" className="input" value={bwLimit}
                placeholder="Ex: 2M (2 MB/s), 500K (500 KB/s), vide = illimité"
                onChange={e => setBw(e.target.value)} />
            </div>
          )}

          {/* ── Planification ──────────────────────────────────────── */}
          {tab === 'schedule' && (
            <div className="tab-content">
              <label className="checkbox-label">
                <input type="checkbox" checked={nightMode} onChange={e => setNightMode(e.target.checked)} />
                <span>
                  <strong>Mode Nuit tranquille</strong><br />
                  <small>Les téléchargements ne démarrent que pendant la fenêtre nocturne définie ci-dessous.</small>
                </span>
              </label>

              {nightMode && (
                <div className="night-window">
                  <div>
                    <label className="field-label">Heure de début</label>
                    <input type="number" className="input short-input" min={0} max={23}
                      value={nightStart} onChange={e => setNightStart(Number(e.target.value))} />
                    <span className="hint-inline">h</span>
                  </div>
                  <div className="night-sep">→</div>
                  <div>
                    <label className="field-label">Heure de fin</label>
                    <input type="number" className="input short-input" min={0} max={23}
                      value={nightEnd} onChange={e => setNightEnd(Number(e.target.value))} />
                    <span className="hint-inline">h</span>
                  </div>
                </div>
              )}

              <div className="settings-info">
                <strong>Planification individuelle</strong><br />
                Vous pouvez aussi programmer un téléchargement à une heure précise directement
                depuis le formulaire en cochant <em>⏱ Planifier</em> avant de cliquer Télécharger.
              </div>
            </div>
          )}

          {/* ── Auth ───────────────────────────────────────────────── */}
          {tab === 'auth' && (
            <div className="tab-content">
              <label className="field-label">Fichier cookies (.txt)</label>
              <input type="text" className="input" value={cookiesFile}
                placeholder="~/.config/tubor/cookies.txt"
                onChange={e => setCookies(e.target.value)} />
              <p className="hint">
                Pour les vidéos privées, membres ou restreintes par l'âge.
                Utilisez l'extension <em>Get cookies.txt LOCALLY</em> pour exporter depuis votre navigateur.
              </p>
            </div>
          )}

          {/* ── Moteur ─────────────────────────────────────────────── */}
          {tab === 'engine' && (
            <div className="tab-content">
              <div className="engine-info">
                <div className="engine-row">
                  <span>Version yt-dlp</span>
                  <strong>{sysInfo?.ytdlp_version ?? '…'}</strong>
                </div>
                <div className="engine-row">
                  <span>ffmpeg disponible</span>
                  <strong className={sysInfo?.ffmpeg_available ? 'ok' : 'nok'}>
                    {sysInfo === null ? '…' : sysInfo.ffmpeg_available ? 'Oui' : 'Non'}
                  </strong>
                </div>
              </div>
              <button className="btn btn-secondary" onClick={handleUpdate} disabled={updating}>
                {updating ? 'Mise à jour…' : 'Mettre à jour yt-dlp'}
              </button>
              {updateMsg && <p className="update-msg">{updateMsg}</p>}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Annuler</button>
          <button className="btn btn-primary" onClick={handleSave}>Enregistrer</button>
        </div>
      </div>
    </div>
  )
}
