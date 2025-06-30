"""
Moteur de décision et validation croisée
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re
import difflib
from statistics import mean, median

from loguru import logger

from ..models.task import Task, TaskResult, ValidationResult
from ..utils.config import Config
from ..utils.text_analysis import TextAnalyzer
from ..utils.similarity import SimilarityCalculator


class DecisionEngine:
    """
    Moteur de décision pour la validation croisée et le consensus
    
    Responsabilités:
    - Validation croisée des résultats
    - Calcul du consensus entre modèles
    - Détection des incohérences
    - Sélection du meilleur résultat
    - Analyse de qualité des réponses
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.text_analyzer = TextAnalyzer()
        self.similarity_calc = SimilarityCalculator()
        
        # Seuils configurables
        self.min_consensus_score = config.get('decision_engine.min_consensus_score', 0.7)
        self.min_confidence_threshold = config.get('decision_engine.min_confidence_threshold', 0.5)
        self.similarity_threshold = config.get('decision_engine.similarity_threshold', 0.6)
        
        logger.info("DecisionEngine initialisé")
    
    async def validate_results(self, task: Task, results: List[TaskResult]) -> ValidationResult:
        """
        Valider les résultats de plusieurs modèles d'IA
        
        Args:
            task: La tâche originale
            results: Liste des résultats des différents modèles
            
        Returns:
            ValidationResult: Résultat de la validation
        """
        if not results:
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                consensus_score=0.0,
                discrepancies=["Aucun résultat à valider"],
                validation_notes="Aucun résultat fourni"
            )
        
        if len(results) == 1:
            # Un seul résultat, validation basique
            result = results[0]
            is_valid = result.confidence >= self.min_confidence_threshold
            
            return ValidationResult(
                is_valid=is_valid,
                confidence=result.confidence,
                consensus_score=1.0,
                recommended_result=result.content if is_valid else None,
                validation_notes=f"Validation d'un seul résultat (confiance: {result.confidence})"
            )
        
        logger.info(f"Validation de {len(results)} résultats pour la tâche {task.id}")
        
        # Analyse comparative des résultats
        analysis = await self._analyze_results(task, results)
        
        # Calcul du score de consensus
        consensus_score = self._calculate_consensus_score(results, analysis)
        
        # Détection des incohérences
        discrepancies = self._detect_discrepancies(results, analysis)
        
        # Sélection du meilleur résultat
        best_result = self._select_best_result(results, analysis)
        
        # Décision finale
        is_valid = (
            consensus_score >= self.min_consensus_score and
            best_result is not None and
            len(discrepancies) <= self.config.get('decision_engine.max_discrepancies', 3)
        )
        
        # Calcul de la confiance globale
        overall_confidence = self._calculate_overall_confidence(results, analysis, consensus_score)
        
        validation_notes = self._generate_validation_notes(analysis, consensus_score, discrepancies)
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=overall_confidence,
            consensus_score=consensus_score,
            discrepancies=discrepancies,
            recommended_result=best_result.content if best_result else None,
            validation_notes=validation_notes
        )
    
    async def _analyze_results(self, task: Task, results: List[TaskResult]) -> Dict[str, Any]:
        """Analyser les résultats en détail"""
        analysis = {
            'content_similarities': [],
            'length_analysis': {},
            'quality_scores': [],
            'semantic_analysis': {},
            'factual_consistency': {},
            'style_analysis': {}
        }
        
        # Analyse des similarités entre contenus
        for i, result1 in enumerate(results):
            for j, result2 in enumerate(results[i+1:], i+1):
                similarity = await self.similarity_calc.calculate_similarity(
                    result1.content, result2.content
                )
                analysis['content_similarities'].append({
                    'models': [result1.model_id, result2.model_id],
                    'similarity': similarity,
                    'indices': [i, j]
                })
        
        # Analyse des longueurs
        lengths = [len(result.content) for result in results]
        analysis['length_analysis'] = {
            'mean': mean(lengths),
            'median': median(lengths),
            'min': min(lengths),
            'max': max(lengths),
            'std_dev': self._calculate_std_dev(lengths)
        }
        
        # Analyse de qualité
        for result in results:
            quality_score = await self.text_analyzer.analyze_quality(result.content)
            analysis['quality_scores'].append({
                'model_id': result.model_id,
                'quality_score': quality_score,
                'confidence': result.confidence
            })
        
        # Analyse sémantique (détection des thèmes principaux)
        all_content = [result.content for result in results]
        analysis['semantic_analysis'] = await self.text_analyzer.analyze_semantic_consistency(all_content)
        
        # Analyse de cohérence factuelle
        analysis['factual_consistency'] = await self._analyze_factual_consistency(results)
        
        # Analyse de style
        analysis['style_analysis'] = await self._analyze_style_consistency(results)
        
        return analysis
    
    def _calculate_consensus_score(self, results: List[TaskResult], analysis: Dict[str, Any]) -> float:
        """Calculer le score de consensus entre les résultats"""
        if len(results) <= 1:
            return 1.0
        
        # Facteurs de consensus
        similarity_factor = self._calculate_similarity_factor(analysis['content_similarities'])
        confidence_factor = self._calculate_confidence_factor(results)
        quality_factor = self._calculate_quality_factor(analysis['quality_scores'])
        semantic_factor = analysis['semantic_analysis'].get('consistency_score', 0.5)
        factual_factor = analysis['factual_consistency'].get('consistency_score', 0.5)
        
        # Score pondéré
        consensus_score = (
            similarity_factor * 0.3 +
            confidence_factor * 0.2 +
            quality_factor * 0.2 +
            semantic_factor * 0.15 +
            factual_factor * 0.15
        )
        
        return min(1.0, max(0.0, consensus_score))
    
    def _calculate_similarity_factor(self, similarities: List[Dict[str, Any]]) -> float:
        """Calculer le facteur de similarité"""
        if not similarities:
            return 0.0
        
        similarity_scores = [sim['similarity'] for sim in similarities]
        return mean(similarity_scores)
    
    def _calculate_confidence_factor(self, results: List[TaskResult]) -> float:
        """Calculer le facteur de confiance"""
        confidences = [result.confidence for result in results]
        
        # Pénaliser les grandes variations de confiance
        confidence_mean = mean(confidences)
        confidence_std = self._calculate_std_dev(confidences)
        
        # Facteur basé sur la moyenne et la stabilité
        stability_factor = max(0, 1 - confidence_std)
        return confidence_mean * stability_factor
    
    def _calculate_quality_factor(self, quality_scores: List[Dict[str, Any]]) -> float:
        """Calculer le facteur de qualité"""
        if not quality_scores:
            return 0.0
        
        scores = [qs['quality_score'] for qs in quality_scores]
        return mean(scores)
    
    def _detect_discrepancies(self, results: List[TaskResult], analysis: Dict[str, Any]) -> List[str]:
        """Détecter les incohérences entre les résultats"""
        discrepancies = []
        
        # Vérifier les similarités faibles
        low_similarities = [
            sim for sim in analysis['content_similarities'] 
            if sim['similarity'] < self.similarity_threshold
        ]
        
        if low_similarities:
            models_with_issues = set()
            for sim in low_similarities:
                models_with_issues.update(sim['models'])
            
            discrepancies.append(
                f"Faible similarité entre les modèles: {', '.join(models_with_issues)}"
            )
        
        # Vérifier les variations de longueur importantes
        length_analysis = analysis['length_analysis']
        if length_analysis['std_dev'] > length_analysis['mean'] * 0.5:
            discrepancies.append(
                f"Variations importantes de longueur (écart-type: {length_analysis['std_dev']:.1f})"
            )
        
        # Vérifier les scores de qualité faibles
        low_quality_models = [
            qs['model_id'] for qs in analysis['quality_scores']
            if qs['quality_score'] < 0.5
        ]
        
        if low_quality_models:
            discrepancies.append(
                f"Qualité faible détectée pour: {', '.join(low_quality_models)}"
            )
        
        # Vérifier la cohérence factuelle
        factual_issues = analysis['factual_consistency'].get('issues', [])
        discrepancies.extend(factual_issues)
        
        # Vérifier la cohérence sémantique
        if analysis['semantic_analysis'].get('consistency_score', 1.0) < 0.6:
            discrepancies.append("Incohérence sémantique détectée entre les réponses")
        
        return discrepancies
    
    def _select_best_result(self, results: List[TaskResult], analysis: Dict[str, Any]) -> Optional[TaskResult]:
        """Sélectionner le meilleur résultat"""
        if not results:
            return None
        
        # Calculer un score composite pour chaque résultat
        scored_results = []
        
        for i, result in enumerate(results):
            # Score de base (confiance)
            score = result.confidence
            
            # Bonus pour la qualité
            quality_info = next(
                (qs for qs in analysis['quality_scores'] if qs['model_id'] == result.model_id),
                {'quality_score': 0.5}
            )
            score += quality_info['quality_score'] * 0.3
            
            # Bonus pour la cohérence avec les autres
            similarity_bonus = 0
            similarity_count = 0
            
            for sim in analysis['content_similarities']:
                if result.model_id in sim['models']:
                    similarity_bonus += sim['similarity']
                    similarity_count += 1
            
            if similarity_count > 0:
                score += (similarity_bonus / similarity_count) * 0.2
            
            # Pénalité pour la longueur excessive ou insuffisante
            length_penalty = 0
            content_length = len(result.content)
            mean_length = analysis['length_analysis']['mean']
            
            if content_length < mean_length * 0.5 or content_length > mean_length * 2:
                length_penalty = 0.1
            
            score -= length_penalty
            
            scored_results.append((result, score))
        
        # Trier par score décroissant
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        return scored_results[0][0]
    
    def _calculate_overall_confidence(
        self, 
        results: List[TaskResult], 
        analysis: Dict[str, Any], 
        consensus_score: float
    ) -> float:
        """Calculer la confiance globale"""
        if not results:
            return 0.0
        
        # Confiance moyenne des résultats
        mean_confidence = mean([result.confidence for result in results])
        
        # Ajustement basé sur le consensus
        consensus_adjustment = consensus_score * 0.3
        
        # Ajustement basé sur la qualité
        quality_scores = [qs['quality_score'] for qs in analysis['quality_scores']]
        quality_adjustment = mean(quality_scores) * 0.2
        
        # Confiance finale
        overall_confidence = mean_confidence + consensus_adjustment + quality_adjustment
        
        return min(1.0, max(0.0, overall_confidence))
    
    def _generate_validation_notes(
        self, 
        analysis: Dict[str, Any], 
        consensus_score: float, 
        discrepancies: List[str]
    ) -> str:
        """Générer les notes de validation"""
        notes = []
        
        notes.append(f"Score de consensus: {consensus_score:.3f}")
        
        # Résumé des similarités
        if analysis['content_similarities']:
            similarities = [sim['similarity'] for sim in analysis['content_similarities']]
            notes.append(f"Similarité moyenne: {mean(similarities):.3f}")
        
        # Résumé de la qualité
        if analysis['quality_scores']:
            qualities = [qs['quality_score'] for qs in analysis['quality_scores']]
            notes.append(f"Qualité moyenne: {mean(qualities):.3f}")
        
        # Analyse sémantique
        semantic_score = analysis['semantic_analysis'].get('consistency_score', 0)
        notes.append(f"Cohérence sémantique: {semantic_score:.3f}")
        
        # Incohérences
        if discrepancies:
            notes.append(f"Incohérences détectées: {len(discrepancies)}")
            for disc in discrepancies[:3]:  # Limiter à 3 pour la lisibilité
                notes.append(f"  - {disc}")
        
        return " | ".join(notes)
    
    async def _analyze_factual_consistency(self, results: List[TaskResult]) -> Dict[str, Any]:
        """Analyser la cohérence factuelle entre les résultats"""
        # Implémentation simplifiée - peut être étendue avec des modèles NLP spécialisés
        
        # Extraire les faits/affirmations de chaque résultat
        facts_by_model = {}
        for result in results:
            facts = await self.text_analyzer.extract_facts(result.content)
            facts_by_model[result.model_id] = facts
        
        # Comparer les faits entre modèles
        consistent_facts = []
        inconsistent_facts = []
        
        all_facts = []
        for facts in facts_by_model.values():
            all_facts.extend(facts)
        
        # Grouper les faits similaires
        fact_groups = await self.text_analyzer.group_similar_facts(all_facts)
        
        for group in fact_groups:
            if len(group) >= len(results) * 0.6:  # Majorité des modèles d'accord
                consistent_facts.extend(group)
            else:
                inconsistent_facts.extend(group)
        
        consistency_score = len(consistent_facts) / max(1, len(all_facts))
        
        issues = []
        if inconsistent_facts:
            issues.append(f"{len(inconsistent_facts)} faits incohérents détectés")
        
        return {
            'consistency_score': consistency_score,
            'consistent_facts': len(consistent_facts),
            'inconsistent_facts': len(inconsistent_facts),
            'issues': issues
        }
    
    async def _analyze_style_consistency(self, results: List[TaskResult]) -> Dict[str, Any]:
        """Analyser la cohérence de style entre les résultats"""
        style_metrics = []
        
        for result in results:
            metrics = await self.text_analyzer.analyze_style(result.content)
            style_metrics.append({
                'model_id': result.model_id,
                'metrics': metrics
            })
        
        # Calculer la variance des métriques de style
        style_variance = {}
        if style_metrics:
            for metric_name in style_metrics[0]['metrics'].keys():
                values = [sm['metrics'][metric_name] for sm in style_metrics]
                style_variance[metric_name] = self._calculate_std_dev(values)
        
        # Score de cohérence basé sur les variances
        consistency_score = 1.0 - mean(style_variance.values()) if style_variance else 1.0
        
        return {
            'consistency_score': max(0.0, min(1.0, consistency_score)),
            'style_variance': style_variance,
            'individual_metrics': style_metrics
        }
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculer l'écart-type"""
        if len(values) <= 1:
            return 0.0
        
        mean_val = mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    async def compare_with_reference(self, results: List[TaskResult], reference: str) -> Dict[str, Any]:
        """Comparer les résultats avec une référence"""
        comparisons = []
        
        for result in results:
            similarity = await self.similarity_calc.calculate_similarity(result.content, reference)
            
            comparisons.append({
                'model_id': result.model_id,
                'similarity_to_reference': similarity,
                'confidence': result.confidence,
                'combined_score': (similarity + result.confidence) / 2
            })
        
        # Trier par score combiné
        comparisons.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return {
            'best_match': comparisons[0] if comparisons else None,
            'all_comparisons': comparisons,
            'average_similarity': mean([c['similarity_to_reference'] for c in comparisons]) if comparisons else 0.0
        }

