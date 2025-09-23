'use client'

import { useEffect } from 'react'
import { PlusIcon, ChatBubbleIcon, PersonIcon, ExitIcon } from '@radix-ui/react-icons'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useAuthStore } from '@/lib/stores/auth'
import { useChatStore } from '@/lib/stores/chat'

interface ChatSidebarProps {
  onNewChat: () => void
  onShowAuth: () => void
}

export function ChatSidebar({ onNewChat, onShowAuth }: ChatSidebarProps) {
  const { user, isAuthenticated, logout, token } = useAuthStore()
  const { conversations, currentConversation, loadConversations, selectConversation } = useChatStore()

  useEffect(() => {
    if (isAuthenticated && token) {
      loadConversations(token)
    }
  }, [isAuthenticated, token, loadConversations])

  const handleSelectConversation = (conversation: any) => {
    if (token) {
      selectConversation(conversation, token)
    }
  }

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <Button
          onClick={onNewChat}
          className="w-full bg-gray-800 hover:bg-gray-700 text-white border border-gray-600"
          variant="outline"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          New chat
        </Button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-2">
        {isAuthenticated ? (
          <div className="space-y-1">
            {conversations.length > 0 ? (
              conversations.map((conversation) => (
                <Button
                  key={conversation.id}
                  variant="ghost"
                  className={`w-full justify-start text-left h-auto p-3 text-sm hover:bg-gray-800 ${
                    currentConversation?.id === conversation.id ? 'bg-gray-800' : ''
                  }`}
                  onClick={() => handleSelectConversation(conversation)}
                >
                  <ChatBubbleIcon className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="truncate">{conversation.title}</span>
                </Button>
              ))
            ) : (
              <div className="text-gray-400 text-sm p-3 text-center">
                No conversations yet
              </div>
            )}
          </div>
        ) : (
          <div className="text-gray-400 text-sm p-3 text-center">
            <ChatBubbleIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>Login to save and view your chat history</p>
          </div>
        )}
      </div>

      <Separator className="bg-gray-700" />

      {/* User Section */}
      <div className="p-4">
        {isAuthenticated && user ? (
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-sm">
              <PersonIcon className="w-4 h-4" />
              <span className="truncate">{user.username}</span>
            </div>
            <Button
              variant="ghost"
              className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-gray-800"
              onClick={logout}
            >
              <ExitIcon className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        ) : (
          <Button
            variant="ghost"
            className="w-full justify-start hover:bg-gray-800"
            onClick={onShowAuth}
          >
            <PersonIcon className="w-4 h-4 mr-2" />
            Login / Register
          </Button>
        )}
      </div>
    </div>
  )
}