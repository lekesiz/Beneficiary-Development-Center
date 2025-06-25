import {
  User,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Target,
  Brain,
  Calendar,
  Download,
  RefreshCw,
  ChevronRight,
  Star,
  Award,
  BookOpen,
  Activity,
  Zap,
  Shield,
} from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ProgressBar } from '@/components/ui/ProgressBar';
import {
  useDevelopmentReport,
  useDownloadReport,
  type DevelopmentReport as DevelopmentReportType,
} from '@/hooks/useReports';


interface DevelopmentReportProps {
  userId: number;
  userName?: string;
  dateRange?: number;
  onClose?: () => void;
}

export const DevelopmentReport: React.FC<DevelopmentReportProps> = ({
  userId,
  userName,
  dateRange = 30,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'analysis' | 'recommendations'
  >('overview');

  // Fetch report data
  const {
    data: report,
    isLoading,
    refetch,
  } = useDevelopmentReport(userId, dateRange);
  const downloadMutation = useDownloadReport();

  if (isLoading) {
    return (
      <div className="p-6 flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-600">Rapor yüklenemedi.</p>
      </div>
    );
  }

  const getRiskBadge = (riskScore: string) => {
    switch (riskScore) {
      case 'Low':
        return <Badge variant="success">Düşük Risk</Badge>;
      case 'Medium':
        return <Badge variant="warning">Orta Risk</Badge>;
      case 'High':
        return <Badge variant="danger">Yüksek Risk</Badge>;
      default:
        return <Badge>Bilinmiyor</Badge>;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'low':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const handleDownload = () => {
    downloadMutation.mutate({
      userId,
      days: dateRange,
      format: 'json',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center">
            <User className="mr-2 h-6 w-6" />
            {report.student_name} - Gelişim Raporu
          </h2>
          <p className="text-gray-600 mt-1">
            Son {dateRange} günlük performans analizi
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Yenile
          </Button>
          <Button variant="outline" onClick={handleDownload}>
            <Download className="mr-2 h-4 w-4" />
            İndir
          </Button>
          {onClose && (
            <Button variant="ghost" onClick={onClose}>
              Kapat
            </Button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Tamamlama Oranı
              </p>
              <p className="text-2xl font-bold">
                {report.summary_score.completion_rate}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Performans İndeksi
              </p>
              <p className="text-2xl font-bold">
                {report.summary_score.performance_index}
              </p>
            </div>
            <Activity className="h-8 w-8 text-blue-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Risk Durumu</p>
              <div className="mt-1">
                {getRiskBadge(report.summary_score.risk_score)}
              </div>
            </div>
            <Shield className="h-8 w-8 text-orange-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Öğrenme Stili</p>
              <p className="text-sm font-semibold capitalize">
                {report.ai_analysis.learning_style.split(' ')[0]}
              </p>
            </div>
            <Brain className="h-8 w-8 text-purple-600 opacity-80" />
          </div>
        </Card>
      </div>

      {/* Progress Summary */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">
          Genel Değerlendirme
        </h3>
        <p className="text-blue-800">{report.progress_summary}</p>
        <p className="text-blue-700 text-sm mt-2">
          {report.summary_score.overall_assessment}
        </p>
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
            Genel Bakış
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'analysis'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            AI Analizi
          </button>
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'recommendations'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Öneriler
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Trend Chart */}
          {report.visualization_data?.performance_trend && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Performans Trendi</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={report.visualization_data.performance_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(date) =>
                      new Date(date).toLocaleDateString('tr-TR', {
                        day: '2-digit',
                        month: 'short',
                      })
                    }
                  />
                  <YAxis domain={[0, 100]} />
                  <Tooltip
                    labelFormatter={(date) =>
                      new Date(date).toLocaleDateString('tr-TR')
                    }
                    formatter={(value) => [`${value}%`, 'Puan']}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    dot={{ fill: '#3B82F6', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          )}

          {/* Milestone Progress */}
          {report.visualization_data?.milestone_progress && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">
                Öğrenme Yolu İlerlemesi
              </h3>
              <div className="space-y-3">
                {report.visualization_data.milestone_progress.map(
                  (milestone, index) => (
                    <div key={index}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium truncate pr-2">
                          {milestone.path}
                        </span>
                        <span className="text-gray-600">
                          {milestone.progress}%
                        </span>
                      </div>
                      <ProgressBar value={milestone.progress} />
                    </div>
                  )
                )}
              </div>
            </Card>
          )}

          {/* Skill Distribution */}
          {report.visualization_data?.skill_distribution && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Beceri Dağılımı</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={report.visualization_data.skill_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="skill" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="average_progress" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          )}

          {/* Suggested Interventions */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Önerilen Müdahaleler</h3>
            <div className="space-y-3">
              {report.suggested_interventions.map((intervention, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg ${getPriorityColor(
                    intervention.priority
                  )}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <Badge
                          variant={
                            intervention.priority === 'high'
                              ? 'danger'
                              : intervention.priority === 'medium'
                              ? 'warning'
                              : 'success'
                          }
                          size="sm"
                        >
                          {intervention.priority === 'high'
                            ? 'Yüksek'
                            : intervention.priority === 'medium'
                            ? 'Orta'
                            : 'Düşük'}{' '}
                          Öncelik
                        </Badge>
                        <span className="text-sm text-gray-600">
                          {intervention.timeline}
                        </span>
                      </div>
                      <p className="font-medium">{intervention.intervention}</p>
                      <p className="text-sm mt-1">
                        <span className="font-medium">Beklenen Sonuç:</span>{' '}
                        {intervention.expected_outcome}
                      </p>
                    </div>
                    <Zap className="h-5 w-5 flex-shrink-0 ml-3 opacity-60" />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'analysis' && (
        <div className="space-y-6">
          {/* Strengths */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Star className="mr-2 h-5 w-5 text-green-600" />
              Güçlü Yönler
            </h3>
            <div className="space-y-3">
              {report.ai_analysis.strengths.map((strength, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <p className="text-gray-700">{strength}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Weaknesses */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Target className="mr-2 h-5 w-5 text-orange-600" />
              Gelişim Alanları
            </h3>
            <div className="space-y-3">
              {report.ai_analysis.weaknesses.map((weakness, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                  <p className="text-gray-700">{weakness}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Performance Risks */}
          {report.ai_analysis.performance_risks.length > 0 && (
            <Card className="p-6 bg-red-50 border-red-200">
              <h3 className="text-lg font-semibold mb-4 flex items-center text-red-900">
                <Shield className="mr-2 h-5 w-5 text-red-600" />
                Performans Riskleri
              </h3>
              <div className="space-y-3">
                {report.ai_analysis.performance_risks.map((risk, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-red-800">{risk}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Learning Style Analysis */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Brain className="mr-2 h-5 w-5 text-purple-600" />
              Öğrenme Stili Analizi
            </h3>
            <p className="text-gray-700">{report.ai_analysis.learning_style}</p>
          </Card>
        </div>
      )}

      {activeTab === 'recommendations' && (
        <div className="space-y-6">
          {/* Immediate Actions */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Zap className="mr-2 h-5 w-5 text-red-600" />
              Hemen Yapılması Gerekenler
            </h3>
            <div className="space-y-2">
              {report.recommendations.immediate_actions.map((action, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-3 p-3 bg-red-50 rounded-lg"
                >
                  <ChevronRight className="h-5 w-5 text-red-600 flex-shrink-0" />
                  <p className="text-red-800">{action}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Long-term Goals */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Target className="mr-2 h-5 w-5 text-blue-600" />
              Uzun Vadeli Hedefler
            </h3>
            <div className="space-y-2">
              {report.recommendations.long_term_goals.map((goal, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg"
                >
                  <Award className="h-5 w-5 text-blue-600 flex-shrink-0" />
                  <p className="text-blue-800">{goal}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Support Needed */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Users className="mr-2 h-5 w-5 text-green-600" />
              Gerekli Destek
            </h3>
            <div className="space-y-2">
              {report.recommendations.support_needed.map((support, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg"
                >
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                  <p className="text-green-800">{support}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Next Evaluation Focus */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <BookOpen className="mr-2 h-5 w-5 text-purple-600" />
              Bir Sonraki Değerlendirme Odakları
            </h3>
            <div className="space-y-2">
              {report.next_evaluation_focus.map((focus, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg"
                >
                  <Target className="h-5 w-5 text-purple-600 flex-shrink-0" />
                  <p className="text-purple-800">{focus}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Report Metadata */}
      {report.metadata && (
        <Card className="p-4 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-4">
              <span>
                <Calendar className="inline-block h-4 w-4 mr-1" />
                Oluşturulma:{' '}
                {new Date(report.metadata.generated_at).toLocaleString('tr-TR')}
              </span>
              <span>
                <User className="inline-block h-4 w-4 mr-1" />
                Oluşturan: {report.metadata.generated_by}
              </span>
            </div>
            <span>Rapor Dönemi: {report.metadata.report_period_days} gün</span>
          </div>
        </Card>
      )}
    </div>
  );
};

// Add missing import
const Users = User;
