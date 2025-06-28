import { useState, useEffect } from 'react'
import { 
  Search, 
  Clock, 
  TrendingUp, 
  Zap, 
  Filter, 
  SortAsc, 
  Eye,
  ChevronDown,
  ChevronUp,
  Star,
  BookOpen
} from 'lucide-react'
import { Transcription, SearchResult } from '../../types/lecture'

interface SearchTabProps {
  transcription: Transcription
  searchResults: SearchResult[]
}

const SearchTab = ({ transcription }: SearchTabProps) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [sortBy, setSortBy] = useState<'relevance' | 'time'>('relevance')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [searchHistory, setSearchHistory] = useState<string[]>([])
  const [selectedSegments, setSelectedSegments] = useState<Set<number>>(new Set())

  // استعلامات شائعة مقترحة
  const suggestedQueries = [
    'ما هو الذكاء الاصطناعي؟',
    'التعلم الآلي',
    'الشبكات العصبية',
    'التطبيقات العملية',
    'المستقبل والتحديات'
  ]

  // محاكاة البحث الدلالي
  const performSearch = (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    setIsSearching(true)
    
    // محاكاة تأخير البحث
    setTimeout(() => {
      const searchTerms = searchQuery.toLowerCase().split(' ')
      const searchResults: SearchResult[] = []

      transcription.segments.forEach((segment, index) => {
        const segmentText = segment.text.toLowerCase()
        let relevanceScore = 0

        // حساب نقاط الصلة
        searchTerms.forEach(term => {
          if (segmentText.includes(term)) {
            relevanceScore += 1
            // نقاط إضافية للمطابقة الدقيقة
            if (segmentText.includes(searchQuery.toLowerCase())) {
              relevanceScore += 2
            }
          }
        })

        if (relevanceScore > 0) {
          // إنشاء السياق (الجمل المحيطة)
          const context = getContext(segment.text, searchQuery)
          
          searchResults.push({
            segment: segment,
            score: relevanceScore / searchTerms.length,
            context: context
          })
        }
      })

      // ترتيب النتائج
      const sortedResults = searchResults.sort((a, b) => {
        if (sortBy === 'relevance') {
          return b.score - a.score
        } else {
          return a.segment.start.localeCompare(b.segment.start)
        }
      })

      setResults(sortedResults.slice(0, 10)) // أول 10 نتائج
      setIsSearching(false)

      // إضافة إلى التاريخ
      if (!searchHistory.includes(searchQuery)) {
        setSearchHistory(prev => [searchQuery, ...prev.slice(0, 4)])
      }
    }, 800)
  }

  const getContext = (text: string, query: string): string => {
    const queryIndex = text.toLowerCase().indexOf(query.toLowerCase())
    if (queryIndex === -1) return text.substring(0, 100) + '...'
    
    const start = Math.max(0, queryIndex - 50)
    const end = Math.min(text.length, queryIndex + query.length + 50)
    
    let context = text.substring(start, end)
    if (start > 0) context = '...' + context
    if (end < text.length) context = context + '...'
    
    return context
  }

  const highlightText = (text: string, query: string) => {
    if (!query) return text
    
    const regex = new RegExp(`(${query})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded font-semibold">
          {part}
        </mark>
      ) : part
    )
  }

  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery)
    performSearch(searchQuery)
  }

  const formatTime = (timeStr: string) => {
    return timeStr.substring(0, 8)
  }

  const toggleSegmentSelection = (index: number) => {
    setSelectedSegments(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  useEffect(() => {
    if (query) {
      performSearch(query)
    }
  }, [sortBy])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            البحث الذكي
          </h2>
          <p className="text-gray-600">
            ابحث في محتوى المحاضرة باللغة الطبيعية واحصل على نتائج دقيقة
          </p>
        </div>

        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center space-x-reverse space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200"
        >
          <Filter className="w-4 h-4" />
          <span>خيارات متقدمة</span>
          {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <Search className="w-5 h-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="ابحث في المحاضرة... مثل: ما هو التعلم الآلي؟"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSearch(query)
            }
          }}
          className="w-full pl-4 pr-12 py-4 text-lg border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-right"
        />
        <button
          onClick={() => handleSearch(query)}
          disabled={isSearching || !query.trim()}
          className="absolute left-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors duration-200 flex items-center space-x-reverse space-x-2"
        >
          {isSearching ? (
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
          ) : (
            <Zap className="w-4 h-4" />
          )}
          <span>{isSearching ? 'جاري البحث...' : 'بحث'}</span>
        </button>
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-reverse sm:space-x-4">
            <label className="text-sm font-medium text-gray-700">ترتيب النتائج:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'relevance' | 'time')}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="relevance">حسب الصلة</option>
              <option value="time">حسب الوقت</option>
            </select>
          </div>
        </div>
      )}

      {/* Suggested Queries */}
      {!query && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900">استعلامات مقترحة:</h3>
          <div className="flex flex-wrap gap-2">
            {suggestedQueries.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSearch(suggestion)}
                className="px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors duration-200 text-sm"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search History */}
      {searchHistory.length > 0 && !query && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900">عمليات البحث الأخيرة:</h3>
          <div className="flex flex-wrap gap-2">
            {searchHistory.map((historyQuery, index) => (
              <button
                key={index}
                onClick={() => handleSearch(historyQuery)}
                className="px-4 py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg transition-colors duration-200 text-sm flex items-center space-x-reverse space-x-2"
              >
                <Clock className="w-3 h-3" />
                <span>{historyQuery}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search Results */}
      {query && (
        <div className="space-y-4">
          {/* Results Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-reverse space-x-3">
              <h3 className="text-lg font-semibold text-gray-900">
                نتائج البحث
              </h3>
              {results.length > 0 && (
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                  {results.length} نتيجة
                </span>
              )}
            </div>
            
            {results.length > 0 && (
              <div className="flex items-center space-x-reverse space-x-2">
                <SortAsc className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  مرتب حسب {sortBy === 'relevance' ? 'الصلة' : 'الوقت'}
                </span>
              </div>
            )}
          </div>

          {/* Results List */}
          {isSearching ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mx-auto mb-4" />
              <p className="text-gray-600">جاري البحث في المحاضرة...</p>
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-4">
              {results.map((result, index) => (
                <div
                  key={index}
                  className={`bg-white rounded-xl border border-gray-200 p-6 transition-all duration-200 hover:shadow-md ${
                    selectedSegments.has(index) ? 'ring-2 ring-blue-500 border-blue-200' : ''
                  }`}
                >
                  <div className="flex items-start justify-between space-x-reverse space-x-4">
                    {/* Result Content */}
                    <div className="flex-1">
                      {/* Relevance Score */}
                      <div className="flex items-center space-x-reverse space-x-2 mb-2">
                        <div className="flex items-center space-x-reverse space-x-1">
                          <Star className="w-4 h-4 text-yellow-500" />
                          <span className="text-sm text-gray-600">
                            صلة: {Math.round(result.score * 100)}%
                          </span>
                        </div>
                        <div className="flex items-center space-x-reverse space-x-1">
                          <Clock className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-600">
                            {formatTime(result.segment.start)}
                          </span>
                        </div>
                      </div>

                      {/* Context */}
                      <div className="mb-3">
                        <p className="text-gray-800 leading-relaxed">
                          {highlightText(result.context, query)}
                        </p>
                      </div>

                      {/* Full Text Toggle */}
                      <button
                        onClick={() => toggleSegmentSelection(index)}
                        className="text-blue-600 hover:text-blue-700 text-sm flex items-center space-x-reverse space-x-1"
                      >
                        <Eye className="w-4 h-4" />
                        <span>
                          {selectedSegments.has(index) ? 'إخفاء النص الكامل' : 'عرض النص الكامل'}
                        </span>
                      </button>

                      {/* Full Text */}
                      {selectedSegments.has(index) && (
                        <div className="mt-3 p-4 bg-gray-50 rounded-lg">
                          <p className="text-gray-700 leading-relaxed">
                            {highlightText(result.segment.text, query)}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col space-y-2">
                      <button
                        className="p-2 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-lg transition-colors duration-200"
                        title="تشغيل من هذه النقطة"
                      >
                        <Clock className="w-4 h-4" />
                      </button>
                      <button
                        className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors duration-200"
                        title="إضافة للمفضلة"
                      >
                        <Star className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : query && !isSearching ? (
            <div className="text-center py-12">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-500 mb-2">
                لا توجد نتائج
              </h3>
              <p className="text-gray-400 mb-4">
                لم يتم العثور على نتائج لـ "{query}"
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <p>جرب:</p>
                <ul className="space-y-1">
                  <li>• استخدام كلمات مختلفة</li>
                  <li>• البحث بكلمات أقل</li>
                  <li>• التحقق من الإملاء</li>
                </ul>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* Search Tips */}
      {!query && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start space-x-reverse space-x-3">
            <TrendingUp className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-2">نصائح للبحث الفعال:</h4>
              <ul className="text-blue-800 space-y-1 text-sm">
                <li>• استخدم أسئلة طبيعية مثل "ما هو الذكاء الاصطناعي؟"</li>
                <li>• ابحث بالكلمات المفتاحية الرئيسية</li>
                <li>• جرب البحث بمرادفات مختلفة</li>
                <li>• استخدم عبارات قصيرة ومحددة</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {transcription.segments.length}
          </div>
          <div className="text-sm text-gray-600">مقطع قابل للبحث</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200 text-center">
          <div className="text-2xl font-bold text-green-600">
            {transcription.full_text.split(' ').length}
          </div>
          <div className="text-sm text-gray-600">كلمة مفهرسة</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {searchHistory.length}
          </div>
          <div className="text-sm text-gray-600">بحث سابق</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {results.length}
          </div>
          <div className="text-sm text-gray-600">نتيجة حالية</div>
        </div>
      </div>
    </div>
  )
}

export default SearchTab
