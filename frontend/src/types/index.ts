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

export interface AdminUser {
  id: string
  email: string
  is_active: boolean
  role: 'user' | 'admin'
  created_at: string
}

export interface AdminStats {
  documents: {
    pending: number
    processing: number
    ready: number
    failed: number
    total: number
  }
  users: {
    total: number
    active: number
  }
}

export interface FailedDocument {
  id: string
  original_filename: string
  owner_email: string
  created_at: string
  updated_at: string
}
