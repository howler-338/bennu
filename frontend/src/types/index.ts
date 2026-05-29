export interface User {
  id: string
  email: string
  is_active: boolean
  role: 'user' | 'admin'
  created_at: string
}

export interface Document {
  id: string
  original_filename: string
  file_size: number
  mime_type: string
  status: 'pending' | 'processing' | 'ready' | 'failed'
  created_at: string
  updated_at: string
}

export interface SearchResult {
  content: string
  similarity: number
  chunk_index: number
  document: Document
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface Source {
  document_id: string
  filename: string
  chunk_index: number
}
