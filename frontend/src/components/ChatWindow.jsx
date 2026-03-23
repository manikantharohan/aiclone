import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import { ChatInput } from './ChatInput'

export function ChatWindow({
  messages,
  streamingContent,
  isLoading,
  error,
  isConnected,
  onSendMessage,
  onStopGeneration,
  onClearChat,
  onCopyLastResponse,
  temperature,
  onTemperatureChange,
  maxTokens,
  onMaxTokensChange,
  darkMode,
}) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  const displayMessages = [...messages]
  if (streamingContent && messages[messages.length - 1]?.role !== 'assistant') {
    displayMessages.push({ role: 'assistant', content: streamingContent })
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-950">
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {displayMessages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-64 text-center text-gray-500 dark:text-gray-400">
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm mt-1">Send a message to get a response from the AI.</p>
          </div>
        )}
        {displayMessages.map((msg, i) => (
          <MessageBubble
            key={i}
            message={msg}
            isStreaming={
              isLoading && i === displayMessages.length - 1 && msg.role === 'assistant'
            }
          />
        ))}
        {isLoading && !streamingContent && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
              <span className="inline-flex gap-1">
                <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }} />
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="mx-4 mb-2 px-4 py-2 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 text-sm">
          {error}
        </div>
      )}

      <div className="flex items-center gap-2 px-4 pb-2">
        <button
          type="button"
          onClick={onCopyLastResponse}
          className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
        >
          Copy last response
        </button>
      </div>

      <ChatInput
        onSend={onSendMessage}
        onStop={onStopGeneration}
        isLoading={isLoading}
        disabled={false}
        temperature={temperature}
        onTemperatureChange={onTemperatureChange}
        maxTokens={maxTokens}
        onMaxTokensChange={onMaxTokensChange}
        darkMode={darkMode}
      />
    </div>
  )
}
