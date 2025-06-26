"""AI-powered adaptive assessment engine using Item Response Theory (IRT)"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler
from tenacity import retry, stop_after_attempt, wait_exponential
import json

from app.models.evaluation import Question, Answer
from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class StudentAbility:
    """Represents a student's estimated ability level"""

    theta: float  # Ability parameter (-3 to 3)
    standard_error: float
    confidence_interval: Tuple[float, float]
    num_responses: int


@dataclass
class QuestionParameters:
    """IRT parameters for a question"""

    question_id: int
    difficulty: float  # b parameter
    discrimination: float  # a parameter
    guessing: float  # c parameter (for 3PL model)


class AdaptiveAssessmentEngine:
    """
    Implements Computer Adaptive Testing (CAT) using Item Response Theory
    """

    def __init__(self):
        self.min_questions = 5
        self.max_questions = 20
        self.stopping_threshold = 0.3  # Standard error threshold
        self.ability_range = (-3.0, 3.0)

    def calculate_probability(self, theta: float, params: QuestionParameters) -> float:
        """
        Calculate probability of correct response using 3-Parameter Logistic Model
        P(θ) = c + (1-c) / (1 + exp(-a(θ-b)))
        """
        exp_val = np.exp(-params.discrimination * (theta - params.difficulty))
        return params.guessing + (1 - params.guessing) / (1 + exp_val)

    def calculate_information(self, theta: float, params: QuestionParameters) -> float:
        """
        Calculate Fisher information for a question at given ability level
        I(θ) = a²P(θ)Q(θ)[(P(θ)-c)²/(1-c)²]
        """
        p = self.calculate_probability(theta, params)
        q = 1 - p

        if params.guessing >= p or params.guessing >= 1:
            return 0.0

        info = (params.discrimination**2) * p * q
        info *= ((p - params.guessing) ** 2) / ((1 - params.guessing) ** 2)

        return info

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def select_next_question(
        self, theta: float, available_questions: List[QuestionParameters], answered_questions: List[int]
    ) -> Optional[QuestionParameters]:
        """
        Select the most informative question for current ability estimate
        """
        if not available_questions:
            return None

        # Filter out already answered questions
        candidates = [q for q in available_questions if q.question_id not in answered_questions]

        if not candidates:
            return None

        # Calculate information for each candidate
        information_values = [(q, self.calculate_information(theta, q)) for q in candidates]

        # Sort by information value (descending)
        information_values.sort(key=lambda x: x[1], reverse=True)

        # Add some randomization to avoid always picking the same question
        # Pick from top 3 most informative questions
        top_candidates = information_values[:3]
        if top_candidates:
            import random

            selected = random.choice(top_candidates)
            return selected[0]

        return information_values[0][0]

    def estimate_ability(self, responses: List[Tuple[QuestionParameters, bool]]) -> StudentAbility:
        """
        Estimate student ability using Maximum Likelihood Estimation
        """
        if not responses:
            return StudentAbility(theta=0.0, standard_error=1.0, confidence_interval=(-2.0, 2.0), num_responses=0)

        # Simple MLE implementation
        theta = 0.0  # Start with average ability

        for _ in range(50):  # Newton-Raphson iterations
            first_derivative = 0.0
            second_derivative = 0.0

            for params, is_correct in responses:
                p = self.calculate_probability(theta, params)

                # First derivative of log-likelihood
                if is_correct:
                    first_derivative += params.discrimination * (1 - p)
                else:
                    first_derivative -= params.discrimination * p

                # Second derivative of log-likelihood
                second_derivative -= params.discrimination**2 * p * (1 - p)

            if abs(second_derivative) < 0.001:
                break

            # Update theta estimate
            theta_update = first_derivative / (-second_derivative)
            theta += theta_update

            # Bound theta to reasonable range
            theta = max(self.ability_range[0], min(self.ability_range[1], theta))

            if abs(theta_update) < 0.01:
                break

        # Calculate standard error
        information_sum = sum(self.calculate_information(theta, params) for params, _ in responses)

        if information_sum > 0:
            standard_error = 1.0 / np.sqrt(information_sum)
        else:
            standard_error = 1.0

        # 95% confidence interval
        confidence_interval = (theta - 1.96 * standard_error, theta + 1.96 * standard_error)

        return StudentAbility(
            theta=theta,
            standard_error=standard_error,
            confidence_interval=confidence_interval,
            num_responses=len(responses),
        )

    def should_stop_assessment(self, ability: StudentAbility) -> bool:
        """
        Determine if assessment should stop based on stopping criteria
        """
        # Check minimum questions
        if ability.num_responses < self.min_questions:
            return False

        # Check maximum questions
        if ability.num_responses >= self.max_questions:
            return True

        # Check standard error threshold
        if ability.standard_error <= self.stopping_threshold:
            return True

        return False

    def generate_performance_report(
        self, ability: StudentAbility, responses: List[Tuple[QuestionParameters, bool]]
    ) -> Dict:
        """
        Generate detailed performance report
        """
        # Convert ability to percentile
        # Using normal CDF approximation
        from scipy.stats import norm

        percentile = norm.cdf(ability.theta) * 100

        # Calculate topic-wise performance
        topic_performance = {}

        # Categorize ability level
        if ability.theta < -1:
            level = "Beginner"
        elif ability.theta < 0:
            level = "Intermediate-Low"
        elif ability.theta < 1:
            level = "Intermediate-High"
        else:
            level = "Advanced"

        return {
            "ability_score": round(ability.theta, 3),
            "percentile": round(percentile, 1),
            "confidence_interval": {
                "lower": round(ability.confidence_interval[0], 3),
                "upper": round(ability.confidence_interval[1], 3),
            },
            "standard_error": round(ability.standard_error, 3),
            "level": level,
            "total_questions": ability.num_responses,
            "accuracy": sum(1 for _, correct in responses if correct) / len(responses) * 100,
        }

    def predict_success_probability(self, ability: StudentAbility, task_difficulty: float) -> float:
        """
        Predict probability of success on a future task
        """
        # Simple prediction using ability vs difficulty
        z_score = (ability.theta - task_difficulty) / (1 + ability.standard_error)

        # Convert to probability using logistic function
        probability = 1 / (1 + np.exp(-z_score))

        return probability


