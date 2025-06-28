"""
وحدة توليد الأسئلة التلقائية من النصوص العربية
"""

import torch
from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM,
    T5ForConditionalGeneration, T5Tokenizer,
    pipeline
)
from typing import List, Dict, Tuple, Optional
import re
import random
import logging
from pathlib import Path
import json
from config.settings import QUESTION_GENERATION_CONFIG

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionGenerator:
    """
    فئة توليد الأسئلة والإجابات التلقائية من النصوص
    """
    
    def __init__(self, model_name: str = None):
        """
        تهيئة مولد الأسئلة
        
        Args:
            model_name: اسم النموذج المستخدم لتوليد الأسئلة
        """
        self.model_name = model_name or QUESTION_GENERATION_CONFIG["model_name"]
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # قوالب الأسئلة العربية
        self.question_templates = {
            "what": ["ما هو", "ما هي", "ماذا", "ما"],
            "how": ["كيف", "كيفية"],
            "why": ["لماذا", "لم", "ما سبب"],
            "when": ["متى", "في أي وقت"],
            "where": ["أين", "في أي مكان"],
            "who": ["من", "من هو", "من هي"],
            "which": ["أي", "أي من"],
            "definition": ["عرّف", "اشرح", "وضح"],
            "list": ["اذكر", "اكتب", "أعطِ"],
            "compare": ["قارن", "ما الفرق بين"],
            "analyze": ["حلل", "ناقش", "اشرح تأثير"]
        }
        
        logger.info(f"تم تهيئة مولد الأسئلة باستخدام: {self.device}")
    
    def load_model(self):
        """تحميل نموذج توليد الأسئلة"""
        try:
            logger.info(f"جاري تحميل نموذج توليد الأسئلة: {self.model_name}")
            
            if "mt5" in self.model_name.lower():
                self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            self.model.to(self.device)
            logger.info("تم تحميل نموذج توليد الأسئلة بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل نموذج توليد الأسئلة: {e}")
            raise
    
    def extract_key_information(self, text: str) -> List[Dict]:
        """
        استخراج المعلومات الرئيسية من النص
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قائمة المعلومات الرئيسية
        """
        key_info = []
        
        # استخراج الجمل الرئيسية
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            info = {
                "text": sentence,
                "type": self._classify_sentence_type(sentence),
                "keywords": self._extract_keywords(sentence),
                "entities": self._extract_entities(sentence)
            }
            
            key_info.append(info)
        
        return key_info
    
    def _classify_sentence_type(self, sentence: str) -> str:
        """تصنيف نوع الجملة"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ["هو", "هي", "يعرف", "تعريف"]):
            return "definition"
        elif any(word in sentence_lower for word in ["سبب", "لأن", "نتيجة"]):
            return "reason"
        elif any(word in sentence_lower for word in ["كيف", "طريقة", "خطوات"]):
            return "process"
        elif any(word in sentence_lower for word in ["مثال", "على سبيل المثال"]):
            return "example"
        elif any(word in sentence_lower for word in ["أنواع", "أقسام", "تصنيف"]):
            return "classification"
        else:
            return "general"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """استخراج الكلمات المفتاحية"""
        # إزالة علامات الترقيم والكلمات الشائعة
        stop_words = {
            "في", "من", "إلى", "على", "عن", "مع", "بين", "أن", "إن", "كان", "كانت",
            "هذا", "هذه", "ذلك", "تلك", "التي", "الذي", "التي", "والتي", "والذي"
        }
        
        words = re.findall(r'\\b[أ-ي]+\\b', text)
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return list(set(keywords))[:5]  # أهم 5 كلمات مفتاحية
    
    def _extract_entities(self, text: str) -> List[str]:
        """استخراج الكيانات المسماة"""
        # بحث عن أنماط الكيانات
        entities = []
        
        # الأرقام والتواريخ
        numbers = re.findall(r'\\d+', text)
        entities.extend(numbers)
        
        # الكلمات المكتوبة بأحرف كبيرة (قد تكون أسماء)
        capitals = re.findall(r'\\b[A-Z][a-z]+\\b', text)
        entities.extend(capitals)
        
        return entities
    
    def generate_questions_from_text(self, text: str, num_questions: int = None) -> List[Dict]:
        """
        توليد أسئلة من النص باستخدام النموذج
        
        Args:
            text: النص المراد توليد أسئلة منه
            num_questions: عدد الأسئلة المطلوبة
            
        Returns:
            قائمة الأسئلة المولدة
        """
        try:
            if self.model is None:
                self.load_model()
            
            num_questions = num_questions or QUESTION_GENERATION_CONFIG["max_questions"]
            
            # تجزئة النص إلى فقرات قصيرة
            paragraphs = self._split_text_for_questions(text)
            
            generated_questions = []
            
            for paragraph in paragraphs[:num_questions]:
                # تحضير النص للنموذج
                input_text = f"generate question: {paragraph}"
                
                # ترميز النص
                inputs = self.tokenizer.encode(
                    input_text,
                    return_tensors="pt",
                    max_length=512,
                    truncation=True
                ).to(self.device)
                
                # توليد السؤال
                with torch.no_grad():
                    question_ids = self.model.generate(
                        inputs,
                        max_length=100,
                        min_length=10,
                        num_beams=3,
                        temperature=0.7,
                        do_sample=True,
                        early_stopping=True
                    )
                
                # فك ترميز السؤال
                question = self.tokenizer.decode(
                    question_ids[0],
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True
                )
                
                if question and len(question) > 5:
                    generated_questions.append({
                        "question": question,
                        "context": paragraph,
                        "answer": self._extract_answer_from_context(question, paragraph),
                        "type": "generated",
                        "difficulty": "medium"
                    })
            
            return generated_questions
            
        except Exception as e:
            logger.error(f"خطأ في توليد الأسئلة: {e}")
            return []
    
    def create_template_questions(self, text: str, num_questions: int = None) -> List[Dict]:
        """
        إنشاء أسئلة باستخدام القوالب الجاهزة
        
        Args:
            text: النص المراد إنشاء أسئلة منه
            num_questions: عدد الأسئلة المطلوبة
            
        Returns:
            قائمة الأسئلة المنشأة
        """
        try:
            num_questions = num_questions or QUESTION_GENERATION_CONFIG["max_questions"]
            
            # استخراج المعلومات الرئيسية
            key_info = self.extract_key_information(text)
            
            template_questions = []
            
            for info in key_info[:num_questions]:
                question_data = self._create_question_from_info(info)
                if question_data:
                    template_questions.append(question_data)
            
            return template_questions
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الأسئلة بالقوالب: {e}")
            return []
    
    def _create_question_from_info(self, info: Dict) -> Optional[Dict]:
        """إنشاء سؤال من معلومة محددة"""
        text = info["text"]
        sentence_type = info["type"]
        keywords = info["keywords"]
        
        if sentence_type == "definition" and keywords:
            # سؤال تعريف
            keyword = keywords[0]
            question = f"ما هو {keyword}؟"
            answer = text
            
        elif sentence_type == "reason":
            # سؤال سببي
            question = f"لماذا {text.split('لأن')[0].strip()}؟"
            answer = text.split('لأن')[1].strip() if 'لأن' in text else text
            
        elif sentence_type == "process":
            # سؤال عن العملية
            question = f"كيف {text.split('كيف')[1].strip()}؟" if 'كيف' in text else f"اشرح العملية المذكورة في النص"
            answer = text
            
        elif keywords:
            # سؤال عام عن الكلمات المفتاحية
            keyword = random.choice(keywords)
            template = random.choice(self.question_templates["what"])
            question = f"{template} {keyword}؟"
            answer = text
            
        else:
            return None
        
        return {
            "question": question,
            "answer": answer,
            "context": text,
            "type": "template",
            "difficulty": self._assess_difficulty(question, answer)
        }
    
    def _split_text_for_questions(self, text: str, max_length: int = 200) -> List[str]:
        """تجزئة النص لتوليد الأسئلة"""
        sentences = re.split(r'[.!?]', text)
        paragraphs = []
        current_paragraph = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_paragraph) + len(sentence) <= max_length:
                current_paragraph += sentence + ". "
            else:
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence + ". "
        
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())
        
        return paragraphs
    
    def _extract_answer_from_context(self, question: str, context: str) -> str:
        """استخراج الإجابة من السياق"""
        # بحث بسيط عن الإجابة في السياق
        question_words = question.split()
        
        for sentence in context.split('.'):
            sentence = sentence.strip()
            if any(word in sentence for word in question_words[-3:]):  # آخر 3 كلمات من السؤال
                return sentence
        
        return context[:100] + "..." if len(context) > 100 else context
    
    def _assess_difficulty(self, question: str, answer: str) -> str:
        """تقييم صعوبة السؤال"""
        if len(answer) < 50:
            return "easy"
        elif len(answer) < 150:
            return "medium"
        else:
            return "hard"
    
    def create_question_bank(self, text: str, include_multiple_choice: bool = True) -> Dict:
        """
        إنشاء بنك أسئلة شامل
        
        Args:
            text: النص المصدر
            include_multiple_choice: تضمين أسئلة الاختيار من متعدد
            
        Returns:
            بنك الأسئلة الشامل
        """
        try:
            logger.info("جاري إنشاء بنك الأسئلة الشامل...")
            
            # توليد أسئلة بالنموذج
            model_questions = self.generate_questions_from_text(text, 5)
            
            # إنشاء أسئلة بالقوالب
            template_questions = self.create_template_questions(text, 5)
            
            # دمج الأسئلة
            all_questions = model_questions + template_questions
            
            # إنشاء أسئلة اختيار من متعدد
            mcq_questions = []
            if include_multiple_choice:
                mcq_questions = self._create_multiple_choice_questions(all_questions[:3])
            
            # تصنيف الأسئلة حسب النوع والصعوبة
            question_bank = {
                "source_text": text,
                "total_questions": len(all_questions) + len(mcq_questions),
                "open_ended_questions": all_questions,
                "multiple_choice_questions": mcq_questions,
                "by_difficulty": {
                    "easy": [q for q in all_questions if q.get("difficulty") == "easy"],
                    "medium": [q for q in all_questions if q.get("difficulty") == "medium"],
                    "hard": [q for q in all_questions if q.get("difficulty") == "hard"]
                },
                "by_type": {
                    "definition": [q for q in all_questions if "ما هو" in q["question"] or "ما هي" in q["question"]],
                    "explanation": [q for q in all_questions if "اشرح" in q["question"] or "وضح" in q["question"]],
                    "analysis": [q for q in all_questions if "حلل" in q["question"] or "ناقش" in q["question"]]
                }
            }
            
            logger.info(f"تم إنشاء بنك أسئلة بـ {question_bank['total_questions']} سؤال")
            
            return question_bank
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء بنك الأسئلة: {e}")
            return {"error": f"خطأ في المعالجة: {str(e)}"}
    
    def _create_multiple_choice_questions(self, questions: List[Dict]) -> List[Dict]:
        """إنشاء أسئلة اختيار من متعدد"""
        mcq_questions = []
        
        for question_data in questions:
            try:
                question = question_data["question"]
                correct_answer = question_data["answer"]
                
                # إنشاء خيارات خاطئة
                wrong_answers = self._generate_wrong_answers(correct_answer)
                
                # ترتيب الخيارات عشوائياً
                all_choices = [correct_answer] + wrong_answers
                random.shuffle(all_choices)
                
                correct_index = all_choices.index(correct_answer)
                choice_labels = ["أ", "ب", "ج", "د"]
                
                mcq = {
                    "question": question,
                    "choices": {
                        choice_labels[i]: choice 
                        for i, choice in enumerate(all_choices)
                    },
                    "correct_answer": choice_labels[correct_index],
                    "explanation": correct_answer,
                    "type": "multiple_choice"
                }
                
                mcq_questions.append(mcq)
                
            except Exception as e:
                logger.warning(f"خطأ في إنشاء سؤال اختيار من متعدد: {e}")
                continue
        
        return mcq_questions
    
    def _generate_wrong_answers(self, correct_answer: str) -> List[str]:
        """توليد إجابات خاطئة لأسئلة الاختيار من متعدد"""
        # بحث عن كلمات مفتاحية في الإجابة الصحيحة
        keywords = self._extract_keywords(correct_answer)
        
        wrong_answers = []
        
        # إنشاء إجابات خاطئة باستبدال الكلمات المفتاحية
        for keyword in keywords[:2]:
            wrong_answer = correct_answer.replace(keyword, f"ليس {keyword}")
            wrong_answers.append(wrong_answer[:80] + "..." if len(wrong_answer) > 80 else wrong_answer)
        
        # إضافة إجابة عامة خاطئة
        wrong_answers.append("لا يمكن تحديد ذلك من النص المعطى")
        
        return wrong_answers[:3]  # أقصى 3 إجابات خاطئة
    
    def save_question_bank(self, question_bank: Dict, output_path: Path):
        """حفظ بنك الأسئلة في ملف JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(question_bank, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم حفظ بنك الأسئلة في: {output_path}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ بنك الأسئلة: {e}")
            raise

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مولد الأسئلة
    question_gen = QuestionGenerator()
    
    # مثال على توليد أسئلة
    sample_text = """
    الذكاء الاصطناعي هو مجال في علوم الحاسوب يهدف إلى إنشاء أنظمة قادرة على أداء مهام تتطلب ذكاءً بشرياً.
    يشمل هذا المجال التعلم الآلي والتعلم العميق ومعالجة اللغة الطبيعية.
    تطبيقات الذكاء الاصطناعي تشمل المركبات ذاتية القيادة والمساعدات الصوتية.
    """
    
    # question_bank = question_gen.create_question_bank(sample_text)
    # print(f"تم إنشاء {question_bank['total_questions']} سؤال")
