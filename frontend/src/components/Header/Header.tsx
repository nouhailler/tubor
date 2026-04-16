import { useState } from 'react'
import HelpModal from '../HelpModal/HelpModal'
import type { Config } from '../../types'
import './Header.css'

interface Props {
  theme: string
  onThemeToggle: () => void
  config: Config | null
  onConfigSave: (patch: Partial<Config>) => void
}

export default function Header({ theme, onThemeToggle }: Props) {
  const [helpOpen, setHelpOpen] = useState(false)

  return (
    <>
      <header className="header">
        <div className="header-brand">
          <span className="header-logo">⬇</span>
          <span className="header-title">Tubor</span>
          <span className="header-version">v0.3.0</span>
        </div>
        <div className="header-actions">
          <button
            className="icon-btn"
            onClick={() => setHelpOpen(true)}
            title="Aide"
            aria-label="Ouvrir l'aide"
          >
            ❓
          </button>
          <button
            className="icon-btn"
            onClick={onThemeToggle}
            title={theme === 'dark' ? 'Passer en clair' : 'Passer en sombre'}
            aria-label="Basculer le thème"
          >
            {theme === 'dark' ? '☀' : '🌙'}
          </button>
        </div>
      </header>

      {helpOpen && (
        <HelpModal onClose={() => setHelpOpen(false)} />
      )}
    </>
  )
}
