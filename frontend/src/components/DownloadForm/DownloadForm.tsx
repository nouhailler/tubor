import { useState, useCallback, useRef } from 'react'
import type { Config, AddDownloadRequest, PreviewInfo } from '../../types'
import { getPreview } from '../../api/preview'
import PreviewModal from '../PreviewModal/PreviewModal'
import './DownloadForm.css'

const VIDEO_QUALITIES = ['best', '1080p', '720p', '480p', '360p']
const AUDIO_QUALITIES = ['best', 'mp3_320', 'mp3_192', 'mp3_128']
const QUALITY_LABELS: Record<string, string> = {
  best: 'Meilleure qualité', '1080p': '1080p (Full HD)', '720p': '720p (HD)',
  '480p': '480p (SD)', '360p': '360p (Basse)', mp3_320: 'MP3 320 kbps',
  mp3_192: 'MP3 192 kbps', mp3_128: 'MP3 128 kbps',
}

interface Props {
  config: Config | null
  onAdd: (req: AddDownloadRequest) => Promise<unknown>
  onConfigPatch: (patch: Partial<Config>) => void
}

/** Extrait toutes les URLs valides depuis un texte brut (collé ou tapé). */
function extractUrls(text: string): string[] {
  return text
    .split(/[\n\r]+/)
    .map(l => l.trim())
    .filter(l => /^https?:\/\//i.test(l))
}

export default function DownloadForm({ config, onAdd, onConfigPatch }: Props) {
  const [urlText,       setUrlText]      = useState('')
  const [format,        setFormat]       = useState(config?.format ?? 'video')
  const [quality,       setQuality]      = useState(config?.quality ?? 'best')
  const [outputFolder,  setOutputFolder] = useState(config?.download_folder ?? '')
  const [playlistMode,  setPlaylistMode] = useState(config?.playlist_mode ?? 'single')
  const [playlistLimit, setLimit]        = useState(config?.playlist_limit ?? 0)
  const [scheduled,     setScheduled]    = useState(false)
  const [scheduledAt,   setScheduledAt]  = useState('')
  const [loading,       setLoading]      = useState(false)
  const [previewing,    setPreviewing]   = useState(false)
  const [preview,       setPreview]      = useState<PreviewInfo | null>(null)
  const [error,         setError]        = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const qualities = format === 'audio' ? AUDIO_QUALITIES : VIDEO_QUALITIES
  const urls = extractUrls(urlText)
  const isMulti = urls.length > 1
  const firstUrl = urls[0] ?? ''

  const proxyConfigured = !!(config?.proxy || (config?.proxy_list?.length ?? 0) > 0)
  const proxyOn = proxyConfigured && (config?.proxy_enabled ?? true)
  const vpnConfigured = !!(config?.vpn_countries?.length ?? 0)
  const vpnOn = !!(config?.vpn_enabled)
  const toggleProxy = () => onConfigPatch({ proxy_enabled: !proxyOn })
  const toggleVpn = () => onConfigPatch({ vpn_enabled: !vpnOn })

  const handleFormatChange = (f: string) => {
    setFormat(f)
    if (!(f === 'audio' ? AUDIO_QUALITIES : VIDEO_QUALITIES).includes(quality))
      setQuality('best')
  }

  /** Coller depuis le presse-papiers, normaliser les lignes */
  const handlePaste = useCallback(async () => {
    try {
      const text = (await navigator.clipboard.readText()).trim()
      // Normaliser : remplacer séparateurs multiples (espace, virgule) par sauts de ligne
      const normalized = text
        .split(/[\n\r]+/)
        .flatMap(line => line.split(/[,\s]+/))
        .map(s => s.trim())
        .filter(Boolean)
        .join('\n')
      setUrlText(normalized)
    } catch { /* denied */ }
  }, [])

  /** Normaliser à la saisie (éviter les lignes vides multiples) */
  const handleUrlChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUrlText(e.target.value)
    setError('')
  }

  const buildRequest = (url: string, overrideFormat?: string, overrideQuality?: string): AddDownloadRequest => ({
    url: url.trim(),
    format:         overrideFormat  ?? format,
    quality:        overrideQuality ?? quality,
    output_folder:  outputFolder || config?.download_folder || '',
    playlist_mode:  playlistMode,
    playlist_limit: playlistLimit,
    embed_metadata:  config?.embed_metadata  ?? true,
    embed_thumbnail: config?.embed_thumbnail ?? true,
    cookies_file:    config?.cookies_file    ?? '',
    scheduled_at:    scheduled && scheduledAt
      ? new Date(scheduledAt).getTime() / 1000
      : 0,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (urls.length === 0) {
      setError('Veuillez saisir au moins une URL valide (http:// ou https://).')
      return
    }

    setLoading(true)
    try {
      for (const url of urls) {
        await onAdd(buildRequest(url))
      }
      setUrlText('')
      setScheduled(false)
      setScheduledAt('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue')
    } finally {
      setLoading(false)
    }
  }

  const handlePreview = async () => {
    if (!firstUrl) {
      setError('Saisissez une URL valide avant de prévisualiser.')
      return
    }
    setError('')
    setPreviewing(true)
    try {
      const data = await getPreview(firstUrl)
      setPreview(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Impossible de récupérer les métadonnées')
    } finally {
      setPreviewing(false)
    }
  }

  return (
    <>
      <form className="download-form" onSubmit={handleSubmit}>
        {/* URL(s) */}
        <div className="form-row url-row">
          <div className="url-textarea-wrap">
            <textarea
              ref={textareaRef}
              className="input url-textarea"
              placeholder={'https://youtube.com/watch?v=...\nhttps://youtube.com/watch?v=...\n(collez autant d\'URLs que vous voulez, une par ligne)'}
              value={urlText}
              onChange={handleUrlChange}
              aria-label="URL(s) à télécharger"
              spellCheck={false}
            />
            {isMulti && (
              <span className="url-count-badge">{urls.length} URLs</span>
            )}
          </div>
          <div className="url-btns">
            <button type="button" className="btn btn-ghost icon-pad" onClick={handlePaste} title="Coller">📋</button>
            <button
              type="button"
              className="btn btn-ghost preview-btn"
              onClick={handlePreview}
              disabled={previewing || !firstUrl}
              title={isMulti ? 'Prévisualiser la première URL' : 'Prévisualiser'}
            >
              {previewing ? '⏳' : '🔍'}
            </button>
          </div>
        </div>

        {error && <p className="form-error">{error}</p>}

        {/* Format + Qualité + Playlist */}
        <div className="form-row options-row">
          <div className="toggle-group">
            <button type="button" className={`toggle-btn ${format === 'video' ? 'active' : ''}`} onClick={() => handleFormatChange('video')}>
              🎬 Vidéo
            </button>
            <button type="button" className={`toggle-btn ${format === 'audio' ? 'active' : ''}`} onClick={() => handleFormatChange('audio')}>
              🎵 Audio
            </button>
          </div>

          <select className="input select" value={quality} onChange={e => setQuality(e.target.value)}>
            {qualities.map(q => <option key={q} value={q}>{QUALITY_LABELS[q]}</option>)}
          </select>

          <div className="toggle-group">
            <button type="button" className={`toggle-btn ${playlistMode === 'single' ? 'active' : ''}`} onClick={() => setPlaylistMode('single')}>
              Vidéo seule
            </button>
            <button type="button" className={`toggle-btn ${playlistMode === 'all' ? 'active' : ''}`} onClick={() => setPlaylistMode('all')}>
              Playlist
            </button>
          </div>

          {playlistMode === 'all' && (
            <input
              type="number"
              className="input limit-input"
              min={0} value={playlistLimit}
              onChange={e => setLimit(Number(e.target.value))}
              placeholder="Limite (0=∞)"
            />
          )}
        </div>

        {/* Dossier */}
        <div className="form-row folder-row">
          <span className="folder-label">📁</span>
          <input
            type="text"
            className="input folder-input"
            placeholder={config?.download_folder ?? '~/Downloads'}
            value={outputFolder}
            onChange={e => setOutputFolder(e.target.value)}
          />
        </div>

        {/* Planification */}
        <div className="form-row schedule-row">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={scheduled}
              onChange={e => setScheduled(e.target.checked)}
            />
            ⏱ Planifier
          </label>
          {scheduled && (
            <input
              type="datetime-local"
              className="input schedule-input"
              value={scheduledAt}
              onChange={e => setScheduledAt(e.target.value)}
              min={new Date().toISOString().slice(0, 16)}
            />
          )}
        </div>

        {/* Boutons Proxy / VPN rapides */}
        <div className="form-row quick-toggles">
          <button
            type="button"
            className={`toggle-pill ${proxyOn ? 'on' : 'off'}`}
            onClick={toggleProxy}
            disabled={!proxyConfigured}
            title={!proxyConfigured ? 'Aucun proxy configuré dans les Paramètres' : proxyOn ? 'Proxy actif — cliquer pour désactiver' : 'Proxy inactif — cliquer pour activer'}
          >
            🌐 Proxy {proxyOn ? 'ON' : 'OFF'}
          </button>
          <button
            type="button"
            className={`toggle-pill ${vpnOn ? 'on' : 'off'}`}
            onClick={toggleVpn}
            disabled={!vpnConfigured}
            title={!vpnConfigured ? 'Aucun pays VPN configuré dans les Paramètres' : vpnOn ? 'VPN actif — cliquer pour désactiver' : 'VPN inactif — cliquer pour activer'}
          >
            🛡 VPN {vpnOn ? 'ON' : 'OFF'}
          </button>
        </div>

        {/* Bouton */}
        <button type="submit" className="btn btn-primary download-btn" disabled={loading || urls.length === 0}>
          {loading
            ? 'Ajout en cours…'
            : isMulti
              ? `⬇ TÉLÉCHARGER ${urls.length} VIDÉOS`
              : scheduled && scheduledAt
                ? '⏱ PLANIFIER'
                : '⬇ TÉLÉCHARGER'
          }
        </button>
      </form>

      {preview && (
        <PreviewModal
          preview={preview}
          config={config}
          onDownload={(f, q) => { setFormat(f); setQuality(q); onAdd(buildRequest(firstUrl, f, q)) }}
          onClose={() => setPreview(null)}
        />
      )}
    </>
  )
}
