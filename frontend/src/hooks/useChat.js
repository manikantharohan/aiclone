import { useCallback, useRef, useState, useEffect } from 'react'
import { createChatWebSocket } from '../services/websocket'

function generateSessionId() {
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`
}

export function useChat() {
  const [sessionId, setSessionId] = useState(() => generateSessionId())
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const wsRef = useRef(null)
  const abortRef = useRef(false)
  const streamBufferRef = useRef('')

  // Connect to backend on load so "Connected" shows when backend is running
  useEffect(() => {
    const sid = sessionId
    const ws = createChatWebSocket(sid, { temperature: 0.7, max_tokens: 512 })
    wsRef.current = ws
    ws.onopen = () => {
      setIsConnected(true)
      setError(null)
    }
    ws.onclose = () => {
      setIsConnected(false)
    }
    ws.onerror = () => {
      setError('Cannot connect to backend. Is it running at http://localhost:8000?')
      setIsConnected(false)
    }
    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [sessionId])

  const sendMessage = useCallback((text, temperature = 0.7, maxTokens = 512) => {
    if (!text?.trim()) return
    setError(null)
    setMessages((prev) => [...prev, { role: 'user', content: text.trim() }])
    setIsLoading(true)
    setStreamingContent('')
    streamBufferRef.current = ''
    abortRef.current = false

    const onMessage = (event) => {
      if (abortRef.current) return
      if (event.data === '') {
        const final = streamBufferRef.current
        setMessages((prev) => [...prev, { role: 'assistant', content: final }])
        setStreamingContent('')
        streamBufferRef.current = ''
        setIsLoading(false)
        return
      }
      if (typeof event.data === 'string' && event.data.startsWith('[ERROR]')) {
        setError(event.data.replace('[ERROR]', '').trim())
        setStreamingContent('')
        setIsLoading(false)
        return
      }
      streamBufferRef.current += event.data
      setStreamingContent(streamBufferRef.current)
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.onmessage = onMessage
      wsRef.current.send(text.trim())
      return
    }

    const ws = createChatWebSocket(sessionId, {
      temperature: Number(temperature),
      max_tokens: Number(maxTokens),
    })
    wsRef.current = ws
    ws.onopen = () => {
      setIsConnected(true)
      setError(null)
      ws.onmessage = onMessage
      ws.send(text.trim())
    }
    ws.onclose = () => setIsConnected(false)
    ws.onerror = () => {
      setError('Connection error')
      setIsLoading(false)
    }
  }, [sessionId])

  const stopGeneration = useCallback(() => {
    abortRef.current = true
    const current = streamBufferRef.current
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.close()
      wsRef.current = null
    }
    if (current) {
      setMessages((prev) => [...prev, { role: 'assistant', content: current }])
    }
    setStreamingContent('')
    streamBufferRef.current = ''
    setIsLoading(false)
    setIsConnected(false)
  }, [])

  const clearChat = useCallback(() => {
    setMessages([])
    setStreamingContent('')
    setError(null)
    setSessionId(generateSessionId())
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
    setIsLoading(false)
  }, [])

  const copyLastResponse = useCallback(() => {
    const withStream = streamingContent
      ? [...messages, { role: 'assistant', content: streamingContent }]
      : messages
    const lastAssistant = [...withStream].reverse().find((m) => m.role === 'assistant')
    const text = lastAssistant?.content
    if (text) navigator.clipboard.writeText(text)
  }, [messages, streamingContent])

  return {
    sessionId,
    messages,
    isLoading,
    error,
    isConnected,
    streamingContent,
    sendMessage,
    stopGeneration,
    clearChat,
    copyLastResponse,
  }
}
