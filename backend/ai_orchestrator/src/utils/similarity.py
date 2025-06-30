"""
Calculateur de similarité pour comparer les textes
"""

import re
import math
from typing import List, Dict, Set
from collections import Counter
import asyncio


class SimilarityCalculator:
    """
    Calculateur de similarité entre textes
    """
    
    def __init__(self):
        # Mots vides pour filtrer
        self.stopwords = {
            # Français
            'le', 'de', 'et', 'à', 'un', 'il', 'être', 'avoir', 'que', 'pour',
            'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'pas', 'tout',
            'plus', 'par', 'grand', 'en', 'du', 'elle', 'au', 'sont', 'comme',
            'mais', 'ou', 'si', 'leur', 'y', 'dire', 'cette', 'où', 'très', 'bien',
            # Anglais
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it',
            'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this',
            'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or'
        }
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculer la similarité entre deux textes
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            
        Returns:
            float: Score de similarité entre 0.0 et 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        # Calculer plusieurs métriques de similarité
        jaccard_sim = self._jaccard_similarity(text1, text2)
        cosine_sim = self._cosine_similarity(text1, text2)
        semantic_sim = await self._semantic_similarity(text1, text2)
        
        # Moyenne pondérée
        similarity = (jaccard_sim * 0.3 + cosine_sim * 0.4 + semantic_sim * 0.3)
        
        return min(1.0, max(0.0, similarity))
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculer la similarité de Jaccard"""
        words1 = self._extract_words(text1)
        words2 = self._extract_words(text2)
        
        set1 = set(words1)
        set2 = set(words2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculer la similarité cosinus"""
        words1 = self._extract_words(text1)
        words2 = self._extract_words(text2)
        
        # Créer les vecteurs de fréquence
        all_words = set(words1 + words2)
        
        if not all_words:
            return 0.0
        
        vector1 = [words1.count(word) for word in all_words]
        vector2 = [words2.count(word) for word in all_words]
        
        # Calculer le produit scalaire
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        
        # Calculer les normes
        norm1 = math.sqrt(sum(a * a for a in vector1))
        norm2 = math.sqrt(sum(b * b for b in vector2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculer la similarité sémantique"""
        # Implémentation simplifiée basée sur les concepts
        concepts1 = self._extract_concepts(text1)
        concepts2 = self._extract_concepts(text2)
        
        if not concepts1 or not concepts2:
            return 0.0
        
        # Comparer les concepts
        common_concepts = concepts1.intersection(concepts2)
        all_concepts = concepts1.union(concepts2)
        
        return len(common_concepts) / len(all_concepts)
    
    def _extract_words(self, text: str) -> List[str]:
        """Extraire et nettoyer les mots d'un texte"""
        # Nettoyer le texte
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filtrer les mots vides et courts
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in self.stopwords
        ]
        
        return filtered_words
    
    def _extract_concepts(self, text: str) -> Set[str]:
        """Extraire les concepts principaux d'un texte"""
        words = self._extract_words(text)
        
        # Compter les fréquences
        word_counts = Counter(words)
        
        # Prendre les mots les plus fréquents comme concepts
        total_words = len(words)
        threshold = max(1, total_words * 0.02)  # Au moins 2% du texte
        
        concepts = {
            word for word, count in word_counts.items() 
            if count >= threshold and len(word) > 3
        }
        
        return concepts
    
    async def calculate_batch_similarity(self, texts: List[str]) -> Dict[tuple, float]:
        """
        Calculer la similarité entre tous les pairs de textes
        
        Args:
            texts: Liste des textes à comparer
            
        Returns:
            Dict avec les pairs comme clés et similarités comme valeurs
        """
        similarities = {}
        
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                similarity = await self.calculate_similarity(texts[i], texts[j])
                similarities[(i, j)] = similarity
        
        return similarities
    
    def find_most_similar(self, target_text: str, candidate_texts: List[str]) -> tuple:
        """
        Trouver le texte le plus similaire au texte cible
        
        Args:
            target_text: Texte de référence
            candidate_texts: Liste des textes candidats
            
        Returns:
            tuple: (index, similarity_score) du texte le plus similaire
        """
        best_index = -1
        best_similarity = 0.0
        
        for i, candidate in enumerate(candidate_texts):
            similarity = asyncio.run(self.calculate_similarity(target_text, candidate))
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_index = i
        
        return (best_index, best_similarity)
    
    def calculate_diversity_score(self, texts: List[str]) -> float:
        """
        Calculer un score de diversité pour une liste de textes
        
        Args:
            texts: Liste des textes
            
        Returns:
            float: Score de diversité (plus élevé = plus diversifié)
        """
        if len(texts) < 2:
            return 1.0
        
        similarities = []
        
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                similarity = asyncio.run(self.calculate_similarity(texts[i], texts[j]))
                similarities.append(similarity)
        
        # Score de diversité = 1 - similarité moyenne
        avg_similarity = sum(similarities) / len(similarities)
        diversity_score = 1.0 - avg_similarity
        
        return max(0.0, min(1.0, diversity_score))
    
    def detect_plagiarism(self, text1: str, text2: str, threshold: float = 0.8) -> Dict[str, any]:
        """
        Détecter un potentiel plagiat entre deux textes
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            threshold: Seuil de similarité pour détecter le plagiat
            
        Returns:
            Dict contenant les résultats de détection
        """
        similarity = asyncio.run(self.calculate_similarity(text1, text2))
        
        is_plagiarism = similarity >= threshold
        
        # Analyser les segments similaires
        similar_segments = self._find_similar_segments(text1, text2)
        
        return {
            'is_plagiarism': is_plagiarism,
            'similarity_score': similarity,
            'threshold': threshold,
            'similar_segments': similar_segments,
            'confidence': min(1.0, similarity * 1.2) if is_plagiarism else 1.0 - similarity
        }
    
    def _find_similar_segments(self, text1: str, text2: str, min_length: int = 5) -> List[Dict[str, str]]:
        """Trouver les segments similaires entre deux textes"""
        words1 = self._extract_words(text1)
        words2 = self._extract_words(text2)
        
        similar_segments = []
        
        # Recherche de séquences communes
        for i in range(len(words1) - min_length + 1):
            for j in range(len(words2) - min_length + 1):
                # Vérifier la longueur de la séquence commune
                length = 0
                while (i + length < len(words1) and 
                       j + length < len(words2) and 
                       words1[i + length] == words2[j + length]):
                    length += 1
                
                if length >= min_length:
                    segment1 = ' '.join(words1[i:i + length])
                    segment2 = ' '.join(words2[j:j + length])
                    
                    similar_segments.append({
                        'text1_segment': segment1,
                        'text2_segment': segment2,
                        'length': length,
                        'position1': i,
                        'position2': j
                    })
        
        # Trier par longueur décroissante
        similar_segments.sort(key=lambda x: x['length'], reverse=True)
        
        return similar_segments[:10]  # Limiter à 10 segments
    
    def calculate_readability_similarity(self, text1: str, text2: str) -> float:
        """
        Calculer la similarité de lisibilité entre deux textes
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            
        Returns:
            float: Score de similarité de lisibilité
        """
        metrics1 = self._calculate_readability_metrics(text1)
        metrics2 = self._calculate_readability_metrics(text2)
        
        # Comparer les métriques
        similarities = []
        
        for metric in ['avg_sentence_length', 'avg_word_length', 'complexity_score']:
            if metric in metrics1 and metric in metrics2:
                val1, val2 = metrics1[metric], metrics2[metric]
                max_val = max(val1, val2)
                if max_val > 0:
                    similarity = 1.0 - abs(val1 - val2) / max_val
                    similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """Calculer les métriques de lisibilité"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = self._extract_words(text)
        
        if not sentences or not words:
            return {
                'avg_sentence_length': 0.0,
                'avg_word_length': 0.0,
                'complexity_score': 0.0
            }
        
        # Longueur moyenne des phrases
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Longueur moyenne des mots
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Score de complexité (basé sur les mots longs)
        long_words = [word for word in words if len(word) > 6]
        complexity_score = len(long_words) / len(words)
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'complexity_score': complexity_score
        }

