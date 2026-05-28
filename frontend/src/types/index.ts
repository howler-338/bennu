export interface HealthResponse {
  status: string
}

export interface Document {
  id: string
  filename: string
  status: 'pending' | 'processing' | 'ready' | 'failed'
  createdAt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: string[]
}
