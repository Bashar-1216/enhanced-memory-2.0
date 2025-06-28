"""
خط الأنابيب المتكامل لمشروع الذاكرة المعززة 2.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import uuid

from .audio_processor import AudioProcessor
from .semantic_search import SemanticSearchEngine
from .text_summarizer import TextSummarizer
from .question_generator import QuestionGenerator
from .concept_mapper import ConceptMapper
from config.settings import *

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMemoryPipeline:
    """
    خط الأنابيب المتكامل لمعالجة المحاضرات وتحويلها إلى مواد دراسة ذكية
    """
    
    def __init__(self):
        """تهيئة خط الأنابيب"""
        self.session_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        
        # تهيئة المكونات
        self.audio_processor = AudioProcessor()
        self.search_engine = SemanticSearchEngine()
        self.summarizer = TextSummarizer()
        self.question_generator = QuestionGenerator()
        self.concept_mapper = ConceptMapper()
        
        # متغيرات الحالة
        self.current_lecture = None
        self.transcription_data = None
        self.search_index_built = False
        
        logger.info(f"تم تهيئة خط الأنابيب - معرف الجلسة: {self.session_id}")
    
    def process_lecture(self, 
                       audio_file_path: Union[str, Path], 
                       lecture_title: str = None,
                       output_dir: Path = None) -> Dict:
        """
        معالجة محاضرة كاملة من البداية للنهاية
        
        Args:
            audio_file_path: مسار ملف الصوت
            lecture_title: عنوان المحاضرة
            output_dir: مجلد حفظ النتائج
            
        Returns:
            قاموس شامل يحتوي على جميع النتائج
        """
        try:
            audio_path = Path(audio_file_path)
            lecture_title = lecture_title or audio_path.stem
            
            if output_dir is None:
                output_dir = DATA_DIR / f"lecture_{self.session_id}"
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"بدء معالجة المحاضرة: {lecture_title}")
            
            # الخطوة 1: تحويل الصوت إلى نص
            logger.info("الخطوة 1: تحويل الصوت إلى نص...")
            transcription_result = self._step_audio_to_text(audio_path, output_dir)
            
            # الخطوة 2: بناء فهرس البحث الدلالي
            logger.info("الخطوة 2: بناء فهرس البحث الدلالي...")
            search_result = self._step_build_search_index(transcription_result, output_dir)
            
            # الخطوة 3: توليد التلخيص
            logger.info("الخطوة 3: توليد التلخيص...")
            summary_result = self._step_generate_summary(transcription_result, output_dir)
            
            # الخطوة 4: توليد بنك الأسئلة
            logger.info("الخطوة 4: توليد بنك الأسئلة...")
            questions_result = self._step_generate_questions(transcription_result, output_dir)
            
            # الخطوة 5: إنشاء خريطة المفاهيم
            logger.info("الخطوة 5: إنشاء خريطة المفاهيم...")
            concept_map_result = self._step_create_concept_map(transcription_result, output_dir)
            
            # دمج جميع النتائج
            final_result = self._combine_results(
                lecture_title=lecture_title,
                audio_path=audio_path,
                output_dir=output_dir,
                transcription=transcription_result,
                search_index=search_result,
                summary=summary_result,
                questions=questions_result,
                concept_map=concept_map_result
            )
            
            # حفظ النتائج النهائية
            self._save_final_results(final_result, output_dir)
            
            logger.info(f"تم الانتهاء من معالجة المحاضرة: {lecture_title}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"خطأ في معالجة المحاضرة: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session_id
            }
    
    def _step_audio_to_text(self, audio_path: Path, output_dir: Path) -> Dict:
        """خطوة تحويل الصوت إلى نص"""
        try:
            result = self.audio_processor.process_lecture(audio_path, output_dir)
            self.transcription_data = result
            
            return {
                "success": True,
                "full_text": result["full_text"],
                "chunks": result["chunks"],
                "segments": result["segments"],
                "total_duration": result["total_duration"],
                "language": result["language"],
                "output_file": output_dir / f"{audio_path.stem}_transcription.json"
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحويل الصوت إلى نص: {e}")
            return {"success": False, "error": str(e)}
    
    def _step_build_search_index(self, transcription_result: Dict, output_dir: Path) -> Dict:
        """خطوة بناء فهرس البحث"""
        try:
            if not transcription_result.get("success"):
                raise ValueError("فشل في تحويل الصوت إلى نص")
            
            chunks = transcription_result["chunks"]
            self.search_engine.build_index(chunks, output_dir / "search_index")
            self.search_index_built = True
            
            return {
                "success": True,
                "index_size": len(chunks),
                "index_path": output_dir / "search_index"
            }
            
        except Exception as e:
            logger.error(f"خطأ في بناء فهرس البحث: {e}")
            return {"success": False, "error": str(e)}
    
    def _step_generate_summary(self, transcription_result: Dict, output_dir: Path) -> Dict:
        """خطوة توليد التلخيص"""
        try:
            if not transcription_result.get("success"):
                raise ValueError("فشل في تحويل الصوت إلى نص")
            
            full_text = transcription_result["full_text"]
            
            # توليد مستويات مختلفة من التلخيص
            summary_levels = self.summarizer.create_summary_levels(full_text)
            
            # حفظ التلخيص
            summary_file = output_dir / "summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_levels, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "summary_levels": summary_levels,
                "output_file": summary_file
            }
            
        except Exception as e:
            logger.error(f"خطأ في توليد التلخيص: {e}")
            return {"success": False, "error": str(e)}
    
    def _step_generate_questions(self, transcription_result: Dict, output_dir: Path) -> Dict:
        """خطوة توليد بنك الأسئلة"""
        try:
            if not transcription_result.get("success"):
                raise ValueError("فشل في تحويل الصوت إلى نص")
            
            full_text = transcription_result["full_text"]
            
            # توليد بنك الأسئلة
            question_bank = self.question_generator.create_question_bank(full_text)
            
            # حفظ بنك الأسئلة
            questions_file = output_dir / "question_bank.json"
            self.question_generator.save_question_bank(question_bank, questions_file)
            
            return {
                "success": True,
                "question_bank": question_bank,
                "output_file": questions_file
            }
            
        except Exception as e:
            logger.error(f"خطأ في توليد الأسئلة: {e}")
            return {"success": False, "error": str(e)}
    
    def _step_create_concept_map(self, transcription_result: Dict, output_dir: Path) -> Dict:
        """خطوة إنشاء خريطة المفاهيم"""
        try:
            if not transcription_result.get("success"):
                raise ValueError("فشل في تحويل الصوت إلى نص")
            
            full_text = transcription_result["full_text"]
            
            # بناء خريطة المفاهيم
            concept_graph = self.concept_mapper.build_concept_map(full_text)
            
            # إنشاء التصورات المرئية
            static_map = self.concept_mapper.visualize_concept_map(
                output_dir / "concept_map", format="png"
            )
            
            interactive_map = self.concept_mapper.visualize_concept_map(
                output_dir / "concept_map_interactive", format="html"
            )
            
            # حفظ بيانات خريطة المفاهيم
            data_file = output_dir / "concept_map_data.json"
            self.concept_mapper.save_concept_map_data(data_file)
            
            return {
                "success": True,
                "static_map": static_map,
                "interactive_map": interactive_map,
                "data_file": data_file,
                "statistics": self.concept_mapper.get_concept_statistics()
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء خريطة المفاهيم: {e}")
            return {"success": False, "error": str(e)}
    
    def _combine_results(self, **kwargs) -> Dict:
        """دمج جميع النتائج في هيكل موحد"""
        return {
            "session_info": {
                "session_id": self.session_id,
                "created_at": self.created_at.isoformat(),
                "lecture_title": kwargs["lecture_title"],
                "audio_file": str(kwargs["audio_path"]),
                "output_directory": str(kwargs["output_dir"])
            },
            "processing_results": {
                "transcription": kwargs["transcription"],
                "search_index": kwargs["search_index"],
                "summary": kwargs["summary"],
                "questions": kwargs["questions"],
                "concept_map": kwargs["concept_map"]
            },
            "success": all(
                result.get("success", False) 
                for result in [
                    kwargs["transcription"],
                    kwargs["search_index"],
                    kwargs["summary"],
                    kwargs["questions"],
                    kwargs["concept_map"]
                ]
            )
        }
    
    def _save_final_results(self, results: Dict, output_dir: Path):
        """حفظ النتائج النهائية"""
        try:
            results_file = output_dir / "final_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"تم حفظ النتائج النهائية في: {results_file}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ النتائج النهائية: {e}")
    
    def search_in_lecture(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        البحث في المحاضرة الحالية
        
        Args:
            query: استعلام البحث
            top_k: عدد النتائج المطلوبة
            
        Returns:
            نتائج البحث
        """
        try:
            if not self.search_index_built:
                raise ValueError("لم يتم بناء فهرس البحث بعد")
            
            results = self.search_engine.search(query, top_k)
            
            logger.info(f"تم العثور على {len(results)} نتيجة للاستعلام: '{query}'")
            
            return results
            
        except Exception as e:
            logger.error(f"خطأ في البحث: {e}")
            return []
    
    def get_lecture_summary(self, summary_level: str = "medium") -> str:
        """
        الحصول على تلخيص المحاضرة
        
        Args:
            summary_level: مستوى التلخيص (brief, medium, detailed)
            
        Returns:
            التلخيص المطلوب
        """
        try:
            if not self.transcription_data:
                raise ValueError("لا توجد محاضرة محملة")
            
            full_text = self.transcription_data["full_text"]
            summary_levels = self.summarizer.create_summary_levels(full_text)
            
            summary_key = f"{summary_level}_summary"
            return summary_levels.get(summary_key, "التلخيص غير متوفر")
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على التلخيص: {e}")
            return f"خطأ: {str(e)}"
    
    def generate_practice_quiz(self, num_questions: int = 5, question_type: str = "mixed") -> List[Dict]:
        """
        توليد اختبار تدريبي من المحاضرة
        
        Args:
            num_questions: عدد الأسئلة
            question_type: نوع الأسئلة (mixed, open_ended, multiple_choice)
            
        Returns:
            أسئلة الاختبار
        """
        try:
            if not self.transcription_data:
                raise ValueError("لا توجد محاضرة محملة")
            
            full_text = self.transcription_data["full_text"]
            
            if question_type == "multiple_choice":
                # توليد أسئلة اختيار من متعدد فقط
                template_questions = self.question_generator.create_template_questions(full_text, num_questions)
                mcq_questions = self.question_generator._create_multiple_choice_questions(template_questions)
                return mcq_questions[:num_questions]
            
            elif question_type == "open_ended":
                # توليد أسئلة مفتوحة فقط
                return self.question_generator.create_template_questions(full_text, num_questions)
            
            else:  # mixed
                # خليط من الأسئلة
                template_questions = self.question_generator.create_template_questions(full_text, num_questions//2)
                mcq_questions = self.question_generator._create_multiple_choice_questions(template_questions[:2])
                
                all_questions = template_questions + mcq_questions
                return all_questions[:num_questions]
            
        except Exception as e:
            logger.error(f"خطأ في توليد الاختبار التدريبي: {e}")
            return []
    
    def get_related_concepts(self, concept_name: str) -> List[str]:
        """
        الحصول على المفاهيم المتعلقة بمفهوم معين
        
        Args:
            concept_name: اسم المفهوم
            
        Returns:
            قائمة المفاهيم المتعلقة
        """
        try:
            concepts = self.concept_mapper.concepts
            
            for concept in concepts:
                if concept_name.lower() in concept["name"].lower():
                    return concept.get("related_concepts", [])
            
            return []
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على المفاهيم المتعلقة: {e}")
            return []
    
    def get_session_statistics(self) -> Dict:
        """الحصول على إحصائيات الجلسة الحالية"""
        stats = {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "has_transcription": self.transcription_data is not None,
            "search_index_built": self.search_index_built
        }
        
        if self.transcription_data:
            stats.update({
                "audio_duration": self.transcription_data.get("total_duration", 0),
                "text_length": len(self.transcription_data.get("full_text", "")),
                "chunks_count": len(self.transcription_data.get("chunks", []))
            })
        
        if hasattr(self.search_engine, 'index') and self.search_engine.index:
            stats.update(self.search_engine.get_statistics())
        
        if hasattr(self.concept_mapper, 'graph') and self.concept_mapper.graph:
            stats.update(self.concept_mapper.get_concept_statistics())
        
        return stats

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء خط الأنابيب
    pipeline = EnhancedMemoryPipeline()
    
    # مثال على معالجة محاضرة
    # audio_file = Path("sample_lecture.mp3")
    # results = pipeline.process_lecture(audio_file, "محاضرة الذكاء الاصطناعي")
    
    # if results["success"]:
    #     print("تم إنشاء المواد الدراسية بنجاح!")
    #     
    #     # اختبار البحث
    #     search_results = pipeline.search_in_lecture("ما هو الذكاء الاصطناعي؟")
    #     print(f"نتائج البحث: {len(search_results)}")
    #     
    #     # اختبار التلخيص
    #     summary = pipeline.get_lecture_summary("brief")
    #     print(f"الملخص: {summary[:100]}...")
    #     
    #     # اختبار الاختبار التدريبي
    #     quiz = pipeline.generate_practice_quiz(3, "mixed")
    #     print(f"الاختبار التدريبي: {len(quiz)} سؤال")
