import { useState, useEffect, useRef } from 'react'
import { documentsApi } from '../api/documents'
import { Document } from '../types'

const STATUS_COLORS: Record<Document['status'], string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  processing: 'bg-blue-100 text-blue-700',
  ready: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
}

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  async function load() {
    try {
      const data = await documentsApi.list()
      setDocuments(data.documents)
    } catch {}
  }

  useEffect(() => {
    load()
    const id = setInterval(() => {
      setDocuments((prev) => {
        const hasActive = prev.some(
          (d) => d.status === 'pending' || d.status === 'processing',
        )
        if (hasActive) load()
        return prev
      })
    }, 3000)
    return () => clearInterval(id)
  }, [])

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError('')
    try {
      const data = await documentsApi.upload(file)
      setDocuments((prev) => [data.document, ...prev])
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  async function handleDelete(id: string) {
    try {
      await documentsApi.delete(id)
      setDocuments((prev) => prev.filter((d) => d.id !== id))
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Documents</h1>
        <div>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.docx"
            onChange={handleUpload}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className={`cursor-pointer inline-block px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
          >
            {uploading ? 'Uploading…' : 'Upload document'}
          </label>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-600 text-sm rounded px-3 py-2">
          {error}
        </div>
      )}

      {documents.length === 0 ? (
        <p className="text-gray-400 text-sm">No documents yet. Upload a PDF, TXT, or DOCX file.</p>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
          {documents.map((doc) => (
            <div key={doc.id} className="flex items-center px-4 py-3 gap-4">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {doc.original_filename}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">{formatBytes(doc.file_size)}</p>
              </div>
              <span
                className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${STATUS_COLORS[doc.status]}`}
              >
                {doc.status}
              </span>
              <button
                onClick={() => handleDelete(doc.id)}
                className="text-sm text-gray-400 hover:text-red-500 shrink-0"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
