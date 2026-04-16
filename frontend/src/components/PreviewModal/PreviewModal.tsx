import { useState } from 'react'
import type { PreviewInfo, Config } from '../../types'
import './PreviewModal.css'

interface Props {
  preview: PreviewInfo
  config: Config | null
  onDownload: (format: 'video' | 'audio', quality: string) => void
  onClose: () => void
}

function fmtViews(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M vues`
  if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}k vues`
  return `${n} vues`
}

function fmtDate(d: string): string {
  // "20240115" → "15/01/2024"
  if (!d || d.length < 8) return d || ''
  return `${d.slice(6, 8)}/${d.slice(4, 6)}/${d.slice(0, 4)}`
}

function fmtBytes(b: number): string {
  if (!b) return '?'
  const u = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (b >= 1024 && i < u.length - 1) { b /= 1024; i++ }
  return `${b.toFixed(0)} ${u[i]}`
}

export default function PreviewModal({ preview, config, onDownload, onClose }: Props) {
  const [showEmbed,    setShowEmbed]    = useState(false)
  const [selFormat,    setSelFormat]    = useState<'video' | 'audio'>('video')
  const [selQuality,   setSelQuality]   = useState(config?.quality ?? 'best')
  const [showFormats,  setShowFormats]  = useState(false)

  const videoQualities = ['best', '1080p', '720p', '480p', '360p']
  const audioQualities = ['best', 'mp3_320', 'mp3_192', 'mp3_128']
  const qualityLabels: Record<string, string> = {
    best: 'Meilleure qualité', '1080p': '1080p Full HD', '720p': '720p HD',
    '480p': '480p', '360p': '360p', mp3_320: 'MP3 320 kbps',
    mp3_192: 'MP3 192 kbps', mp3_128: 'MP3 128 kbps',
  }

  const handleFormatChange = (f: 'video' | 'audio') => {
    setSelFormat(f)
    setSelQuality('best')
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal preview-modal" onClick={e => e.stopPropagation()}>

        <div className="modal-header">
          <h2 className="modal-title">🔍 Prévisualisation</h2>
          <button className="icon-btn" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body preview-body">
          <div className="preview-top">

            {/* Miniature / Embed */}
            <div className="preview-thumb-wrap">
              {showEmbed && preview.embed_url ? (
                <iframe
                  className="preview-embed"
                  src={preview.embed_url}
                  allow="autoplay; encrypted-media"
                  allowFullScreen
                  title="Aperçu vidéo"
                />
              ) : (
                <div className="preview-thumb-box">
                  {preview.thumbnail
                    ? <img src={preview.thumbnail} alt={preview.title} className="preview-thumb" />
                    : <div className="preview-thumb-placeholder">🎬</div>
                  }
                  {preview.embed_url && (
                    <button
                      className="play-btn"
                      onClick={() => setShowEmbed(true)}
                      title="Lire l'extrait (30s)"
                    >
                      ▶ Lire l'extrait (30s)
                    </button>
                  )}
                  {preview.is_live && (
                    <span className="live-badge">🔴 LIVE</span>
                  )}
                </div>
              )}
            </div>

            {/* Métadonnées */}
            <div className="preview-meta">
              <h3 className="preview-title">{preview.title}</h3>

              <div className="preview-info-grid">
                {preview.uploader && (
                  <><span className="info-key">Auteur</span><span>{preview.uploader}</span></>
                )}
                {preview.duration > 0 && (
                  <><span className="info-key">Durée</span><span>{preview.duration_str}</span></>
                )}
                {preview.view_count > 0 && (
                  <><span className="info-key">Vues</span><span>{fmtViews(preview.view_count)}</span></>
                )}
                {preview.upload_date && (
                  <><span className="info-key">Date</span><span>{fmtDate(preview.upload_date)}</span></>
                )}
              </div>

              {preview.description && (
                <p className="preview-desc">{preview.description}</p>
              )}
            </div>
          </div>

          {/* Formats disponibles */}
          {preview.formats.length > 0 && (
            <div className="preview-formats">
              <button
                className="formats-toggle"
                onClick={() => setShowFormats(v => !v)}
              >
                {showFormats ? '▼' : '▶'} {preview.formats.length} formats disponibles
              </button>
              {showFormats && (
                <table className="formats-table">
                  <thead>
                    <tr>
                      <th>Résolution</th>
                      <th>Extension</th>
                      <th>Vidéo</th>
                      <th>Audio</th>
                      <th>FPS</th>
                      <th>Taille</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.formats.map(f => (
                      <tr key={f.format_id}>
                        <td><strong>{f.resolution}</strong></td>
                        <td>{f.ext}</td>
                        <td className="codec">{f.vcodec || '—'}</td>
                        <td className="codec">{f.acodec || '—'}</td>
                        <td>{f.fps ? `${f.fps}fps` : '—'}</td>
                        <td>{f.filesize > 0 ? fmtBytes(f.filesize) : f.note || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {/* Sélection format + téléchargement */}
          <div className="preview-dl-bar">
            <div className="toggle-group">
              <button
                type="button"
                className={`toggle-btn ${selFormat === 'video' ? 'active' : ''}`}
                onClick={() => handleFormatChange('video')}
              >🎬 Vidéo</button>
              <button
                type="button"
                className={`toggle-btn ${selFormat === 'audio' ? 'active' : ''}`}
                onClick={() => handleFormatChange('audio')}
              >🎵 Audio</button>
            </div>

            <select
              className="input select"
              value={selQuality}
              onChange={e => setSelQuality(e.target.value)}
            >
              {(selFormat === 'audio' ? audioQualities : videoQualities).map(q => (
                <option key={q} value={q}>{qualityLabels[q]}</option>
              ))}
            </select>

            <button
              className="btn btn-primary"
              onClick={() => { onDownload(selFormat, selQuality); onClose() }}
            >
              ⬇ Télécharger
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
