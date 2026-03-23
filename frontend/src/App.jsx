import { useState, useCallback } from 'react'
import { Header } from './components/Header'
import { ChatWindow } from './components/ChatWindow'
import { useChat } from './hooks/useChat'

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(512)

  const {
    messages,
    isLoading,
    error,
    isConnected,
    streamingContent,
    sendMessage,
    stopGeneration,
    clearChat,
    copyLastResponse,
  } = useChat()

  const toggleDarkMode = useCallback(() => {
    setDarkMode((d) => {
      const next = !d
      if (typeof document !== 'undefined') {
        document.documentElement.classList.toggle('dark', next)
      }
      return next
    })
  }, [])

  if (typeof document !== 'undefined') {
    document.documentElement.classList.toggle('dark', darkMode)
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="flex flex-col h-screen bg-white dark:bg-gray-900">
        <Header
          darkMode={darkMode}
          onToggleDarkMode={toggleDarkMode}
          onClearChat={clearChat}
          isConnected={isConnected}
        />
        <main className="flex-1 min-h-0 flex flex-col">
          <ChatWindow
            messages={messages}
            streamingContent={streamingContent}
            isLoading={isLoading}
            error={error}
            isConnected={isConnected}
            onSendMessage={sendMessage}
            onStopGeneration={stopGeneration}
            onClearChat={clearChat}
            onCopyLastResponse={copyLastResponse}
            temperature={temperature}
            onTemperatureChange={setTemperature}
            maxTokens={maxTokens}
            onMaxTokensChange={setMaxTokens}
            darkMode={darkMode}
          />
        </main>
      </div>
    </div>
  )
}

export default App
