import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, MessageCircle, Settings, Download, Trash2 } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface Soul {
  bro_name: string
  created_at: string
}

export default function HomePage() {
  const [souls, setSouls] = useState<Soul[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSouls()
  }, [])

  const fetchSouls = async () => {
    try {
      const response = await fetch('/api/souls')
      const result = await response.json()
      if (result.ok) {
        setSouls(result.data)
      } else {
        toast.error('获取SOUL列表失败')
      }
    } catch (error) {
      toast.error('网络错误')
    } finally {
      setLoading(false)
    }
  }

  const deleteSoul = async (broName: string) => {
    if (!confirm(`确定要删除 ${broName} 的SOUL吗？`)) return
    
    try {
      const response = await fetch(`/api/souls/${broName}`, {
        method: 'DELETE'
      })
      const result = await response.json()
      if (result.ok) {
        toast.success('删除成功')
        fetchSouls()
      } else {
        toast.error('删除失败')
      }
    } catch (error) {
      toast.error('网络错误')
    }
  }

  const exportSoul = async (broName: string) => {
    try {
      const response = await fetch(`/api/souls/${broName}/export`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${broName}_SOUL.md`
        a.click()
        window.URL.revokeObjectURL(url)
        toast.success('导出成功')
      } else {
        toast.error('导出失败')
      }
    } catch (error) {
      toast.error('网络错误')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-3xl font-bold text-gray-900">Distill Your Bro</h1>
                <p className="text-sm text-gray-600 mt-1">AI人格蒸馏与对话平台</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/sessions"
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                对话管理
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : souls.length === 0 ? (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <div className="h-24 w-24 mx-auto bg-indigo-100 rounded-full flex items-center justify-center mb-6">
                <Settings className="h-12 w-12 text-indigo-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">还没有创建任何SOUL</h3>
              <p className="text-gray-600 mb-6">
                开始创建你的第一个兄弟人格吧！上传聊天记录，让AI学会你兄弟的说话方式。
              </p>
              <Link
                to="/souls/create"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Plus className="h-5 w-5 mr-2" />
                创建SOUL
              </Link>
            </div>
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">我的SOUL们</h2>
              <Link
                to="/souls/create"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                新建SOUL
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {souls.map((soul) => (
                <div key={soul.bro_name} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-xl font-semibold text-gray-900">{soul.bro_name}</h3>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => exportSoul(soul.bro_name)}
                          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                          title="导出"
                        >
                          <Download className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => deleteSoul(soul.bro_name)}
                          className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                          title="删除"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">
                      创建于 {new Date(soul.created_at).toLocaleDateString()}
                    </p>
                    <div className="flex space-x-3">
                      <Link
                        to={`/sessions`}
                        className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        <MessageCircle className="h-4 w-4 mr-2" />
                        开始对话
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Floating Action Button */}
      <div className="fixed bottom-8 right-8">
        <Link
          to="/souls/create"
          className="inline-flex items-center justify-center w-14 h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <Plus className="h-6 w-6" />
        </Link>
      </div>
    </div>
  )
}