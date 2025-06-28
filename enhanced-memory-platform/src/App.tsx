import { useState } from 'react'
import { Brain, Upload, FileAudio, Sparkles } from 'lucide-react'
import HomePage from './components/HomePage'
import ProcessingPage from './components/ProcessingPage'
import ResultsPage from './components/ResultsPage'
import { LectureData } from './types/lecture'

type AppState = 'home' | 'processing' | 'results'

function App() {
  const [currentState, setCurrentState] = useState<AppState>('home')
  const [lectureData, setLectureData] = useState<LectureData | null>(null)

  const handleFileUpload = (file: File) => {
    setCurrentState('processing')
    // محاكاة معالجة الملف
    setTimeout(() => {
      // تحميل البيانات التجريبية
      fetch('/data/sample-lecture.json')
        .then(response => response.json())
        .then(data => {
          setLectureData(data)
          setCurrentState('results')
        })
        .catch(error => {
          console.error('خطأ في تحميل البيانات:', error)
          setCurrentState('home')
        })
    }, 3000)
  }

  const handleBackToHome = () => {
    setCurrentState('home')
    setLectureData(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-reverse space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-blue rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 font-arabic">
                  الذاكرة المعززة 2.0
                </h1>
                <p className="text-sm text-gray-600">منصة تحويل المحاضرات إلى مواد دراسة ذكية</p>
              </div>
            </div>
            {currentState !== 'home' && (
              <button
                onClick={handleBackToHome}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200"
              >
                العودة للرئيسية
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentState === 'home' && (
          <HomePage onFileUpload={handleFileUpload} />
        )}
        
        {currentState === 'processing' && (
          <ProcessingPage />
        )}
        
        {currentState === 'results' && lectureData && (
          <ResultsPage lectureData={lectureData} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-center items-center space-x-reverse space-x-2 text-gray-600">
            <Sparkles className="w-5 h-5" />
            <span className="text-sm">مطور بتقنيات الذكاء الاصطناعي المتطورة</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
