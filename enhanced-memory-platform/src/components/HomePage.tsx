import { useState, useRef } from 'react'
import { Upload, FileAudio, Brain, Lightbulb, Search, Target, Clock, CheckCircle } from 'lucide-react'

interface HomePageProps {
  onFileUpload: (file: File) => void
}

const HomePage = ({ onFileUpload }: HomePageProps) => {
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (isValidAudioFile(file)) {
        onFileUpload(file)
      } else {
        alert('يرجى رفع ملف صوتي صالح (MP3, WAV, M4A)')
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (isValidAudioFile(file)) {
        onFileUpload(file)
      } else {
        alert('يرجى رفع ملف صوتي صالح (MP3, WAV, M4A)')
      }
    }
  }

  const isValidAudioFile = (file: File) => {
    const validTypes = ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/mp4']
    const validExtensions = ['.mp3', '.wav', '.m4a']
    return validTypes.includes(file.type) || validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
  }

  const features = [
    {
      icon: <FileAudio className="w-8 h-8 text-memory-blue-600" />,
      title: "تحويل صوتي متقدم",
      description: "تحويل المحاضرات الصوتية إلى نصوص مكتوبة بدقة عالية باستخدام تقنية Whisper"
    },
    {
      icon: <Brain className="w-8 h-8 text-memory-green-600" />,
      title: "تلخيص ذكي",
      description: "تلخيص المحاضرات بمستويات مختلفة من التفصيل باستخدام الذكاء الاصطناعي"
    },
    {
      icon: <Target className="w-8 h-8 text-orange-600" />,
      title: "بنك أسئلة تلقائي",
      description: "توليد أسئلة متنوعة واختبارات تدريبية من محتوى المحاضرة"
    },
    {
      icon: <Search className="w-8 h-8 text-purple-600" />,
      title: "بحث دلالي ذكي",
      description: "البحث في المحاضرة باللغة الطبيعية والحصول على نتائج دقيقة"
    },
    {
      icon: <Lightbulb className="w-8 h-8 text-yellow-600" />,
      title: "خرائط المفاهيم",
      description: "إنشاء خرائط مفاهيم تفاعلية تربط بين الأفكار الرئيسية"
    },
    {
      icon: <Clock className="w-8 h-8 text-red-600" />,
      title: "معالجة سريعة",
      description: "معالجة الملفات الصوتية بسرعة وكفاءة عالية"
    }
  ]

  const steps = [
    {
      step: "1",
      title: "رفع الملف الصوتي",
      description: "قم برفع ملف المحاضرة الصوتية بتنسيق MP3 أو WAV أو M4A"
    },
    {
      step: "2", 
      title: "المعالجة التلقائية",
      description: "انتظر بينما نقوم بتحويل الصوت ومعالجة المحتوى بالذكاء الاصطناعي"
    },
    {
      step: "3",
      title: "استلام النتائج",
      description: "احصل على النص المكتوب والتلخيص والأسئلة وخريطة المفاهيم"
    }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 font-arabic">
            الذاكرة المعززة 
            <span className="bg-gradient-memory bg-clip-text text-transparent"> 2.0</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            حوّل محاضراتك الصوتية إلى مواد دراسة ذكية ومنظمة باستخدام أحدث تقنيات الذكاء الاصطناعي.
            احصل على النصوص والتلخيصات والأسئلة وخرائط المفاهيم في دقائق معدودة.
          </p>
        </div>

        {/* Upload Area */}
        <div className="max-w-2xl mx-auto">
          <div
            className={`relative border-2 border-dashed rounded-xl p-12 transition-all duration-300 ${
              dragActive 
                ? 'border-memory-blue-500 bg-memory-blue-50' 
                : 'border-gray-300 bg-white hover:border-memory-blue-400 hover:bg-gray-50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".mp3,.wav,.m4a,audio/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <div className="text-center space-y-4">
              <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center ${
                dragActive ? 'bg-memory-blue-100' : 'bg-gray-100'
              }`}>
                <Upload className={`w-8 h-8 ${dragActive ? 'text-memory-blue-600' : 'text-gray-500'}`} />
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  اسحب وأفلت ملف المحاضرة هنا
                </h3>
                <p className="text-gray-600 mb-4">
                  أو اضغط لتحديد ملف من جهازك
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-3 btn-gradient text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300"
                >
                  اختيار ملف صوتي
                </button>
              </div>
              
              <div className="text-sm text-gray-500">
                الصيغ المدعومة: MP3, WAV, M4A (حتى 100 ميجابايت)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            مميزات المنصة
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            تقنيات متطورة لتحويل المحاضرات إلى مواد دراسة شاملة وفعالة
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 card-hover"
            >
              <div className="flex items-center space-x-reverse space-x-4 mb-4">
                <div className="flex-shrink-0">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {feature.title}
                </h3>
              </div>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* How it Works */}
      <div className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            كيف يعمل النظام؟
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            ثلاث خطوات بسيطة للحصول على مواد دراسة شاملة من محاضراتك
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="text-center space-y-4">
                <div className="mx-auto w-16 h-16 bg-gradient-blue rounded-full flex items-center justify-center text-white text-xl font-bold">
                  {step.step}
                </div>
                <h3 className="text-xl font-semibold text-gray-900">
                  {step.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white rounded-2xl p-8 border border-gray-200">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div className="space-y-2">
            <div className="text-3xl font-bold text-memory-blue-600">99%</div>
            <div className="text-gray-600">دقة التحويل الصوتي</div>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-memory-green-600">5 دقائق</div>
            <div className="text-gray-600">متوسط وقت المعالجة</div>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-orange-600">100+</div>
            <div className="text-gray-600">سؤال تلقائي</div>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-purple-600">24/7</div>
            <div className="text-gray-600">متاح دائماً</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
