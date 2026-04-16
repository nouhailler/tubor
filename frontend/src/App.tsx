import { useState, useEffect, useCallback } from 'react'
import type { Config } from './types'
import { getConfig, updateConfig } from './api/config'
import { useDownloads } from './hooks/useDownloads'
import Header from './components/Header/Header'
import DownloadForm from './components/DownloadForm/DownloadForm'
import DownloadList from './components/DownloadList/DownloadList'
import LogPanel from './components/LogPanel/LogPanel'
import Dashboard from './components/Dashboard/Dashboard'
import SettingsPage from './components/SettingsPage/SettingsPage'
import './App.css'

type View = 'main' | 'dashboard' | 'settings'

export default function App() {
  const [config,  setConfig]  = useState<Config | null>(null)
  const [theme,   setTheme]   = useState('dark')
  const [showLog, setShowLog] = useState(false)
  const [view,    setView]    = useState<View>('main')

  const { downloads, logs, activeCount, add, cancel, stopAll, clearDone, reorder } = useDownloads()

  useEffect(() => {
    getConfig()
      .then(cfg => { setConfig(cfg); setTheme(cfg.theme ?? 'dark') })
      .catch(() => {})
  }, [])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const handleThemeToggle = useCallback(async () => {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    try { const u = await updateConfig({ theme: next }); setConfig(u) } catch { /* noop */ }
  }, [theme])

  const handleConfigSave = useCallback(async (patch: Partial<Config>) => {
    try {
      const updated = await updateConfig(patch)
      setConfig(updated)
      if (patch.theme) setTheme(patch.theme)
    } catch { /* noop */ }
  }, [])

  return (
    <div className="app">
      <Header
        theme={theme}
        onThemeToggle={handleThemeToggle}
        config={config}
        onConfigSave={handleConfigSave}
      />

      {/* Barre de navigation principale */}
      <nav className="app-nav">
        <button className={`nav-btn ${view === 'main' ? 'active' : ''}`} onClick={() => setView('main')}>
          ⬇ Téléchargements
          {activeCount > 0 && <span className="nav-badge">{activeCount}</span>}
        </button>
        <button className={`nav-btn ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>
          📊 Tableau de bord
        </button>
        <button className={`nav-btn ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
          ⚙ Paramètres
        </button>
      </nav>

      <main className="app-main">
        {view === 'main' && (
          <>
            <DownloadForm config={config} onAdd={add} onConfigPatch={handleConfigSave} />
            <DownloadList
              downloads={downloads}
              onCancel={cancel}
              onClearDone={clearDone}
              onStopAll={stopAll}
              onReorder={reorder}
              activeCount={activeCount}
            />
            <LogPanel logs={logs} visible={showLog} onToggle={() => setShowLog(v => !v)} />
          </>
        )}
        {view === 'dashboard' && <Dashboard />}
        {view === 'settings' && config && (
          <SettingsPage
            config={config}
            onSave={handleConfigSave}
          />
        )}
      </main>
    </div>
  )
}
