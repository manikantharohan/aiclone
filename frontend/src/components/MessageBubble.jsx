export function MessageBubble({ message, isStreaming }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-md'
        }`}
      >
        <div className="text-sm whitespace-pre-wrap break-words">
          {message.content}
          {isStreaming && (
            <span className="inline-block w-2 h-4 ml-0.5 bg-current animate-pulse align-middle" />
          )}
        </div>
      </div>
    </div>
  )
}
