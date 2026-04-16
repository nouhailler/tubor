import { api } from './client'
import type { Config } from '../types'

export const getConfig    = ()                          => api.get<Config>('/config')
export const updateConfig = (patch: Partial<Config>)   => api.put<Config>('/config', patch)
