import { useState } from 'react'
import { 
  HelpCircle, 
  CheckCircle, 
  XCircle, 
  Award, 
  RotateCcw, 
  Download,
  BookOpen,
  Target,
  Clock,
  Lightbulb
} from 'lucide-react'
import { Questions } from '../../types/lecture'

interface QuestionsTabProps {
  questions: Questions
}

type QuestionMode = 'multiple_choice' | 'open_ended' | 'mixed'

const QuestionsTab = ({ questions }: QuestionsTabProps) => {
  const [questionMode, setQuestionMode] = useState<QuestionMode>('multiple_choice')
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({})
  const [showExplanation, setShowExplanation] = useState<Record<number, boolean>>({})
  const [testMode, setTestMode] = useState(false)
  const [testCompleted, setTestCompleted] = useState(false)
  const [score, setScore] = useState(0)

  const mcQuestions = questions.multiple_choice
  const openQuestions = questions.open_ended

  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    if (testMode && testCompleted) return
    
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: answerIndex
    }))

    if (!testMode) {
      setShowExplanation(prev => ({
        ...prev,
        [questionIndex]: true
      }))
    }
  }

  const startTest = () => {
    setTestMode(true)
    setTestCompleted(false)
    setSelectedAnswers({})
    setShowExplanation({})
    setCurrentQuestionIndex(0)
    setScore(0)
  }

  const completeTest = () => {
    const correctAnswers = mcQuestions.reduce((acc, question, index) => {
      if (selectedAnswers[index] === question.correct_answer) {
        return acc + 1
      }
      return acc
    }, 0)
    
    setScore(correctAnswers)
    setTestCompleted(true)
    
    // إظهار جميع الشروحات
    const allExplanations = mcQuestions.reduce((acc, _, index) => ({
      ...acc,
      [index]: true
    }), {})
    setShowExplanation(allExplanations)
  }

  const resetTest = () => {
    setTestMode(false)
    setTestCompleted(false)
    setSelectedAnswers({})
    setShowExplanation({})
    setCurrentQuestionIndex(0)
    setScore(0)
  }

  const getScoreColor = () => {
    const percentage = (score / mcQuestions.length) * 100
    if (percentage >= 80) return 'text-green-600'
    if (percentage >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreMessage = () => {
    const percentage = (score / mcQuestions.length) * 100
    if (percentage >= 90) return 'ممتاز! أداء رائع 🎉'
    if (percentage >= 80) return 'جيد جداً! استمر في التطور 👏'
    if (percentage >= 70) return 'جيد! يمكنك التحسن أكثر 💪'
    if (percentage >= 60) return 'مقبول، راجع المادة مرة أخرى 📚'
    return 'يحتاج إلى مراجعة شاملة للمادة 🔄'
  }

  const questionModes = [
    {
      id: 'multiple_choice' as QuestionMode,
      label: 'اختيار متعدد',
      icon: <Target className="w-4 h-4" />,
      count: mcQuestions.length,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      id: 'open_ended' as QuestionMode,
      label: 'أسئلة مفتوحة',
      icon: <BookOpen className="w-4 h-4" />,
      count: openQuestions.length,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            بنك الأسئلة التفاعلي
          </h2>
          <p className="text-gray-600">
            أسئلة متنوعة تم إنشاؤها تلقائياً من محتوى المحاضرة
          </p>
        </div>

        <div className="flex items-center space-x-reverse space-x-2">
          {questionMode === 'multiple_choice' && !testMode && (
            <button
              onClick={startTest}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 flex items-center space-x-reverse space-x-2"
            >
              <Clock className="w-4 h-4" />
              <span>بدء اختبار</span>
            </button>
          )}
          
          {testMode && !testCompleted && (
            <button
              onClick={completeTest}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors duration-200 flex items-center space-x-reverse space-x-2"
            >
              <CheckCircle className="w-4 h-4" />
              <span>إنهاء الاختبار</span>
            </button>
          )}
          
          {testCompleted && (
            <button
              onClick={resetTest}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200 flex items-center space-x-reverse space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>إعادة المحاولة</span>
            </button>
          )}
        </div>
      </div>

      {/* Test Results */}
      {testCompleted && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
              <Award className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900">
              نتيجة الاختبار
            </h3>
            <div className={`text-4xl font-bold ${getScoreColor()}`}>
              {score} / {mcQuestions.length}
            </div>
            <div className={`text-lg font-semibold ${getScoreColor()}`}>
              {Math.round((score / mcQuestions.length) * 100)}%
            </div>
            <p className="text-gray-600">
              {getScoreMessage()}
            </p>
          </div>
        </div>
      )}

      {/* Question Mode Selector */}
      <div className="grid grid-cols-2 gap-4">
        {questionModes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => setQuestionMode(mode.id)}
            className={`p-4 rounded-lg border-2 transition-all duration-200 ${
              questionMode === mode.id
                ? `${mode.bgColor} border-current ${mode.color}`
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-reverse space-x-3">
                {mode.icon}
                <span className="font-semibold">{mode.label}</span>
              </div>
              <span className="text-2xl font-bold">{mode.count}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Multiple Choice Questions */}
      {questionMode === 'multiple_choice' && (
        <div className="space-y-6">
          {mcQuestions.map((question, questionIndex) => (
            <div key={questionIndex} className="bg-white rounded-xl border border-gray-200 p-6">
              {/* Question Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-reverse space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold text-sm">
                      {questionIndex + 1}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {question.question}
                  </h3>
                </div>
                
                {selectedAnswers[questionIndex] !== undefined && (
                  <div className={`p-2 rounded-lg ${
                    selectedAnswers[questionIndex] === question.correct_answer
                      ? 'bg-green-100 text-green-600'
                      : 'bg-red-100 text-red-600'
                  }`}>
                    {selectedAnswers[questionIndex] === question.correct_answer ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <XCircle className="w-5 h-5" />
                    )}
                  </div>
                )}
              </div>

              {/* Options */}
              <div className="space-y-3 mb-4">
                {question.options.map((option, optionIndex) => {
                  const isSelected = selectedAnswers[questionIndex] === optionIndex
                  const isCorrect = optionIndex === question.correct_answer
                  const showResult = showExplanation[questionIndex]

                  return (
                    <button
                      key={optionIndex}
                      onClick={() => handleAnswerSelect(questionIndex, optionIndex)}
                      disabled={testMode && testCompleted}
                      className={`w-full p-4 text-right rounded-lg border-2 transition-all duration-200 ${
                        showResult
                          ? isCorrect
                            ? 'border-green-500 bg-green-50 text-green-800'
                            : isSelected
                            ? 'border-red-500 bg-red-50 text-red-800'
                            : 'border-gray-200 bg-gray-50 text-gray-600'
                          : isSelected
                          ? 'border-blue-500 bg-blue-50 text-blue-800'
                          : 'border-gray-200 bg-white text-gray-800 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span>{option}</span>
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          showResult
                            ? isCorrect
                              ? 'border-green-500 bg-green-500'
                              : isSelected
                              ? 'border-red-500 bg-red-500'
                              : 'border-gray-300'
                            : isSelected
                            ? 'border-blue-500 bg-blue-500'
                            : 'border-gray-300'
                        }`}>
                          {((showResult && isCorrect) || (isSelected && !showResult)) && (
                            <CheckCircle className="w-4 h-4 text-white" />
                          )}
                          {(showResult && isSelected && !isCorrect) && (
                            <XCircle className="w-4 h-4 text-white" />
                          )}
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>

              {/* Explanation */}
              {showExplanation[questionIndex] && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start space-x-reverse space-x-2">
                    <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div className="text-blue-800">
                      <h4 className="font-semibold mb-1">الشرح:</h4>
                      <p>{question.explanation}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Open Ended Questions */}
      {questionMode === 'open_ended' && (
        <div className="space-y-6">
          {openQuestions.map((question, questionIndex) => (
            <div key={questionIndex} className="bg-white rounded-xl border border-gray-200 p-6">
              {/* Question */}
              <div className="flex items-start space-x-reverse space-x-3 mb-4">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-green-600 font-bold text-sm">
                    {questionIndex + 1}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {question.question}
                </h3>
              </div>

              {/* Answer Area */}
              <div className="mb-4">
                <textarea
                  placeholder="اكتب إجابتك هنا..."
                  rows={4}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-right resize-none"
                />
              </div>

              {/* Key Points */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2 flex items-center space-x-reverse space-x-2">
                  <Target className="w-4 h-4" />
                  <span>النقاط الرئيسية للإجابة:</span>
                </h4>
                <ul className="space-y-1 text-green-800">
                  {question.key_points.map((point, pointIndex) => (
                    <li key={pointIndex} className="flex items-start space-x-reverse space-x-2">
                      <span className="text-green-600 font-bold">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {mcQuestions.length}
          </div>
          <div className="text-sm text-gray-600">اختيار متعدد</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200 text-center">
          <div className="text-2xl font-bold text-green-600">
            {openQuestions.length}
          </div>
          <div className="text-sm text-gray-600">أسئلة مفتوحة</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {mcQuestions.length + openQuestions.length}
          </div>
          <div className="text-sm text-gray-600">إجمالي الأسئلة</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round((mcQuestions.length + openQuestions.length) * 2)}
          </div>
          <div className="text-sm text-gray-600">دقيقة متوقعة</div>
        </div>
      </div>
    </div>
  )
}

export default QuestionsTab