class QuestionBankOptimizer:
    """
    Optimizes question bank based on usage statistics and psychometric properties
    """

    def __init__(self):
        self.scaler = StandardScaler()

    def analyze_question_quality(self, question_stats: Dict) -> Dict:
        """
        Analyze psychometric properties of questions
        """
        # Calculate discrimination index
        discrimination = self._calculate_discrimination(question_stats)

        # Calculate difficulty index
        difficulty = question_stats.get("correct_responses", 0) / max(question_stats.get("total_responses", 1), 1)

        # Calculate reliability (point-biserial correlation)
        reliability = self._calculate_reliability(question_stats)

        return {
            "discrimination": discrimination,
            "difficulty": difficulty,
            "reliability": reliability,
            "quality_score": (discrimination + reliability) / 2,
            "usage_count": question_stats.get("total_responses", 0),
        }

    def _calculate_discrimination(self, stats: Dict) -> float:
        """
        Calculate discrimination index using upper-lower method
        """
        upper_correct = stats.get("upper_third_correct", 0)
        upper_total = stats.get("upper_third_total", 1)
        lower_correct = stats.get("lower_third_correct", 0)
        lower_total = stats.get("lower_third_total", 1)

        if upper_total == 0 or lower_total == 0:
            return 0.0

        discrimination = (upper_correct / upper_total) - (lower_correct / lower_total)
        return max(0, min(1, discrimination))

    def _calculate_reliability(self, stats: Dict) -> float:
        """
        Calculate point-biserial correlation coefficient
        """
        # Simplified reliability calculation
        # In production, would use actual response data
        return stats.get("reliability_coefficient", 0.7)

    def recommend_questions_for_revision(self, question_analytics: List[Dict]) -> List[Dict]:
        """
        Identify questions that need revision based on quality metrics
        """
        recommendations = []

        for question in question_analytics:
            quality = question.get("quality_score", 0)
            discrimination = question.get("discrimination", 0)
            usage = question.get("usage_count", 0)

            issues = []

            if discrimination < 0.2:
                issues.append("Low discrimination - doesn't differentiate between ability levels")

            if quality < 0.4:
                issues.append("Poor psychometric properties")

            if usage < 10:
                issues.append("Insufficient usage data for reliable analysis")

            if issues:
                recommendations.append(
                    {
                        "question_id": question["id"],
                        "issues": issues,
                        "priority": "high" if discrimination < 0.1 else "medium",
                        "suggested_action": "revise" if discrimination < 0.2 else "monitor",
                    }
                )

        return recommendations
