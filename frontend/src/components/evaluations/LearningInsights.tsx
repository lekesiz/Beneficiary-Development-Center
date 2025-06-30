import {
  Brain,
  Activity,
  Target,
  Zap,
  BarChart3,
  CheckCircle,
  AlertCircle,
  BookOpen,
  Award,
  Lightbulb,
} from 'lucide-react';
import * as React from 'react';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import {
  useEvaluationInsights,
  getPerformanceLevelColor,
  getPerformanceLevelLabel,
  getTrendIcon,
  getTrendLabel,
  formatPerformanceMetrics,
} from '@/hooks/useEvaluationInsights';

interface LearningInsightsProps {
  evaluationId: number;
  attemptId: number;
}

// Performance Metric Card
const MetricCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
  description?: string;
}> = ({ icon, label, value, color, description }) => (
  <Card className="p-4">
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-1">
          <div className="text-gray-500">{icon}</div>
          <p className="text-sm font-medium text-gray-600">{label}</p>
        </div>
        <p className={`text-2xl font-bold ${color}`}>{value}</p>
        {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
      </div>
    </div>
  </Card>
);

// Insight Item Component
const InsightItem: React.FC<{
  icon: React.ReactNode;
  text: string;
  type: 'strength' | 'weakness' | 'recommendation';
}> = ({ icon, text, type }) => {
  const getColorClass = () => {
    switch (type) {
      case 'strength':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'weakness':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'recommendation':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className={`flex items-start space-x-3 p-3 rounded-lg border ${getColorClass()}`}>
      <div className="flex-shrink-0 mt-0.5">{icon}</div>
      <p className="text-sm leading-relaxed">{text}</p>
    </div>
  );
};

// Progress Bar Component
const ProgressBar: React.FC<{
  value: number;
  max?: number;
  label?: string;
  color?: string;
}> = ({ value, max = 100, label, color = 'bg-blue-600' }) => {
  const percentage = (value / max) * 100;

  return (
    <div className="space-y-1">
      {label && (
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">{label}</span>
          <span className="font-medium">{value.toFixed(0)}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`${color} h-2.5 rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
};

export const LearningInsights: React.FC<LearningInsightsProps> = ({ evaluationId, attemptId }) => {
  const { data: insights, isLoading, error } = useEvaluationInsights(evaluationId, attemptId);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <LoadingSpinner size="lg" />
        <p className="ml-3 text-gray-600">AI öğrenme tavsiyeleri hazırlanıyor...</p>
      </div>
    );
  }

  if (error || !insights) {
    return (
      <Card className="p-6">
        <div className="text-center py-8">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">Öğrenme tavsiyeleri yüklenemedi.</p>
        </div>
      </Card>
    );
  }

  const metrics = formatPerformanceMetrics(insights.performance_metrics);

  return (
    <div className="space-y-6">
      {/* Performance Overview */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Brain className="mr-2 h-5 w-5 text-purple-600" />
            AI Öğrenme Analizi
          </h3>
          <div className="flex items-center space-x-3">
            <Badge
              variant="outline"
              className={getPerformanceLevelColor(insights.visual_indicators.level)}
            >
              <Award className="mr-1 h-3 w-3" />
              {getPerformanceLevelLabel(insights.visual_indicators.level)}
            </Badge>
            <Badge variant="outline" className="flex items-center">
              <span className="mr-1">{getTrendIcon(insights.visual_indicators.trend)}</span>
              {getTrendLabel(insights.visual_indicators.trend)}
            </Badge>
          </div>
        </div>

        {/* Performance Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <MetricCard
            icon={<Target className="h-5 w-5" />}
            label={metrics.overallScore.label}
            value={metrics.overallScore.formatted}
            color={metrics.overallScore.color}
          />
          <MetricCard
            icon={<CheckCircle className="h-5 w-5" />}
            label={metrics.accuracy.label}
            value={metrics.accuracy.formatted}
            color={metrics.accuracy.color}
          />
          <MetricCard
            icon={<Zap className="h-5 w-5" />}
            label={metrics.timeEfficiency.label}
            value={metrics.timeEfficiency.formatted}
            color={metrics.timeEfficiency.color}
            description="Hız ve doğruluk dengesi"
          />
          <MetricCard
            icon={<Activity className="h-5 w-5" />}
            label={metrics.consistency.label}
            value={metrics.consistency.formatted}
            color={metrics.consistency.color}
            description="Performans tutarlılığı"
          />
        </div>
      </div>

      {/* Performance Progress Bars */}
      <Card className="p-6">
        <h4 className="font-semibold mb-4 flex items-center">
          <BarChart3 className="mr-2 h-5 w-5 text-blue-600" />
          Detaylı Performans Metrikleri
        </h4>
        <div className="space-y-4">
          <ProgressBar
            value={insights.performance_metrics.accuracy_percentage}
            label="Doğruluk Oranı"
            color={
              insights.performance_metrics.accuracy_percentage >= 80
                ? 'bg-green-600'
                : insights.performance_metrics.accuracy_percentage >= 60
                ? 'bg-yellow-600'
                : 'bg-red-600'
            }
          />
          <ProgressBar
            value={insights.performance_metrics.time_efficiency}
            label="Zaman Verimliliği"
            color={
              insights.performance_metrics.time_efficiency >= 80
                ? 'bg-green-600'
                : insights.performance_metrics.time_efficiency >= 60
                ? 'bg-yellow-600'
                : 'bg-red-600'
            }
          />
          <ProgressBar
            value={insights.performance_metrics.consistency_score}
            label="Tutarlılık Skoru"
            color={
              insights.performance_metrics.consistency_score >= 80
                ? 'bg-green-600'
                : insights.performance_metrics.consistency_score >= 60
                ? 'bg-yellow-600'
                : 'bg-red-600'
            }
          />
        </div>
      </Card>

      {/* Strengths, Weaknesses, and Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Strengths */}
        <Card className="p-6">
          <h4 className="font-semibold mb-4 flex items-center text-green-700">
            <CheckCircle className="mr-2 h-5 w-5" />
            Güçlü Yönler
          </h4>
          <div className="space-y-3">
            {insights.strengths.length > 0 ? (
              insights.strengths.map((strength, index) => (
                <InsightItem
                  key={index}
                  icon={<CheckCircle className="h-4 w-4 text-green-600" />}
                  text={strength}
                  type="strength"
                />
              ))
            ) : (
              <p className="text-sm text-gray-500">Henüz belirlenmiş güçlü yön yok</p>
            )}
          </div>
        </Card>

        {/* Weaknesses */}
        <Card className="p-6">
          <h4 className="font-semibold mb-4 flex items-center text-red-700">
            <AlertCircle className="mr-2 h-5 w-5" />
            Gelişim Alanları
          </h4>
          <div className="space-y-3">
            {insights.weaknesses.length > 0 ? (
              insights.weaknesses.map((weakness, index) => (
                <InsightItem
                  key={index}
                  icon={<AlertCircle className="h-4 w-4 text-red-600" />}
                  text={weakness}
                  type="weakness"
                />
              ))
            ) : (
              <p className="text-sm text-gray-500">Henüz belirlenmiş gelişim alanı yok</p>
            )}
          </div>
        </Card>

        {/* Recommendations */}
        <Card className="p-6">
          <h4 className="font-semibold mb-4 flex items-center text-blue-700">
            <BookOpen className="mr-2 h-5 w-5" />
            Öneriler
          </h4>
          <div className="space-y-3">
            {insights.recommendations.length > 0 ? (
              insights.recommendations.map((recommendation, index) => (
                <InsightItem
                  key={index}
                  icon={<Lightbulb className="h-4 w-4 text-blue-600" />}
                  text={recommendation}
                  type="recommendation"
                />
              ))
            ) : (
              <p className="text-sm text-gray-500">Henüz öneri bulunmuyor</p>
            )}
          </div>
        </Card>
      </div>

      {/* Study Tips */}
      <Card className="p-6 bg-gradient-to-r from-purple-50 to-blue-50">
        <h4 className="font-semibold mb-4 flex items-center">
          <Lightbulb className="mr-2 h-5 w-5 text-purple-600" />
          Çalışma İpuçları
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm text-gray-700">
              <span className="font-medium">🎯 Hedef Belirleme:</span> Zayıf olduğunuz konulara
              öncelik verin
            </p>
            <p className="text-sm text-gray-700">
              <span className="font-medium">⏰ Düzenli Çalışma:</span> Günde en az 30 dakika pratik
              yapın
            </p>
            <p className="text-sm text-gray-700">
              <span className="font-medium">📝 Not Alma:</span> Yanlış yaptığınız soruları not edin
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-gray-700">
              <span className="font-medium">🔄 Tekrar:</span> Öğrendiğiniz konuları düzenli
              tekrarlayın
            </p>
            <p className="text-sm text-gray-700">
              <span className="font-medium">💪 Motivasyon:</span> Küçük başarılarınızı kutlayın
            </p>
            <p className="text-sm text-gray-700">
              <span className="font-medium">🤝 Destek:</span> Anlamadığınız konularda yardım isteyin
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
