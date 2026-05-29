import { apiFetch } from './client'
import { ChatMessage, Source } from '../types'

export const chatApi = {
  send: (message: string, history: ChatMessage[], limit = 5) =>
    apiFetch<{ reply: string; sources: Source[] }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history, limit }),
    }),
}
