import { useState, FormEvent, useRef, useEffect } from 'react'
import { chatApi } from '../api/chat'
import { ChatMessage, Source } from '../types'

interface Turn {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}

export default function ChatPage() {
  const [turns, setTurns] = useState<Turn[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [turns, loading])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const message = input.trim()
    if (!message || loading) return
    setInput('')
    setError('')
    setTurns((prev) => [...prev, { role: 'user', content: message }])
    setLoading(true)

    const history: ChatMessage[] = turns.map(({ role, content }) => ({ role, content }))
    try {
      const { reply, sources } = await chatApi.send(message, history)
      setTurns((prev) => [...prev, { role: 'assistant', content: reply, sources }])
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Request failed')
      setTurns((prev) => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-8 py-5 border-b border-gray-200 bg-white shrink-0">
        <h1 className="text-xl font-semibold text-gray-900">Chat</h1>
      </div>

      <div className="flex-1 overflow-auto px-8 py-6 space-y-6">
        {turns.length === 0 && (
          <p className="text-gray-400 text-sm text-center mt-20">
            Ask a question about your documents.
          </p>
        )}

        {turns.map((turn, i) => (
          <div key={i} className={`flex ${turn.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className="max-w-xl w-full">
              <div
                className={`rounded-2xl px-4 py-3 text-sm ${
                  turn.role === 'user'
                    ? 'bg-indigo-600 text-white ml-auto'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                <p className="whitespace-pre-wrap">{turn.content}</p>
              </div>
              {turn.sources && turn.sources.length > 0 && (
                <div className="mt-1 px-1 space-y-0.5">
                  {turn.sources.map((s, j) => (
                    <p key={j} className="text-xs text-gray-400">
                      {s.filename} · chunk {s.chunk_index}
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
              <span className="text-gray-400 text-sm">Thinking…</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="mx-8 mb-2 bg-red-50 border border-red-200 text-red-600 text-sm rounded px-3 py-2">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="px-8 py-4 border-t border-gray-200 bg-white flex gap-2 shrink-0"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something…"
          disabled={loading}
          className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  )
}
