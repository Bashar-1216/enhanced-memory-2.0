import { useState, useEffect } from 'react'
import { FileAudio, Brain, Search, Target, Lightbulb, CheckCircle, Loader2 } from 'lucide-react'

const ProcessingPage = () => {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)

  const steps = [
    {
      id: 'upload',
      title: 'رفع الملف',
      description: 'جاري رفع ملف المحاضرة...',
      icon: <FileAudio className="w-6 h-6" />,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      id: 'transcription',
      title: 'تحويل الصوت لنص',
      description: 'تحويل المحاضرة الصوتية إلى نص باستخدام Whisper AI...',
      icon: <Brain className="w-6 h-6" />,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      id: 'search_index',
      title: 'بناء فهرس البحث',
      description: 'إنشاء فهرس بحث ذكي للمحتوى...',
      icon: <Search className="w-6 h-6" />,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      id: 'summarization',
      title: 'التلخيص الذكي',
      description: 'إنشاء تلخيصات متعددة المستويات...',
      icon: <Target className="w-6 h-6" />,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    },
    {
      id: 'questions',
      title: 'توليد الأسئلة',
      description: 'إنشاء بنك أسئلة تدريبية...',
      icon: <Lightbulb className="w-6 h-6" />,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    },
    {
      id: 'concept_map',
      title: 'خريطة المفاهيم',
      description: 'رسم خريطة المفاهيم التفاعلية...',
      icon: <CheckCircle className="w-6 h-6" />,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-100'
    }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          return prev
        }
        const newProgress = prev + 2
        
        // تحديث الخطوة الحالية بناءً على التقدم
        const stepIndex = Math.floor((newProgress / 100) * steps.length)
        setCurrentStep(Math.min(stepIndex, steps.length - 1))
        
        return newProgress
      })
    }, 100)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-[600px] flex items-center justify-center">
      <div className="max-w-4xl mx-auto text-center space-y-12">
        {/* Header */}
        <div className="space-y-4">
          <div className="mx-auto w-20 h-20 bg-gradient-blue rounded-full flex items-center justify-center animate-pulse-soft">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">
            جاري معالجة المحاضرة...
          </h1>
          <p className="text-lg text-gray-600">
            يتم الآن تحليل المحاضرة وإنشاء المواد التعليمية بتقنيات الذكاء الاصطناعي
          </p>
        </div>

        {/* Progress Bar */}
        <div className="space-y-4">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <span>التقدم</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-gradient-blue h-3 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-6">
          {steps.map((step, index) => {
            const isCompleted = index < currentStep
            const isCurrent = index === currentStep
            const isPending = index > currentStep

            return (
              <div 
                key={step.id}
                className={`flex items-center space-x-reverse space-x-4 p-4 rounded-lg transition-all duration-300 ${
                  isCompleted ? 'bg-green-50 border border-green-200' :
                  isCurrent ? 'bg-blue-50 border border-blue-200 animate-fade-in' :
                  'bg-gray-50 border border-gray-200'
                }`}
              >
                {/* Icon */}
                <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
                  isCompleted ? 'bg-green-100 text-green-600' :
                  isCurrent ? `${step.bgColor} ${step.color}` :
                  'bg-gray-200 text-gray-400'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : isCurrent ? (
                    <div className="flex items-center space-x-reverse space-x-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      {step.icon}
                    </div>
                  ) : (
                    step.icon
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 text-right">
                  <h3 className={`text-lg font-semibold ${
                    isCompleted ? 'text-green-900' :
                    isCurrent ? 'text-blue-900' :
                    'text-gray-500'
                  }`}>
                    {step.title}
                  </h3>
                  <p className={`text-sm ${
                    isCompleted ? 'text-green-700' :
                    isCurrent ? 'text-blue-700' :
                    'text-gray-400'
                  }`}>
                    {isCompleted ? 'تم بنجاح ✓' : step.description}
                  </p>
                </div>

                {/* Status Indicator */}
                <div className="flex-shrink-0">
                  {isCompleted && (
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  )}
                  {isCurrent && (
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                  )}
                  {isPending && (
                    <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Processing Info */}
        <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            ما يتم إنجازه الآن:
          </h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div className="flex items-center space-x-reverse space-x-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>تحليل الملف الصوتي</span>
            </div>
            <div className="flex items-center space-x-reverse space-x-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>استخراج النصوص بدقة عالية</span>
            </div>
            <div className="flex items-center space-x-reverse space-x-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>إنشاء تلخيصات ذكية</span>
            </div>
            <div className="flex items-center space-x-reverse space-x-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>توليد أسئلة تفاعلية</span>
            </div>
          </div>
        </div>

        {/* Estimated Time */}
        <div className="text-center text-gray-500">
          <p className="text-sm">
            الوقت المتوقع للانتهاء: دقيقتان إضافيتان
          </p>
        </div>
      </div>
    </div>
  )
}

export default ProcessingPage
