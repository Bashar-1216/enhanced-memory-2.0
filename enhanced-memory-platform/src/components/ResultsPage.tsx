import { useState } from 'react'
import { 
  FileText, 
  Brain, 
  HelpCircle, 
  GitBranch, 
  Search, 
  Download,
  Play,
  Pause,
  SkipForward,
  Volume2,
  BookOpen,
  Target,
  CheckCircle2,
  X
} from 'lucide-react'
import { LectureData } from '../types/lecture'
import TranscriptionTab from './results/TranscriptionTab'
import SummaryTab from './results/SummaryTab'
import QuestionsTab from './results/QuestionsTab'
import ConceptMapTab from './results/ConceptMapTab'
import SearchTab from './results/SearchTab'

interface ResultsPageProps {
  lectureData: LectureData
}

type TabType = 'transcription' | 'summary' | 'questions' | 'concept-map' | 'search'

const ResultsPage = ({ lectureData }: ResultsPageProps) => {
  const [activeTab, setActiveTab] = useState<TabType>('summary')
  const [isPlaying, setIsPlaying] = useState(false)

  const tabs = [
    {
      id: 'summary' as TabType,
      label: 'التلخيص',
      icon: <Brain className="w-5 h-5" />,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      id: 'transcription' as TabType,
      label: 'النص الكامل',
      icon: <FileText className="w-5 h-5" />,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      id: 'questions' as TabType,
      label: 'بنك الأسئلة',
      icon: <HelpCircle className="w-5 h-5" />,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    },
    {
      id: 'concept-map' as TabType,
      label: 'خريطة المفاهيم',
      icon: <GitBranch className="w-5 h-5" />,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      id: 'search' as TabType,
      label: 'البحث الذكي',
      icon: <Search className="w-5 h-5" />,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50'
    }
  ]

  const handleDownload = (type: string) => {
    // محاكاة تحميل الملفات
    const data = type === 'pdf' ? lectureData.summaries : lectureData
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${lectureData.title}_${type}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between space-y-4 md:space-y-0">
          {/* Lecture Info */}
          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-gray-900">
              {lectureData.title}
            </h1>
            <div className="flex items-center space-x-reverse space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-reverse space-x-1">
                <Volume2 className="w-4 h-4" />
                <span>المدة: {lectureData.duration}</span>
              </div>
              <div className="flex items-center space-x-reverse space-x-1">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <span>تمت المعالجة بنجاح</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-reverse space-x-2">
            <button
              onClick={() => handleDownload('pdf')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 flex items-center space-x-reverse space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>تحميل PDF</span>
            </button>
            <button
              onClick={() => handleDownload('json')}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200 flex items-center space-x-reverse space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>تحميل JSON</span>
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {lectureData.transcription.segments.length}
            </div>
            <div className="text-sm text-gray-600">مقطع نصي</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {lectureData.summaries.key_points.length}
            </div>
            <div className="text-sm text-gray-600">نقطة رئيسية</div>
          </div>
          <div className="text-center p-3 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {lectureData.questions.multiple_choice.length + lectureData.questions.open_ended.length}
            </div>
            <div className="text-sm text-gray-600">سؤال</div>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {lectureData.concept_map.nodes.length}
            </div>
            <div className="text-sm text-gray-600">مفهوم</div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-reverse space-x-2 px-4 py-4 text-sm font-medium transition-colors duration-200 ${
                  activeTab === tab.id
                    ? `${tab.color} ${tab.bgColor} border-b-2 border-current`
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6 min-h-[500px]">
          {activeTab === 'transcription' && (
            <TranscriptionTab transcription={lectureData.transcription} />
          )}
          
          {activeTab === 'summary' && (
            <SummaryTab summaries={lectureData.summaries} />
          )}
          
          {activeTab === 'questions' && (
            <QuestionsTab questions={lectureData.questions} />
          )}
          
          {activeTab === 'concept-map' && (
            <ConceptMapTab conceptMap={lectureData.concept_map} />
          )}
          
          {activeTab === 'search' && (
            <SearchTab 
              transcription={lectureData.transcription}
              searchResults={lectureData.search_results}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default ResultsPage
