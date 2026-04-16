import { useState, useRef } from 'react'
import type { DownloadItem } from '../../types'
import DownloadCard from '../DownloadCard/DownloadCard'
import './DownloadList.css'

interface Props {
  downloads:   DownloadItem[]
  onCancel:    (id: string) => void
  onClearDone: () => void
  onStopAll:   () => void
  onReorder:   (newOrder: string[]) => void
  activeCount: number
}

export default function DownloadList({
  downloads, onCancel, onClearDone, onStopAll, onReorder, activeCount,
}: Props) {
  const [draggingId, setDraggingId] = useState<string | null>(null)
  const [dragOverId, setDragOverId] = useState<string | null>(null)
  const dragCounter = useRef(0)

  const hasDone = downloads.some(d => ['finished','error','cancelled'].includes(d.status))
  const waitingIds = downloads.filter(d => d.status === 'waiting').map(d => d.id)

  const handleDragStart = (e: React.DragEvent, id: string) => {
    e.dataTransfer.effectAllowed = 'move'
    setDraggingId(id)
  }

  const handleDragEnter = (e: React.DragEvent, id: string) => {
    e.preventDefault()
    dragCounter.current++
    if (waitingIds.includes(id)) setDragOverId(id)
  }

  const handleDragLeave = () => {
    dragCounter.current--
    if (dragCounter.current === 0) setDragOverId(null)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDrop = (e: React.DragEvent, targetId: string) => {
    e.preventDefault()
    dragCounter.current = 0
    setDragOverId(null)

    if (!draggingId || draggingId === targetId) {
      setDraggingId(null)
      return
    }

    // Réordonne uniquement les items en attente
    const newOrder = [...waitingIds]
    const fromIdx  = newOrder.indexOf(draggingId)
    const toIdx    = newOrder.indexOf(targetId)
    if (fromIdx === -1 || toIdx === -1) { setDraggingId(null); return }

    newOrder.splice(fromIdx, 1)
    newOrder.splice(toIdx, 0, draggingId)

    setDraggingId(null)
    onReorder(newOrder)
  }

  const handleDragEnd = () => {
    setDraggingId(null)
    setDragOverId(null)
    dragCounter.current = 0
  }

  return (
    <div className="download-list-container">
      {/* Barre d'état globale */}
      {activeCount > 0 && (
        <div className="status-bar">
          <span className="status-bar-text">
            <span className="spinner" />
            {activeCount} téléchargement{activeCount > 1 ? 's' : ''} en cours
          </span>
          <button className="btn btn-danger btn-sm" onClick={onStopAll}>⏹ Tout arrêter</button>
        </div>
      )}

      {/* Liste */}
      <div className="download-list" role="list">
        {downloads.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">⬇</span>
            <p>Aucun téléchargement.<br />Saisissez une URL ci-dessus pour commencer.</p>
          </div>
        ) : downloads.map(d => {
          const isWaiting  = d.status === 'waiting'
          const isDragging = draggingId === d.id
          const isDragOver = dragOverId === d.id && !isDragging

          return (
            <div
              key={d.id}
              role="listitem"
              className={`list-item ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
              draggable={isWaiting}
              onDragStart={isWaiting ? e => handleDragStart(e, d.id) : undefined}
              onDragEnter={isWaiting ? e => handleDragEnter(e, d.id) : undefined}
              onDragLeave={isWaiting ? handleDragLeave : undefined}
              onDragOver={isWaiting ? handleDragOver : undefined}
              onDrop={isWaiting ? e => handleDrop(e, d.id) : undefined}
              onDragEnd={handleDragEnd}
            >
              {isWaiting && (
                <span className="drag-handle" title="Glisser pour réorganiser">⋮⋮</span>
              )}
              <DownloadCard item={d} onCancel={onCancel} />
            </div>
          )
        })}
      </div>

      {hasDone && (
        <div className="list-footer">
          <button className="btn btn-ghost btn-sm" onClick={onClearDone}>
            🗑 Effacer les terminés
          </button>
        </div>
      )}
    </div>
  )
}
