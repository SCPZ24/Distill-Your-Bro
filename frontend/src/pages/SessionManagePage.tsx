import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, MessageCircle, Trash2, Clock, User } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface Session {
  id: string
  bro_name: string
  created_at: string
  last_message_at: string
}

interface Soul {
  bro_name: string
  created_at: string
}

export default function SessionManagePage() {
  const navigate = useNavigate()
  const [sessions, setSessions] = useState<Session[]>([])
  const [souls, setSouls] = useState<Soul[]>([])
  const [loading, setLoading] = useState(true)
  const [showNewSessionModal, setShowNewSessionModal] = useState(false)
  const [selectedBro, setSelectedBro] = useState('')

  useEffect(() => {
    fetchSessions()
    fetchSouls()
  }, [])

  const fetchSessions = async () => {
    try {
      const response = await fetch('/api/sessions')
      const result = await response.json()
      if (result.ok) {
        setSessions(result.data)
      } else {
        toast.error('获取会话列表失败')
      }
    } catch (error) {
      toast.error('网络错误')
    } finally {
      setLoading(false)
    }
  }

  const fetchSouls = async () => {
    try {
      const response = await fetch('/api/souls')
      const result = await response.json()
      if (result.ok) {
        setSouls(result.data)
      }
    } catch (error) {
      console.error('获取SOUL列表失败', error)
    }
  }

  const createSession = async () => {
    if (!selectedBro) {
      toast.error('请选择要对话的兄弟')
      return
    }

    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bro_name: selectedBro })
      })
      
      const result = await response.json()
      if (result.ok) {
        toast.success('会话创建成功')
        setShowNewSessionModal(false)
        setSelectedBro('')
        fetchSessions()
      } else {
        toast.error('创建失败')
      }
    } catch (error) {
      toast.error('网络错误')
    }
  }

  const deleteSession = async (sessionId: string) => {
    if (!confirm('确定要删除这个会话吗？')) return
    
    try {
      const response = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      const result = await response.json()
      if (result.ok) {
        toast.success('删除成功')
        fetchSessions()
      } else {
        toast.error('删除失败')
      }
    } catch (error) {
      toast.error('网络错误')
    }
  }

  const enterChat = (sessionId: string) => {
    navigate(`/sessions/${sessionId}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link
                to="/"
                className="inline-flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeft className="h-5 w-5 mr-2" />
                返回
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">对话管理</h1>
            </div>
            <button
              onClick={() => setShowNewSessionModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <Plus className="h-4 w-4 mr-2" />
              新建对话
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <div className="h-24 w-24 mx-auto bg-indigo-100 rounded-full flex items-center justify-center mb-6">
                <MessageCircle className="h-12 w-12 text-indigo-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">还没有任何对话</h3>
              <p className="text-gray-600 mb-6">
                开始创建你的第一个对话吧！选择一个SOUL，开始和你兄弟的AI人格聊天。
              </p>
              <button
                onClick={() => setShowNewSessionModal(true)}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Plus className="h-5 w-5 mr-2" />
                创建对话
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">我的对话</h2>
              <button
                onClick={() => setShowNewSessionModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                新建对话
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {sessions.map((session) => (
                <div key={session.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center">
                        <User className="h-5 w-5 text-indigo-600 mr-2" />
                        <h3 className="text-xl font-semibold text-gray-900">{session.bro_name}</h3>
                      </div>
                      <button
                        onClick={() => deleteSession(session.id)}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        title="删除"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="space-y-2 text-sm text-gray-600 mb-4">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-2" />
                        <span>创建于 {new Date(session.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center">
                        <MessageCircle className="h-4 w-4 mr-2" />
                        <span>最后消息 {new Date(session.last_message_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => enterChat(session.id)}
                        className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        <MessageCircle className="h-4 w-4 mr-2" />
                        继续对话
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* New Session Modal */}
      {showNewSessionModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">创建新对话</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    选择要对话的兄弟
                  </label>
                  <select
                    value={selectedBro}
                    onChange={(e) => setSelectedBro(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">请选择...</option>
                    {souls.map((soul) => (
                      <option key={soul.bro_name} value={soul.bro_name}>
                        {soul.bro_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowNewSessionModal(false)
                    setSelectedBro('')
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  取消
                </button>
                <button
                  onClick={createSession}
                  disabled={!selectedBro}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  创建
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}