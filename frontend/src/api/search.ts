import { apiFetch } from './client'
import { SearchResult } from '../types'

export const searchApi = {
  search: (query: string, limit = 5) =>
    apiFetch<{ results: SearchResult[] }>('/search', {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    }),
}
