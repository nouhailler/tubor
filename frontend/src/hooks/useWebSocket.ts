import { useEffect, useRef, useCallback } from 'react'
import type { WsEvent } from '../types'

const WS_URL = `ws://${window.location.hostname}:8000/ws`

export function useWebSocket(onEvent: (e: WsEvent) => void) {
  const wsRef    = useRef<WebSocket | null>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout>>()
  const cbRef    = useRef(onEvent)
  cbRef.current  = onEvent

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onmessage = (ev) => {
      try {
        cbRef.current(JSON.parse(ev.data) as WsEvent)
      } catch { /* ignore malformed frames */ }
    }

    ws.onclose = () => {
      timerRef.current = setTimeout(connect, 2000)
    }

    ws.onerror = () => { ws.close() }

    // Keepalive ping toutes les 20 s pour détecter les déconnexions réseau
    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send('ping')
    }, 20_000)

    ws.onclose = () => {
      clearInterval(ping)
      timerRef.current = setTimeout(connect, 2000)
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(timerRef.current)
      wsRef.current?.close()
    }
  }, [connect])
}
