import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Upload, Settings, Eye, Save, RefreshCw } from 'lucide-react'
import { toast } from 'react-hot-toast'

type ParsedChatLog = {
  type?: string
  messages_count?: number
  participants?: string[]
  parsed_at?: string
}

export default function SoulCreatePage() {
  const navigate = useNavigate()
  const [broName, setBroName] = useState('')
  const [type, setType] = useState('txt')
  const [textOnly, setTextOnly] = useState(true)
  const myName = '我'
  const [chatLog, setChatLog] = useState('')
  const [isParsing, setIsParsing] = useState(false)
  const [isDistilling, setIsDistilling] = useState(false)
  const [parsedData, setParsedData] = useState<ParsedChatLog | null>(null)
  const [soulPreview, setSoulPreview] = useState('')
  const [currentStep, setCurrentStep] = useState<'upload' | 'parse' | 'distill' | 'preview'>('upload')

  const handleFileUpload = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setChatLog(event.target.value)
  }

  const parseChatLog = async () => {
    if (!chatLog.trim() || !broName.trim()) {
      toast.error('请填写聊天记录和兄弟名称')
      return
    }

    setIsParsing(true)
    try {
      const response = await fetch('/api/chatlogs/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bro_name: broName,
          type,
          payload: chatLog,
          options: { text_only: textOnly, my_name: myName }
        })
      })
      
      const result = await response.json()
      if (result.ok) {
        setParsedData(result.data)
        setCurrentStep('parse')
        toast.success('聊天记录解析成功')
      } else {
        toast.error('解析失败')
      }
    } catch (error) {
      toast.error('网络错误')
    } finally {
      setIsParsing(false)
    }
  }

  const distillSoul = async () => {
    if (!parsedData) {
      toast.error('请先解析聊天记录')
      return
    }

    setIsDistilling(true)
    try {
      const response = await fetch('/api/souls/distill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bro_name: broName })
      })
      
      const result = await response.json()
      if (result.ok) {
        setSoulPreview(result.data.soul_markdown)
        setCurrentStep('distill')
        toast.success('SOUL生成成功')
      } else {
        toast.error('生成失败')
      }
    } catch (error) {
      toast.error('网络错误')
    } finally {
      setIsDistilling(false)
    }
  }

  const saveSoul = async () => {
    if (!soulPreview) {
      toast.error('没有可保存的SOUL')
      return
    }

    try {
      const response = await fetch('/api/souls/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bro_name: broName,
          soul_markdown: soulPreview
        })
      })
      
      const result = await response.json()
      if (result.ok) {
        toast.success('SOUL保存成功')
        navigate('/')
      } else {
        toast.error('保存失败')
      }
    } catch (error) {
      toast.error('网络错误')
    }
  }

  const reparse = () => {
    setCurrentStep('upload')
    setParsedData(null)
    setSoulPreview('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link
                to="/"
                className="inline-flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeft className="h-5 w-5 mr-2" />
                返回
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">创建SOUL</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          {[
            { key: 'upload', label: '上传记录', icon: Upload },
            { key: 'parse', label: '解析数据', icon: Settings },
            { key: 'distill', label: '生成SOUL', icon: Eye },
            { key: 'preview', label: '预览保存', icon: Save }
          ].map((step, index) => {
            const Icon = step.icon
            const isActive = currentStep === step.key
            const isCompleted = ['parse', 'distill', 'preview'].includes(currentStep) && 
              ['upload', 'parse', 'distill'].indexOf(step.key) < ['upload', 'parse', 'distill'].indexOf(currentStep)
            
            return (
              <div key={step.key} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                  isActive ? 'bg-indigo-600 text-white' : 
                  isCompleted ? 'bg-green-600 text-white' : 
                  'bg-gray-200 text-gray-600'
                }`}>
                  <Icon className="h-5 w-5" />
                </div>
                <span className={`ml-2 text-sm font-medium ${
                  isActive ? 'text-indigo-600' : 
                  isCompleted ? 'text-green-600' : 
                  'text-gray-500'
                }`}>
                  {step.label}
                </span>
                {index < 3 && (
                  <div className={`ml-4 w-16 h-0.5 ${
                    isCompleted ? 'bg-green-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            )
          })}
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-md p-8">
          {currentStep === 'upload' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  兄弟名称
                </label>
                <input
                  type="text"
                  value={broName}
                  onChange={(e) => setBroName(e.target.value)}
                  placeholder="输入在聊天记录中 你兄弟的id"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  聊天平台
                </label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="qq">QQ</option>
                  <option value="wechat">微信</option>
                  <option value="telegram">Telegram</option>
                </select>
              </div>

              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={textOnly}
                    onChange={(e) => setTextOnly(e.target.checked)}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">仅处理文本消息</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  聊天记录
                </label>
                <textarea
                  value={chatLog}
                  onChange={handleFileUpload}
                  placeholder="粘贴你的聊天记录内容..."
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
                <p className="mt-1 text-sm text-gray-500">
                  支持文本格式的聊天记录，建议包含完整的对话上下文
                </p>
              </div>

              <div className="flex justify-end space-x-4">
                <button
                  onClick={parseChatLog}
                  disabled={isParsing || !chatLog.trim() || !broName.trim()}
                  className="inline-flex items-center px-6 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  {isParsing ? (
                    <>
                      <RefreshCw className="animate-spin h-4 w-4 mr-2" />
                      解析中...
                    </>
                  ) : (
                    <>
                      <Settings className="h-4 w-4 mr-2" />
                      解析聊天记录
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {currentStep === 'parse' && parsedData && (
            <div className="space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-green-800 mb-2">解析结果</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-green-700">平台：</span>
                    <span className="text-green-600">{parsedData.type ?? type}</span>
                  </div>
                  <div>
                    <span className="font-medium text-green-700">消息数：</span>
                    <span className="text-green-600">{parsedData.messages_count ?? 0}</span>
                  </div>
                  <div>
                    <span className="font-medium text-green-700">参与者：</span>
                    <span className="text-green-600">{parsedData.participants?.join(', ') ?? '-'}</span>
                  </div>
                  <div>
                    <span className="font-medium text-green-700">解析时间：</span>
                    <span className="text-green-600">
                      {parsedData.parsed_at ? new Date(parsedData.parsed_at).toLocaleString() : '-'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex justify-between space-x-4">
                <button
                  onClick={reparse}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  重新解析
                </button>
                <button
                  onClick={distillSoul}
                  disabled={isDistilling}
                  className="inline-flex items-center px-6 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  {isDistilling ? (
                    <>
                      <RefreshCw className="animate-spin h-4 w-4 mr-2" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <Eye className="h-4 w-4 mr-2" />
                      开始蒸馏
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {currentStep === 'distill' && soulPreview && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">SOUL预览</h3>
                <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap">{soulPreview}</pre>
                </div>
              </div>

              <div className="flex justify-between space-x-4">
                <button
                  onClick={reparse}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  重新解析
                </button>
                <button
                  onClick={() => setCurrentStep('preview')}
                  className="inline-flex items-center px-6 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <Save className="h-4 w-4 mr-2" />
                  确认并保存
                </button>
              </div>
            </div>
          )}

          {currentStep === 'preview' && soulPreview && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-blue-800 mb-2">最终确认</h3>
                <p className="text-blue-700 mb-4">
                  你即将保存 {broName} 的SOUL人格。保存后可以在主界面查看并与TA对话。
                </p>
                <div className="bg-white rounded p-3 max-h-32 overflow-y-auto">
                  <pre className="text-xs text-gray-600">{soulPreview.substring(0, 500)}...</pre>
                </div>
              </div>

              <div className="flex justify-end space-x-4">
                <Link
                  to="/"
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  取消
                </Link>
                <button
                  onClick={saveSoul}
                  className="inline-flex items-center px-6 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <Save className="h-4 w-4 mr-2" />
                  保存SOUL
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
