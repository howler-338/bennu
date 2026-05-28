export function HomePage() {
  return (
    <section className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">
        Enterprise AI Knowledge Platform
      </h1>
      <p className="max-w-2xl text-slate-400">
        Upload documents, search semantically, and chat with your knowledge base
        using RAG and self-hosted inference via Ollama.
      </p>
      <div className="flex gap-4">
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500"
        >
          Upload document
        </button>
        <button
          type="button"
          className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 hover:border-slate-500"
        >
          Start chat
        </button>
      </div>
    </section>
  )
}
