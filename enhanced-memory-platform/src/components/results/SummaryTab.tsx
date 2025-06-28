import { useState } from 'react'
import { BookOpen, List, FileText, Target, Copy, Check } from 'lucide-react'
import { Summaries } from '../../types/lecture'

interface SummaryTabProps {
  summaries: Summaries
}

type SummaryType = 'brief' | 'medium' | 'detailed' | 'key_points'

const SummaryTab = ({ summaries }: SummaryTabProps) => {
  const [activeSummary, setActiveSummary] = useState<SummaryType>('medium')
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({})

  const summaryTypes = [
    {
      id: 'brief' as SummaryType,
      label: 'ملخص مختصر',
      icon: <Target className="w-4 h-4" />,
      description: 'نظرة سريعة على المحتوى الأساسي',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200'
    },
    {
      id: 'medium' as SummaryType,
      label: 'ملخص متوسط',
      icon: <BookOpen className="w-4 h-4" />,
      description: 'تفاصيل مناسبة للمراجعة',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200'
    },
    {
      id: 'detailed' as SummaryType,
      label: 'ملخص مفصل',
      icon: <FileText className="w-4 h-4" />,
      description: 'شرح شامل لجميع النقاط',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200'
    },
    {
      id: 'key_points' as SummaryType,
      label: 'النقاط الرئيسية',
      icon: <List className="w-4 h-4" />,
      description: 'أهم الأفكار في نقاط منظمة',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200'
    }
  ]

  const handleCopy = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedStates(prev => ({ ...prev, [type]: true }))
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [type]: false }))
      }, 2000)
    } catch (error) {
      console.error('فشل في النسخ:', error)
    }
  }

  const getCurrentSummary = () => {
    switch (activeSummary) {
      case 'brief':
        return summaries.brief
      case 'medium':
        return summaries.medium
      case 'detailed':
        return summaries.detailed
      case 'key_points':
        return summaries.key_points
      default:
        return summaries.medium
    }
  }

  const activeType = summaryTypes.find(type => type.id === activeSummary)!

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            التلخيص الذكي
          </h2>
          <p className="text-gray-600">
            ملخصات متعددة المستويات تم إنشاؤها بواسطة الذكاء الاصطناعي
          </p>
        </div>
        
        <button
          onClick={() => handleCopy(
            activeSummary === 'key_points' 
              ? summaries.key_points.join('\n• ') 
              : getCurrentSummary() as string,
            activeSummary
          )}
          className={`px-4 py-2 rounded-lg transition-all duration-200 flex items-center space-x-reverse space-x-2 ${
            copiedStates[activeSummary]
              ? 'bg-green-100 text-green-700 border border-green-200'
              : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-200'
          }`}
        >
          {copiedStates[activeSummary] ? (
            <>
              <Check className="w-4 h-4" />
              <span>تم النسخ</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>نسخ</span>
            </>
          )}
        </button>
      </div>

      {/* Summary Type Selector */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => setActiveSummary(type.id)}
            className={`p-4 rounded-lg border-2 transition-all duration-200 text-right ${
              activeSummary === type.id
                ? `${type.bgColor} ${type.borderColor} ${type.color}`
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center space-x-reverse space-x-3 mb-2">
              <div className={`p-2 rounded-lg ${
                activeSummary === type.id ? type.bgColor : 'bg-gray-100'
              }`}>
                {type.icon}
              </div>
              <h3 className="font-semibold text-sm">{type.label}</h3>
            </div>
            <p className="text-xs text-gray-500">{type.description}</p>
          </button>
        ))}
      </div>

      {/* Summary Content */}
      <div className={`rounded-xl border-2 ${activeType.borderColor} ${activeType.bgColor} p-6`}>
        <div className="flex items-center space-x-reverse space-x-3 mb-4">
          <div className={`p-3 rounded-lg ${activeType.bgColor}`}>
            {activeType.icon}
          </div>
          <h3 className={`text-xl font-bold ${activeType.color}`}>
            {activeType.label}
          </h3>
        </div>

        {activeSummary === 'key_points' ? (
          <div className="space-y-3">
            {summaries.key_points.map((point, index) => (
              <div key={index} className="flex items-start space-x-reverse space-x-3">
                <div className={`w-6 h-6 rounded-full ${activeType.color.replace('text-', 'bg-').replace('600', '100')} flex items-center justify-center flex-shrink-0 mt-1`}>
                  <span className={`text-sm font-bold ${activeType.color}`}>
                    {index + 1}
                  </span>
                </div>
                <p className="text-gray-800 leading-relaxed text-right flex-1">
                  {point}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="prose prose-lg max-w-none text-right">
            <p className="text-gray-800 leading-relaxed whitespace-pre-line">
              {getCurrentSummary()}
            </p>
          </div>
        )}
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {summaries.brief.split(' ').length}
          </div>
          <div className="text-sm text-gray-600">كلمة (مختصر)</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
          <div className="text-2xl font-bold text-green-600">
            {summaries.medium.split(' ').length}
          </div>
          <div className="text-sm text-gray-600">كلمة (متوسط)</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {summaries.detailed.split(' ').length}
          </div>
          <div className="text-sm text-gray-600">كلمة (مفصل)</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {summaries.key_points.length}
          </div>
          <div className="text-sm text-gray-600">نقطة رئيسية</div>
        </div>
      </div>
    </div>
  )
}

export default SummaryTab
