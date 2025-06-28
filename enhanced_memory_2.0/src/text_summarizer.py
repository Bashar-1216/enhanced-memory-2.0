"""
وحدة التلخيص التجريدي للنصوص العربية
"""

import torch
from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM,
    pipeline, T5ForConditionalGeneration, T5Tokenizer
)
from typing import List, Dict, Optional, Union
import numpy as np
import logging
from pathlib import Path
import re
from config.settings import SUMMARIZATION_CONFIG, TEXT_CONFIG

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextSummarizer:
    """
    فئة التلخيص التجريدي للنصوص العربية والمتعددة اللغات
    """
    
    def __init__(self, model_name: str = None):
        """
        تهيئة مُلخص النصوص
        
        Args:
            model_name: اسم النموذج المستخدم للتلخيص
        """
        self.model_name = model_name or SUMMARIZATION_CONFIG["model_name"]
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"تم تهيئة مُلخص النصوص باستخدام: {self.device}")
    
    def load_model(self):
        """تحميل نموذج التلخيص"""
        try:
            logger.info(f"جاري تحميل نموذج التلخيص: {self.model_name}")
            
            if "mbart" in self.model_name.lower():
                self._load_mbart_model()
            elif "t5" in self.model_name.lower():
                self._load_t5_model()
            else:
                self._load_generic_model()
            
            logger.info("تم تحميل نموذج التلخيص بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل نموذج التلخيص: {e}")
            raise
    
    def _load_mbart_model(self):
        """تحميل نموذج mBART"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
    
    def _load_t5_model(self):
        """تحميل نموذج T5"""
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
        self.model.to(self.device)
    
    def _load_generic_model(self):
        """تحميل نموذج عام"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
    
    def preprocess_text(self, text: str) -> str:
        """
        معالجة مسبقة للنص قبل التلخيص
        
        Args:
            text: النص المراد معالجته
            
        Returns:
            النص المعالج
        """
        if not text:
            return ""
        
        # إزالة المسافات الزائدة والأسطر الفارغة
        text = re.sub(r'\\s+', ' ', text)
        
        # إزالة الأحرف الخاصة غير المرغوب فيها
        text = re.sub(r'[\\n\\t\\r]', ' ', text)
        
        # إزالة المسافات في البداية والنهاية
        text = text.strip()
        
        # التأكد من أن النص ليس فارغاً
        if len(text) < 10:
            return ""
        
        return text
    
    def split_text_into_chunks(self, text: str, max_length: int = None) -> List[str]:
        """
        تجزئة النص إلى أجزاء قابلة للمعالجة
        
        Args:
            text: النص الكامل
            max_length: الحد الأقصى لطول كل جزء
            
        Returns:
            قائمة أجزاء النص
        """
        max_length = max_length or TEXT_CONFIG["max_chunk_size"]
        
        # تقسيم النص إلى جمل
        sentences = re.split(r'[.!?]', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # إضافة الجملة إذا كانت لا تتجاوز الحد الأقصى
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + ". "
            else:
                # حفظ الجزء الحالي وبدء جزء جديد
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        # إضافة الجزء الأخير
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def summarize_text(self, text: str, max_length: int = None, min_length: int = None) -> str:
        """
        تلخيص نص واحد
        
        Args:
            text: النص المراد تلخيصه
            max_length: الحد الأقصى لطول الملخص
            min_length: الحد الأدنى لطول الملخص
            
        Returns:
            الملخص
        """
        try:
            if self.model is None:
                self.load_model()
            
            # معالجة النص
            processed_text = self.preprocess_text(text)
            if not processed_text:
                return "لا يوجد محتوى كافٍ للتلخيص"
            
            max_length = max_length or SUMMARIZATION_CONFIG["max_length"]
            min_length = min_length or SUMMARIZATION_CONFIG["min_length"]
            
            # تحضير النص للنموذج
            if "t5" in self.model_name.lower():
                input_text = f"summarize: {processed_text}"
            else:
                input_text = processed_text
            
            # ترميز النص
            inputs = self.tokenizer.encode(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)
            
            # توليد الملخص
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs,
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=SUMMARIZATION_CONFIG["num_beams"],
                    temperature=SUMMARIZATION_CONFIG["temperature"],
                    do_sample=True,
                    early_stopping=True,
                    no_repeat_ngram_size=2
                )
            
            # فك ترميز الملخص
            summary = self.tokenizer.decode(
                summary_ids[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"خطأ في تلخيص النص: {e}")
            return f"خطأ في التلخيص: {str(e)}"
    
    def summarize_long_text(self, text: str, max_length: int = None) -> Dict:
        """
        تلخيص نص طويل بتجزئته إلى أجزاء
        
        Args:
            text: النص الطويل
            max_length: الحد الأقصى لطول الملخص النهائي
            
        Returns:
            قاموس يحتوي على الملخصات المختلفة
        """
        try:
            logger.info("جاري تلخيص النص الطويل...")
            
            # تجزئة النص
            chunks = self.split_text_into_chunks(text)
            
            if not chunks:
                return {"error": "لا يوجد محتوى كافٍ للتلخيص"}
            
            logger.info(f"تم تجزئة النص إلى {len(chunks)} جزء")
            
            # تلخيص كل جزء
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"جاري تلخيص الجزء {i+1}/{len(chunks)}")
                summary = self.summarize_text(chunk, max_length=200)
                if summary and "خطأ" not in summary:
                    chunk_summaries.append(summary)
            
            if not chunk_summaries:
                return {"error": "فشل في تلخيص أي جزء من النص"}
            
            # دمج الملخصات الجزئية
            combined_summary = " ".join(chunk_summaries)
            
            # تلخيص نهائي إذا كان النص المدمج طويلاً
            final_summary = combined_summary
            if len(combined_summary) > (max_length or SUMMARIZATION_CONFIG["max_length"]):
                logger.info("جاري إنشاء الملخص النهائي...")
                final_summary = self.summarize_text(combined_summary, max_length=max_length)
            
            return {
                "original_length": len(text),
                "chunks_count": len(chunks),
                "chunk_summaries": chunk_summaries,
                "combined_summary": combined_summary,
                "final_summary": final_summary,
                "compression_ratio": len(text) / len(final_summary) if final_summary else 0
            }
            
        except Exception as e:
            logger.error(f"خطأ في تلخيص النص الطويل: {e}")
            return {"error": f"خطأ في التلخيص: {str(e)}"}
    
    def create_bullet_points(self, text: str) -> List[str]:
        """
        تحويل النص إلى نقاط رئيسية
        
        Args:
            text: النص المراد تحويله
            
        Returns:
            قائمة النقاط الرئيسية
        """
        try:
            # تلخيص النص أولاً
            summary = self.summarize_text(text, max_length=300)
            
            # تقسيم إلى جمل
            sentences = re.split(r'[.!?]', summary)
            
            # تنظيف وتحويل إلى نقاط
            bullet_points = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:
                    # إضافة رمز النقطة
                    if not sentence.startswith("•"):
                        sentence = "• " + sentence
                    bullet_points.append(sentence)
            
            return bullet_points
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النقاط الرئيسية: {e}")
            return [f"• خطأ في المعالجة: {str(e)}"]
    
    def create_summary_levels(self, text: str) -> Dict:
        """
        إنشاء مستويات مختلفة من التلخيص
        
        Args:
            text: النص الأصلي
            
        Returns:
            قاموس يحتوي على مستويات التلخيص المختلفة
        """
        try:
            logger.info("جاري إنشاء مستويات التلخيص المختلفة...")
            
            results = {
                "original_text": text,
                "word_count": len(text.split())
            }
            
            # ملخص مفصل (30% من النص الأصلي)
            detailed_length = max(100, len(text) // 3)
            results["detailed_summary"] = self.summarize_text(text, max_length=detailed_length)
            
            # ملخص متوسط (15% من النص الأصلي)
            medium_length = max(50, len(text) // 6)
            results["medium_summary"] = self.summarize_text(text, max_length=medium_length)
            
            # ملخص مختصر (5% من النص الأصلي)
            brief_length = max(30, len(text) // 20)
            results["brief_summary"] = self.summarize_text(text, max_length=brief_length)
            
            # النقاط الرئيسية
            results["bullet_points"] = self.create_bullet_points(text)
            
            return results
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء مستويات التلخيص: {e}")
            return {"error": f"خطأ في المعالجة: {str(e)}"}
    
    def get_model_info(self) -> Dict:
        """
        الحصول على معلومات النموذج
        
        Returns:
            معلومات النموذج
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "model_loaded": self.model is not None,
            "max_length": SUMMARIZATION_CONFIG["max_length"],
            "min_length": SUMMARIZATION_CONFIG["min_length"]
        }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مُلخص النصوص
    summarizer = TextSummarizer()
    
    # مثال على تلخيص نص
    sample_text = """
    الذكاء الاصطناعي هو مجال في علوم الحاسوب يهدف إلى إنشاء أنظمة قادرة على أداء مهام تتطلب ذكاءً بشرياً.
    يشمل هذا المجال العديد من التقنيات مثل التعلم الآلي والتعلم العميق ومعالجة اللغة الطبيعية.
    تطبيقات الذكاء الاصطناعي متنوعة وتشمل المركبات ذاتية القيادة والمساعدات الصوتية وأنظمة التوصية.
    """
    
    # summary = summarizer.summarize_text(sample_text)
    # print(f"الملخص: {summary}")
