import {
  ArrowLeft,
  Trophy,
  Target,
  Clock,
  CheckCircle,
  XCircle,
  RotateCcw,
  Download,
  Share2,
  BarChart3,
  TrendingUp,
  Star,
  AlertCircle,
  Brain,
  FileText,
} from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { LearningInsights } from '@/components/evaluations/LearningInsights';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import {
  useEvaluation,
  useEvaluationAttempt,
  useMyEvaluationAttempts,
} from '@/hooks/useEvaluations';
import { useCreateLearningPath } from '@/hooks/useLearningPath';

// Result Card Component
const ResultCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  value: string | number;
  subtitle?: string;
  color?: string;
}> = ({ icon, title, value, subtitle, color = 'text-gray-600' }) => (
  <Card className="p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className={`text-3xl font-bold ${color}`}>{value}</p>
        {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
      </div>
      <div className={`${color} opacity-80`}>{icon}</div>
    </div>
  </Card>
);

// Question Review Component
const QuestionReview: React.FC<{
  question: any;
  response: any;
  index: number;
}> = ({ question, response, index }) => {
  const isCorrect = response?.is_correct;
  const pointsEarned = response?.points_earned || 0;
  const maxPoints = question.points;

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div
            className={`
            w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
            ${isCorrect ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}
          `}
          >
            {index + 1}
          </div>
          <div>
            <h3 className="font-medium">{question.question_text}</h3>
            <div className="flex items-center space-x-2 mt-1">
              <Badge variant="outline">
                {question.question_type === 'multiple_choice' && 'Çoktan Seçmeli'}
                {question.question_type === 'true_false' && 'Doğru/Yanlış'}
                {question.question_type === 'short_answer' && 'Kısa Cevap'}
                {question.question_type === 'essay' && 'Kompozisyon'}
              </Badge>
              <span className="text-sm text-gray-500">
                {pointsEarned} / {maxPoints} puan
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {isCorrect ? (
            <CheckCircle className="h-6 w-6 text-green-600" />
          ) : (
            <XCircle className="h-6 w-6 text-red-600" />
          )}
        </div>
      </div>

      {/* Question Details */}
      <div className="space-y-3">
        {/* User Response */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Sizin Cevabınız:</h4>
          <div className="p-3 bg-gray-50 rounded-lg">
            {question.question_type === 'multiple_choice' && (
              <p>{response?.response_data?.selected_option || 'Cevaplanmadı'}</p>
            )}
            {question.question_type === 'true_false' && (
              <p>{response?.response_data?.selected_option ? 'Doğru' : 'Yanlış'}</p>
            )}
            {(question.question_type === 'short_answer' || question.question_type === 'essay') && (
              <p>{response?.response_data?.text || 'Cevaplanmadı'}</p>
            )}
          </div>
        </div>

        {/* Correct Answer (for objective questions) */}
        {(question.question_type === 'multiple_choice' ||
          question.question_type === 'true_false') && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Doğru Cevap:</h4>
            <div className="p-3 bg-green-50 rounded-lg">
              {question.question_type === 'multiple_choice' && (
                <p className="text-green-800">{question.question_data.correct_answer}</p>
              )}
              {question.question_type === 'true_false' && (
                <p className="text-green-800">
                  {question.question_data.correct_answer ? 'Doğru' : 'Yanlış'}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Explanation */}
        {question.explanation && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Açıklama:</h4>
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-blue-800 text-sm">{question.explanation}</p>
            </div>
          </div>
        )}

        {/* AI Feedback */}
        {response?.ai_feedback && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">AI Geri Bildirimi:</h4>
            <div className="p-3 bg-purple-50 rounded-lg">
              <p className="text-purple-800 text-sm">{response.ai_feedback}</p>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

// Performance Chart Component (placeholder)
const PerformanceChart: React.FC<{
  data: {
    correct: number;
    incorrect: number;
    unanswered: number;
  };
}> = ({ data }) => {
  const total = data.correct + data.incorrect + data.unanswered;
  const correctPercentage = (data.correct / total) * 100;
  const incorrectPercentage = (data.incorrect / total) * 100;
  const unansweredPercentage = (data.unanswered / total) * 100;

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Soru Analizi</h3>

      {/* Progress bars */}
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Doğru ({data.correct})</span>
            <span>{correctPercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full"
              style={{ width: `${correctPercentage}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Yanlış ({data.incorrect})</span>
            <span>{incorrectPercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-red-600 h-2 rounded-full"
              style={{ width: `${incorrectPercentage}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Cevaplanmayan ({data.unanswered})</span>
            <span>{unansweredPercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gray-600 h-2 rounded-full"
              style={{ width: `${unansweredPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex justify-center space-x-6 mt-6">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-600 rounded-full" />
          <span className="text-sm">Doğru</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-600 rounded-full" />
          <span className="text-sm">Yanlış</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-gray-600 rounded-full" />
          <span className="text-sm">Cevaplanmayan</span>
        </div>
      </div>
    </Card>
  );
};

// Recommendations Component
const Recommendations: React.FC<{
  performance: any;
  weakAreas: string[];
}> = ({ performance, weakAreas }) => (
  <Card className="p-6">
    <h3 className="text-lg font-semibold mb-4 flex items-center">
      <Star className="mr-2 h-5 w-5 text-yellow-600" />
      Öneriler
    </h3>

    <div className="space-y-4">
      {performance.percentage_score >= 85 && (
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-green-800 font-medium">🎉 Mükemmel Performans!</p>
          <p className="text-green-700 text-sm mt-1">
            Harika bir sonuç aldınız. Bu konudaki bilginiz oldukça güçlü.
          </p>
        </div>
      )}

      {performance.percentage_score >= 70 && performance.percentage_score < 85 && (
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-blue-800 font-medium">👍 İyi Performans</p>
          <p className="text-blue-700 text-sm mt-1">
            Başarılı bir sonuç. Biraz daha çalışmayla mükemmel olabilirsiniz.
          </p>
        </div>
      )}

      {performance.percentage_score < 70 && (
        <div className="p-4 bg-orange-50 rounded-lg">
          <p className="text-orange-800 font-medium">💪 Gelişim Alanları</p>
          <p className="text-orange-700 text-sm mt-1">
            Bu konularda daha fazla çalışma yapmanız faydalı olacaktır.
          </p>
        </div>
      )}

      {weakAreas.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Güçlendirilmesi Gereken Alanlar:</h4>
          <ul className="space-y-1">
            {weakAreas.map((area, index) => (
              <li key={index} className="text-sm text-gray-600 flex items-center">
                <div className="w-2 h-2 bg-orange-400 rounded-full mr-2" />
                {area}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="pt-4 border-t">
        <h4 className="font-medium text-gray-700 mb-2">Önerilen Aksiyonlar:</h4>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            Yanlış cevapladığınız soruları tekrar inceleyin
          </li>
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            Eksik konular için ek çalışma materyalleri edinin
          </li>
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            Benzer değerlendirmeleri tekrar çözebilirsiniz
          </li>
        </ul>
      </div>
    </div>
  </Card>
);

export default function EvaluationResults() {
  const { id, attemptId } = useParams<{ id: string; attemptId: string }>();
  const navigate = useNavigate();
  const [showQuestionReview, setShowQuestionReview] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'insights' | 'review'>('overview');

  const evaluationId = parseInt(id!);
  const attemptIdNum = parseInt(attemptId!);

  // Learning path mutation
  const createLearningPathMutation = useCreateLearningPath();

  // React Query hooks
  const { data: evaluation, isLoading: evaluationLoading } = useEvaluation(evaluationId);
  const { data: attempt, isLoading: attemptLoading } = useEvaluationAttempt(
    evaluationId,
    attemptIdNum
  );
  const { data: allAttempts } = useMyEvaluationAttempts(evaluationId);

  // Calculate performance metrics
  const performanceData = React.useMemo(() => {
    if (!attempt || !attempt.responses) return null;

    const correct = attempt.responses.filter((r) => r.is_correct === true).length;
    const incorrect = attempt.responses.filter((r) => r.is_correct === false).length;
    const unanswered = attempt.total_questions - attempt.responses.length;

    return { correct, incorrect, unanswered };
  }, [attempt]);

  // Mock weak areas calculation
  const weakAreas = ['Matematik - Toplama İşlemleri', 'Türkçe - Gramer'];

  if (evaluationLoading || attemptLoading) {
    return (
      <div className="p-6 flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!evaluation || !attempt) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">Sonuçlar bulunamadı.</p>
          <button
            onClick={() => navigate('/evaluations')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Geri Dön
          </button>
        </div>
      </div>
    );
  }

  const isPassed = attempt.passed;
  const canRetake =
    evaluation.max_attempts > 1 && allAttempts && allAttempts.length < evaluation.max_attempts;

  // Handle create learning path
  const handleCreateLearningPath = async () => {
    try {
      const result = await createLearningPathMutation.mutateAsync({
        evaluationId,
        attemptId: attemptIdNum,
      });
      navigate(`/learning-paths/${result.id}`);
    } catch (error) {
      console.error('Failed to create learning path:', error);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/evaluations')}
            className="p-2 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">{evaluation.title} - Sonuçlar</h1>
            <p className="text-gray-600">
              {new Date(attempt.completed_at!).toLocaleString('tr-TR')} tarihinde tamamlandı
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            PDF İndir
          </Button>
          <Button variant="outline">
            <Share2 className="mr-2 h-4 w-4" />
            Paylaş
          </Button>
          {canRetake && (
            <Button onClick={() => navigate(`/evaluations/${evaluationId}/take`)}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Tekrar Dene
            </Button>
          )}
        </div>
      </div>

      {/* Result Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <ResultCard
          icon={<Trophy className="h-8 w-8" />}
          title="Toplam Puan"
          value={`${attempt.score_earned.toFixed(1)} / ${attempt.total_points}`}
          color={isPassed ? 'text-green-600' : 'text-red-600'}
        />

        <ResultCard
          icon={<Target className="h-8 w-8" />}
          title="Yüzde Skoru"
          value={`${attempt.percentage_score.toFixed(1)}%`}
          subtitle={isPassed ? 'Geçti' : 'Kaldı'}
          color={isPassed ? 'text-green-600' : 'text-red-600'}
        />

        <ResultCard
          icon={<Clock className="h-8 w-8" />}
          title="Süre"
          value={attempt.duration_display}
          subtitle={`${attempt.questions_answered} / ${attempt.total_questions} cevaplanmış`}
          color="text-blue-600"
        />

        <ResultCard
          icon={<BarChart3 className="h-8 w-8" />}
          title="Deneme"
          value={`${attempt.attempt_number} / ${evaluation.max_attempts}`}
          subtitle={allAttempts ? `${allAttempts.length} toplam deneme` : ''}
          color="text-purple-600"
        />
      </div>

      {/* Pass/Fail Status */}
      <Card
        className={`p-6 ${isPassed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}
      >
        <div className="flex items-center justify-center space-x-3">
          {isPassed ? (
            <CheckCircle className="h-8 w-8 text-green-600" />
          ) : (
            <XCircle className="h-8 w-8 text-red-600" />
          )}
          <div className="text-center">
            <h2 className={`text-2xl font-bold ${isPassed ? 'text-green-800' : 'text-red-800'}`}>
              {isPassed ? 'Tebrikler! Başarılı oldunuz.' : 'Maalesef başarısız oldunuz.'}
            </h2>
            <p className={`${isPassed ? 'text-green-700' : 'text-red-700'}`}>
              Geçme puanı: {attempt.passing_score}% | Sizin puanınız:{' '}
              {attempt.percentage_score.toFixed(1)}%
            </p>
          </div>
        </div>
      </Card>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <BarChart3 className="mr-2 h-4 w-4" />
              Genel Bakış
            </div>
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'insights'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <Brain className="mr-2 h-4 w-4" />
              AI Öğrenme Tavsiyeleri
            </div>
          </button>
          <button
            onClick={() => setActiveTab('review')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'review'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <FileText className="mr-2 h-4 w-4" />
              Soru İncelemesi
            </div>
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Performance Analysis */}
          <div className="lg:col-span-2 space-y-6">
            {performanceData && <PerformanceChart data={performanceData} />}
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            <Recommendations performance={attempt} weakAreas={weakAreas} />

            {/* Attempt History */}
            {allAttempts && allAttempts.length > 1 && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <TrendingUp className="mr-2 h-5 w-5 text-blue-600" />
                  Deneme Geçmişi
                </h3>

                <div className="space-y-3">
                  {allAttempts.map((att, index) => (
                    <div
                      key={att.id}
                      className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <p className="font-medium">Deneme {att.attempt_number}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(att.completed_at!).toLocaleDateString('tr-TR')}
                        </p>
                      </div>
                      <div className="text-right">
                        <p
                          className={`font-bold ${att.passed ? 'text-green-600' : 'text-red-600'}`}
                        >
                          {att.percentage_score.toFixed(1)}%
                        </p>
                        <p className="text-sm text-gray-600">{att.passed ? 'Geçti' : 'Kaldı'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && (
        <div className="space-y-6">
          <LearningInsights evaluationId={evaluationId} attemptId={attemptIdNum} />

          {/* Create Learning Path Button */}
          <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Brain className="h-12 w-12 text-blue-600" />
                <div>
                  <h3 className="text-lg font-semibold text-blue-900">
                    Kişiselleştirilmiş Öğrenme Planı Oluştur
                  </h3>
                  <p className="text-blue-700">
                    AI, performansınıza göre size özel bir öğrenme planı hazırlayacak
                  </p>
                </div>
              </div>
              <Button
                onClick={handleCreateLearningPath}
                disabled={createLearningPathMutation.isPending}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {createLearningPathMutation.isPending ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Oluşturuluyor...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Plan Oluştur
                  </>
                )}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Review Tab */}
      {activeTab === 'review' && (
        <div className="space-y-6">
          {attempt.responses && attempt.responses.length > 0 ? (
            <div className="space-y-4">
              {attempt.responses.map((response, index) => (
                <QuestionResponse key={response.id} response={response} index={index} />
              ))}
            </div>
          ) : (
            <Card className="p-6">
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Henüz cevaplanmış soru bulunmuyor.</p>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}

// Question Response Component (for review)
const QuestionResponse: React.FC<{
  response: any;
  index: number;
}> = ({ response, index }) => {
  // This would typically include the question data as well
  // For now using mock data
  const mockQuestion = {
    id: response.question_id,
    question_text: `Soru ${index + 1} metni burada görünecek`,
    question_type: 'multiple_choice',
    points: 2,
    explanation: 'Bu sorunun açıklaması burada yer alacak.',
    question_data: {
      correct_answer: 'Doğru cevap seçeneği',
    },
  };

  return <QuestionReview question={mockQuestion} response={response} index={index} />;
};
