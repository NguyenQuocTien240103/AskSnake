'use client'

import { useState, useRef, useEffect } from 'react'
import { PaperPlaneIcon } from '@radix-ui/react-icons'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useAuthStore } from '@/lib/stores/auth'
import { useChatStore } from '@/lib/stores/chat'

interface Message {
  id: number
  content: string
  is_user: boolean
  created_at: string
}

export function ChatArea() {
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  const { isAuthenticated, token } = useAuthStore()
  const { currentConversation, tempMessages, sendMessage } = useChatStore()

  const messages = isAuthenticated && currentConversation 
    ? currentConversation.messages 
    : tempMessages

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const messageText = input.trim()
    setInput('')
    setIsTyping(true)

    try {
      await sendMessage(messageText, token || undefined)
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
    }
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [input])

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-4">💬</div>
              <h2 className="text-xl font-semibold mb-2">
                {isAuthenticated ? 'Start a new conversation' : 'Welcome to ChatGPT Clone'}
              </h2>
              <p className="text-sm">
                {isAuthenticated 
                  ? 'Ask me anything and I\'ll do my best to help!'
                  : 'You can chat as a guest, but login to save your conversations!'
                }
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.is_user ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] p-3 rounded-lg ${
                    message.is_user
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="whitespace-pre-wrap break-words">{message.content}</div>
                  <div
                    className={`text-xs mt-1 opacity-70 ${
                      message.is_user ? 'text-blue-100' : 'text-gray-500'
                    }`}
                  >
                    {new Date(message.created_at).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 p-3 rounded-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Status Bar */}
      {!isAuthenticated && (
        <div className="bg-yellow-50 border-t border-yellow-200 p-2 text-center text-sm text-yellow-800">
          💡 You're chatting as a guest. <strong>Login to save your conversations!</strong>
        </div>
      )}

      {/* Input */}
      <div className="border-t bg-white p-4">
        <form onSubmit={handleSubmit} className="flex items-end space-x-2">
          <div className="flex-1">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message here..."
              className="min-h-[44px] max-h-[120px] resize-none"
              rows={1}
            />
          </div>
          <Button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="h-[44px] px-4"
          >
            <PaperPlaneIcon className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}