# إعدادات مشروع الذاكرة المعززة 2.0
"""
ملف الإعدادات الرئيسي للمشروع
"""

import os
from pathlib import Path

# المسارات الأساسية
BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

# إعدادات الصوت
AUDIO_CONFIG = {
    "max_file_size": 100 * 1024 * 1024,  # 100 MB
    "supported_formats": [".mp3", ".wav", ".m4a", ".flac"],
    "sample_rate": 16000,
    "chunk_duration": 30  # ثواني
}

# إعدادات Whisper
WHISPER_CONFIG = {
    "model_size": "base",  # يمكن تغييرها إلى small, medium, large
    "language": "ar",  # العربية
    "temperature": 0.1,
    "best_of": 1
}

# إعدادات معالجة النصوص
TEXT_CONFIG = {
    "max_chunk_size": 512,  # الحد الأقصى لحجم النص المجزأ
    "overlap_size": 50,     # التداخل بين الأجزاء
    "min_sentence_length": 10
}

# إعدادات التضمين الدلالي
EMBEDDING_CONFIG = {
    "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "vector_size": 384,
    "similarity_threshold": 0.7
}

# إعدادات التلخيص
SUMMARIZATION_CONFIG = {
    "model_name": "facebook/mbart-large-50-many-to-many-mmt",
    "max_length": 512,
    "min_length": 50,
    "num_beams": 4,
    "temperature": 0.7
}

# إعدادات توليد الأسئلة
QUESTION_GENERATION_CONFIG = {
    "model_name": "google/mt5-base",
    "max_questions": 10,
    "min_answer_length": 3,
    "max_answer_length": 50
}

# إعدادات خريطة المفاهيم
CONCEPT_MAP_CONFIG = {
    "max_concepts": 20,
    "min_relation_strength": 0.5,
    "layout_algorithm": "spring",
    "node_size_factor": 1000
}

# إعدادات الواجهة
UI_CONFIG = {
    "page_title": "الذاكرة المعززة 2.0",
    "page_icon": "🧠",
    "layout": "wide",
    "sidebar_state": "expanded"
}

# إعدادات قاعدة البيانات
DATABASE_CONFIG = {
    "type": "sqlite",
    "name": "enhanced_memory.db",
    "path": DATA_DIR / "enhanced_memory.db"
}

# إنشاء المجلدات إذا لم تكن موجودة
for directory in [UPLOADS_DIR, MODELS_DIR, DATA_DIR, STATIC_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
