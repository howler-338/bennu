import type { ReactNode } from 'react'

interface MainLayoutProps {
  children: ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="text-lg font-semibold tracking-tight">Bennu</span>
          <nav className="flex gap-6 text-sm text-slate-400">
            <a href="#" className="hover:text-slate-200">
              Documents
            </a>
            <a href="#" className="hover:text-slate-200">
              Chat
            </a>
            <a href="#" className="hover:text-slate-200">
              Admin
            </a>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  )
}
