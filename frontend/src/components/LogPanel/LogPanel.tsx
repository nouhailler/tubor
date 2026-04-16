import { useEffect, useRef } from 'react'
import './LogPanel.css'

interface Props {
  logs: string[]
  visible: boolean
  onToggle: () => void
}

export default function LogPanel({ logs, visible, onToggle }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (visible) bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs, visible])

  return (
    <div className={`log-panel ${visible ? 'open' : 'closed'}`}>
      <button className="log-toggle" onClick={onToggle} aria-expanded={visible}>
        <span>Journal</span>
        <span className="log-count">{logs.length}</span>
        <span className="log-chevron">{visible ? '▼' : '▲'}</span>
      </button>

      {visible && (
        <div className="log-content" role="log" aria-live="polite">
          {logs.length === 0
            ? <span className="log-empty">Aucun message.</span>
            : logs.map((line, i) => (
                <div
                  key={i}
                  className={`log-line ${
                    line.includes('[ERREUR') || line.startsWith('ERROR:') ? 'log-error'
                    : line.includes('[OK]') || line.includes('Terminé') ? 'log-ok'
                    : line.includes('[CMD]') ? 'log-cmd'
                    : ''
                  }`}
                >
                  {line}
                </div>
              ))
          }
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  )
}
