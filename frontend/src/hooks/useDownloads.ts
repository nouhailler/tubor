import { useState, useCallback } from 'react'
import type { DownloadItem, AddDownloadRequest, WsEvent } from '../types'
import { addDownload, cancelDownload, cancelAll, clearFinished, reorderQueue } from '../api/downloads'
import { useWebSocket } from './useWebSocket'

export function useDownloads() {
  const [downloads,   setDownloads]  = useState<Record<string, DownloadItem>>({})
  const [queueOrder,  setQueueOrder] = useState<string[]>([])
  const [logs,        setLogs]       = useState<string[]>([])

  const handleEvent = useCallback((e: WsEvent) => {
    if (e.type === 'snapshot') {
      const map: Record<string, DownloadItem> = {}
      for (const d of e.downloads) map[d.id] = d
      setDownloads(map)
      setQueueOrder(e.queue_order)

    } else if (e.type === 'added') {
      setDownloads(prev => ({ ...prev, [e.data.id]: e.data }))
      setQueueOrder(e.queue_order)

    } else if (e.type === 'progress' || e.type === 'finished') {
      setDownloads(prev => ({ ...prev, [e.data.id]: e.data }))

    } else if (e.type === 'reorder') {
      setQueueOrder(e.queue_order)

    } else if (e.type === 'log') {
      setLogs(prev => [...prev.slice(-499), e.message])
    }
  }, [])

  useWebSocket(handleEvent)

  // ── Actions ──────────────────────────────────────────────────────────────

  const add     = useCallback((req: AddDownloadRequest) => addDownload(req), [])
  const cancel  = useCallback((id: string) => cancelDownload(id), [])
  const stopAll = useCallback(() => cancelAll(), [])

  const clearDone = useCallback(async () => {
    await clearFinished()
    setDownloads(prev => {
      const next = { ...prev }
      for (const [id, d] of Object.entries(next))
        if (['finished', 'error', 'cancelled'].includes(d.status)) delete next[id]
      return next
    })
  }, [])

  const reorder = useCallback(async (newOrder: string[]) => {
    setQueueOrder(newOrder)          // optimistic update
    try { await reorderQueue(newOrder) } catch { /* ignore */ }
  }, [])

  // ── Liste triée ───────────────────────────────────────────────────────────

  const STATUS_PRIO: Record<string, number> = {
    downloading: 0, processing: 1, retrying: 2,
    waiting: 3, finished: 4, error: 5, cancelled: 6,
  }

  const list = Object.values(downloads).sort((a, b) => {
    const pa = STATUS_PRIO[a.status] ?? 9
    const pb = STATUS_PRIO[b.status] ?? 9
    if (pa !== pb) return pa - pb
    // Pour les éléments en attente, respecter l'ordre de la file
    if (a.status === 'waiting' && b.status === 'waiting') {
      const ia = queueOrder.indexOf(a.id)
      const ib = queueOrder.indexOf(b.id)
      return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib)
    }
    return 0
  })

  const activeCount = list.filter(d =>
    d.status === 'downloading' || d.status === 'processing' || d.status === 'retrying'
  ).length

  return { downloads: list, queueOrder, logs, activeCount, add, cancel, stopAll, clearDone, reorder }
}
