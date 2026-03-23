/**
 * WebSocket service for chat streaming.
 * Connects to backend ws://localhost:8000/ws/chat/{sessionId}
 * API keys are never used in frontend; backend uses HF_TOKEN from env.
 */

const getWsBaseUrl = () => {
  if (import.meta.env.VITE_WS_URL) {
    const u = String(import.meta.env.VITE_WS_URL).trim()
    // Convert http:// to ws:// and https:// to wss://
    if (u.startsWith('https://')) {
      return u.replace(/^https:\/\//, 'wss://')
    }
    if (u.startsWith('http://')) {
      return u.replace(/^http:\/\//, 'ws://')
    }
    return u
  }
  // In dev, backend is always on port 8000 (same machine)
  if (import.meta.env.DEV) {
    return 'ws://localhost:8000'
  }
  const { protocol, hostname } = window.location
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:'
  const port = window.location.port || ''
  return `${wsProtocol}//${hostname}${port ? ':' + port : ''}`
}

export function buildChatWsUrl(sessionId, { temperature, maxTokens } = {}) {
  const base = getWsBaseUrl()
  const path = `/ws/chat/${encodeURIComponent(sessionId)}`
  const params = new URLSearchParams()
  if (temperature != null && temperature !== '') params.set('temperature', String(temperature))
  if (maxTokens != null && maxTokens !== '') params.set('max_tokens', String(maxTokens))
  const qs = params.toString()
  return qs ? `${base}${path}?${qs}` : `${base}${path}`
}

export function createChatWebSocket(sessionId, options = {}) {
  const url = buildChatWsUrl(sessionId, options)
  return new WebSocket(url)
}
