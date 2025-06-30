"""
Analyseur de texte pour la validation et l'analyse de qualité
"""

import re
import string
from typing import List, Dict, Any
from collections import Counter
import asyncio


class TextAnalyzer:
    """
    Analyseur de texte pour évaluer la qualité et extraire des informations
    """
    
    def __init__(self):
        # Mots vides français
        self.french_stopwords = {
            'le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour',
            'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'pas', 'tout', 'plus',
            'par', 'grand', 'en', 'une', 'être', 'et', 'à', 'il', 'avoir', 'ne', 'je', 'son',
            'que', 'se', 'qui', 'ce', 'dans', 'en', 'du', 'elle', 'au', 'de', 'ce', 'le',
            'pour', 'sont', 'avec', 'ils', 'tout', 'nous', 'sa', 'comme', 'mais', 'ou',
            'si', 'leur', 'y', 'dire', 'cette', 'où', 'très', 'bien', 'même', 'faire'
        }
        
        # Mots vides anglais
        self.english_stopwords = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for',
            'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his',
            'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my',
            'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if',
            'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like',
            'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your'
        }
    
    async def analyze_quality(self, text: str) -> float:
        """
        Analyser la qualité d'un texte
        
        Args:
            text: Le texte à analyser
            
        Returns:
            float: Score de qualité entre 0.0 et 1.0
        """
        if not text or len(text.strip()) == 0:
            return 0.0
        
        scores = []
        
        # 1. Longueur appropriée
        length_score = self._analyze_length(text)
        scores.append(length_score)
        
        # 2. Diversité du vocabulaire
        vocabulary_score = self._analyze_vocabulary_diversity(text)
        scores.append(vocabulary_score)
        
        # 3. Structure des phrases
        sentence_score = self._analyze_sentence_structure(text)
        scores.append(sentence_score)
        
        # 4. Cohérence grammaticale basique
        grammar_score = self._analyze_basic_grammar(text)
        scores.append(grammar_score)
        
        # 5. Présence d'informations utiles
        content_score = self._analyze_content_richness(text)
        scores.append(content_score)
        
        # Score final pondéré
        weights = [0.15, 0.25, 0.20, 0.20, 0.20]
        final_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return min(1.0, max(0.0, final_score))
    
    def _analyze_length(self, text: str) -> float:
        """Analyser la longueur du texte"""
        length = len(text.strip())
        
        if length < 10:
            return 0.2
        elif length < 50:
            return 0.5
        elif length < 200:
            return 0.8
        elif length < 2000:
            return 1.0
        elif length < 5000:
            return 0.9
        else:
            return 0.7  # Très long, peut être verbeux
    
    def _analyze_vocabulary_diversity(self, text: str) -> float:
        """Analyser la diversité du vocabulaire"""
        words = self._extract_words(text)
        
        if len(words) == 0:
            return 0.0
        
        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words)
        
        # Normaliser le score
        if diversity_ratio > 0.7:
            return 1.0
        elif diversity_ratio > 0.5:
            return 0.8
        elif diversity_ratio > 0.3:
            return 0.6
        else:
            return 0.4
    
    def _analyze_sentence_structure(self, text: str) -> float:
        """Analyser la structure des phrases"""
        sentences = self._split_sentences(text)
        
        if len(sentences) == 0:
            return 0.0
        
        scores = []
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            # Longueur optimale des phrases
            if 5 <= sentence_length <= 25:
                scores.append(1.0)
            elif 3 <= sentence_length <= 35:
                scores.append(0.8)
            elif sentence_length <= 50:
                scores.append(0.6)
            else:
                scores.append(0.3)
        
        return sum(scores) / len(scores)
    
    def _analyze_basic_grammar(self, text: str) -> float:
        """Analyse grammaticale basique"""
        score = 1.0
        
        # Vérifier la ponctuation basique
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 0:
                # Vérifier que les phrases commencent par une majuscule
                if not sentence[0].isupper():
                    score -= 0.1
                
                # Vérifier la ponctuation finale
                if not sentence.endswith(('.', '!', '?', ':', ';')):
                    score -= 0.1
        
        # Vérifier les répétitions excessives
        words = self._extract_words(text)
        word_counts = Counter(words)
        
        for word, count in word_counts.items():
            if len(word) > 3 and count > len(words) * 0.1:  # Plus de 10% du texte
                score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _analyze_content_richness(self, text: str) -> float:
        """Analyser la richesse du contenu"""
        words = self._extract_words(text)
        
        if len(words) == 0:
            return 0.0
        
        # Filtrer les mots vides
        content_words = [
            word for word in words 
            if word.lower() not in self.french_stopwords 
            and word.lower() not in self.english_stopwords
            and len(word) > 2
        ]
        
        content_ratio = len(content_words) / len(words)
        
        # Vérifier la présence de différents types de mots
        has_numbers = any(char.isdigit() for char in text)
        has_punctuation = any(char in string.punctuation for char in text)
        has_varied_case = any(char.isupper() for char in text) and any(char.islower() for char in text)
        
        bonus = 0.0
        if has_numbers:
            bonus += 0.1
        if has_punctuation:
            bonus += 0.1
        if has_varied_case:
            bonus += 0.1
        
        return min(1.0, content_ratio + bonus)
    
    def _extract_words(self, text: str) -> List[str]:
        """Extraire les mots d'un texte"""
        # Nettoyer le texte
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [word for word in words if len(word) > 0]
    
    def _split_sentences(self, text: str) -> List[str]:
        """Diviser le texte en phrases"""
        # Pattern simple pour diviser les phrases
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    async def extract_facts(self, text: str) -> List[str]:
        """
        Extraire les faits/affirmations d'un texte
        
        Args:
            text: Le texte à analyser
            
        Returns:
            List[str]: Liste des faits extraits
        """
        facts = []
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Heuristiques simples pour identifier les faits
            if self._is_factual_sentence(sentence):
                facts.append(sentence)
        
        return facts
    
    def _is_factual_sentence(self, sentence: str) -> bool:
        """Déterminer si une phrase contient un fait"""
        sentence_lower = sentence.lower()
        
        # Indicateurs de faits
        fact_indicators = [
            'est', 'sont', 'était', 'étaient', 'sera', 'seront',
            'a', 'ont', 'avait', 'avaient', 'aura', 'auront',
            'mesure', 'pèse', 'coûte', 'vaut', 'contient',
            'situé', 'localisé', 'fondé', 'créé', 'inventé',
            'né', 'mort', 'publié', 'découvert'
        ]
        
        # Indicateurs d'opinion (à éviter)
        opinion_indicators = [
            'pense', 'crois', 'suppose', 'imagine', 'semble',
            'paraît', 'probablement', 'peut-être', 'sans doute',
            'opinion', 'avis', 'sentiment', 'impression'
        ]
        
        # Vérifier la présence d'indicateurs de faits
        has_fact_indicator = any(indicator in sentence_lower for indicator in fact_indicators)
        
        # Vérifier l'absence d'indicateurs d'opinion
        has_opinion_indicator = any(indicator in sentence_lower for indicator in opinion_indicators)
        
        # Vérifier la présence de nombres ou dates
        has_numbers = re.search(r'\d+', sentence)
        
        return (has_fact_indicator or has_numbers) and not has_opinion_indicator
    
    async def group_similar_facts(self, facts: List[str]) -> List[List[str]]:
        """
        Grouper les faits similaires
        
        Args:
            facts: Liste des faits
            
        Returns:
            List[List[str]]: Groupes de faits similaires
        """
        if not facts:
            return []
        
        groups = []
        used_facts = set()
        
        for i, fact1 in enumerate(facts):
            if i in used_facts:
                continue
            
            current_group = [fact1]
            used_facts.add(i)
            
            for j, fact2 in enumerate(facts[i+1:], i+1):
                if j in used_facts:
                    continue
                
                # Calculer la similarité simple
                similarity = self._calculate_text_similarity(fact1, fact2)
                
                if similarity > 0.6:  # Seuil de similarité
                    current_group.append(fact2)
                    used_facts.add(j)
            
            groups.append(current_group)
        
        return groups
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculer la similarité entre deux textes"""
        words1 = set(self._extract_words(text1.lower()))
        words2 = set(self._extract_words(text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def analyze_semantic_consistency(self, texts: List[str]) -> Dict[str, Any]:
        """
        Analyser la cohérence sémantique entre plusieurs textes
        
        Args:
            texts: Liste des textes à comparer
            
        Returns:
            Dict contenant l'analyse de cohérence
        """
        if len(texts) < 2:
            return {'consistency_score': 1.0, 'main_themes': [], 'divergences': []}
        
        # Extraire les thèmes principaux de chaque texte
        themes_by_text = []
        for text in texts:
            themes = self._extract_main_themes(text)
            themes_by_text.append(themes)
        
        # Trouver les thèmes communs
        all_themes = set()
        for themes in themes_by_text:
            all_themes.update(themes)
        
        common_themes = []
        for theme in all_themes:
            count = sum(1 for themes in themes_by_text if theme in themes)
            if count >= len(texts) * 0.6:  # Présent dans au moins 60% des textes
                common_themes.append(theme)
        
        # Calculer le score de cohérence
        consistency_score = len(common_themes) / max(1, len(all_themes))
        
        # Identifier les divergences
        divergences = []
        for i, themes in enumerate(themes_by_text):
            unique_themes = themes - set(common_themes)
            if unique_themes:
                divergences.append(f"Texte {i+1}: {', '.join(list(unique_themes)[:3])}")
        
        return {
            'consistency_score': consistency_score,
            'main_themes': common_themes,
            'divergences': divergences
        }
    
    def _extract_main_themes(self, text: str) -> set:
        """Extraire les thèmes principaux d'un texte"""
        words = self._extract_words(text.lower())
        
        # Filtrer les mots vides et courts
        content_words = [
            word for word in words 
            if word not in self.french_stopwords 
            and word not in self.english_stopwords
            and len(word) > 3
        ]
        
        # Compter les fréquences
        word_counts = Counter(content_words)
        
        # Prendre les mots les plus fréquents comme thèmes
        threshold = max(1, len(content_words) * 0.02)  # Au moins 2% du texte
        themes = {word for word, count in word_counts.items() if count >= threshold}
        
        return themes
    
    async def analyze_style(self, text: str) -> Dict[str, float]:
        """
        Analyser le style d'un texte
        
        Args:
            text: Le texte à analyser
            
        Returns:
            Dict contenant les métriques de style
        """
        sentences = self._split_sentences(text)
        words = self._extract_words(text)
        
        if not sentences or not words:
            return {
                'avg_sentence_length': 0.0,
                'avg_word_length': 0.0,
                'formality_score': 0.0,
                'complexity_score': 0.0
            }
        
        # Longueur moyenne des phrases
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Longueur moyenne des mots
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Score de formalité (basé sur la longueur des mots et la complexité)
        long_words = [word for word in words if len(word) > 6]
        formality_score = len(long_words) / len(words)
        
        # Score de complexité (basé sur la structure des phrases)
        complex_sentences = [s for s in sentences if len(s.split()) > 15]
        complexity_score = len(complex_sentences) / len(sentences)
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'formality_score': formality_score,
            'complexity_score': complexity_score
        }

