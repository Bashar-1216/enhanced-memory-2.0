import { useState } from 'react'
import { Clock, Play, Pause, Search, Copy, Check, FileText, Volume2 } from 'lucide-react'
import { Transcription } from '../../types/lecture'

interface TranscriptionTabProps {
  transcription: Transcription
}

const TranscriptionTab = ({ transcription }: TranscriptionTabProps) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [currentSegment, setCurrentSegment] = useState<number | null>(null)
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({})
  const [viewMode, setViewMode] = useState<'segments' | 'full'>('segments')

  const filteredSegments = transcription.segments.filter(segment =>
    segment.text.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCopy = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedStates(prev => ({ ...prev, [id]: true }))
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }))
      }, 2000)
    } catch (error) {
      console.error('فشل في النسخ:', error)
    }
  }

  const highlightText = (text: string, searchTerm: string) => {
    if (!searchTerm) return text
    
    const regex = new RegExp(`(${searchTerm})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {part}
        </mark>
      ) : part
    )
  }

  const formatTime = (timeStr: string) => {
    return timeStr.substring(0, 8) // تحويل من 00:00:00 إلى 00:00:00
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            النص الكامل للمحاضرة
          </h2>
          <p className="text-gray-600">
            النص المحول من الصوت مع الطوابع الزمنية
          </p>
        </div>

        <div className="flex items-center space-x-reverse space-x-2">
          <button
            onClick={() => setViewMode(viewMode === 'segments' ? 'full' : 'segments')}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200 flex items-center space-x-reverse space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>{viewMode === 'segments' ? 'عرض مستمر' : 'عرض مقطعي'}</span>
          </button>
          
          <button
            onClick={() => handleCopy(transcription.full_text, 'full')}
            className={`px-4 py-2 rounded-lg transition-all duration-200 flex items-center space-x-reverse space-x-2 ${
              copiedStates.full
                ? 'bg-green-100 text-green-700 border border-green-200'
                : 'bg-blue-100 hover:bg-blue-200 text-blue-700 border border-blue-200'
            }`}
          >
            {copiedStates.full ? (
              <>
                <Check className="w-4 h-4" />
                <span>تم النسخ</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>نسخ الكل</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <Search className="w-5 h-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="البحث في النص..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-4 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-right"
        />
        {searchTerm && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
            <span className="text-sm text-gray-500">
              {filteredSegments.length} نتيجة
            </span>
          </div>
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {transcription.full_text.split(' ').length}
          </div>
          <div className="text-sm text-gray-600">كلمة</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200 text-center">
          <div className="text-2xl font-bold text-green-600">
            {transcription.segments.length}
          </div>
          <div className="text-sm text-gray-600">مقطع</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {transcription.full_text.split('.').length}
          </div>
          <div className="text-sm text-gray-600">جملة</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round(transcription.full_text.split(' ').length / 150)}
          </div>
          <div className="text-sm text-gray-600">دقيقة قراءة</div>
        </div>
      </div>

      {/* Content */}
      {viewMode === 'full' ? (
        // Full Text View
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="prose prose-lg max-w-none text-right">
            <p className="text-gray-800 leading-relaxed whitespace-pre-line">
              {highlightText(transcription.full_text, searchTerm)}
            </p>
          </div>
        </div>
      ) : (
        // Segments View
        <div className="space-y-4">
          {(searchTerm ? filteredSegments : transcription.segments).map((segment, index) => (
            <div
              key={index}
              className={`bg-white rounded-xl border border-gray-200 p-6 transition-all duration-200 hover:shadow-md ${
                currentSegment === index ? 'ring-2 ring-blue-500 border-blue-200' : ''
              }`}
            >
              <div className="flex items-start justify-between space-x-reverse space-x-4">
                {/* Time and Controls */}
                <div className="flex items-center space-x-reverse space-x-3 flex-shrink-0">
                  <div className="bg-gray-100 rounded-lg px-3 py-2 text-sm font-mono text-gray-600">
                    <div className="flex items-center space-x-reverse space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{formatTime(segment.start)}</span>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => setCurrentSegment(currentSegment === index ? null : index)}
                    className="p-2 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-lg transition-colors duration-200"
                    title="تشغيل/إيقاف"
                  >
                    {currentSegment === index ? (
                      <Pause className="w-4 h-4" />
                    ) : (
                      <Play className="w-4 h-4" />
                    )}
                  </button>

                  <button
                    onClick={() => handleCopy(segment.text, `segment-${index}`)}
                    className={`p-2 rounded-lg transition-colors duration-200 ${
                      copiedStates[`segment-${index}`]
                        ? 'bg-green-100 text-green-600'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                    }`}
                    title="نسخ"
                  >
                    {copiedStates[`segment-${index}`] ? (
                      <Check className="w-4 h-4" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>

                {/* Text Content */}
                <div className="flex-1 text-right">
                  <p className="text-gray-800 leading-relaxed">
                    {highlightText(segment.text, searchTerm)}
                  </p>
                  
                  {/* Duration */}
                  <div className="mt-2 text-xs text-gray-500">
                    المدة: {formatTime(segment.start)} - {formatTime(segment.end)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results */}
      {searchTerm && filteredSegments.length === 0 && (
        <div className="text-center py-12">
          <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-500 mb-2">
            لا توجد نتائج
          </h3>
          <p className="text-gray-400">
            لم يتم العثور على "{searchTerm}" في النص
          </p>
        </div>
      )}
    </div>
  )
}

export default TranscriptionTab
