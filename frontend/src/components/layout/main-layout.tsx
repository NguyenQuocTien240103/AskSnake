'use client'

import { useState, useEffect } from 'react'
import { AuthForms } from '@/components/auth/auth-forms'
import { ChatSidebar } from '@/components/chat/chat-sidebar'
import { ChatArea } from '@/components/chat/chat-area'
import { useAuthStore } from '@/lib/stores/auth'
import { useChatStore } from '@/lib/stores/chat'

export function MainLayout() {
  const [showAuth, setShowAuth] = useState(false)
  const { isAuthenticated, token } = useAuthStore()
  const { createConversation, clearChat } = useChatStore()

  useEffect(() => {
    if (isAuthenticated) {
      setShowAuth(false)
    }
  }, [isAuthenticated])

  const handleNewChat = async () => {
    if (isAuthenticated && token) {
      // Create new conversation for authenticated users
      await createConversation('New Chat', token)
    } else {
      // Clear temp messages for guest users
      clearChat()
    }
  }

  const handleShowAuth = () => {
    setShowAuth(true)
  }

  const handleAuthSuccess = () => {
    setShowAuth(false)
  }

  if (showAuth) {
    return (
      <div className="h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-full max-w-md">
          <div className="mb-6 text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">ChatGPT Clone</h1>
            <p className="text-gray-600">Your AI-powered conversation assistant</p>
          </div>
          <AuthForms onSuccess={handleAuthSuccess} />
          <div className="mt-4 text-center">
            <button
              onClick={() => setShowAuth(false)}
              className="text-blue-600 hover:text-blue-800 text-sm underline"
            >
              Continue as guest
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-white flex">
      <ChatSidebar onNewChat={handleNewChat} onShowAuth={handleShowAuth} />
      <ChatArea />
    </div>
  )
}