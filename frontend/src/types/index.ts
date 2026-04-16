// ── Téléchargements ──────────────────────────────────────────────────────────

export type DownloadStatus =
  | 'waiting' | 'downloading' | 'processing'
  | 'finished' | 'error' | 'cancelled' | 'retrying'

export interface DownloadItem {
  id: string
  url: string
  format: string
  quality: string
  status: DownloadStatus
  title: string
  filename: string
  filepath: string
  percent: number
  speed: string
  eta: string
  error_message: string
  retry_count: number
  country_code: string
  country_name: string
}

export interface AddDownloadRequest {
  url: string
  format: string
  quality: string
  output_folder: string
  playlist_mode: string
  playlist_limit: number
  embed_metadata: boolean
  embed_thumbnail: boolean
  cookies_file: string
  scheduled_at: number   // Unix timestamp, 0 = immédiat
}

// ── Configuration ─────────────────────────────────────────────────────────────

export interface Config {
  download_folder: string
  format: string
  quality: string
  theme: string
  embed_metadata: boolean
  embed_thumbnail: boolean
  playlist_mode: string
  playlist_limit: number
  cookies_file: string
  concurrent_downloads: number
  // Réseau
  proxy_enabled: boolean
  proxy: string
  proxy_list: string[]
  proxy_rotation: boolean
  max_retries: number
  sleep_interval: number
  bandwidth_limit: string
  // Planification
  night_mode: boolean
  night_start: number
  night_end: number
  // VPN
  vpn_enabled: boolean
  vpn_type: string
  vpn_countries: string[]
  vpn_custom_cmd: string
  vpn_reconnect_delay: number
}

// ── Système ───────────────────────────────────────────────────────────────────

export interface SystemInfo {
  ytdlp_version: string
  ffmpeg_available: boolean
}

// ── WebSocket ─────────────────────────────────────────────────────────────────

export type WsEvent =
  | { type: 'snapshot';  downloads: DownloadItem[]; queue_order: string[] }
  | { type: 'added';     data: DownloadItem; queue_order: string[] }
  | { type: 'progress' | 'finished'; data: DownloadItem }
  | { type: 'reorder';   queue_order: string[] }
  | { type: 'log';       task_id: string; message: string; level: string }

// ── Prévisualisation ──────────────────────────────────────────────────────────

export interface FormatInfo {
  format_id: string
  ext: string
  resolution: string
  filesize: number
  vcodec: string
  acodec: string
  fps: number | null
  note: string
}

export interface PreviewInfo {
  title: string
  thumbnail: string
  duration: number
  duration_str: string
  uploader: string
  description: string
  view_count: number
  upload_date: string
  webpage_url: string
  youtube_id: string | null
  embed_url: string | null
  formats: FormatInfo[]
  is_live: boolean
}

// ── Statistiques ──────────────────────────────────────────────────────────────

export interface StatsSummary {
  total_downloads: number
  successful_downloads: number
  failed_downloads: number
  today_downloads: number
  total_size_bytes: number
  success_rate: number
}

export interface DailyStat {
  day: string       // "2024-01-15"
  count: number
  size_bytes: number
  count_success: number
  count_error: number
}

export interface PlatformStat {
  platform: string
  count: number
}

export interface FormatStat {
  format: string
  quality: string
  count: number
  avg_seconds: number | null
}

export interface HistoryItem {
  id: string
  url: string
  title: string
  format: string
  quality: string
  platform: string
  status: string
  file_size: number
  filepath: string
  error_message: string
  started_at: number
  finished_at: number
  country_code: string
}
