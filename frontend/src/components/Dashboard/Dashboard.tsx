import { useState, useEffect, useCallback, useRef } from 'react'
import {
  getStatsSummary, getDailyStats, getPlatformStats, getHistory,
} from '../../api/stats'
import type { StatsSummary, DailyStat, PlatformStat, HistoryItem } from '../../types'
import './Dashboard.css'

// ── Utilitaires ───────────────────────────────────────────────────────────────

function fmtBytes(b: number): string {
  if (b <= 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (b >= 1024 && i < units.length - 1) { b /= 1024; i++ }
  return `${b.toFixed(1)} ${units[i]}`
}

function fmtDate(ts: number): string {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleDateString('fr-FR', {
    day: '2-digit', month: '2-digit', year: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

function countryFlag(code: string): string {
  if (!code || code.length !== 2) return ''
  const base = 0x1F1E6 - 65
  return String.fromCodePoint(code.charCodeAt(0) + base) +
         String.fromCodePoint(code.charCodeAt(1) + base)
}

function fmtDay(isoDate: string): string {
  const parts = isoDate.split('-')
  return parts.length === 3 ? `${parts[2]}/${parts[1]}` : isoDate
}

function truncate(s: string, n = 55): string {
  return s && s.length > n ? s.slice(0, n - 1) + '…' : (s || '—')
}

// ── Graphique en barres empilées (vert succès / rouge erreur) ─────────────────

function StackedBarChart({ data }: { data: DailyStat[] }) {
  const max = Math.max(...data.map(d => d.count), 1)
  return (
    <div className="bar-chart">
      {data.map((d, i) => {
        const totalPct = (d.count / max) * 100
        const successPct = d.count > 0 ? (d.count_success / d.count) * 100 : 0
        const errorPct   = d.count > 0 ? (d.count_error   / d.count) * 100 : 0
        const otherPct   = 100 - successPct - errorPct
        return (
          <div key={i} className="bar-item">
            <div className="bar-track">
              <div
                className="bar-fill-stack"
                style={{ height: `${totalPct}%` }}
                title={`${d.count} total · ${d.count_success} réussis · ${d.count_error} échoués`}
              >
                {/* Rouge en bas, puis autre, puis vert en haut */}
                {errorPct > 0 && (
                  <div className="bar-seg bar-seg-error"   style={{ flex: errorPct }} />
                )}
                {otherPct > 0 && (
                  <div className="bar-seg bar-seg-other"   style={{ flex: otherPct }} />
                )}
                {successPct > 0 && (
                  <div className="bar-seg bar-seg-success" style={{ flex: successPct }} />
                )}
              </div>
            </div>
            <div className="bar-label">{fmtDay(d.day)}</div>
          </div>
        )
      })}
    </div>
  )
}

function HBar({ data }: { data: { label: string; value: number }[] }) {
  const max = Math.max(...data.map(d => d.value), 1)
  return (
    <div className="hbar-list">
      {data.map((d, i) => (
        <div key={i} className="hbar-row">
          <div className="hbar-label">{d.label}</div>
          <div className="hbar-track">
            <div className="hbar-fill" style={{ width: `${(d.value / max) * 100}%` }} />
          </div>
          <div className="hbar-value">{d.value}</div>
        </div>
      ))}
    </div>
  )
}

// ── Composant principal ───────────────────────────────────────────────────────

type DTab = 'overview' | 'success' | 'error' | 'history'

export default function Dashboard() {
  const [tab,       setTab]       = useState<DTab>('overview')
  const [summary,   setSummary]   = useState<StatsSummary | null>(null)
  const [daily,     setDaily]     = useState<DailyStat[]>([])
  const [platforms, setPlatforms] = useState<PlatformStat[]>([])
  const [history,   setHistory]   = useState<HistoryItem[]>([])
  const [successList, setSuccessList] = useState<HistoryItem[]>([])
  const [errorList,   setErrorList]   = useState<HistoryItem[]>([])
  const [loading,   setLoading]   = useState(true)
  const [histFilter, setHistFilter] = useState({ status: '', format: '' })
  const [copied,    setCopied]    = useState<string | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // ── Chargement des données ─────────────────────────────────────────────────

  const loadOverview = useCallback(async () => {
    try {
      const [s, d, p] = await Promise.all([
        getStatsSummary(), getDailyStats(14), getPlatformStats(),
      ])
      setSummary(s); setDaily(d); setPlatforms(p)
    } catch { /* ignore */ }
  }, [])

  const loadSuccessTab = useCallback(async () => {
    try {
      const h = await getHistory({ limit: 100, status_filter: 'finished' })
      setSuccessList(h)
    } catch { /* ignore */ }
  }, [])

  const loadErrorTab = useCallback(async () => {
    try {
      const h = await getHistory({ limit: 100, status_filter: 'error' })
      setErrorList(h)
    } catch { /* ignore */ }
  }, [])

  const loadHistory = useCallback(async () => {
    try {
      const h = await getHistory({
        limit: 150,
        status_filter: histFilter.status,
        format_filter: histFilter.format,
      })
      setHistory(h)
    } catch { /* ignore */ }
  }, [histFilter])

  const refreshAll = useCallback(async () => {
    setLoading(true)
    await Promise.all([loadOverview(), loadSuccessTab(), loadErrorTab()])
    setLoading(false)
  }, [loadOverview, loadSuccessTab, loadErrorTab])

  // Chargement initial
  useEffect(() => { refreshAll() }, [refreshAll])

  // Rafraîchissement automatique toutes les 30 secondes
  useEffect(() => {
    intervalRef.current = setInterval(refreshAll, 30_000)
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [refreshAll])

  // Recharger l'historique quand filtres changent ou onglet actif
  useEffect(() => {
    if (tab === 'history') loadHistory()
  }, [tab, loadHistory])

  // ── Données graphique 14j (jours manquants remplis) ───────────────────────

  const last14: DailyStat[] = Array.from({ length: 14 }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() - (13 - i))
    const key = d.toISOString().slice(0, 10)
    const found = daily.find(x => x.day === key)
    return found ?? { day: key, count: 0, size_bytes: 0, count_success: 0, count_error: 0 }
  })

  const hasData = last14.some(d => d.count > 0)

  // ── Copier URL ──────────────────────────────────────────────────────────────

  const copyUrl = async (url: string, id: string) => {
    try {
      await navigator.clipboard.writeText(url)
      setCopied(id)
      setTimeout(() => setCopied(null), 2000)
    } catch { /* ignore */ }
  }

  // ── Rendu ─────────────────────────────────────────────────────────────────

  return (
    <div className="dashboard">

      {/* ── Onglets ──────────────────────────────────────────────────────── */}
      <div className="dash-tabs">
        <button className={`tab-btn ${tab === 'overview' ? 'active' : ''}`} onClick={() => setTab('overview')}>
          📊 Vue d'ensemble
        </button>
        <button className={`tab-btn ${tab === 'success' ? 'active' : ''}`} onClick={() => setTab('success')}>
          ✔ Réussis
          {summary && summary.successful_downloads > 0 && (
            <span className="tab-count success-count">{summary.successful_downloads}</span>
          )}
        </button>
        <button className={`tab-btn ${tab === 'error' ? 'active' : ''}`} onClick={() => setTab('error')}>
          ✗ Échoués
          {summary && summary.failed_downloads > 0 && (
            <span className="tab-count error-count">{summary.failed_downloads}</span>
          )}
        </button>
        <button className={`tab-btn ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}>
          🕑 Historique
        </button>
        <button
          className="tab-btn refresh-btn"
          onClick={refreshAll}
          title="Actualiser"
          disabled={loading}
        >
          {loading ? '⏳' : '🔄'}
        </button>
      </div>

      {/* ── Vue d'ensemble ─────────────────────────────────────────────────── */}
      {tab === 'overview' && (
        <div className="dash-content">

          {/* Cartes cliquables */}
          <div className="stat-cards">
            <div className="stat-card" onClick={() => setTab('history')}>
              <div className="stat-value">{summary?.total_downloads ?? 0}</div>
              <div className="stat-label">Total</div>
            </div>
            <div className="stat-card success clickable" onClick={() => setTab('success')}>
              <div className="stat-value">{summary?.successful_downloads ?? 0}</div>
              <div className="stat-label">Réussis ↗</div>
            </div>
            <div className="stat-card error clickable" onClick={() => setTab('error')}>
              <div className="stat-value">{summary?.failed_downloads ?? 0}</div>
              <div className="stat-label">Échoués ↗</div>
            </div>
            <div className="stat-card today">
              <div className="stat-value">{summary?.today_downloads ?? 0}</div>
              <div className="stat-label">Aujourd'hui</div>
            </div>
            <div className="stat-card size">
              <div className="stat-value">{fmtBytes(summary?.total_size_bytes ?? 0)}</div>
              <div className="stat-label">Téléchargé</div>
            </div>
            <div className="stat-card rate">
              <div className="stat-value">{summary?.success_rate ?? 0}%</div>
              <div className="stat-label">Taux de succès</div>
            </div>
          </div>

          <div className="dash-row">
            {/* Graphique empilé */}
            <div className="dash-panel">
              <h3 className="panel-title">Téléchargements — 14 derniers jours</h3>
              <div className="bar-legend">
                <span className="legend-dot success" /> Réussis
                <span className="legend-dot error" style={{ marginLeft: '0.9rem' }} /> Échoués
              </div>
              {!hasData
                ? <p className="dash-empty">Aucune donnée sur cette période.</p>
                : <StackedBarChart data={last14} />
              }
            </div>

            {/* Top plateformes */}
            <div className="dash-panel">
              <h3 className="panel-title">Top plateformes</h3>
              {platforms.length === 0
                ? <p className="dash-empty">Aucune donnée.</p>
                : <HBar data={platforms.map(p => ({ label: p.platform, value: p.count }))} />
              }
            </div>
          </div>
        </div>
      )}

      {/* ── Réussis ────────────────────────────────────────────────────────── */}
      {tab === 'success' && (
        <div className="dash-content">
          <h3 className="list-section-title">
            <span className="dot-success">✔</span>
            {successList.length} téléchargement{successList.length !== 1 ? 's' : ''} réussi{successList.length !== 1 ? 's' : ''}
          </h3>
          {successList.length === 0 ? (
            <div className="dash-empty-center">Aucun téléchargement réussi pour l'instant.</div>
          ) : (
            <div className="item-list">
              {successList.map(h => (
                <div key={h.id} className="item-row item-success">
                  <span className="item-icon">✔</span>
                  <div className="item-info">
                    <div className="item-title" title={h.title || h.url}>
                      {truncate(h.title || h.url)}
                    </div>
                    <div className="item-meta">
                      {h.platform && <span>{h.platform}</span>}
                      {h.format && <span>{h.format === 'audio' ? '🎵 MP3' : '🎬 MP4'} · {h.quality}</span>}
                      {h.file_size > 0 && <span>{fmtBytes(h.file_size)}</span>}
                      <span>{fmtDate(h.finished_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Échoués ────────────────────────────────────────────────────────── */}
      {tab === 'error' && (
        <div className="dash-content">
          <h3 className="list-section-title">
            <span className="dot-error">✗</span>
            {errorList.length} téléchargement{errorList.length !== 1 ? 's' : ''} échoué{errorList.length !== 1 ? 's' : ''}
          </h3>
          {errorList.length === 0 ? (
            <div className="dash-empty-center">Aucun téléchargement échoué.</div>
          ) : (
            <div className="item-list">
              {errorList.map(h => (
                <div key={h.id} className="item-row item-error">
                  <span className="item-icon error">✗</span>
                  <div className="item-info">
                    <div className="item-title" title={h.title || h.url}>
                      {truncate(h.title || h.url)}
                    </div>
                    {h.error_message && (
                      <div className="item-error-msg" title={h.error_message}>
                        {truncate(h.error_message, 90)}
                      </div>
                    )}
                    <div className="item-meta">
                      {h.platform && <span>{h.platform}</span>}
                      {h.country_code && (
                        <span title={`Tentative depuis : ${h.country_code}`}>
                          {countryFlag(h.country_code)} {h.country_code}
                        </span>
                      )}
                      <span>{fmtDate(h.finished_at)}</span>
                    </div>
                  </div>
                  <button
                    className={`copy-url-btn ${copied === h.id ? 'copied' : ''}`}
                    onClick={() => copyUrl(h.url, h.id)}
                    title={copied === h.id ? 'Copié !' : `Copier l'URL pour réessayer\n${h.url}`}
                  >
                    {copied === h.id ? '✔ Copié' : '📋 Copier URL'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Historique complet ─────────────────────────────────────────────── */}
      {tab === 'history' && (
        <div className="dash-content">
          <div className="hist-filters">
            <select
              className="input select"
              value={histFilter.status}
              onChange={e => setHistFilter(f => ({ ...f, status: e.target.value }))}
            >
              <option value="">Tous les statuts</option>
              <option value="finished">✔ Terminés</option>
              <option value="error">✗ Erreurs</option>
              <option value="cancelled">⊘ Annulés</option>
            </select>
            <select
              className="input select"
              value={histFilter.format}
              onChange={e => setHistFilter(f => ({ ...f, format: e.target.value }))}
            >
              <option value="">Tous les formats</option>
              <option value="video">🎬 Vidéo</option>
              <option value="audio">🎵 Audio</option>
            </select>
          </div>

          <div className="hist-table-wrap">
            <table className="hist-table">
              <thead>
                <tr>
                  <th>Statut</th>
                  <th>Titre</th>
                  <th>Plateforme</th>
                  <th>Pays</th>
                  <th>Format</th>
                  <th>Taille</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {history.length === 0 ? (
                  <tr><td colSpan={7} className="hist-empty">Aucun téléchargement dans l'historique.</td></tr>
                ) : history.map(h => (
                  <tr key={h.id}>
                    <td>
                      <span className={`hist-status-badge status-${h.status}`}>
                        {h.status === 'finished' ? '✔' : h.status === 'error' ? '✗' : '⊘'}
                      </span>
                    </td>
                    <td className="hist-title" title={h.title || h.url}>
                      {truncate(h.title || h.url)}
                    </td>
                    <td>{h.platform || '—'}</td>
                    <td className="hist-country" title={h.country_code || ''}>
                      {h.country_code ? `${countryFlag(h.country_code)} ${h.country_code}` : '—'}
                    </td>
                    <td>{h.format === 'audio' ? '🎵 MP3' : '🎬 MP4'} · {h.quality}</td>
                    <td>{h.file_size > 0 ? fmtBytes(h.file_size) : '—'}</td>
                    <td className="hist-date">{fmtDate(h.finished_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
