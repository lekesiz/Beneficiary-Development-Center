import {
  ArrowLeft,
  Calendar,
  Clock,
  Target,
  BookOpen,
  CheckCircle,
  ChevronRight,
  Award,
  TrendingUp,
  Brain,
  Users,
  Star,
  Edit3,
  MessageSquare,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { LearningPathAcceptanceFlow } from '@/components/learning-paths/LearningPathAcceptanceFlow';
import { LearningPathTimeline } from '@/components/learning-paths/LearningPathTimeline';
import { MilestoneCard } from '@/components/learning-paths/MilestoneCard';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ProgressBar } from '@/components/ui/ProgressBar';
import {
  useLearningPath,
  useAcceptLearningPath,
  useUpdateLearningPath,
  useProvideFeedback,
} from '@/hooks/useLearningPath';
import { useMyDevelopmentReport } from '@/hooks/useReports';

export default function LearningPathPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const pathId = parseInt(id!);

  const [showAcceptanceFlow, setShowAcceptanceFlow] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // React Query hooks
  const { data: learningPath, isLoading, error } = useLearningPath(pathId);
  const acceptMutation = useAcceptLearningPath();
  const updateMutation = useUpdateLearningPath();
  const feedbackMutation = useProvideFeedback();

  // Handle acceptance
  const handleAccept = async (customizationNotes?: string) => {
    try {
      await acceptMutation.mutateAsync({ pathId, customizationNotes });
      setShowAcceptanceFlow(false);
    } catch (error) {
      console.error('Failed to accept learning path:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !learningPath) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">Öğrenme planı bulunamadı.</p>
          <Button onClick={() => navigate('/evaluations')} className="mt-4">
            Geri Dön
          </Button>
        </div>
      </div>
    );
  }

  const isProposed = learningPath.status === 'proposed';
  const isAccepted = learningPath.status === 'accepted' || learningPath.status === 'in_progress';
  const progressPercentage = learningPath.overall_progress || 0;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-md">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">{learningPath.title}</h1>
            <p className="text-gray-600">{learningPath.description}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {isProposed && !showAcceptanceFlow && (
            <Button
              onClick={() => setShowAcceptanceFlow(true)}
              className="bg-green-600 hover:bg-green-700"
            >
              <CheckCircle className="mr-2 h-4 w-4" />
              Planı İncele ve Kabul Et
            </Button>
          )}
          {isAccepted && (
            <>
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                <Edit3 className="mr-2 h-4 w-4" />
                Düzenle
              </Button>
              <Button variant="outline">
                <MessageSquare className="mr-2 h-4 w-4" />
                Geri Bildirim
              </Button>
              <Button variant="outline" onClick={() => navigate('/reports/my-development')}>
                <FileText className="mr-2 h-4 w-4" />
                Gelişim Raporu
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Acceptance Flow Modal */}
      {showAcceptanceFlow && (
        <LearningPathAcceptanceFlow
          learningPath={learningPath}
          onAccept={handleAccept}
          onCancel={() => setShowAcceptanceFlow(false)}
          isLoading={acceptMutation.isPending}
        />
      )}

      {/* Status Banner */}
      {isProposed && (
        <Card className="p-6 bg-blue-50 border-blue-200">
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-blue-600" />
            <div>
              <h3 className="font-semibold text-blue-900">
                AI Tarafından Oluşturulan Kişiselleştirilmiş Plan
              </h3>
              <p className="text-blue-700">
                Bu plan, değerlendirme sonuçlarınıza göre özel olarak hazırlandı. İnceleyip
                onayladıktan sonra öğrenmeye başlayabilirsiniz.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Süre</p>
              <p className="text-2xl font-bold">{learningPath.duration_weeks} Hafta</p>
              <p className="text-sm text-gray-500">
                {learningPath.estimated_hours_per_week} saat/hafta
              </p>
            </div>
            <Calendar className="h-8 w-8 text-blue-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">İlerleme</p>
              <p className="text-2xl font-bold">{progressPercentage.toFixed(0)}%</p>
              <p className="text-sm text-gray-500">
                {learningPath.completed_milestones} / {learningPath.total_milestones} tamamlandı
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Öğrenme Stili</p>
              <p className="text-2xl font-bold capitalize">
                {learningPath.learning_style === 'mixed' ? 'Karma' : learningPath.learning_style}
              </p>
              <p className="text-sm text-gray-500">{learningPath.difficulty_adjustment}</p>
            </div>
            <Users className="h-8 w-8 text-purple-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Hedef</p>
              <p className="text-lg font-bold">
                {learningPath.ai_insights_summary?.performance_level || 'Gelişim'}
              </p>
              <p className="text-sm text-gray-500">Mevcut seviye</p>
            </div>
            <Target className="h-8 w-8 text-orange-600 opacity-80" />
          </div>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Timeline and Milestones */}
        <div className="lg:col-span-2 space-y-6">
          {/* Progress Overview */}
          {isAccepted && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Genel İlerleme</h3>
              <ProgressBar value={progressPercentage} className="mb-2" showLabel />
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {learningPath.completed_milestones}
                  </p>
                  <p className="text-sm text-gray-600">Tamamlanan</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">
                    {learningPath.milestones.filter((m) => m.status === 'in_progress').length}
                  </p>
                  <p className="text-sm text-gray-600">Devam Eden</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-600">
                    {learningPath.milestones.filter((m) => m.status === 'pending').length}
                  </p>
                  <p className="text-sm text-gray-600">Bekleyen</p>
                </div>
              </div>
            </Card>
          )}

          {/* Timeline View */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Öğrenme Takvimi</h3>
            <LearningPathTimeline
              weeklySchedule={learningPath.weekly_schedule}
              milestones={learningPath.milestones}
              startDate={learningPath.start_date}
            />
          </Card>

          {/* Milestones */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Öğrenme Hedefleri</h3>
            {learningPath.milestones.map((milestone) => (
              <MilestoneCard
                key={milestone.id}
                milestone={milestone}
                pathId={learningPath.id}
                isPathAccepted={isAccepted}
              />
            ))}
          </div>
        </div>

        {/* Right Column - Resources and Info */}
        <div className="space-y-6">
          {/* Learning Objective */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Target className="mr-2 h-5 w-5 text-blue-600" />
              Ana Hedef
            </h3>
            <p className="text-gray-700">{learningPath.objective}</p>
          </Card>

          {/* Prerequisites */}
          {learningPath.prerequisites.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-3">Ön Koşullar</h3>
              <ul className="space-y-2">
                {learningPath.prerequisites.map((prereq, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-orange-400 rounded-full mt-1.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{prereq}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Success Metrics */}
          {learningPath.success_metrics && learningPath.success_metrics.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <Award className="mr-2 h-5 w-5 text-green-600" />
                Başarı Kriterleri
              </h3>
              <ul className="space-y-2">
                {learningPath.success_metrics.map((metric, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{metric}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Resources */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <BookOpen className="mr-2 h-5 w-5 text-purple-600" />
              Kaynaklar
            </h3>
            <div className="space-y-4">
              {learningPath.resources.map((category, index) => (
                <div key={index}>
                  <h4 className="font-medium text-gray-700 mb-2">{category.category}</h4>
                  <ul className="space-y-2">
                    {category.items.map((resource, rIndex) => (
                      <li key={rIndex} className="text-sm">
                        <a
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline flex items-center"
                        >
                          <ChevronRight className="h-3 w-3 mr-1" />
                          {resource.title}
                        </a>
                        <span className="text-gray-500 ml-4">
                          {resource.type} • {resource.estimated_time}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </Card>

          {/* AI Insights Summary */}
          {learningPath.ai_insights_summary && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <Brain className="mr-2 h-5 w-5 text-indigo-600" />
                AI Analizi
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Güçlü Yönler</span>
                  <Badge variant="success">
                    {learningPath.ai_insights_summary.strengths_addressed}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Gelişim Alanları</span>
                  <Badge variant="warning">
                    {learningPath.ai_insights_summary.weaknesses_targeted}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Performans Seviyesi</span>
                  <Badge variant="primary">
                    {learningPath.ai_insights_summary.performance_level}
                  </Badge>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
