import { useState, useEffect, useCallback } from 'react'
import { adminApi } from '../api/admin'
import { AdminUser, AdminStats, FailedDocument } from '../types'

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg px-5 py-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-semibold text-gray-900">{value}</p>
    </div>
  )
}

export default function AdminPage() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [users, setUsers] = useState<AdminUser[]>([])
  const [failedDocs, setFailedDocs] = useState<FailedDocument[]>([])
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      const [statsData, usersData, failedData] = await Promise.all([
        adminApi.getStats(),
        adminApi.listUsers(),
        adminApi.getFailedDocuments(),
      ])
      setStats(statsData)
      setUsers(usersData.users)
      setFailedDocs(failedData.documents)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load admin data')
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleToggleActive(user: AdminUser) {
    try {
      const updated = await adminApi.updateUser(user.id, { is_active: !user.is_active })
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)))
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Update failed')
    }
  }

  async function handleToggleRole(user: AdminUser) {
    const newRole = user.role === 'admin' ? 'user' : 'admin'
    try {
      const updated = await adminApi.updateUser(user.id, { role: newRole })
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)))
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Update failed')
    }
  }

  async function handleDeleteUser(id: string) {
    if (!confirm('Delete this user and all their documents?')) return
    try {
      await adminApi.deleteUser(id)
      setUsers((prev) => prev.filter((u) => u.id !== id))
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  async function handleReprocess(id: string) {
    try {
      await adminApi.reprocessDocument(id)
      setFailedDocs((prev) => prev.filter((d) => d.id !== id))
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Reprocess failed')
    }
  }

  return (
    <div className="p-8 max-w-5xl space-y-10">
      <h1 className="text-xl font-semibold text-gray-900">Admin Dashboard</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded px-3 py-2">
          {error}
        </div>
      )}

      {stats && (
        <section>
          <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
            System Stats
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
            <StatCard label="Total documents" value={stats.documents.total} />
            <StatCard label="Ready" value={stats.documents.ready} />
            <StatCard label="Processing" value={stats.documents.processing + stats.documents.pending} />
            <StatCard label="Failed" value={stats.documents.failed} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <StatCard label="Total users" value={stats.users.total} />
            <StatCard label="Active users" value={stats.users.active} />
          </div>
        </section>
      )}

      <section>
        <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
          Users ({users.length})
        </h2>
        {users.length === 0 ? (
          <p className="text-gray-400 text-sm">No users.</p>
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
            {users.map((user) => (
              <div key={user.id} className="flex items-center px-4 py-3 gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{user.email}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    Joined {new Date(user.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${
                    user.role === 'admin'
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {user.role}
                </span>
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${
                    user.is_active
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-600'
                  }`}
                >
                  {user.is_active ? 'active' : 'inactive'}
                </span>
                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => handleToggleActive(user)}
                    className="text-xs text-gray-500 hover:text-gray-800"
                  >
                    {user.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button
                    onClick={() => handleToggleRole(user)}
                    className="text-xs text-gray-500 hover:text-gray-800"
                  >
                    Make {user.role === 'admin' ? 'user' : 'admin'}
                  </button>
                  <button
                    onClick={() => handleDeleteUser(user.id)}
                    className="text-xs text-gray-400 hover:text-red-500"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
          Failed Documents ({failedDocs.length})
        </h2>
        {failedDocs.length === 0 ? (
          <p className="text-gray-400 text-sm">No failed documents.</p>
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
            {failedDocs.map((doc) => (
              <div key={doc.id} className="flex items-center px-4 py-3 gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {doc.original_filename}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">{doc.owner_email}</p>
                </div>
                <button
                  onClick={() => handleReprocess(doc.id)}
                  className="text-xs text-indigo-600 hover:text-indigo-800 shrink-0"
                >
                  Reprocess
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
