"""
وحدة البحث الدلالي والتضمين للبحث الذكي في النصوص
"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import json
import pickle
from pathlib import Path
import logging
from config.settings import EMBEDDING_CONFIG

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticSearchEngine:
    """
    محرك البحث الدلالي للبحث الذكي في النصوص العربية
    """
    
    def __init__(self, model_name: str = None):
        """
        تهيئة محرك البحث الدلالي
        
        Args:
            model_name: اسم نموذج التضمين
        """
        self.model_name = model_name or EMBEDDING_CONFIG["model_name"]
        self.model = None
        self.index = None
        self.chunks = []
        self.chunk_metadata = []
        
    def load_model(self):
        """تحميل نموذج التضمين"""
        try:
            logger.info(f"جاري تحميل نموذج التضمين: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("تم تحميل نموذج التضمين بنجاح")
        except Exception as e:
            logger.error(f"خطأ في تحميل نموذج التضمين: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        معالجة مسبقة للنص
        
        Args:
            text: النص المراد معالجته
            
        Returns:
            النص المعالج
        """
        if not text:
            return ""
        
        # إزالة المسافات الزائدة
        text = " ".join(text.split())
        
        # إزالة الأحرف الغير مرغوب فيها
        text = text.replace("\\n", " ").replace("\\t", " ")
        
        return text.strip()
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        إنشاء تضمينات للنصوص
        
        Args:
            texts: قائمة النصوص
            
        Returns:
            مصفوفة التضمينات
        """
        try:
            if self.model is None:
                self.load_model()
            
            # معالجة النصوص
            processed_texts = [self.preprocess_text(text) for text in texts]
            
            # إنشاء التضمينات
            logger.info(f"جاري إنشاء تضمينات لـ {len(processed_texts)} نص")
            embeddings = self.model.encode(processed_texts, show_progress_bar=True)
            
            logger.info(f"تم إنشاء التضمينات: الشكل = {embeddings.shape}")
            
            return embeddings.astype('float32')
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء التضمينات: {e}")
            raise
    
    def build_index(self, chunks: List[Dict], save_path: Path = None):
        """
        بناء فهرس البحث من الأجزاء النصية
        
        Args:
            chunks: قائمة أجزاء النص مع البيانات الوصفية
            save_path: مسار حفظ الفهرس
        """
        try:
            logger.info(f"جاري بناء فهرس البحث لـ {len(chunks)} جزء")
            
            # استخراج النصوص والبيانات الوصفية
            texts = []
            metadata = []
            
            for i, chunk in enumerate(chunks):
                text = chunk.get("text", "")
                if len(text.strip()) > 0:
                    texts.append(text)
                    metadata.append({
                        "chunk_id": i,
                        "start_time": chunk.get("start", 0),
                        "end_time": chunk.get("end", 0),
                        "text": text,
                        "length": len(text)
                    })
            
            if not texts:
                raise ValueError("لا توجد نصوص صالحة لبناء الفهرس")
            
            # إنشاء التضمينات
            embeddings = self.create_embeddings(texts)
            
            # بناء فهرس FAISS
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner Product للشبه
            
            # تطبيع التضمينات للحصول على شبه تطابق أفضل
            faiss.normalize_L2(embeddings)
            
            # إضافة التضمينات للفهرس
            self.index.add(embeddings)
            
            # حفظ البيانات
            self.chunks = texts
            self.chunk_metadata = metadata
            
            logger.info(f"تم بناء الفهرس بنجاح: {self.index.ntotal} عنصر")
            
            # حفظ الفهرس إذا تم تحديد المسار
            if save_path:
                self.save_index(save_path)
            
        except Exception as e:
            logger.error(f"خطأ في بناء الفهرس: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5, threshold: float = None) -> List[Dict]:
        """
        البحث في الفهرس
        
        Args:
            query: استعلام البحث
            top_k: عدد النتائج المطلوبة
            threshold: حد أدنى للشبه
            
        Returns:
            قائمة النتائج مرتبة حسب الشبه
        """
        try:
            if self.index is None:
                raise ValueError("لم يتم بناء الفهرس بعد")
            
            if self.model is None:
                self.load_model()
            
            threshold = threshold or EMBEDDING_CONFIG["similarity_threshold"]
            
            # إنشاء تضمين للاستعلام
            query_embedding = self.create_embeddings([query])
            faiss.normalize_L2(query_embedding)
            
            # البحث في الفهرس
            scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            # تنظيم النتائج
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= threshold:
                    metadata = self.chunk_metadata[idx].copy()
                    metadata["similarity_score"] = float(score)
                    metadata["rank"] = i + 1
                    results.append(metadata)
            
            logger.info(f"تم العثور على {len(results)} نتيجة للاستعلام: '{query[:50]}...'")
            
            return results
            
        except Exception as e:
            logger.error(f"خطأ في البحث: {e}")
            raise
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """
        حساب الشبه الدلالي بين نصين
        
        Args:
            text1: النص الأول
            text2: النص الثاني
            
        Returns:
            درجة الشبه (0-1)
        """
        try:
            if self.model is None:
                self.load_model()
            
            embeddings = self.create_embeddings([text1, text2])
            
            # حساب الشبه التطابقي
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"خطأ في حساب الشبه: {e}")
            return 0.0
    
    def find_related_chunks(self, chunk_id: int, top_k: int = 3) -> List[Dict]:
        """
        العثور على الأجزاء المتعلقة بجزء معين
        
        Args:
            chunk_id: معرف الجزء
            top_k: عدد الأجزاء المتعلقة
            
        Returns:
            قائمة الأجزاء المتعلقة
        """
        try:
            if chunk_id >= len(self.chunks):
                raise ValueError("معرف الجزء غير صالح")
            
            # استخدم نص الجزء للبحث عن أجزاء مشابهة
            chunk_text = self.chunks[chunk_id]
            results = self.search(chunk_text, top_k + 1)  # +1 لتجنب الجزء نفسه
            
            # إزالة الجزء الأصلي من النتائج
            related = [r for r in results if r["chunk_id"] != chunk_id][:top_k]
            
            return related
            
        except Exception as e:
            logger.error(f"خطأ في العثور على الأجزاء المتعلقة: {e}")
            return []
    
    def save_index(self, save_path: Path):
        """
        حفظ الفهرس والبيانات الوصفية
        
        Args:
            save_path: مسار الحفظ
        """
        try:
            save_path.mkdir(parents=True, exist_ok=True)
            
            # حفظ فهرس FAISS
            faiss_path = save_path / "search_index.faiss"
            faiss.write_index(self.index, str(faiss_path))
            
            # حفظ البيانات الوصفية
            metadata_path = save_path / "metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump({
                    "chunks": self.chunks,
                    "chunk_metadata": self.chunk_metadata,
                    "model_name": self.model_name
                }, f)
            
            logger.info(f"تم حفظ الفهرس في: {save_path}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الفهرس: {e}")
            raise
    
    def load_index(self, load_path: Path):
        """
        تحميل الفهرس والبيانات الوصفية
        
        Args:
            load_path: مسار التحميل
        """
        try:
            # تحميل فهرس FAISS
            faiss_path = load_path / "search_index.faiss"
            if not faiss_path.exists():
                raise FileNotFoundError(f"ملف الفهرس غير موجود: {faiss_path}")
            
            self.index = faiss.read_index(str(faiss_path))
            
            # تحميل البيانات الوصفية
            metadata_path = load_path / "metadata.pkl"
            if not metadata_path.exists():
                raise FileNotFoundError(f"ملف البيانات الوصفية غير موجود: {metadata_path}")
            
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data["chunks"]
                self.chunk_metadata = data["chunk_metadata"]
                if "model_name" in data:
                    self.model_name = data["model_name"]
            
            logger.info(f"تم تحميل الفهرس من: {load_path}")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل الفهرس: {e}")
            raise
    
    def get_statistics(self) -> Dict:
        """
        الحصول على إحصائيات الفهرس
        
        Returns:
            قاموس الإحصائيات
        """
        if self.index is None:
            return {"status": "no_index"}
        
        total_chunks = len(self.chunks)
        avg_length = np.mean([len(chunk) for chunk in self.chunks]) if self.chunks else 0
        
        return {
            "total_chunks": total_chunks,
            "average_chunk_length": avg_length,
            "index_size": self.index.ntotal,
            "model_name": self.model_name
        }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء محرك البحث
    search_engine = SemanticSearchEngine()
    
    # مثال على بناء فهرس من أجزاء المحاضرة
    sample_chunks = [
        {"text": "مقدمة عن الذكاء الاصطناعي ومجالاته", "start": 0, "end": 30},
        {"text": "تطبيقات التعلم الآلي في الحياة اليومية", "start": 30, "end": 60},
        {"text": "أنواع خوارزميات التعلم العميق", "start": 60, "end": 90}
    ]
    
    # search_engine.build_index(sample_chunks)
    
    # مثال على البحث
    # results = search_engine.search("ما هو الذكاء الاصطناعي؟")
    # print(f"تم العثور على {len(results)} نتيجة")
