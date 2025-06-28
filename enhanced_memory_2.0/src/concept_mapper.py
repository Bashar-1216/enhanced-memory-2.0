"""
وحدة إنشاء خرائط المفاهيم الرسومية من النصوص
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple, Optional, Set
import re
import json
from pathlib import Path
import logging
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
import plotly.express as px
from pyvis.network import Network
from config.settings import CONCEPT_MAP_CONFIG

# إعداد matplotlib للغة العربية
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConceptMapper:
    """
    فئة إنشاء خرائط المفاهيم من النصوص العربية
    """
    
    def __init__(self):
        """تهيئة مُنشئ خرائط المفاهيم"""
        self.graph = nx.Graph()
        self.concepts = []
        self.relationships = []
        
        # كلمات الربط العربية
        self.connection_words = {
            "causes": ["يسبب", "ينتج عن", "يؤدي إلى", "نتيجة"],
            "contains": ["يحتوي على", "يشمل", "يضم", "من ضمنه"],
            "types": ["نوع من", "أنواع", "تصنيف", "يصنف"],
            "properties": ["خصائص", "صفات", "مميزات", "سمات"],
            "processes": ["عملية", "خطوات", "مراحل", "طريقة"],
            "examples": ["مثال", "أمثلة", "على سبيل المثال"],
            "definitions": ["تعريف", "يعرف", "معنى", "مفهوم"],
            "relationships": ["علاقة", "ترابط", "صلة", "ارتباط"]
        }
        
        # كلمات الإيقاف العربية
        self.stop_words = {
            "في", "من", "إلى", "على", "عن", "مع", "بين", "أن", "إن", "كان", "كانت",
            "هذا", "هذه", "ذلك", "تلك", "التي", "الذي", "والتي", "والذي", "لكن",
            "أو", "إما", "كما", "حيث", "بحيث", "لذلك", "وبالتالي", "ومن ثم",
            "الذي", "التي", "اللذان", "اللتان", "الذين", "اللواتي", "اللاتي"
        }
        
        logger.info("تم تهيئة مُنشئ خرائط المفاهيم")
    
    def extract_concepts(self, text: str) -> List[Dict]:
        """
        استخراج المفاهيم من النص
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قائمة المفاهيم المستخرجة
        """
        try:
            logger.info("جاري استخراج المفاهيم من النص...")
            
            # تنظيف النص
            cleaned_text = self._clean_text(text)
            
            # استخراج المفاهيم الأساسية
            basic_concepts = self._extract_basic_concepts(cleaned_text)
            
            # استخراج المفاهيم باستخدام TF-IDF
            tfidf_concepts = self._extract_tfidf_concepts(cleaned_text)
            
            # استخراج مفاهيم بناءً على الأنماط
            pattern_concepts = self._extract_pattern_concepts(cleaned_text)
            
            # دمج جميع المفاهيم
            all_concepts = basic_concepts + tfidf_concepts + pattern_concepts
            
            # إزالة التكرارات وترتيب حسب الأهمية
            unique_concepts = self._deduplicate_and_rank_concepts(all_concepts)
            
            # تحديد خصائص كل مفهوم
            enriched_concepts = self._enrich_concepts(unique_concepts, cleaned_text)
            
            self.concepts = enriched_concepts[:CONCEPT_MAP_CONFIG["max_concepts"]]
            
            logger.info(f"تم استخراج {len(self.concepts)} مفهوم")
            
            return self.concepts
            
        except Exception as e:
            logger.error(f"خطأ في استخراج المفاهيم: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """تنظيف النص"""
        # إزالة علامات الترقيم الزائدة
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_basic_concepts(self, text: str) -> List[Dict]:
        """استخراج المفاهيم الأساسية"""
        words = text.split()
        
        # تصفية الكلمات
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in self.stop_words
        ]
        
        # حساب تكرار الكلمات
        word_freq = Counter(filtered_words)
        
        concepts = []
        for word, freq in word_freq.most_common(20):
            concepts.append({
                "name": word,
                "type": "basic",
                "frequency": freq,
                "importance": freq / len(filtered_words)
            })
        
        return concepts
    
    def _extract_tfidf_concepts(self, text: str) -> List[Dict]:
        """استخراج المفاهيم باستخدام TF-IDF"""
        try:
            # تجزئة النص إلى جمل
            sentences = re.split(r'[.!?]', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
            if len(sentences) < 2:
                return []
            
            # تطبيق TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=50,
                stop_words=list(self.stop_words),
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # حساب متوسط TF-IDF لكل مصطلح
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            concepts = []
            for i, score in enumerate(mean_scores):
                if score > 0.1:  # عتبة للأهمية
                    concepts.append({
                        "name": feature_names[i],
                        "type": "tfidf",
                        "score": float(score),
                        "importance": float(score)
                    })
            
            return sorted(concepts, key=lambda x: x["score"], reverse=True)[:15]
            
        except Exception as e:
            logger.warning(f"خطأ في استخراج مفاهيم TF-IDF: {e}")
            return []
    
    def _extract_pattern_concepts(self, text: str) -> List[Dict]:
        """استخراج مفاهيم بناءً على الأنماط اللغوية"""
        concepts = []
        
        # البحث عن أنماط التعريف
        definition_patterns = [
            r'(.+?)\s+(?:هو|هي|يعرف)\s+(.+?)(?:\.|$)',
            r'(?:تعريف|مفهوم)\s+(.+?)\s+(?:\.|$)',
            r'(.+?)\s+(?:يعني|معناه)\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                concept_name = match.group(1).strip()
                definition = match.group(2).strip()
                
                concepts.append({
                    "name": concept_name,
                    "type": "definition",
                    "definition": definition,
                    "importance": 0.8
                })
        
        # البحث عن أنماط التصنيف
        classification_patterns = [
            r'(?:أنواع|أقسام|تصنيفات)\s+(.+?)\s+(?:هي|تشمل)?\s*:?\s*(.+?)(?:\.|$)',
            r'(.+?)\s+(?:ينقسم|يصنف)\s+(?:إلى|على)\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in classification_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                main_concept = match.group(1).strip()
                sub_concepts = match.group(2).strip()
                
                concepts.append({
                    "name": main_concept,
                    "type": "category",
                    "subcategories": sub_concepts,
                    "importance": 0.7
                })
        
        return concepts
    
    def _deduplicate_and_rank_concepts(self, concepts: List[Dict]) -> List[Dict]:
        """إزالة التكرارات وترتيب المفاهيم"""
        # دمج المفاهيم المتشابهة
        unique_concepts = {}
        
        for concept in concepts:
            name = concept["name"].lower()
            
            # البحث عن مفهوم مشابه
            similar_key = None
            for existing_key in unique_concepts.keys():
                if self._calculate_similarity(name, existing_key) > 0.8:
                    similar_key = existing_key
                    break
            
            if similar_key:
                # دمج مع المفهوم الموجود
                existing = unique_concepts[similar_key]
                existing["importance"] = max(existing["importance"], concept["importance"])
                if "frequency" in concept:
                    existing["frequency"] = existing.get("frequency", 0) + concept["frequency"]
            else:
                # إضافة مفهوم جديد
                unique_concepts[name] = concept
        
        # ترتيب حسب الأهمية
        sorted_concepts = sorted(
            unique_concepts.values(),
            key=lambda x: x["importance"],
            reverse=True
        )
        
        return sorted_concepts
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """حساب التشابه بين نصين"""
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0
    
    def _enrich_concepts(self, concepts: List[Dict], text: str) -> List[Dict]:
        """إثراء المفاهيم بمعلومات إضافية"""
        enriched = []
        
        for concept in concepts:
            name = concept["name"]
            
            # البحث عن السياق
            context = self._find_context(name, text)
            
            # تحديد نوع المفهوم
            concept_type = self._classify_concept_type(name, context)
            
            # البحث عن العلاقات
            related_concepts = self._find_related_concepts(name, context, concepts)
            
            enriched_concept = {
                **concept,
                "context": context,
                "concept_type": concept_type,
                "related_concepts": related_concepts
            }
            
            enriched.append(enriched_concept)
        
        return enriched
    
    def _find_context(self, concept_name: str, text: str) -> str:
        """العثور على السياق المحيط بالمفهوم"""
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            if concept_name.lower() in sentence.lower():
                return sentence.strip()
        
        return ""
    
    def _classify_concept_type(self, name: str, context: str) -> str:
        """تصنيف نوع المفهوم"""
        combined_text = (name + " " + context).lower()
        
        if any(word in combined_text for word in ["تعريف", "مفهوم", "معنى"]):
            return "definition"
        elif any(word in combined_text for word in ["عملية", "خطوات", "طريقة"]):
            return "process"
        elif any(word in combined_text for word in ["نوع", "أنواع", "تصنيف"]):
            return "category"
        elif any(word in combined_text for word in ["خاصية", "صفة", "مميزة"]):
            return "property"
        elif any(word in combined_text for word in ["مثال", "تطبيق"]):
            return "example"
        else:
            return "general"
    
    def _find_related_concepts(self, concept_name: str, context: str, all_concepts: List[Dict]) -> List[str]:
        """العثور على المفاهيم المتعلقة"""
        related = []
        
        for other_concept in all_concepts:
            other_name = other_concept["name"]
            if other_name != concept_name:
                # البحث في السياق
                if other_name.lower() in context.lower():
                    related.append(other_name)
        
        return related[:3]  # أقصى 3 مفاهيم متعلقة
    
    def extract_relationships(self, text: str) -> List[Dict]:
        """
        استخراج العلاقات بين المفاهيم
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قائمة العلاقات
        """
        try:
            logger.info("جاري استخراج العلاقات بين المفاهيم...")
            
            relationships = []
            
            # استخراج علاقات مباشرة من النص
            direct_relations = self._extract_direct_relationships(text)
            relationships.extend(direct_relations)
            
            # استخراج علاقات بناءً على التجاور
            proximity_relations = self._extract_proximity_relationships(text)
            relationships.extend(proximity_relations)
            
            # استخراج علاقات دلالية
            semantic_relations = self._extract_semantic_relationships()
            relationships.extend(semantic_relations)
            
            self.relationships = relationships
            
            logger.info(f"تم استخراج {len(relationships)} علاقة")
            
            return relationships
            
        except Exception as e:
            logger.error(f"خطأ في استخراج العلاقات: {e}")
            return []
    
    def _extract_direct_relationships(self, text: str) -> List[Dict]:
        """استخراج العلاقات المباشرة من النص"""
        relationships = []
        
        for relation_type, keywords in self.connection_words.items():
            for keyword in keywords:
                pattern = r'(.+?)\s+' + re.escape(keyword) + r'\s+(.+?)(?:\.|$)'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    source = match.group(1).strip()
                    target = match.group(2).strip()
                    
                    # تنظيف المفاهيم
                    source = self._clean_concept_name(source)
                    target = self._clean_concept_name(target)
                    
                    if source and target:
                        relationships.append({
                            "source": source,
                            "target": target,
                            "relation_type": relation_type,
                            "keyword": keyword,
                            "strength": 0.8
                        })
        
        return relationships
    
    def _extract_proximity_relationships(self, text: str) -> List[Dict]:
        """استخراج علاقات بناءً على قرب المفاهيم"""
        relationships = []
        
        if not self.concepts:
            return relationships
        
        concept_names = [c["name"] for c in self.concepts]
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            # العثور على المفاهيم في هذه الجملة
            concepts_in_sentence = []
            for concept in concept_names:
                if concept.lower() in sentence.lower():
                    concepts_in_sentence.append(concept)
            
            # إنشاء علاقات بين المفاهيم المتجاورة
            if len(concepts_in_sentence) >= 2:
                for i, concept1 in enumerate(concepts_in_sentence):
                    for concept2 in concepts_in_sentence[i+1:]:
                        relationships.append({
                            "source": concept1,
                            "target": concept2,
                            "relation_type": "proximity",
                            "context": sentence.strip(),
                            "strength": 0.5
                        })
        
        return relationships
    
    def _extract_semantic_relationships(self) -> List[Dict]:
        """استخراج العلاقات الدلالية بين المفاهيم"""
        relationships = []
        
        if len(self.concepts) < 2:
            return relationships
        
        # حساب التشابه الدلالي بين المفاهيم
        concept_texts = [c.get("context", c["name"]) for c in self.concepts]
        
        try:
            vectorizer = TfidfVectorizer(stop_words=list(self.stop_words))
            tfidf_matrix = vectorizer.fit_transform(concept_texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # إنشاء علاقات للمفاهيم المتشابهة
            for i, concept1 in enumerate(self.concepts):
                for j, concept2 in enumerate(self.concepts[i+1:], i+1):
                    similarity = similarity_matrix[i][j]
                    
                    if similarity > CONCEPT_MAP_CONFIG["min_relation_strength"]:
                        relationships.append({
                            "source": concept1["name"],
                            "target": concept2["name"],
                            "relation_type": "semantic",
                            "strength": float(similarity)
                        })
        
        except Exception as e:
            logger.warning(f"خطأ في حساب التشابه الدلالي: {e}")
        
        return relationships
    
    def _clean_concept_name(self, name: str) -> str:
        """تنظيف اسم المفهوم"""
        # إزالة الكلمات الزائدة
        words = name.split()
        cleaned_words = [word for word in words if word not in self.stop_words]
        
        return " ".join(cleaned_words[:3])  # أقصى 3 كلمات
    
    def build_concept_map(self, text: str) -> nx.Graph:
        """
        بناء خريطة المفاهيم الكاملة
        
        Args:
            text: النص المصدر
            
        Returns:
            رسم بياني يمثل خريطة المفاهيم
        """
        try:
            logger.info("جاري بناء خريطة المفاهيم...")
            
            # استخراج المفاهيم والعلاقات
            self.extract_concepts(text)
            self.extract_relationships(text)
            
            # إنشاء الرسم البياني
            self.graph = nx.Graph()
            
            # إضافة المفاهيم كعقد
            for concept in self.concepts:
                self.graph.add_node(
                    concept["name"],
                    type=concept.get("concept_type", "general"),
                    importance=concept["importance"],
                    context=concept.get("context", "")
                )
            
            # إضافة العلاقات كحواف
            for relationship in self.relationships:
                source = relationship["source"]
                target = relationship["target"]
                
                # التأكد من وجود العقد
                if source in self.graph.nodes and target in self.graph.nodes:
                    self.graph.add_edge(
                        source,
                        target,
                        relation_type=relationship["relation_type"],
                        strength=relationship["strength"]
                    )
            
            logger.info(f"تم بناء خريطة المفاهيم: {len(self.graph.nodes)} مفهوم، {len(self.graph.edges)} علاقة")
            
            return self.graph
            
        except Exception as e:
            logger.error(f"خطأ في بناء خريطة المفاهيم: {e}")
            return nx.Graph()
    
    def visualize_concept_map(self, output_path: Path, format: str = "png") -> Path:
        """
        إنشاء تصور مرئي لخريطة المفاهيم
        
        Args:
            output_path: مسار حفظ الصورة
            format: تنسيق الصورة (png, html, svg)
            
        Returns:
            مسار الملف المحفوظ
        """
        try:
            if self.graph.number_of_nodes() == 0:
                raise ValueError("لا توجد خريطة مفاهيم لعرضها")
            
            if format.lower() == "html":
                return self._create_interactive_visualization(output_path)
            else:
                return self._create_static_visualization(output_path, format)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء التصور المرئي: {e}")
            raise
    
    def _create_static_visualization(self, output_path: Path, format: str) -> Path:
        """إنشاء تصور مرئي ثابت"""
        plt.figure(figsize=(16, 12))
        
        # تحديد موضع العقد
        layout_algorithm = CONCEPT_MAP_CONFIG["layout_algorithm"]
        
        if layout_algorithm == "spring":
            pos = nx.spring_layout(self.graph, k=3, iterations=50)
        elif layout_algorithm == "circular":
            pos = nx.circular_layout(self.graph)
        else:
            pos = nx.random_layout(self.graph)
        
        # تحديد أحجام العقد بناءً على الأهمية
        node_sizes = []
        for node in self.graph.nodes():
            importance = self.graph.nodes[node].get("importance", 0.1)
            size = importance * CONCEPT_MAP_CONFIG["node_size_factor"]
            node_sizes.append(max(100, min(2000, size)))
        
        # تحديد ألوان العقد بناءً على النوع
        node_colors = []
        color_map = {
            "definition": "#FF6B6B",
            "process": "#4ECDC4",
            "category": "#45B7D1",
            "property": "#96CEB4",
            "example": "#FFEAA7",
            "general": "#DDA0DD"
        }
        
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get("type", "general")
            node_colors.append(color_map.get(node_type, color_map["general"]))
        
        # رسم العقد
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_size=node_sizes,
            node_color=node_colors,
            alpha=0.8
        )
        
        # رسم الحواف
        edge_weights = [self.graph[u][v].get("strength", 0.5) for u, v in self.graph.edges()]
        nx.draw_networkx_edges(
            self.graph, pos,
            width=[w * 3 for w in edge_weights],
            alpha=0.6,
            edge_color="gray"
        )
        
        # إضافة التسميات
        labels = {}
        for node in self.graph.nodes():
            # تقصير النص الطويل
            label = node[:20] + "..." if len(node) > 20 else node
            labels[node] = label
        
        nx.draw_networkx_labels(
            self.graph, pos,
            labels=labels,
            font_size=8,
            font_family='Arial Unicode MS'
        )
        
        plt.title("خريطة المفاهيم", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # حفظ الصورة
        output_file = output_path.with_suffix(f".{format}")
        plt.savefig(output_file, format=format, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"تم حفظ خريطة المفاهيم في: {output_file}")
        
        return output_file
    
    def _create_interactive_visualization(self, output_path: Path) -> Path:
        """إنشاء تصور مرئي تفاعلي باستخدام Pyvis"""
        try:
            # إنشاء شبكة تفاعلية
            net = Network(
                height="600px",
                width="100%",
                bgcolor="#ffffff",
                font_color="black",
                directed=False
            )
            
            # إضافة العقد
            for node in self.graph.nodes():
                node_data = self.graph.nodes[node]
                
                # تحديد حجم العقدة
                importance = node_data.get("importance", 0.1)
                size = max(10, min(50, importance * 100))
                
                # تحديد لون العقدة
                node_type = node_data.get("type", "general")
                color_map = {
                    "definition": "#FF6B6B",
                    "process": "#4ECDC4",
                    "category": "#45B7D1",
                    "property": "#96CEB4",
                    "example": "#FFEAA7",
                    "general": "#DDA0DD"
                }
                color = color_map.get(node_type, color_map["general"])
                
                # إضافة معلومات إضافية
                title = f"النوع: {node_type}\\nالأهمية: {importance:.2f}"
                if node_data.get("context"):
                    title += f"\\nالسياق: {node_data['context'][:100]}..."
                
                net.add_node(
                    node,
                    label=node,
                    title=title,
                    size=size,
                    color=color
                )
            
            # إضافة الحواف
            for edge in self.graph.edges():
                source, target = edge
                edge_data = self.graph.edges[edge]
                
                relation_type = edge_data.get("relation_type", "unknown")
                strength = edge_data.get("strength", 0.5)
                
                net.add_edge(
                    source,
                    target,
                    title=f"نوع العلاقة: {relation_type}\\nالقوة: {strength:.2f}",
                    width=strength * 5
                )
            
            # تحسين التخطيط
            net.set_options("""
            var options = {
                "physics": {
                    "enabled": true,
                    "stabilization": {"iterations": 100}
                },
                "nodes": {
                    "font": {"size": 14}
                },
                "edges": {
                    "smooth": true
                }
            }
            """)
            
            # حفظ الملف
            output_file = output_path.with_suffix(".html")
            net.save_graph(str(output_file))
            
            logger.info(f"تم حفظ خريطة المفاهيم التفاعلية في: {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء التصور التفاعلي: {e}")
            raise
    
    def save_concept_map_data(self, output_path: Path):
        """حفظ بيانات خريطة المفاهيم في ملف JSON"""
        try:
            data = {
                "concepts": self.concepts,
                "relationships": self.relationships,
                "graph_info": {
                    "nodes_count": len(self.graph.nodes),
                    "edges_count": len(self.graph.edges)
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم حفظ بيانات خريطة المفاهيم في: {output_path}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات خريطة المفاهيم: {e}")
            raise
    
    def get_concept_statistics(self) -> Dict:
        """الحصول على إحصائيات خريطة المفاهيم"""
        if not self.graph:
            return {"status": "no_map"}
        
        return {
            "total_concepts": len(self.concepts),
            "total_relationships": len(self.relationships),
            "graph_density": nx.density(self.graph),
            "connected_components": nx.number_connected_components(self.graph),
            "average_clustering": nx.average_clustering(self.graph),
            "concept_types": {
                concept_type: len([c for c in self.concepts if c.get("concept_type") == concept_type])
                for concept_type in ["definition", "process", "category", "property", "example", "general"]
            }
        }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مُنشئ خرائط المفاهيم
    mapper = ConceptMapper()
    
    # مثال على إنشاء خريطة مفاهيم
    sample_text = """
    الذكاء الاصطناعي هو مجال في علوم الحاسوب يهدف إلى إنشاء أنظمة ذكية.
    يشمل التعلم الآلي والتعلم العميق ومعالجة اللغة الطبيعية.
    التعلم الآلي يسبب تحسينات في الأداء من خلال الخبرة.
    """
    
    # graph = mapper.build_concept_map(sample_text)
    # print(f"تم إنشاء خريطة مفاهيم بـ {len(graph.nodes)} مفهوم")
