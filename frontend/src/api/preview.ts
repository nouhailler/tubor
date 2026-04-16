import { api } from './client'
import type { PreviewInfo } from '../types'

export const getPreview = (url: string) =>
  api.get<PreviewInfo>(`/preview?url=${encodeURIComponent(url)}`)
