import { api } from './client'
import type { AddDownloadRequest, DownloadItem } from '../types'

export const getDownloads  = ()                          => api.get<DownloadItem[]>('/downloads')
export const addDownload   = (req: AddDownloadRequest)   => api.post<DownloadItem>('/downloads', req)
export const cancelDownload = (id: string)               => api.delete<void>(`/downloads/${id}`)
export const cancelAll     = ()                          => api.delete<void>('/downloads')
export const clearFinished = ()                          => api.post<void>('/downloads/clear-finished')
export const openFile      = (id: string)                => api.post<void>(`/downloads/${id}/open`)
export const reorderQueue  = (order: string[])           => api.put<void>('/downloads/reorder', { order })
