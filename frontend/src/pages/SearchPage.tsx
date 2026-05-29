import { useState, FormEvent } from 'react'
import { searchApi } from '../api/search'
import { SearchResult } from '../types'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    try {
      const data = await searchApi.search(query)
      setResults(data.results)
      setSearched(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-xl font-semibold text-gray-900 mb-6">Semantic Search</h1>

      <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search your documents…"
          className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-600 text-sm rounded px-3 py-2">
          {error}
        </div>
      )}

      {searched && results.length === 0 && (
        <p className="text-gray-400 text-sm">No results found.</p>
      )}

      <div className="space-y-4">
        {results.map((r, i) => (
          <div key={i} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500">
                {r.document.original_filename} · chunk {r.chunk_index}
              </span>
              <span className="text-xs text-indigo-600 font-medium">
                {(r.similarity * 100).toFixed(1)}% match
              </span>
            </div>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{r.content}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
