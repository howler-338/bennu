import { apiFetch } from './client'
import { AdminUser, AdminStats, FailedDocument } from '../types'

export const adminApi = {
  getStats: () => apiFetch<AdminStats>('/admin/stats'),

  listUsers: () => apiFetch<{ users: AdminUser[]; total: number }>('/admin/users'),

  updateUser: (id: string, patch: { is_active?: boolean; role?: 'user' | 'admin' }) =>
    apiFetch<AdminUser>(`/admin/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(patch),
    }),

  deleteUser: (id: string) =>
    apiFetch<{ message: string }>(`/admin/users/${id}`, { method: 'DELETE' }),

  getFailedDocuments: () =>
    apiFetch<{ documents: FailedDocument[] }>('/admin/documents/failed'),

  reprocessDocument: (id: string) =>
    apiFetch<{ message: string }>(`/admin/documents/${id}/reprocess`, { method: 'POST' }),
}
