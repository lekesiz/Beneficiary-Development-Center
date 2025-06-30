"""
AI Service for adaptive evaluation features.
Handles OpenAI GPT integration for intelligent question selection.
"""

import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from flask import current_app


class AIService:
    """Service for AI-powered adaptive evaluation features."""

    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY", "dummy-key-for-testing")
        if api_key and api_key != "dummy-key-for-testing":
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    def determine_next_difficulty(
        self, recent_responses: List[Dict[str, Any]], current_difficulty: str, evaluation_context: Dict[str, Any]
    ) -> str:
        """
        Determine the next question difficulty based on recent responses.

        Args:
            recent_responses: List of recent question responses with correctness
            current_difficulty: Current difficulty level ('easy', 'medium', 'hard')
            evaluation_context: Additional context about the evaluation

        Returns:
            Next difficulty level ('easy', 'medium', 'hard')
        """
        # Calculate performance metrics
        if not recent_responses:
            return current_difficulty

        correct_count = sum(1 for r in recent_responses if r.get("is_correct", False))
        total_count = len(recent_responses)
        accuracy = correct_count / total_count if total_count > 0 else 0

        # Prepare context for GPT
        prompt = self._build_difficulty_prompt(recent_responses, accuracy, current_difficulty, evaluation_context)

        try:
            if not self.client:
                # Fallback logic when AI is not available
                if accuracy >= 0.8:
                    return "hard" if current_difficulty != "hard" else "hard"
                elif accuracy <= 0.4:
                    return "easy" if current_difficulty != "easy" else "easy"
                else:
                    return "medium"

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational assessment expert. Analyze student performance and recommend appropriate difficulty levels.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=50,
            )

            # Parse response
            ai_response = response.choices[0].message.content.strip().lower()

            # Extract difficulty level from response
            if "easy" in ai_response:
                return "easy"
            elif "hard" in ai_response or "difficult" in ai_response:
                return "hard"
            else:
                return "medium"

        except Exception as e:
            current_app.logger.error(f"OpenAI API error: {str(e)}")
            # Fallback logic if AI fails
            return self._fallback_difficulty_logic(accuracy, current_difficulty)

    def _build_difficulty_prompt(
        self,
        recent_responses: List[Dict[str, Any]],
        accuracy: float,
        current_difficulty: str,
        evaluation_context: Dict[str, Any],
    ) -> str:
        """Build prompt for GPT to determine next difficulty."""
        # Format recent responses for the prompt
        response_summary = []
        for resp in recent_responses[-5:]:  # Last 5 responses
            response_summary.append(
                {
                    "question_type": resp.get("question_type"),
                    "difficulty": resp.get("difficulty"),
                    "correct": resp.get("is_correct"),
                    "time_spent": resp.get("time_spent_seconds"),
                }
            )

        prompt = f"""
        Student Performance Analysis:
        - Current accuracy: {accuracy * 100:.1f}%
        - Current difficulty: {current_difficulty}
        - Recent responses: {json.dumps(response_summary, indent=2)}
        - Evaluation subject: {evaluation_context.get('subject', 'General')}
        - Total questions answered: {len(recent_responses)}
        
        Based on this performance:
        1. If accuracy > 80% and current is not 'hard', increase difficulty
        2. If accuracy < 40% and current is not 'easy', decrease difficulty
        3. Consider response time - very quick correct answers suggest mastery
        4. Consider consecutive correct/incorrect patterns
        
        Recommend next difficulty level (easy/medium/hard) with brief reasoning.
        """

        return prompt

    def _fallback_difficulty_logic(self, accuracy: float, current_difficulty: str) -> str:
        """
        Fallback logic for difficulty determination if AI fails.

        Args:
            accuracy: Recent accuracy rate (0-1)
            current_difficulty: Current difficulty level

        Returns:
            Next difficulty level
        """
        difficulty_map = {"easy": 0, "medium": 1, "hard": 2}
        current_level = difficulty_map.get(current_difficulty, 1)

        # Simple rule-based logic
        if accuracy >= 0.8 and current_level < 2:
            # Increase difficulty
            next_level = current_level + 1
        elif accuracy <= 0.4 and current_level > 0:
            # Decrease difficulty
            next_level = current_level - 1
        else:
            # Maintain current difficulty
            next_level = current_level

        # Convert back to string
        for diff, level in difficulty_map.items():
            if level == next_level:
                return diff

        return "medium"  # Default

    def analyze_learning_patterns(self, all_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze learning patterns from all responses for insights.

        Args:
            all_responses: All question responses from the attempt

        Returns:
            Dictionary with learning insights
        """
        if not all_responses:
            return {"insights": [], "recommendations": []}

        # Group by topic/subject
        topic_performance = {}
        for resp in all_responses:
            topic = resp.get("topic", "General")
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}

            topic_performance[topic]["total"] += 1
            if resp.get("is_correct"):
                topic_performance[topic]["correct"] += 1

        # Calculate topic accuracies
        weak_topics = []
        strong_topics = []

        for topic, perf in topic_performance.items():
            accuracy = perf["correct"] / perf["total"] if perf["total"] > 0 else 0
            if accuracy < 0.5:
                weak_topics.append(topic)
            elif accuracy > 0.8:
                strong_topics.append(topic)

        return {
            "insights": {
                "total_questions": len(all_responses),
                "overall_accuracy": sum(1 for r in all_responses if r.get("is_correct")) / len(all_responses),
                "weak_topics": weak_topics,
                "strong_topics": strong_topics,
                "topic_performance": topic_performance,
            },
            "recommendations": self._generate_recommendations(weak_topics, strong_topics),
        }

    def generate_learning_insights(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive learning insights using GPT-4.

        Args:
            performance_data: Detailed performance data from evaluation attempt

        Returns:
            Dictionary with strengths, weaknesses, and recommendations
        """
        # Prepare performance summary
        summary = self._prepare_performance_summary(performance_data)

        # Build prompt for GPT-4
        prompt = self._build_insights_prompt(summary)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational psychologist and learning coach. 
                        Analyze student performance data and provide personalized learning insights.
                        Respond in JSON format with 'strengths', 'weaknesses', and 'recommendations' arrays.
                        Write in Turkish language.""",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )

            # Parse AI response
            ai_insights = json.loads(response.choices[0].message.content)

            # Validate and enhance response
            return self._validate_and_enhance_insights(ai_insights, performance_data)

        except Exception as e:
            current_app.logger.error(f"OpenAI API error in generate_learning_insights: {str(e)}")
            # Fallback to rule-based insights
            return self._generate_fallback_insights(performance_data)

    def _prepare_performance_summary(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a concise performance summary for AI analysis."""
        responses = performance_data.get("responses", [])

        # Calculate key metrics
        total_questions = len(responses)
        correct_count = sum(1 for r in responses if r.get("is_correct"))
        accuracy = correct_count / total_questions if total_questions > 0 else 0

        # Analyze by difficulty
        difficulty_performance = {"easy": [], "medium": [], "hard": []}
        for resp in responses:
            diff = resp.get("difficulty", "medium")
            difficulty_performance[diff].append(resp.get("is_correct", False))

        # Analyze by question type
        type_performance = {}
        for resp in responses:
            q_type = resp.get("question_type", "unknown")
            if q_type not in type_performance:
                type_performance[q_type] = {"correct": 0, "total": 0}
            type_performance[q_type]["total"] += 1
            if resp.get("is_correct"):
                type_performance[q_type]["correct"] += 1

        # Time analysis
        time_data = []
        for resp in responses:
            if resp.get("time_spent_seconds"):
                time_data.append(
                    {
                        "time": resp["time_spent_seconds"],
                        "correct": resp.get("is_correct", False),
                        "difficulty": resp.get("difficulty", "medium"),
                    }
                )

        return {
            "total_questions": total_questions,
            "correct_count": correct_count,
            "accuracy": accuracy,
            "difficulty_performance": {k: sum(v) / len(v) if v else 0 for k, v in difficulty_performance.items()},
            "type_performance": type_performance,
            "time_analysis": time_data,
            "topic_performance": performance_data.get("topic_performance", {}),
            "evaluation_info": performance_data.get("evaluation_info", {}),
        }

    def _build_insights_prompt(self, summary: Dict[str, Any]) -> str:
        """Build comprehensive prompt for GPT-4 insights generation."""
        prompt = f"""
        Öğrenci Değerlendirme Performans Analizi:
        
        Genel Bilgiler:
        - Toplam soru sayısı: {summary['total_questions']}
        - Doğru cevap sayısı: {summary['correct_count']}
        - Genel başarı oranı: {summary['accuracy'] * 100:.1f}%
        - Değerlendirme konusu: {summary['evaluation_info'].get('title', 'Genel')}
        
        Zorluk Seviyesine Göre Performans:
        - Kolay sorular: {summary['difficulty_performance'].get('easy', 0) * 100:.1f}% başarı
        - Orta sorular: {summary['difficulty_performance'].get('medium', 0) * 100:.1f}% başarı
        - Zor sorular: {summary['difficulty_performance'].get('hard', 0) * 100:.1f}% başarı
        
        Soru Tipine Göre Performans:
        {json.dumps(summary['type_performance'], indent=2, ensure_ascii=False)}
        
        Konu Bazlı Performans:
        {json.dumps(summary['topic_performance'], indent=2, ensure_ascii=False)}
        
        Zaman Analizi:
        - Ortalama cevaplama süresi: {self._calculate_avg_time(summary['time_analysis'])} saniye
        - Hızlı ve doğru cevaplar: {self._count_fast_correct(summary['time_analysis'])}
        - Yavaş ama yanlış cevaplar: {self._count_slow_incorrect(summary['time_analysis'])}
        
        Lütfen bu verileri analiz ederek öğrencinin:
        1. Güçlü yönlerini (strengths) - En az 3 madde
        2. Zayıf yönlerini (weaknesses) - En az 3 madde
        3. Gelişim önerilerini (recommendations) - En az 5 madde, spesifik ve uygulanabilir
        
        Yanıtı JSON formatında ver. Her madde Türkçe olmalı ve eğitici/motive edici bir dilde yazılmalı.
        """

        return prompt

    def _calculate_avg_time(self, time_data: List[Dict]) -> float:
        """Calculate average response time."""
        if not time_data:
            return 0
        times = [t["time"] for t in time_data if t.get("time")]
        return sum(times) / len(times) if times else 0

    def _count_fast_correct(self, time_data: List[Dict]) -> int:
        """Count fast and correct responses."""
        if not time_data:
            return 0
        avg_time = self._calculate_avg_time(time_data)
        return sum(1 for t in time_data if t.get("time", 0) < avg_time and t.get("correct", False))

    def _count_slow_incorrect(self, time_data: List[Dict]) -> int:
        """Count slow but incorrect responses."""
        if not time_data:
            return 0
        avg_time = self._calculate_avg_time(time_data)
        return sum(1 for t in time_data if t.get("time", 0) > avg_time and not t.get("correct", False))

    def _validate_and_enhance_insights(
        self, ai_insights: Dict[str, Any], performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and enhance AI-generated insights."""
        # Ensure all required fields exist
        validated = {
            "strengths": ai_insights.get("strengths", []),
            "weaknesses": ai_insights.get("weaknesses", []),
            "recommendations": ai_insights.get("recommendations", []),
        }

        # Add performance metrics
        validated["performance_metrics"] = {
            "overall_score": performance_data.get("score", 0),
            "accuracy_percentage": performance_data.get("accuracy", 0) * 100,
            "time_efficiency": self._calculate_time_efficiency(performance_data),
            "consistency_score": self._calculate_consistency_score(performance_data),
        }

        # Add visual indicators
        validated["visual_indicators"] = {
            "trend": self._determine_performance_trend(performance_data),
            "level": self._determine_mastery_level(performance_data.get("accuracy", 0)),
        }

        return validated

    def _calculate_time_efficiency(self, performance_data: Dict[str, Any]) -> float:
        """Calculate time efficiency score (0-100)."""
        responses = performance_data.get("responses", [])
        if not responses:
            return 50

        # Compare actual time vs expected time
        efficiency_scores = []
        for resp in responses:
            if resp.get("time_spent_seconds") and resp.get("expected_time_seconds"):
                efficiency = min(100, (resp["expected_time_seconds"] / resp["time_spent_seconds"]) * 100)
                efficiency_scores.append(efficiency)

        return sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 50

    def _calculate_consistency_score(self, performance_data: Dict[str, Any]) -> float:
        """Calculate consistency in performance (0-100)."""
        responses = performance_data.get("responses", [])
        if len(responses) < 3:
            return 50

        # Calculate variance in performance over time
        window_size = 3
        accuracies = []

        for i in range(0, len(responses) - window_size + 1):
            window = responses[i : i + window_size]
            window_accuracy = sum(1 for r in window if r.get("is_correct")) / window_size
            accuracies.append(window_accuracy)

        if not accuracies:
            return 50

        # Lower variance means higher consistency
        variance = sum((a - sum(accuracies) / len(accuracies)) ** 2 for a in accuracies) / len(accuracies)
        consistency = max(0, min(100, (1 - variance) * 100))

        return consistency

    def _determine_performance_trend(self, performance_data: Dict[str, Any]) -> str:
        """Determine if performance is improving, declining, or stable."""
        responses = performance_data.get("responses", [])
        if len(responses) < 5:
            return "stable"

        # Compare first half vs second half performance
        mid = len(responses) // 2
        first_half = responses[:mid]
        second_half = responses[mid:]

        first_accuracy = sum(1 for r in first_half if r.get("is_correct")) / len(first_half)
        second_accuracy = sum(1 for r in second_half if r.get("is_correct")) / len(second_half)

        if second_accuracy > first_accuracy + 0.1:
            return "improving"
        elif second_accuracy < first_accuracy - 0.1:
            return "declining"
        else:
            return "stable"

    def _determine_mastery_level(self, accuracy: float) -> str:
        """Determine mastery level based on accuracy."""
        if accuracy >= 0.9:
            return "expert"
        elif accuracy >= 0.8:
            return "proficient"
        elif accuracy >= 0.7:
            return "developing"
        elif accuracy >= 0.6:
            return "novice"
        else:
            return "beginner"

    def _generate_fallback_insights(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule-based insights as fallback when AI fails."""
        summary = self._prepare_performance_summary(performance_data)

        strengths = []
        weaknesses = []
        recommendations = []

        # Analyze strengths
        if summary["accuracy"] > 0.8:
            strengths.append("Genel başarı oranınız oldukça yüksek")

        if summary["difficulty_performance"].get("hard", 0) > 0.7:
            strengths.append("Zor sorularda güçlü performans gösteriyorsunuz")

        for q_type, perf in summary["type_performance"].items():
            if perf["total"] > 0 and perf["correct"] / perf["total"] > 0.8:
                strengths.append(f"{q_type} tipindeki sorularda başarılısınız")

        # Analyze weaknesses
        if summary["accuracy"] < 0.6:
            weaknesses.append("Genel başarı oranı geliştirilmeli")

        if summary["difficulty_performance"].get("easy", 1) < 0.8:
            weaknesses.append("Temel konularda eksiklikler var")

        for topic, perf in summary["topic_performance"].items():
            if perf["total"] > 0 and perf["correct"] / perf["total"] < 0.5:
                weaknesses.append(f"{topic} konusunda güçlendirme gerekli")

        # Generate recommendations
        if summary["accuracy"] < 0.7:
            recommendations.append("Temel konuları tekrar gözden geçirin")

        if summary["difficulty_performance"].get("easy", 1) < 0.9:
            recommendations.append("Önce kolay seviye sorularla pratik yapın")

        recommendations.extend(
            [
                "Yanlış cevapladığınız soruların çözümlerini inceleyin",
                "Günlük düzenli çalışma rutini oluşturun",
                "Zayıf olduğunuz konularda ek kaynaklardan yararlanın",
                "Benzer soruları farklı kaynaklardan çözerek pratik yapın",
                "Öğrenme hedefinizi belirleyin ve ilerlemenizi takip edin",
            ]
        )

        return {
            "strengths": strengths[:3] if strengths else ["Çalışmaya devam ederek gelişim gösterebilirsiniz"],
            "weaknesses": weaknesses[:3] if weaknesses else ["Daha fazla pratik yaparak gelişebilirsiniz"],
            "recommendations": recommendations[:5],
            "performance_metrics": {
                "overall_score": performance_data.get("score", 0),
                "accuracy_percentage": summary["accuracy"] * 100,
                "time_efficiency": 50,
                "consistency_score": 50,
            },
            "visual_indicators": {"trend": "stable", "level": self._determine_mastery_level(summary["accuracy"])},
        }

    def _generate_recommendations(self, weak_topics: List[str], strong_topics: List[str]) -> List[str]:
        """Generate personalized recommendations based on performance."""
        recommendations = []

        if weak_topics:
            recommendations.append(f"Focus on improving in: {', '.join(weak_topics[:3])}")

        if strong_topics:
            recommendations.append(f"Great performance in: {', '.join(strong_topics[:3])}")

        return recommendations

    def generate_learning_path(
        self, learning_insights: Dict[str, Any], user_info: Dict[str, Any], evaluation_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a personalized learning path based on AI insights.

        Args:
            learning_insights: AI-generated insights from evaluation
            user_info: User profile and preferences
            evaluation_info: Evaluation context and details

        Returns:
            Dictionary with learning path structure
        """
        # Build comprehensive prompt
        prompt = self._build_learning_path_prompt(learning_insights, user_info, evaluation_info)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational curriculum designer and learning coach. 
                        Create personalized learning paths based on student performance analysis.
                        Respond in JSON format with detailed learning milestones and weekly schedules.
                        Write all content in Turkish language.
                        Focus on practical, achievable goals with specific resources.""",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            # Parse AI response
            learning_path = json.loads(response.choices[0].message.content)

            # Validate and enhance the learning path
            return self._validate_and_enhance_learning_path(learning_path, learning_insights)

        except Exception as e:
            current_app.logger.error(f"OpenAI API error in generate_learning_path: {str(e)}")
            # Fallback to template-based learning path
            return self._generate_fallback_learning_path(learning_insights, evaluation_info)

    def _build_learning_path_prompt(
        self, learning_insights: Dict[str, Any], user_info: Dict[str, Any], evaluation_info: Dict[str, Any]
    ) -> str:
        """Build comprehensive prompt for learning path generation."""
        prompt = f"""
        Öğrenci Performans Analizi ve Öğrenme Planı Oluşturma:
        
        Değerlendirme Bilgileri:
        - Konu: {evaluation_info.get('title', 'Genel')}
        - Toplam Skor: {learning_insights.get('attempt_summary', {}).get('percentage', '0%')}
        - Geçme Durumu: {'Geçti' if learning_insights.get('attempt_summary', {}).get('passed', False) else 'Kaldı'}
        
        Güçlü Yönler:
        {json.dumps(learning_insights.get('strengths', []), indent=2, ensure_ascii=False)}
        
        Gelişim Alanları:
        {json.dumps(learning_insights.get('weaknesses', []), indent=2, ensure_ascii=False)}
        
        AI Önerileri:
        {json.dumps(learning_insights.get('recommendations', []), indent=2, ensure_ascii=False)}
        
        Performans Metrikleri:
        - Doğruluk: {learning_insights.get('performance_metrics', {}).get('accuracy_percentage', 0):.1f}%
        - Zaman Verimliliği: {learning_insights.get('performance_metrics', {}).get('time_efficiency', 0):.0f}%
        - Tutarlılık: {learning_insights.get('performance_metrics', {}).get('consistency_score', 0):.0f}%
        - Seviye: {learning_insights.get('visual_indicators', {}).get('level', 'beginner')}
        
        Kullanıcı Bilgileri:
        - Öğrenme Stili Tercihi: {user_info.get('learning_style', 'mixed')}
        - Haftalık Çalışma Süresi: {user_info.get('weekly_hours', '5-10')} saat
        - Deneyim Seviyesi: {user_info.get('experience_level', 'intermediate')}
        
        Lütfen bu bilgilere dayanarak 4 haftalık kişiselleştirilmiş bir öğrenme planı oluştur.
        
        JSON formatında şu yapıyı kullan:
        {{
            "title": "Kişiselleştirilmiş öğrenme planı başlığı",
            "description": "Plan açıklaması",
            "objective": "Ana öğrenme hedefi",
            "duration_weeks": 4,
            "estimated_hours_per_week": 5-10 arası uygun saat,
            "learning_style": "visual/auditory/kinesthetic/reading/mixed",
            "difficulty_adjustment": "easy/balanced/challenging",
            "prerequisites": ["Ön koşul 1", "Ön koşul 2"],
            "milestones": [
                {{
                    "week_number": 1,
                    "title": "Milestone başlığı",
                    "description": "Detaylı açıklama",
                    "objective": "Bu haftanın hedefi",
                    "estimated_hours": 2.5,
                    "skill_focus": "Odaklanılan beceri",
                    "resources": [
                        {{
                            "type": "video/article/exercise/book",
                            "title": "Kaynak başlığı",
                            "url": "https://example.com",
                            "duration": "30 dakika",
                            "description": "Kaynak açıklaması"
                        }}
                    ],
                    "activities": [
                        {{
                            "title": "Aktivite başlığı",
                            "description": "Ne yapılacak",
                            "duration": "45 dakika",
                            "type": "practice/study/project"
                        }}
                    ],
                    "assessment_criteria": ["Kriter 1", "Kriter 2"]
                }}
            ],
            "weekly_schedule": {{
                "week_1": {{
                    "monday": {{"activities": ["Aktivite 1"], "duration": "1 saat"}},
                    "wednesday": {{"activities": ["Aktivite 2"], "duration": "1.5 saat"}},
                    "friday": {{"activities": ["Aktivite 3"], "duration": "2 saat"}}
                }}
            }},
            "resources": [
                {{
                    "category": "Temel Kaynaklar",
                    "items": [
                        {{
                            "title": "Kaynak başlığı",
                            "type": "course/book/video_series",
                            "provider": "Platform adı",
                            "url": "https://example.com",
                            "cost": "free/paid",
                            "estimated_time": "10 saat"
                        }}
                    ]
                }}
            ],
            "success_metrics": [
                "Başarı kriteri 1",
                "Başarı kriteri 2"
            ]
        }}
        
        Plan oluştururken:
        1. Zayıf alanlara odaklan ama güçlü yönleri de geliştir
        2. Gerçekçi ve uygulanabilir hedefler koy
        3. Çeşitli öğrenme materyalleri öner
        4. Progressive (aşamalı) zorluk artışı sağla
        5. Her hafta için net hedefler belirle
        """

        return prompt

    def _validate_and_enhance_learning_path(
        self, learning_path: Dict[str, Any], learning_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and enhance AI-generated learning path."""
        # Ensure all required fields exist
        validated = {
            "title": learning_path.get("title", "Kişiselleştirilmiş Öğrenme Planı"),
            "description": learning_path.get("description", ""),
            "objective": learning_path.get("objective", ""),
            "duration_weeks": learning_path.get("duration_weeks", 4),
            "estimated_hours_per_week": learning_path.get("estimated_hours_per_week", 5),
            "learning_style": learning_path.get("learning_style", "mixed"),
            "difficulty_adjustment": learning_path.get("difficulty_adjustment", "balanced"),
            "prerequisites": learning_path.get("prerequisites", []),
            "milestones": learning_path.get("milestones", []),
            "weekly_schedule": learning_path.get("weekly_schedule", {}),
            "resources": learning_path.get("resources", []),
            "success_metrics": learning_path.get("success_metrics", []),
        }

        # Add insights summary
        validated["ai_insights_summary"] = {
            "strengths_addressed": len(learning_insights.get("strengths", [])),
            "weaknesses_targeted": len(learning_insights.get("weaknesses", [])),
            "performance_level": learning_insights.get("visual_indicators", {}).get("level", "beginner"),
            "recommendations_incorporated": len(learning_insights.get("recommendations", [])),
        }

        # Ensure milestones are properly structured
        for i, milestone in enumerate(validated["milestones"]):
            milestone["order_index"] = i
            milestone["status"] = "pending"
            milestone["progress"] = 0.0

            # Ensure resources and activities exist
            if "resources" not in milestone:
                milestone["resources"] = []
            if "activities" not in milestone:
                milestone["activities"] = []
            if "assessment_criteria" not in milestone:
                milestone["assessment_criteria"] = []

        # Calculate total milestones
        validated["total_milestones"] = len(validated["milestones"])

        return validated

    def _generate_fallback_learning_path(
        self, learning_insights: Dict[str, Any], evaluation_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a template-based learning path as fallback."""
        performance_level = learning_insights.get("visual_indicators", {}).get("level", "beginner")
        accuracy = learning_insights.get("performance_metrics", {}).get("accuracy_percentage", 0)

        # Determine focus areas based on performance
        if accuracy < 60:
            focus = "temel kavramları güçlendirme"
            difficulty = "easy"
            hours_per_week = 7
        elif accuracy < 80:
            focus = "orta seviye becerileri geliştirme"
            difficulty = "balanced"
            hours_per_week = 5
        else:
            focus = "ileri seviye uzmanlık kazanma"
            difficulty = "challenging"
            hours_per_week = 4

        # Create basic milestones
        milestones = []
        milestone_templates = [
            {"title": "Temel Kavramları Gözden Geçirme", "skill_focus": "Temel bilgi", "week": 1},
            {"title": "Pratik Uygulamalar", "skill_focus": "Uygulama becerisi", "week": 2},
            {"title": "İleri Seviye Konular", "skill_focus": "Derinlemesine anlayış", "week": 3},
            {"title": "Proje ve Değerlendirme", "skill_focus": "Sentez ve değerlendirme", "week": 4},
        ]

        for i, template in enumerate(milestone_templates):
            milestone = {
                "week_number": template["week"],
                "title": template["title"],
                "description": f"{template['week']}. hafta için {focus} odaklı çalışma planı",
                "objective": f"{template['skill_focus']} seviyesini artırmak",
                "estimated_hours": hours_per_week / 2,
                "skill_focus": template["skill_focus"],
                "order_index": i,
                "resources": [
                    {
                        "type": "article",
                        "title": f"{template['title']} - Okuma Materyali",
                        "url": "https://example.com/resource",
                        "duration": "30 dakika",
                        "description": "Temel okuma materyali",
                    }
                ],
                "activities": [
                    {
                        "title": f"{template['title']} - Pratik",
                        "description": "Öğrenilenleri pekiştirmek için pratik çalışma",
                        "duration": "1 saat",
                        "type": "practice",
                    }
                ],
                "assessment_criteria": [
                    f"{template['skill_focus']} konusunda yeterlilik",
                    "Verilen aktiviteleri tamamlama",
                ],
            }
            milestones.append(milestone)

        # Create weekly schedule
        weekly_schedule = {}
        for week in range(1, 5):
            weekly_schedule[f"week_{week}"] = {
                "monday": {"activities": ["Teori çalışması"], "duration": f"{hours_per_week / 3:.1f} saat"},
                "wednesday": {"activities": ["Pratik uygulama"], "duration": f"{hours_per_week / 3:.1f} saat"},
                "friday": {"activities": ["Tekrar ve değerlendirme"], "duration": f"{hours_per_week / 3:.1f} saat"},
            }

        return {
            "title": f"{evaluation_info.get('title', 'Konu')} - Kişiselleştirilmiş Öğrenme Planı",
            "description": f"Performansınıza göre hazırlanmış {4} haftalık öğrenme planı",
            "objective": f"Mevcut {accuracy:.0f}% başarı oranını geliştirmek ve {focus}",
            "duration_weeks": 4,
            "estimated_hours_per_week": hours_per_week,
            "learning_style": "mixed",
            "difficulty_adjustment": difficulty,
            "prerequisites": learning_insights.get("weaknesses", [])[:2],
            "milestones": milestones,
            "weekly_schedule": weekly_schedule,
            "resources": [
                {
                    "category": "Temel Kaynaklar",
                    "items": [
                        {
                            "title": "Online Kurs Önerisi",
                            "type": "course",
                            "provider": "Platform",
                            "url": "https://example.com",
                            "cost": "free",
                            "estimated_time": "10 saat",
                        }
                    ],
                }
            ],
            "success_metrics": [
                "Tüm haftalık aktiviteleri tamamlama",
                "Her milestone için belirlenen kriterleri karşılama",
                f"Başarı oranını {min(accuracy + 20, 100):.0f}% seviyesine çıkarma",
            ],
            "ai_insights_summary": {
                "strengths_addressed": len(learning_insights.get("strengths", [])),
                "weaknesses_targeted": len(learning_insights.get("weaknesses", [])),
                "performance_level": performance_level,
                "recommendations_incorporated": len(learning_insights.get("recommendations", [])),
            },
            "total_milestones": 4,
        }

    def generate_development_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive development report using GPT-4.

        Args:
            report_data: Combined data from evaluations, learning paths, and user info

        Returns:
            Development report in structured JSON format
        """
        # Build comprehensive prompt
        prompt = self._build_development_report_prompt(report_data)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational psychologist and learning analytics specialist. 
                        Generate comprehensive development reports that provide actionable insights.
                        Respond ONLY in JSON format with Turkish content.
                        Focus on constructive feedback and practical recommendations.""",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            # Parse AI response
            report = json.loads(response.choices[0].message.content)

            # Validate and enhance report
            return self._validate_and_enhance_report(report, report_data)

        except Exception as e:
            current_app.logger.error(f"OpenAI API error in generate_development_report: {str(e)}")
            # Fallback to template-based report
            return self._generate_fallback_report(report_data)

    def _build_development_report_prompt(self, report_data: Dict[str, Any]) -> str:
        """Build comprehensive prompt for development report generation."""
        user_info = report_data["user_info"]
        eval_data = report_data["evaluation_results"]
        path_data = report_data["learning_paths"]
        metrics = report_data["performance_metrics"]

        # Extract insights
        strengths = []
        weaknesses = []
        for insight in eval_data.get("insights", []):
            strengths.extend(insight["insights"].get("strengths", []))
            weaknesses.extend(insight["insights"].get("weaknesses", []))

        prompt = f"""
        Öğrenci Gelişim Raporu Oluşturma
        
        Öğrenci Bilgileri:
        - Ad Soyad: {user_info['name']}
        - Öğrenme Stili: {user_info.get('learning_style', 'mixed')}
        - Rapor Dönemi: Son {report_data['date_range']['days']} gün
        
        Değerlendirme Sonuçları:
        - Toplam Deneme: {eval_data['total_attempts']}
        - Başarılı Deneme: {eval_data['passed_attempts']}
        - Ortalama Puan: {eval_data['average_score']:.1f}%
        - Performans Trendi: {json.dumps(eval_data['performance_trend'][-5:], ensure_ascii=False)}
        
        Öğrenme Yolu İlerlemesi:
        - Toplam Plan: {path_data['total_paths']}
        - Aktif Plan: {path_data['active_paths']}
        - Tamamlanan Plan: {path_data['completed_paths']}
        - Ortalama İlerleme: {path_data['average_progress']:.1f}%
        - Milestone Tamamlama: {path_data['milestone_completion_rate']:.1f}%
        
        Performans Metrikleri:
        - Tamamlama Oranı: {metrics['completion_rate']:.1f}%
        - Performans İndeksi: {metrics['performance_index']:.1f}
        - Katılım Puanı: {metrics['engagement_score']:.1f}
        - Tutarlılık Puanı: {metrics['consistency_score']:.1f}
        - Risk Göstergeleri: {json.dumps(metrics['risk_indicators'], ensure_ascii=False)}
        
        AI Tespit Edilen Güçlü Yönler:
        {json.dumps(list(set(strengths[:5])), indent=2, ensure_ascii=False)}
        
        AI Tespit Edilen Gelişim Alanları:
        {json.dumps(list(set(weaknesses[:5])), indent=2, ensure_ascii=False)}
        
        Öğrenci Geri Bildirimleri:
        {json.dumps(path_data.get('feedback_notes', [])[:3], indent=2, ensure_ascii=False)}
        
        Öğrenme Yolu Detayları:
        {json.dumps(path_data.get('paths', [])[:2], indent=2, ensure_ascii=False)}
        
        Lütfen aşağıdaki JSON formatında kapsamlı bir gelişim raporu oluştur:
        {{
            "student_name": "{user_info['name']}",
            "progress_summary": "Öğrencinin genel durumu ve gelişimi hakkında 2-3 cümlelik özet",
            "ai_analysis": {{
                "learning_style": "Tespit edilen veya önerilen öğrenme stili ve açıklama",
                "strengths": [
                    "Güçlü yön 1 - Detaylı açıklama",
                    "Güçlü yön 2 - Detaylı açıklama",
                    "Güçlü yön 3 - Detaylı açıklama"
                ],
                "weaknesses": [
                    "Gelişim alanı 1 - Detaylı açıklama",
                    "Gelişim alanı 2 - Detaylı açıklama",
                    "Gelişim alanı 3 - Detaylı açıklama"
                ],
                "performance_risks": [
                    "Risk 1 - Açıklama ve olası sonuçlar",
                    "Risk 2 - Açıklama ve olası sonuçlar"
                ]
            }},
            "suggested_interventions": [
                {{
                    "priority": "high/medium/low",
                    "intervention": "Müdahale önerisi",
                    "expected_outcome": "Beklenen sonuç",
                    "timeline": "Önerilen süre"
                }}
            ],
            "summary_score": {{
                "completion_rate": "{metrics['completion_rate']:.0f}%",
                "performance_index": {metrics['performance_index']:.0f},
                "risk_score": "Low/Medium/High",
                "overall_assessment": "Genel değerlendirme (1-2 cümle)"
            }},
            "recommendations": {{
                "immediate_actions": [
                    "Hemen yapılması gereken eylem 1",
                    "Hemen yapılması gereken eylem 2"
                ],
                "long_term_goals": [
                    "Uzun vadeli hedef 1",
                    "Uzun vadeli hedef 2"
                ],
                "support_needed": [
                    "Gerekli destek 1",
                    "Gerekli destek 2"
                ]
            }},
            "next_evaluation_focus": [
                "Bir sonraki değerlendirmede odaklanılacak konu 1",
                "Bir sonraki değerlendirmede odaklanılacak konu 2"
            ]
        }}
        
        Raporu oluştururken:
        1. Yapıcı ve motive edici bir dil kullan
        2. Somut ve uygulanabilir öneriler sun
        3. Verilere dayalı objektif değerlendirmeler yap
        4. Öğrencinin potansiyelini vurgula
        5. Kısa ve orta vadeli hedefler belirle
        """

        return prompt

    def _validate_and_enhance_report(self, report: Dict[str, Any], report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance AI-generated report."""
        # Ensure all required fields exist
        validated = {
            "student_name": report.get("student_name", report_data["user_info"]["name"]),
            "progress_summary": report.get("progress_summary", ""),
            "ai_analysis": report.get("ai_analysis", {}),
            "suggested_interventions": report.get("suggested_interventions", []),
            "summary_score": report.get("summary_score", {}),
            "recommendations": report.get("recommendations", {}),
            "next_evaluation_focus": report.get("next_evaluation_focus", []),
        }

        # Ensure ai_analysis has all required fields
        if "ai_analysis" not in validated or not validated["ai_analysis"]:
            validated["ai_analysis"] = {}

        validated["ai_analysis"].setdefault("learning_style", report_data["user_info"].get("learning_style", "mixed"))
        validated["ai_analysis"].setdefault("strengths", [])
        validated["ai_analysis"].setdefault("weaknesses", [])
        validated["ai_analysis"].setdefault("performance_risks", [])

        # Ensure summary_score has all fields
        if "summary_score" not in validated or not validated["summary_score"]:
            validated["summary_score"] = {}

        metrics = report_data["performance_metrics"]
        validated["summary_score"].setdefault("completion_rate", f"{metrics['completion_rate']:.0f}%")
        validated["summary_score"].setdefault("performance_index", round(metrics["performance_index"]))

        # Determine risk score
        risk_count = len(metrics.get("risk_indicators", []))
        if risk_count == 0:
            risk_score = "Low"
        elif risk_count <= 2:
            risk_score = "Medium"
        else:
            risk_score = "High"

        validated["summary_score"].setdefault("risk_score", risk_score)
        validated["summary_score"].setdefault("overall_assessment", "")

        # Add data visualization hints
        validated["visualization_data"] = {
            "performance_trend": report_data["evaluation_results"].get("performance_trend", []),
            "milestone_progress": [
                {"path": path["title"], "progress": path["progress"]}
                for path in report_data["learning_paths"].get("paths", [])
            ],
            "skill_distribution": self._calculate_skill_distribution(report_data),
        }

        return validated

    def _calculate_skill_distribution(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate skill distribution from learning paths."""
        skill_counts = {}

        for path in report_data["learning_paths"].get("paths", []):
            for milestone in path.get("milestones", []):
                skill = milestone.get("skill_focus", "Genel")
                if skill not in skill_counts:
                    skill_counts[skill] = {"count": 0, "total_progress": 0}

                skill_counts[skill]["count"] += 1
                skill_counts[skill]["total_progress"] += milestone.get("progress", 0)

        # Convert to list format
        distribution = []
        for skill, data in skill_counts.items():
            avg_progress = data["total_progress"] / data["count"] if data["count"] > 0 else 0
            distribution.append(
                {"skill": skill, "focus_count": data["count"], "average_progress": round(avg_progress, 1)}
            )

        return sorted(distribution, key=lambda x: x["focus_count"], reverse=True)

    def _generate_fallback_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a template-based report as fallback."""
        user_info = report_data["user_info"]
        eval_data = report_data["evaluation_results"]
        path_data = report_data["learning_paths"]
        metrics = report_data["performance_metrics"]

        # Determine risk score
        risk_count = len(metrics.get("risk_indicators", []))
        if risk_count == 0:
            risk_score = "Low"
            risk_desc = "Düşük risk"
        elif risk_count <= 2:
            risk_score = "Medium"
            risk_desc = "Orta düzeyde risk"
        else:
            risk_score = "High"
            risk_desc = "Yüksek risk"

        # Generate summary based on performance
        perf_index = metrics["performance_index"]
        if perf_index >= 80:
            summary = f"{user_info['name']} son dönemde çok başarılı bir performans göstermiştir. Öğrenme hedeflerinde tutarlı ilerleme kaydedilmektedir."
        elif perf_index >= 60:
            summary = f"{user_info['name']} genel olarak iyi bir performans sergilemektedir. Bazı alanlarda gelişim fırsatları bulunmaktadır."
        else:
            summary = f"{user_info['name']} için özel destek ve yönlendirme gerekebilir. Öğrenme stratejilerinin gözden geçirilmesi önerilir."

        # Build report
        report = {
            "student_name": user_info["name"],
            "progress_summary": summary,
            "ai_analysis": {
                "learning_style": f"{user_info.get('learning_style', 'mixed')} öğrenme stiline sahip",
                "strengths": [],
                "weaknesses": [],
                "performance_risks": [],
            },
            "suggested_interventions": [],
            "summary_score": {
                "completion_rate": f"{metrics['completion_rate']:.0f}%",
                "performance_index": round(metrics["performance_index"]),
                "risk_score": risk_score,
                "overall_assessment": f"Öğrenci {risk_desc} grubunda değerlendirilmektedir.",
            },
            "recommendations": {"immediate_actions": [], "long_term_goals": [], "support_needed": []},
            "next_evaluation_focus": [],
        }

        # Add strengths
        if eval_data["average_score"] >= 80:
            report["ai_analysis"]["strengths"].append("Değerlendirmelerde yüksek başarı gösteriyor")
        if path_data["milestone_completion_rate"] >= 70:
            report["ai_analysis"]["strengths"].append("Öğrenme hedeflerini düzenli tamamlıyor")
        if metrics["consistency_score"] >= 80:
            report["ai_analysis"]["strengths"].append("Tutarlı performans sergiliyor")

        # Add weaknesses
        if eval_data["average_score"] < 60:
            report["ai_analysis"]["weaknesses"].append("Değerlendirme puanları geliştirilmeli")
        if path_data["average_progress"] < 50:
            report["ai_analysis"]["weaknesses"].append("Öğrenme planı ilerlemesi yavaş")
        if metrics["engagement_score"] < 50:
            report["ai_analysis"]["weaknesses"].append("Katılım düzeyi artırılmalı")

        # Add risks
        report["ai_analysis"]["performance_risks"] = [
            f"{risk} - Yakından takip edilmeli" for risk in metrics.get("risk_indicators", [])
        ]

        # Add interventions
        if eval_data["average_score"] < 60:
            report["suggested_interventions"].append(
                {
                    "priority": "high",
                    "intervention": "Bireysel destek seansları düzenlenmeli",
                    "expected_outcome": "Değerlendirme puanlarında artış",
                    "timeline": "2 hafta içinde başlanmalı",
                }
            )

        if path_data["average_progress"] < 50 and path_data["active_paths"] > 0:
            report["suggested_interventions"].append(
                {
                    "priority": "medium",
                    "intervention": "Öğrenme planı gözden geçirilmeli",
                    "expected_outcome": "İlerleme hızında artış",
                    "timeline": "1 hafta içinde",
                }
            )

        # Add recommendations
        report["recommendations"]["immediate_actions"] = [
            "Zayıf konularda ek pratik yapılmalı",
            "Öğrenme planındaki aktivitelere düzenli katılım sağlanmalı",
        ]

        report["recommendations"]["long_term_goals"] = [
            "Tüm değerlendirmelerde %80 üzeri başarı hedeflenmeli",
            "Öğrenme planlarını zamanında tamamlama alışkanlığı edinilmeli",
        ]

        report["recommendations"]["support_needed"] = ["Haftalık ilerleme takibi", "Motivasyon desteği"]

        # Add next evaluation focus
        report["next_evaluation_focus"] = ["Zayıf performans gösterilen konular", "Yeni öğrenilen beceriler"]

        # Add visualization data
        report["visualization_data"] = {
            "performance_trend": eval_data.get("performance_trend", []),
            "milestone_progress": [
                {"path": path["title"], "progress": path["progress"]} for path in path_data.get("paths", [])
            ],
            "skill_distribution": self._calculate_skill_distribution(report_data),
        }

        return report

    def generate_student_profile_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered analysis for student profile.

        Args:
            profile_data: Student performance and activity data

        Returns:
            AI analysis with strengths, weaknesses, and recommendations
        """
        # Build prompt for profile analysis
        prompt = self._build_profile_analysis_prompt(profile_data)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational psychologist specializing in student development analysis. 
                        Analyze student data to identify patterns, strengths, weaknesses, and provide actionable recommendations.
                        Respond in JSON format with Turkish content.
                        Focus on constructive, motivating insights that help both the student and coach.""",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )

            # Parse AI response
            analysis = json.loads(response.choices[0].message.content)

            # Validate and enhance analysis
            return self._validate_profile_analysis(analysis, profile_data)

        except Exception as e:
            current_app.logger.error(f"OpenAI API error in generate_student_profile_analysis: {str(e)}")
            # Return fallback analysis
            return self._generate_fallback_profile_analysis(profile_data)

    def _build_profile_analysis_prompt(self, profile_data: Dict[str, Any]) -> str:
        """Build prompt for student profile analysis."""
        scores = profile_data.get("scores", {})
        evaluations = profile_data.get("recent_evaluations", [])
        response_patterns = profile_data.get("response_patterns", {})
        learning_progress = profile_data.get("learning_progress", [])

        prompt = f"""
        Öğrenci Profil Analizi
        
        Performans Skorları:
        - Performans İndeksi: {scores.get('performance_index', 0)}
        - Katılım Skoru: {scores.get('engagement_score', 0)}
        - Tamamlama Oranı: {scores.get('completion_rate', 0)}%
        - Ortalama Puan: {scores.get('average_score', 0)}
        - Risk Seviyesi: {scores.get('risk_score', 'Unknown')}
        - Risk Faktörleri: {', '.join(scores.get('risk_factors', []))}
        
        Son Değerlendirmeler:
        {json.dumps(evaluations[:5], indent=2, ensure_ascii=False)}
        
        Cevap Analizi:
        - Toplam Soru: {response_patterns.get('total_responses', 0)}
        - Doğru Oranı: {response_patterns.get('correct_rate', 0):.1f}%
        - Ortalama Süre: {response_patterns.get('avg_time_per_question', 0):.0f} saniye
        - Zorluk Performansı: {json.dumps(response_patterns.get('difficulty_performance', {}), ensure_ascii=False)}
        
        Öğrenme İlerlemesi:
        - Aktif Öğrenme Yolları: {scores.get('active_learning_paths', 0)}
        - Tamamlanan Yollar: {scores.get('completed_learning_paths', 0)}
        - Son Oturumlar: {len(learning_progress)}
        
        Lütfen bu verileri analiz ederek aşağıdaki JSON formatında kapsamlı bir analiz oluştur:
        {{
            "strengths": [
                "Güçlü yön 1 - Detaylı açıklama ve veri desteği",
                "Güçlü yön 2 - Detaylı açıklama ve veri desteği",
                "Güçlü yön 3 - Detaylı açıklama ve veri desteği"
            ],
            "weaknesses": [
                "Gelişim alanı 1 - Detaylı açıklama ve öneriler",
                "Gelişim alanı 2 - Detaylı açıklama ve öneriler",
                "Gelişim alanı 3 - Detaylı açıklama ve öneriler"
            ],
            "learning_pattern": "Öğrencinin öğrenme stili ve davranış kalıpları hakkında detaylı analiz",
            "motivation_level": "Yüksek/Orta/Düşük - Açıklama ile birlikte",
            "recommendations": [
                "Spesifik ve uygulanabilir öneri 1",
                "Spesifik ve uygulanabilir öneri 2",
                "Spesifik ve uygulanabilir öneri 3"
            ],
            "intervention_suggestions": [
                {{
                    "type": "immediate/short_term/long_term",
                    "action": "Yapılması gereken müdahale",
                    "expected_impact": "Beklenen etki"
                }}
            ],
            "predicted_trajectory": "Mevcut performans devam ederse 3 ay sonraki tahmini durum",
            "personalized_learning_tips": [
                "Öğrenciye özel öğrenme tavsiyesi 1",
                "Öğrenciye özel öğrenme tavsiyesi 2"
            ]
        }}
        
        Analiz yaparken:
        1. Verilere dayalı, objektif değerlendirmeler yap
        2. Hem güçlü yönleri hem de gelişim alanlarını dengeli sun
        3. Yapıcı ve motive edici bir dil kullan
        4. Koç için uygulanabilir müdahale önerileri sun
        5. Öğrencinin potansiyelini vurgula
        """

        return prompt

    def _validate_profile_analysis(self, analysis: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance AI-generated profile analysis."""
        # Ensure all required fields exist
        validated = {
            "strengths": analysis.get("strengths", [])[:3],
            "weaknesses": analysis.get("weaknesses", [])[:3],
            "learning_pattern": analysis.get("learning_pattern", ""),
            "motivation_level": analysis.get("motivation_level", "Orta"),
            "recommendations": analysis.get("recommendations", [])[:3],
            "intervention_suggestions": analysis.get("intervention_suggestions", []),
            "predicted_trajectory": analysis.get("predicted_trajectory", ""),
            "personalized_learning_tips": analysis.get("personalized_learning_tips", []),
        }

        # Add data-driven insights
        scores = profile_data.get("scores", {})
        validated["key_metrics"] = {
            "performance_trend": self._determine_trend(profile_data.get("recent_evaluations", [])),
            "engagement_status": "Aktif" if scores.get("engagement_score", 0) >= 60 else "Düşük",
            "risk_level": scores.get("risk_score", "Unknown"),
        }

        return validated

    def _determine_trend(self, evaluations: List[Dict[str, Any]]) -> str:
        """Determine performance trend from recent evaluations."""
        if len(evaluations) < 2:
            return "Yetersiz veri"

        # Compare recent vs older scores
        recent_avg = sum(e["score"] for e in evaluations[:2]) / 2
        older_avg = sum(e["score"] for e in evaluations[2:4]) / 2 if len(evaluations) >= 4 else evaluations[-1]["score"]

        if recent_avg > older_avg + 5:
            return "Yükseliş"
        elif recent_avg < older_avg - 5:
            return "Düşüş"
        else:
            return "Stabil"

    def _generate_fallback_profile_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback profile analysis when AI is not available."""
        scores = profile_data.get("scores", {})

        analysis = {
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "learning_pattern": "Standart öğrenme modeli",
            "motivation_level": "Orta",
            "intervention_suggestions": [],
            "predicted_trajectory": "Mevcut performans devam ederse stabil ilerleme bekleniyor",
            "personalized_learning_tips": [],
        }

        # Determine strengths
        if scores.get("average_score", 0) >= 80:
            analysis["strengths"].append("Değerlendirmelerde tutarlı yüksek başarı")
        if scores.get("engagement_score", 0) >= 70:
            analysis["strengths"].append("Yüksek katılım ve öğrenme motivasyonu")
        if scores.get("completion_rate", 0) >= 80:
            analysis["strengths"].append("Öğrenme hedeflerini düzenli tamamlama")

        # Determine weaknesses
        if scores.get("average_score", 0) < 60:
            analysis["weaknesses"].append("Değerlendirme performansı geliştirilmeli")
        if scores.get("engagement_score", 0) < 50:
            analysis["weaknesses"].append("Düşük katılım seviyesi")
        if len(scores.get("risk_factors", [])) > 2:
            analysis["weaknesses"].append("Birden fazla risk faktörü mevcut")

        # Add recommendations based on risk
        if scores.get("risk_score") == "High":
            analysis["recommendations"] = [
                "Acil birebir görüşme planlanmalı",
                "Öğrenme planı yeniden değerlendirilmeli",
                "Haftalık takip toplantıları düzenlenmeli",
            ]
            analysis["motivation_level"] = "Düşük"
        elif scores.get("risk_score") == "Medium":
            analysis["recommendations"] = [
                "İki haftada bir ilerleme kontrolü yapılmalı",
                "Ek motivasyon desteği sağlanmalı",
                "Zayıf konularda ek pratik önerilmeli",
            ]
        else:
            analysis["recommendations"] = [
                "Mevcut ilerleme takdir edilmeli",
                "İleri seviye konulara yönlendirilmeli",
                "Başarılar ödüllendirilmeli",
            ]
            analysis["motivation_level"] = "Yüksek"

        # Add intervention suggestions
        if scores.get("risk_score") in ["High", "Medium"]:
            analysis["intervention_suggestions"] = [
                {
                    "type": "immediate",
                    "action": "Öğrenciyle motivasyon görüşmesi yapılmalı",
                    "expected_impact": "Katılım ve performansta artış",
                }
            ]

        # Add learning tips
        analysis["personalized_learning_tips"] = [
            "Günlük 30 dakika düzenli çalışma rutini oluştur",
            "Zayıf konularda video içeriklerden yararlan",
        ]

        return analysis

    def generate_student_profile_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI analysis for student development profile.

        Args:
            profile_data: Student profile data including scores, activities, responses

        Returns:
            Dictionary with AI analysis results
        """
        # Build comprehensive prompt
        prompt = self._build_profile_analysis_prompt(profile_data)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational psychologist and learning analyst. 
                        Analyze student development profiles and provide comprehensive insights.
                        Respond in JSON format with detailed analysis.
                        Write all content in Turkish language.
                        Be encouraging, specific, and action-oriented.""",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )

            # Parse AI response
            ai_analysis = json.loads(response.choices[0].message.content)

            # Validate and enhance
            return self._validate_profile_analysis(ai_analysis, profile_data)

        except Exception as e:
            current_app.logger.error(f"OpenAI API error in generate_student_profile_analysis: {str(e)}")
            # Fallback to rule-based analysis
            return self._generate_fallback_profile_analysis(profile_data)

    def _build_profile_analysis_prompt(self, profile_data: Dict[str, Any]) -> str:
        """Build prompt for student profile analysis."""
        scores = profile_data.get("scores", {})
        evaluations = profile_data.get("recent_evaluations", [])
        patterns = profile_data.get("response_patterns", {})
        recent_activities = profile_data.get("recent_activities", {})

        # Calculate activity gap
        last_activity = recent_activities.get("last_activity_date")
        activity_gap_days = 0
        if last_activity:
            from datetime import datetime

            activity_date = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
            activity_gap_days = (datetime.utcnow() - activity_date.replace(tzinfo=None)).days

        # Check performance trend
        performance_trend = "stable"
        if evaluations and len(evaluations) >= 3:
            recent_scores = [e.get("score", 0) for e in evaluations[:3]]
            if all(recent_scores[i] < recent_scores[i + 1] for i in range(len(recent_scores) - 1)):
                performance_trend = "declining"
            elif all(recent_scores[i] > recent_scores[i + 1] for i in range(len(recent_scores) - 1)):
                performance_trend = "improving"

        prompt = f"""
        Öğrenci Gelişim Profili Analizi:
        
        Gelişim Skorları:
        - Performans İndeksi: {scores.get('performance_index', 0)}
        - Katılım Skoru: {scores.get('engagement_score', 0)}
        - Tamamlama Oranı: {scores.get('completion_rate', 0)}%
        - Risk Seviyesi: {scores.get('risk_score', 'Unknown')}
        - Risk Faktörleri: {', '.join(scores.get('risk_factors', []))}
        
        Aktivite Durumu:
        - Son aktiviteden bu yana geçen gün: {activity_gap_days}
        - Performans trendi: {performance_trend}
        - Son değerlendirme sayısı: {len(evaluations)}
        
        Son Değerlendirmeler:
        {json.dumps(evaluations[:5], indent=2, ensure_ascii=False)}
        
        Cevap Analizi:
        - Toplam cevap: {patterns.get('total_responses', 0)}
        - Doğru oranı: {patterns.get('correct_rate', 0)}%
        - Ortalama cevap süresi: {patterns.get('avg_time_per_question', 0)} saniye
        
        Zorluk Performansı:
        {json.dumps(patterns.get('difficulty_performance', {}), indent=2, ensure_ascii=False)}
        
        Lütfen bu öğrenci için detaylı analiz yap:
        
        1. Güçlü yönleri (strengths) - En az 3 madde
        2. Gelişim alanları (weaknesses) - En az 3 madde
        3. Öneriler (recommendations) - En az 5 madde, spesifik ve uygulanabilir
        4. Öğrenme modeli (learning_pattern) - Öğrencinin öğrenme tarzı
        5. Motivasyon seviyesi (motivation_level) - Yüksek/Orta/Düşük
        
        6. Uyarılar (alerts) - Aşağıdaki kriterlere göre uyarılar oluştur:
           - Eğer {activity_gap_days} gün aktivite yoksa
           - Eğer performans trendi "declining" ise
           - Eğer risk seviyesi "High" ise
           - Her uyarı için: {{"type": "warning/danger", "message": "Uyarı mesajı", "priority": "high/medium/low"}}
        
        7. Müdahale önerileri (interventions) - Detaylı müdahale planları:
           - Risk seviyesi veya motivasyon düşükse acil müdahaleler
           - Her müdahale için:
             {{
               "type": "immediate/short_term/long_term",
               "title": "Müdahale başlığı",
               "description": "Detaylı açıklama",
               "expected_impact": "Beklenen etki",
               "priority": "critical/high/medium",
               "action_items": ["Yapılacak 1", "Yapılacak 2"],
               "timeline": "24 saat içinde / 1 hafta içinde / 1 ay içinde"
             }}
        
        Yanıtı JSON formatında ver. Tüm içerik Türkçe olmalı, koçlara yönelik profesyonel ve yapıcı bir dilde yazılmalı.
        """

        return prompt

    def _validate_profile_analysis(self, ai_analysis: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance AI profile analysis."""
        validated = {
            "strengths": ai_analysis.get("strengths", []),
            "weaknesses": ai_analysis.get("weaknesses", []),
            "recommendations": ai_analysis.get("recommendations", []),
            "learning_pattern": ai_analysis.get("learning_pattern", "Karma öğrenme modeli"),
            "motivation_level": ai_analysis.get("motivation_level", "Orta"),
            "alerts": ai_analysis.get("alerts", []),
            "interventions": ai_analysis.get("interventions", []),
        }

        # Ensure alerts have proper structure
        if validated["alerts"]:
            validated["alerts"] = [
                {
                    "type": alert.get("type", "warning"),
                    "message": alert.get("message", "Dikkat edilmesi gereken durum"),
                    "priority": alert.get("priority", "medium"),
                }
                for alert in validated["alerts"]
            ]

        # Ensure interventions have proper structure
        if validated["interventions"]:
            validated["interventions"] = [
                {
                    "type": intervention.get("type", "short_term"),
                    "title": intervention.get("title", "Müdahale önerisi"),
                    "description": intervention.get("description", ""),
                    "expected_impact": intervention.get("expected_impact", "Gelişim bekleniyor"),
                    "priority": intervention.get("priority", "medium"),
                    "action_items": intervention.get("action_items", []),
                    "timeline": intervention.get("timeline", "1 hafta içinde"),
                }
                for intervention in validated["interventions"]
            ]

        # Legacy support for intervention_suggestions
        if ai_analysis.get("intervention_suggestions"):
            # Convert old format to new format
            for suggestion in ai_analysis["intervention_suggestions"]:
                if isinstance(suggestion, str):
                    validated["interventions"].append(
                        {
                            "type": "immediate",
                            "title": suggestion,
                            "description": suggestion,
                            "expected_impact": "Risk seviyesinde azalma",
                            "priority": "high",
                            "action_items": [suggestion],
                            "timeline": "24 saat içinde",
                        }
                    )

        return validated

    def _generate_fallback_profile_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback analysis when AI is not available."""
        scores = profile_data.get("scores", {})
        patterns = profile_data.get("response_patterns", {})
        recent_activities = profile_data.get("recent_activities", {})

        strengths = []
        weaknesses = []
        recommendations = []
        alerts = []
        interventions = []

        # Calculate activity gap
        last_activity = recent_activities.get("last_activity_date")
        activity_gap_days = 0
        if last_activity:
            from datetime import datetime

            try:
                activity_date = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
                activity_gap_days = (datetime.utcnow() - activity_date.replace(tzinfo=None)).days
            except (ValueError, AttributeError):
                activity_gap_days = 999  # Default to high value if parsing fails

        # Generate alerts
        if activity_gap_days >= 14:
            alerts.append(
                {
                    "type": "danger",
                    "message": f"Son {activity_gap_days} gündür aktivite göstermiyor",
                    "priority": "high",
                }
            )
        elif activity_gap_days >= 7:
            alerts.append(
                {"type": "warning", "message": f"Son {activity_gap_days} gündür aktivite azalmış", "priority": "medium"}
            )

        # Check performance trend
        evaluations = profile_data.get("recent_evaluations", [])
        if len(evaluations) >= 3:
            recent_scores = [e.get("score", 0) for e in evaluations[:3]]
            if all(recent_scores[i] < recent_scores[i + 1] for i in range(len(recent_scores) - 1)):
                alerts.append(
                    {"type": "danger", "message": "Son 3 değerlendirmede sürekli düşüş var", "priority": "high"}
                )

        if scores.get("risk_score") == "High":
            alerts.append(
                {"type": "danger", "message": "Yüksek risk grubunda - Acil müdahale gerekiyor", "priority": "high"}
            )

        # Analyze strengths
        if scores.get("performance_index", 0) >= 80:
            strengths.append("Değerlendirmelerde yüksek başarı gösteriyor")
        if scores.get("engagement_score", 0) >= 70:
            strengths.append("Yüksek katılım ve motivasyon sergiliyor")
        if patterns.get("correct_rate", 0) >= 80:
            strengths.append("Soruları yüksek doğruluk oranıyla yanıtlıyor")

        # Analyze weaknesses
        if scores.get("performance_index", 0) < 60:
            weaknesses.append("Performans seviyesi geliştirilmeli")
        if scores.get("completion_rate", 0) < 50:
            weaknesses.append("Öğrenme planlarını tamamlama oranı düşük")
        if patterns.get("avg_time_per_question", 0) > 120:
            weaknesses.append("Soru çözme hızı artırılmalı")

        # Generate interventions based on risk factors
        if scores.get("risk_score") == "High" or scores.get("engagement_score", 0) < 50:
            interventions.append(
                {
                    "type": "immediate",
                    "title": "Acil Birebir Koç Görüşmesi",
                    "description": "Öğrenci ile 24 saat içinde motivasyon ve destek görüşmesi yapılmalı",
                    "expected_impact": "Motivasyon artışı ve risk seviyesinde azalma",
                    "priority": "critical",
                    "action_items": [
                        "Öğrenci ile randevu ayarla",
                        "Sorunları ve engelleri tespit et",
                        "Kişiselleştirilmiş destek planı oluştur",
                    ],
                    "timeline": "24 saat içinde",
                }
            )

        if activity_gap_days >= 14:
            interventions.append(
                {
                    "type": "immediate",
                    "title": "Aktivite Canlandırma Programı",
                    "description": "Öğrenciyi platforma geri kazandırmak için özel program",
                    "expected_impact": "Platforma geri dönüş ve aktivite artışı",
                    "priority": "high",
                    "action_items": [
                        "Hatırlatma mesajı gönder",
                        "Mini hedefler belirle",
                        "İlk hafta için özel takip planı oluştur",
                    ],
                    "timeline": "48 saat içinde",
                }
            )

        if scores.get("completion_rate", 0) < 30:
            interventions.append(
                {
                    "type": "short_term",
                    "title": "Tamamlama Desteği Programı",
                    "description": "Öğrencinin başladığı aktiviteleri tamamlamasına yardımcı olma",
                    "expected_impact": "Tamamlama oranında %20 artış",
                    "priority": "medium",
                    "action_items": [
                        "Yarım kalan aktiviteleri listele",
                        "Tamamlama için mini ödüller belirle",
                        "Haftalık kontrol noktaları oluştur",
                    ],
                    "timeline": "1 hafta içinde",
                }
            )

        # Generate recommendations
        if scores.get("risk_score") == "High":
            recommendations.extend(
                [
                    "Acil müdahale gerekiyor - birebir görüşme planlanmalı",
                    "Öğrenme hızı ve yöntemi yeniden değerlendirilmeli",
                    "Ek destek ve motivasyon kaynakları sağlanmalı",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Mevcut ilerleme düzenli olarak takip edilmeli",
                    "Güçlü yönler üzerine odaklanarak gelişim sağlanmalı",
                    "Yeni zorluklar ve hedefler sunulmalı",
                ]
            )

        recommendations.extend(["Haftalık ilerleme değerlendirmeleri yapılmalı", "Akran öğrenmesi teşvik edilmeli"])

        # Determine learning pattern
        learning_pattern = "Görsel ve uygulamalı öğrenme"
        if patterns.get("correct_rate", 0) > 70:
            learning_pattern = "Analitik ve sistematik öğrenme"
        elif scores.get("engagement_score", 0) > 70:
            learning_pattern = "Sosyal ve etkileşimli öğrenme"

        # Determine motivation level
        motivation_level = "Orta"
        if scores.get("engagement_score", 0) >= 80:
            motivation_level = "Yüksek"
        elif scores.get("engagement_score", 0) < 50:
            motivation_level = "Düşük"

        return {
            "strengths": strengths[:3] if strengths else ["Gelişim potansiyeli yüksek"],
            "weaknesses": weaknesses[:3] if weaknesses else ["Sürekli gelişim gösteriyor"],
            "recommendations": recommendations[:5],
            "learning_pattern": learning_pattern,
            "motivation_level": motivation_level,
            "alerts": alerts,
            "interventions": interventions,
        }


# Initialize singleton instance
ai_service = AIService()
