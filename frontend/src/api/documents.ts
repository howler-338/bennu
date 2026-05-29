import { apiFetch } from './client'
import { Document } from '../types'

export const documentsApi = {
  list: () => apiFetch<{ documents: Document[] }>('/documents'),
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiFetch<{ document: Document; message: string }>('/documents', {
      method: 'POST',
      body: form,
    })
  },
  delete: (id: string) =>
    apiFetch<{ message: string }>(`/documents/${id}`, { method: 'DELETE' }),
}
