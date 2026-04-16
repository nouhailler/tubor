import { api } from './client'
import type { StatsSummary, DailyStat, PlatformStat, FormatStat, HistoryItem } from '../types'

export const getStatsSummary = () => api.get<StatsSummary>('/stats/summary')
export const getDailyStats   = (days = 14) => api.get<DailyStat[]>(`/stats/daily?days=${days}`)
export const getPlatformStats = () => api.get<PlatformStat[]>('/stats/platforms')
export const getFormatStats  = () => api.get<FormatStat[]>('/stats/formats')
export const getHistory      = (params?: {
  limit?: number; offset?: number
  status_filter?: string; format_filter?: string
}) => {
  const q = new URLSearchParams()
  if (params?.limit)         q.set('limit',  String(params.limit))
  if (params?.offset)        q.set('offset', String(params.offset))
  if (params?.status_filter) q.set('status_filter', params.status_filter)
  if (params?.format_filter) q.set('format_filter', params.format_filter)
  return api.get<HistoryItem[]>(`/stats/history?${q}`)
}
