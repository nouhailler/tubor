import { useState } from 'react'
import type { DownloadItem } from '../../types'
import { openFile } from '../../api/downloads'
import './DownloadCard.css'

interface Props {
  item: DownloadItem
  onCancel: (id: string) => void
}

const STATUS_ICON: Record<string, string> = {
  waiting:     '⏸',
  downloading: '⬇',
  processing:  '⚙',
  retrying:    '🔄',
  finished:    '✔',
  error:       '✗',
  cancelled:   '⊘',
}

const STATUS_LABEL: Record<string, string> = {
  waiting:     'En attente',
  downloading: 'Téléchargement',
  processing:  'Traitement…',
  retrying:    'Nouvelle tentative…',
  finished:    'Terminé',
  error:       'Erreur',
  cancelled:   'Annulé',
}

function truncate(s: string, n = 60) {
  return s.length > n ? s.slice(0, n - 1) + '…' : s
}

function countryFlag(code: string): string {
  if (!code || code.length !== 2) return ''
  const base = 0x1F1E6 - 65
  return String.fromCodePoint(code.charCodeAt(0) + base) +
         String.fromCodePoint(code.charCodeAt(1) + base)
}

export default function DownloadCard({ item, onCancel }: Props) {
  const [openError, setOpenError] = useState('')
  const [opening,   setOpening]   = useState(false)

  const isActive  = item.status === 'downloading' || item.status === 'processing'
  const isRetrying = item.status === 'retrying'
  const isWaiting = item.status === 'waiting'
  const isDone    = item.status === 'finished' || item.status === 'error' || item.status === 'cancelled'

  const canOpen = item.status === 'finished' && !!item.filepath

  const handleOpen = async () => {
    setOpenError('')
    setOpening(true)
    try {
      await openFile(item.id)
    } catch (e) {
      setOpenError(e instanceof Error ? e.message : 'Impossible d\'ouvrir le fichier')
    } finally {
      setOpening(false)
    }
  }

  return (
    <div className={`download-card status-${item.status}`}>
      {/* Ligne principale */}
      <div className="card-main">
        <span className={`format-badge format-${item.format}`}>
          {item.format === 'audio' ? '🎵 AUDIO' : '🎬 VIDÉO'}
        </span>

        <div className="card-info">
          <div className="card-title" title={item.title || item.url}>
            {item.title || truncate(item.url)}
            {item.country_code && (
              <span
                className="card-flag"
                title={`Téléchargé depuis : ${item.country_name || item.country_code}`}
              >
                {countryFlag(item.country_code)}
              </span>
            )}
          </div>
          {item.filepath && item.status === 'finished' && (
            <div className="card-filepath" title={item.filepath}>
              {truncate(item.filepath, 70)}
            </div>
          )}
          {!item.title && !item.filepath && (
            <div className="card-url" title={item.url}>
              {truncate(item.url)}
            </div>
          )}
        </div>

        <div className="card-actions">
          {/* Bouton Ouvrir — affiché uniquement si fichier disponible */}
          {canOpen && (
            <button
              className="open-btn"
              onClick={handleOpen}
              disabled={opening}
              title={`Ouvrir avec le lecteur par défaut\n${item.filepath}`}
              aria-label="Ouvrir le fichier"
            >
              {opening ? '…' : '📂 Ouvrir'}
            </button>
          )}

          {/* Icône statut */}
          <span className="status-icon" title={STATUS_LABEL[item.status]}>
            {STATUS_ICON[item.status]}
          </span>

          {/* Bouton annulation */}
          {!isDone && (
            <button
              className="cancel-btn"
              onClick={() => onCancel(item.id)}
              title="Annuler"
              aria-label="Annuler ce téléchargement"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Barre de progression */}
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${Math.min(item.percent, 100)}%` }}
        />
      </div>

      {/* Ligne de statut */}
      <div className="card-status-row">
        {isActive && (
          <span className="status-text">
            {item.percent > 0 && <>{item.percent.toFixed(1)}%</>}
            {item.speed && <> · {item.speed}</>}
            {item.eta && <> · ETA {item.eta}</>}
            {item.status === 'processing' && ' Traitement ffmpeg…'}
          </span>
        )}
        {isWaiting   && <span className="status-text muted">En attente dans la file…</span>}
        {isRetrying  && (
          <span className="status-text retrying" title={item.error_message}>
            🔄 {item.error_message || 'Nouvelle tentative en cours…'}
          </span>
        )}
        {item.status === 'finished' && !openError && (
          <span className="status-text success">✔ Téléchargement terminé</span>
        )}
        {openError && (
          <span className="status-text error" title={openError}>{truncate(openError, 80)}</span>
        )}
        {item.status === 'error' && (
          <span className="status-text error" title={item.error_message}>
            {truncate(item.error_message, 80)}
          </span>
        )}
        {item.status === 'cancelled' && (
          <span className="status-text muted">Annulé par l'utilisateur</span>
        )}
      </div>
    </div>
  )
}
