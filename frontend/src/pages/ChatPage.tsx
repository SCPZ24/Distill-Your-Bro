import { useState, useEffect, useRef } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Send, User, Bot, Trash2 } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Session {
  id: string
  bro_name: string
  chat_history: Message[]
}

export default function ChatPage() {
  const { id } = useParams<{ id: string }>()
  const [session, setSession] = useState<Session | null>(null)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!id) return
    let isActive = true

    const run = async () => {
      try {
        const response = await fetch(`/api/sessions/${id}`)
        const result = await response.json()
        if (!isActive) return

        if (result.ok) {
          setSession(result.data)
        } else {
          toast.error('获取会话失败')
        }
      } catch (error) {
        if (isActive) {
          toast.error('网络错误')
        }
      } finally {
        if (isActive) {
          setLoading(false)
        }
      }
    }

    run()

    return () => {
      isActive = false
    }
  }, [id])

  useEffect(() => {
    scrollToBottom()
  }, [session?.chat_history])

  const sendMessage = async () => {
    if (!message.trim() || !id) return
    
    setSending(true)
    try {
      const response = await fetch(`/api/sessions/${id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })
      
      const result = await response.json()
      if (result.ok) {
        setSession(prev => prev ? {
          ...prev,
          chat_history: result.data.chat_history
        } : null)
        setMessage('')
      } else {
        toast.error('发送消息失败')
      }
    } catch (error) {
      toast.error('网络错误')
    } finally {
      setSending(false)
    }
  }

  const deleteSession = async () => {
    if (!id || !confirm('确定要删除这个会话吗？')) return
    
    try {
      const response = await fetch(`/api/sessions/${id}`, {
        method: 'DELETE'
      })
      const result = await response.json()
      if (result.ok) {
        toast.success('删除成功')
        window.history.back()
      } else {
        toast.error('删除失败')
      }
    } catch (error) {
      toast.error('网络错误')
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">会话不存在</h2>
          <Link
            to="/sessions"
            className="text-indigo-600 hover:text-indigo-800"
          >
            返回会话列表
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <Link
                to="/sessions"
                className="inline-flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeft className="h-5 w-5 mr-2" />
                返回
              </Link>
              <div className="flex items-center">
                <div className="h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                  <User className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">{session.bro_name}</h1>
                  <p className="text-sm text-gray-600">AI人格对话</p>
                </div>
              </div>
            </div>
            <button
              onClick={deleteSession}
              className="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="删除会话"
            >
              <Trash2 className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {session.chat_history.length === 0 ? (
            <div className="text-center py-12">
              <div className="h-16 w-16 mx-auto bg-indigo-100 rounded-full flex items-center justify-center mb-4">
                <Bot className="h-8 w-8 text-indigo-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">开始对话</h3>
              <p className="text-gray-600">
                和 {session.bro_name} 的AI人格开始聊天吧！
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {session.chat_history.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start max-w-xs lg:max-w-md ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                      msg.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'
                    }`}>
                      {msg.role === 'user' ? (
                        <User className={`h-4 w-4 ${msg.role === 'user' ? 'text-blue-600' : 'text-gray-600'}`} />
                      ) : (
                        <Bot className="h-4 w-4 text-gray-600" />
                      )}
                    </div>
                    <div className={`mx-2 ${msg.role === 'user' ? 'mr-2' : 'ml-2'}`}>
                      <div className={`inline-block px-4 py-2 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-900 border border-gray-200'
                      }`}>
                        <p className="text-sm">{msg.content}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {/* Input */}
      <div className="bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入消息..."
                rows={1}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!message.trim() || sending}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              {sending ? (
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
