import { api } from './client'
import type { SystemInfo } from '../types'

export const getSystemInfo  = ()  => api.get<SystemInfo>('/system')
export const updateYtdlp    = ()  => api.post<{ success: boolean; message: string }>('/system/update-ytdlp')
