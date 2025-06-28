"""
وحدة معالجة الصوت وتحويله إلى نص باستخدام Whisper
"""

import whisper
import torch
import librosa
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import logging
from config.settings import WHISPER_CONFIG, AUDIO_CONFIG

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    فئة معالجة الصوت وتحويله إلى نص مع الحفاظ على الطوابع الزمنية
    """
    
    def __init__(self, model_size: str = None):
        """
        تهيئة معالج الصوت
        
        Args:
            model_size: حجم نموذج Whisper (tiny, base, small, medium, large)
        """
        self.model_size = model_size or WHISPER_CONFIG["model_size"]
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"تم تهيئة معالج الصوت باستخدام: {self.device}")
        
    def load_model(self):
        """تحميل نموذج Whisper"""
        try:
            logger.info(f"جاري تحميل نموذج Whisper: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info("تم تحميل النموذج بنجاح")
        except Exception as e:
            logger.error(f"خطأ في تحميل النموذج: {e}")
            raise
    
    def validate_audio_file(self, file_path: Path) -> bool:
        """
        التحقق من صحة ملف الصوت
        
        Args:
            file_path: مسار ملف الصوت
            
        Returns:
            True إذا كان الملف صالحاً، False خلاف ذلك
        """
        try:
            # التحقق من وجود الملف
            if not file_path.exists():
                logger.error(f"الملف غير موجود: {file_path}")
                return False
            
            # التحقق من امتداد الملف
            if file_path.suffix.lower() not in AUDIO_CONFIG["supported_formats"]:
                logger.error(f"تنسيق الملف غير مدعوم: {file_path.suffix}")
                return False
            
            # التحقق من حجم الملف
            file_size = file_path.stat().st_size
            if file_size > AUDIO_CONFIG["max_file_size"]:
                logger.error(f"حجم الملف كبير جداً: {file_size / (1024*1024):.1f} MB")
                return False
            
            # محاولة قراءة الملف
            audio, sr = librosa.load(str(file_path), sr=None, duration=1.0)
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الملف: {e}")
            return False
    
    def preprocess_audio(self, file_path: Path) -> np.ndarray:
        """
        معالجة مسبقة للصوت
        
        Args:
            file_path: مسار ملف الصوت
            
        Returns:
            البيانات الصوتية المعالجة
        """
        try:
            logger.info(f"جاري معالجة الملف الصوتي: {file_path.name}")
            
            # تحميل الصوت بمعدل أخذ العينات المطلوب
            audio, _ = librosa.load(
                str(file_path), 
                sr=AUDIO_CONFIG["sample_rate"],
                mono=True
            )
            
            # تطبيع الصوت
            audio = librosa.util.normalize(audio)
            
            # إزالة الصمت من البداية والنهاية
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            logger.info(f"تم معالجة الصوت: المدة = {len(audio) / AUDIO_CONFIG['sample_rate']:.1f} ثانية")
            
            return audio
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الصوت: {e}")
            raise
    
    def transcribe_audio(self, file_path: Path, return_segments: bool = True) -> Dict:
        """
        تحويل الصوت إلى نص مع الطوابع الزمنية
        
        Args:
            file_path: مسار ملف الصوت
            return_segments: إرجاع الأجزاء مع الطوابع الزمنية
            
        Returns:
            قاموس يحتوي على النص والأجزاء
        """
        try:
            # تحميل النموذج إذا لم يكن محملاً
            if self.model is None:
                self.load_model()
            
            # التحقق من صحة الملف
            if not self.validate_audio_file(file_path):
                raise ValueError("ملف الصوت غير صالح")
            
            # معالجة الصوت
            audio = self.preprocess_audio(file_path)
            
            # تحويل إلى نص
            logger.info("جاري تحويل الصوت إلى نص...")
            
            result = self.model.transcribe(
                audio,
                language=WHISPER_CONFIG["language"],
                temperature=WHISPER_CONFIG["temperature"],
                best_of=WHISPER_CONFIG["best_of"],
                verbose=False
            )
            
            # تنظيم النتائج
            transcription = {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": []
            }
            
            if return_segments and "segments" in result:
                for segment in result["segments"]:
                    transcription["segments"].append({
                        "id": segment["id"],
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"].strip(),
                        "confidence": segment.get("avg_logprob", 0.0)
                    })
            
            logger.info(f"تم تحويل الصوت بنجاح: {len(transcription['text'])} حرف")
            
            return transcription
            
        except Exception as e:
            logger.error(f"خطأ في تحويل الصوت إلى نص: {e}")
            raise
    
    def chunk_segments_by_time(self, segments: List[Dict], chunk_duration: int = None) -> List[Dict]:
        """
        تجزئة الأجزاء حسب الوقت
        
        Args:
            segments: قائمة الأجزاء
            chunk_duration: مدة كل جزء بالثواني
            
        Returns:
            قائمة الأجزاء المجمعة
        """
        chunk_duration = chunk_duration or AUDIO_CONFIG["chunk_duration"]
        chunks = []
        current_chunk = {
            "start": 0,
            "end": 0,
            "text": "",
            "segments": []
        }
        
        for segment in segments:
            # إذا تجاوز الجزء الحالي المدة المحددة، ابدأ جزءً جديداً
            if segment["end"] - current_chunk["start"] > chunk_duration and current_chunk["text"]:
                chunks.append(current_chunk.copy())
                current_chunk = {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"],
                    "segments": [segment]
                }
            else:
                # أضف إلى الجزء الحالي
                if not current_chunk["text"]:
                    current_chunk["start"] = segment["start"]
                
                current_chunk["end"] = segment["end"]
                current_chunk["text"] += " " + segment["text"]
                current_chunk["segments"].append(segment)
        
        # أضف الجزء الأخير إذا كان يحتوي على نص
        if current_chunk["text"]:
            chunks.append(current_chunk)
        
        # تنظيف النصوص
        for chunk in chunks:
            chunk["text"] = chunk["text"].strip()
        
        logger.info(f"تم تجزئة الصوت إلى {len(chunks)} جزء")
        
        return chunks
    
    def save_transcription(self, transcription: Dict, output_path: Path):
        """
        حفظ نتائج التحويل في ملف JSON
        
        Args:
            transcription: نتائج التحويل
            output_path: مسار ملف الحفظ
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcription, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم حفظ النتائج في: {output_path}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ النتائج: {e}")
            raise
    
    def process_lecture(self, file_path: Path, output_dir: Path = None) -> Dict:
        """
        معالجة محاضرة كاملة وإرجاع النتائج المنظمة
        
        Args:
            file_path: مسار ملف الصوت
            output_dir: مجلد الحفظ
            
        Returns:
            نتائج المعالجة الكاملة
        """
        try:
            # تحويل الصوت إلى نص
            transcription = self.transcribe_audio(file_path)
            
            # تجزئة الأجزاء
            chunks = self.chunk_segments_by_time(transcription["segments"])
            
            # تنظيم النتائج النهائية
            result = {
                "file_name": file_path.name,
                "full_text": transcription["text"],
                "language": transcription["language"],
                "total_duration": transcription["segments"][-1]["end"] if transcription["segments"] else 0,
                "chunks": chunks,
                "segments": transcription["segments"]
            }
            
            # حفظ النتائج إذا تم تحديد مجلد الحفظ
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / f"{file_path.stem}_transcription.json"
                self.save_transcription(result, output_file)
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في معالجة المحاضرة: {e}")
            raise

# مثال على الاستخدام
if __name__ == "__main__":
    processor = AudioProcessor()
    
    # مثال على معالجة ملف صوتي
    # audio_file = Path("sample_lecture.mp3")
    # result = processor.process_lecture(audio_file)
    # print(f"تم تحويل {result['file_name']} بنجاح!")
    # print(f"النص الكامل: {result['full_text'][:200]}...")
