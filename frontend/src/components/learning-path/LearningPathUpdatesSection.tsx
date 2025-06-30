import {
  BookOpen,
  Plus,
  RefreshCw,
  AlertCircle,
  ChevronRight,
  Clock,
  Target,
  CheckCircle,
  XCircle,
  Edit3,
  Trash2,
} from 'lucide-react';
import { useState } from 'react';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import {
  useSuggestLearningPathUpdates,
  usePendingLearningPathUpdates,
  useStudentLearningPaths,
  useApproveLearningPathUpdate,
  useRejectLearningPathUpdate,
  useApplyLearningPathUpdate,
  type LearningPathUpdate,
} from '@/hooks/useLearningPathUpdates';

interface LearningPathUpdatesSectionProps {
  studentId: number;
}

export default function LearningPathUpdatesSection({ studentId }: LearningPathUpdatesSectionProps) {
  const [selectedPathId, setSelectedPathId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState<number | null>(null);

  // Queries
  const { data: learningPaths, isLoading: pathsLoading } = useStudentLearningPaths(studentId);
  const { data: pendingUpdates, isLoading: updatesLoading } =
    usePendingLearningPathUpdates(selectedPathId);

  // Mutations
  const suggestMutation = useSuggestLearningPathUpdates();
  const approveMutation = useApproveLearningPathUpdate();
  const rejectMutation = useRejectLearningPathUpdate();
  const applyMutation = useApplyLearningPathUpdate();

  const handleSuggestUpdates = async () => {
    try {
      await suggestMutation.mutateAsync(studentId);
    } catch (error) {
      console.error('Failed to generate suggestions:', error);
    }
  };

  const handleApprove = async (updateId: number) => {
    try {
      await approveMutation.mutateAsync(updateId);
    } catch (error) {
      console.error('Failed to approve update:', error);
    }
  };

  const handleReject = async (updateId: number) => {
    try {
      await rejectMutation.mutateAsync({ updateId, reason: rejectReason });
      setShowRejectModal(null);
      setRejectReason('');
    } catch (error) {
      console.error('Failed to reject update:', error);
    }
  };

  const handleApply = async (updateId: number) => {
    try {
      await applyMutation.mutateAsync(updateId);
    } catch (error) {
      console.error('Failed to apply update:', error);
    }
  };

  const getUpdateIcon = (type: string) => {
    switch (type) {
      case 'add_milestone':
        return <Plus className="h-4 w-4" />;
      case 'modify_milestone':
        return <Edit3 className="h-4 w-4" />;
      case 'obsolete_milestone':
        return <Trash2 className="h-4 w-4" />;
      case 'reorder':
        return <RefreshCw className="h-4 w-4" />;
      default:
        return <ChevronRight className="h-4 w-4" />;
    }
  };

  const getUpdateTypeLabel = (type: string) => {
    switch (type) {
      case 'add_milestone':
        return 'Yeni Adım';
      case 'modify_milestone':
        return 'Güncelleme';
      case 'obsolete_milestone':
        return 'Kaldırma';
      case 'reorder':
        return 'Sıralama';
      default:
        return type;
    }
  };

  const getPriorityBadge = (priority: string) => {
    const variants = {
      critical: 'danger',
      high: 'warning',
      medium: 'default',
      low: 'secondary',
    } as const;

    const labels = {
      critical: 'Kritik',
      high: 'Yüksek',
      medium: 'Orta',
      low: 'Düşük',
    };

    return (
      <Badge variant={variants[priority as keyof typeof variants] || 'default'} size="sm">
        {labels[priority as keyof typeof labels] || priority}
      </Badge>
    );
  };

  if (pathsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Learning Paths Selection */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <BookOpen className="mr-2 h-5 w-5" />
            Aktif Öğrenme Yolları
          </h3>
          <Button onClick={handleSuggestUpdates} disabled={suggestMutation.isPending} size="sm">
            <RefreshCw
              className={`mr-2 h-4 w-4 ${suggestMutation.isPending ? 'animate-spin' : ''}`}
            />
            Önerileri Güncelle
          </Button>
        </div>

        {learningPaths && learningPaths.length > 0 ? (
          <div className="space-y-3">
            {learningPaths.map((path: any) => (
              <div
                key={path.id}
                onClick={() => setSelectedPathId(path.id)}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedPathId === path.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">{path.title}</h4>
                    <p className="text-sm text-gray-600">
                      İlerleme: {path.overall_progress}% •{path.completed_milestones}/
                      {path.total_milestones} adım tamamlandı
                    </p>
                  </div>
                  <Badge variant={path.status === 'in_progress' ? 'primary' : 'default'}>
                    {path.status === 'in_progress' ? 'Devam Ediyor' : 'Kabul Edildi'}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">
            Öğrencinin aktif öğrenme yolu bulunmuyor.
          </p>
        )}
      </Card>

      {/* Pending Updates */}
      {selectedPathId && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <AlertCircle className="mr-2 h-5 w-5 text-orange-500" />
            Bekleyen Güncellemeler
          </h3>

          {updatesLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : pendingUpdates && pendingUpdates.updates.length > 0 ? (
            <div className="space-y-4">
              {pendingUpdates.updates.map((update: LearningPathUpdate) => (
                <Card key={update.id} className="p-5 border-l-4 border-blue-500">
                  <div className="space-y-3">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div
                          className={`p-2 rounded-full ${
                            update.source === 'ai'
                              ? 'bg-purple-100'
                              : update.source === 'system'
                              ? 'bg-blue-100'
                              : 'bg-gray-100'
                          }`}
                        >
                          {getUpdateIcon(update.update_type)}
                        </div>
                        <div>
                          <h4 className="font-medium flex items-center">
                            {getUpdateTypeLabel(update.update_type)}
                            <Badge variant="outline" size="sm" className="ml-2">
                              {update.source === 'ai'
                                ? 'AI'
                                : update.source === 'system'
                                ? 'Sistem'
                                : 'Manuel'}
                            </Badge>
                          </h4>
                          <p className="text-sm text-gray-600">{update.reason}</p>
                        </div>
                      </div>
                      {getPriorityBadge(update.priority)}
                    </div>

                    {/* Expected Impact */}
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="text-sm font-medium text-green-800">Beklenen Etki:</p>
                      <p className="text-sm text-green-700">{update.expected_impact}</p>
                    </div>

                    {/* Suggested Milestones */}
                    {update.suggested_milestones.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-700">Önerilen Adımlar:</p>
                        {update.suggested_milestones.map((milestone, index) => (
                          <div key={index} className="ml-4 p-3 bg-gray-50 rounded-lg">
                            <h5 className="font-medium text-sm">{milestone.title}</h5>
                            {milestone.description && (
                              <p className="text-xs text-gray-600 mt-1">{milestone.description}</p>
                            )}
                            <div className="flex items-center mt-2 text-xs text-gray-500 space-x-4">
                              <span className="flex items-center">
                                <Clock className="h-3 w-3 mr-1" />
                                {milestone.estimated_hours} saat
                              </span>
                              <span className="flex items-center">
                                <Target className="h-3 w-3 mr-1" />
                                Hafta {milestone.week_number}
                              </span>
                              {milestone.skill_focus && <span>Odak: {milestone.skill_focus}</span>}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center justify-end space-x-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowRejectModal(update.id)}
                      >
                        <XCircle className="mr-2 h-4 w-4" />
                        Reddet
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleApprove(update.id)}
                        disabled={approveMutation.isPending}
                      >
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Onayla
                      </Button>
                      {update.status === 'approved' && (
                        <Button
                          variant="success"
                          size="sm"
                          onClick={() => handleApply(update.id)}
                          disabled={applyMutation.isPending}
                        >
                          <CheckCircle className="mr-2 h-4 w-4" />
                          Uygula
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <RefreshCw className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">Bekleyen güncelleme yok</p>
              <Button
                variant="outline"
                size="sm"
                onClick={handleSuggestUpdates}
                className="mt-3"
                disabled={suggestMutation.isPending}
              >
                Yeni Öneriler Oluştur
              </Button>
            </div>
          )}
        </Card>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Güncellemeyi Reddet</h3>
            <p className="text-sm text-gray-600 mb-4">Lütfen reddetme nedeninizi belirtin:</p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Reddetme nedeni..."
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
            <div className="flex justify-end space-x-2 mt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setShowRejectModal(null);
                  setRejectReason('');
                }}
              >
                İptal
              </Button>
              <Button
                variant="danger"
                onClick={() => handleReject(showRejectModal)}
                disabled={!rejectReason.trim() || rejectMutation.isPending}
              >
                {rejectMutation.isPending ? 'Reddediliyor...' : 'Reddet'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
