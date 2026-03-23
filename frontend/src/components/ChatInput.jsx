import { useState } from 'react'

export function ChatInput({
  onSend,
  onStop,
  isLoading,
  disabled,
  temperature,
  onTemperatureChange,
  maxTokens,
  onMaxTokensChange,
  darkMode,
}) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || isLoading || disabled) return
    onSend(text, temperature, maxTokens)
    setInput('')
  }

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
      {/* Temperature & max_tokens controls */}
      <div className="flex flex-wrap items-center gap-4 mb-3 text-sm">
        <label className="flex items-center gap-2">
          <span className="text-gray-600 dark:text-gray-400">Temperature</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={temperature}
            onChange={(e) => onTemperatureChange(Number(e.target.value))}
            className="w-24 h-2 rounded-lg appearance-none bg-gray-200 dark:bg-gray-600"
          />
          <span className="text-gray-700 dark:text-gray-300 tabular-nums w-6">{temperature}</span>
        </label>
        <label className="flex items-center gap-2">
          <span className="text-gray-600 dark:text-gray-400">Max tokens</span>
          <input
            type="number"
            min="64"
            max="2048"
            step="64"
            value={maxTokens}
            onChange={(e) => onMaxTokensChange(Number(e.target.value) || 512)}
            className="w-20 px-2 py-1 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </label>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          disabled={disabled || isLoading}
          className="flex-1 px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
        />
        {isLoading ? (
          <button
            type="button"
            onClick={onStop}
            className="px-4 py-3 rounded-xl font-medium bg-red-600 hover:bg-red-700 text-white transition-colors"
          >
            Stop
          </button>
        ) : (
          <button
            type="submit"
            disabled={!input.trim() || disabled}
            className="px-4 py-3 rounded-xl font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        )}
      </form>
    </div>
  )
}
