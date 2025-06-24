import React, { useState } from 'react';
import {
  Target,
  Clock,
  CheckCircle,
  Play,
  HelpCircle,
  Calendar,
  TrendingUp,
  BookOpen,
  AlertCircle,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import {
  useStudentMilestones,
  useStartMilestone,
  useCompleteMilestone,
  useRequestHelp,
  type StudentMilestone
} from '@/hooks/useStudentMilestones';

export default function LearningPathMilestones() {
  const [expandedMilestone, setExpandedMilestone] = useState<number | null>(null);
  const [helpMessage, setHelpMessage] = useState('');
  const [showHelpModal, setShowHelpModal] = useState<number | null>(null);

  // Queries and mutations
  const { data: milestones, isLoading, error } = useStudentMilestones();
  const startMutation = useStartMilestone();
  const completeMutation = useCompleteMilestone();
  const helpMutation = useRequestHelp();

  const handleStart = async (milestoneId: number) => {
    try {
      await startMutation.mutateAsync(milestoneId);
    } catch (error) {
      console.error('Failed to start milestone:', error);
    }
  };

  const handleComplete = async (milestoneId: number) => {
    try {
      await completeMutation.mutateAsync(milestoneId);
    } catch (error) {
      console.error('Failed to complete milestone:', error);
    }
  };

  const handleRequestHelp = async (milestoneId: number) => {
    try {
      await helpMutation.mutateAsync({
        milestoneId,
        message: helpMessage
      });
      setShowHelpModal(null);
      setHelpMessage('');
    } catch (error) {
      console.error('Failed to request help:', error);
    }
  };

  const toggleExpanded = (milestoneId: number) => {
    setExpandedMilestone(expandedMilestone === milestoneId ? null : milestoneId);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success" size="sm">Tamamlandı</Badge>;
      case 'in_progress':
        return <Badge variant="primary" size="sm">Devam Ediyor</Badge>;
      case 'pending':
        return <Badge variant="default" size="sm">Bekliyor</Badge>;
      default:
        return null;
    }
  };

  const getProgressVariant = (progress: number) => {
    if (progress >= 80) return 'success';
    if (progress >= 50) return 'warning';
    return 'default';
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !milestones) {
    return (
      <Card className="p-6">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">Öğrenme yolu yüklenemedi.</p>
        </div>
      </Card>
    );
  }

  const activeMilestones = milestones.filter(m => m.status !== 'completed');
  const completedMilestones = milestones.filter(m => m.status === 'completed');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold flex items-center">
          <Target className="mr-2 h-6 w-6" />
          Öğrenme Yolu Hedeflerim
        </h2>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">
            Toplam İlerleme: {milestones.length > 0 
              ? Math.round((completedMilestones.length / milestones.length) * 100) 
              : 0}%
          </div>
          <ProgressBar 
            value={milestones.length > 0 
              ? (completedMilestones.length / milestones.length) * 100 
              : 0} 
            className="w-32"
            variant="success"
          />
        </div>
      </div>

      {/* Active Milestones */}
      {activeMilestones.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold flex items-center">
            <TrendingUp className="mr-2 h-5 w-5 text-blue-600" />
            Aktif Hedefler
          </h3>
          {activeMilestones.map((milestone) => (
            <Card 
              key={milestone.id} 
              className={`transition-all duration-200 ${
                milestone.status === 'in_progress' ? 'border-blue-500 shadow-md' : ''
              }`}
            >
              <div className="p-6">
                {/* Milestone Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="text-lg font-semibold">{milestone.title}</h4>
                      {getStatusBadge(milestone.status)}
                    </div>
                    <p className="text-gray-600 text-sm">{milestone.description}</p>
                  </div>
                  <button
                    onClick={() => toggleExpanded(milestone.id)}
                    className="ml-4 p-2 hover:bg-gray-100 rounded-full transition-colors"
                    aria-label={expandedMilestone === milestone.id ? 'Daralt' : 'Genişlet'}
                  >
                    {expandedMilestone === milestone.id 
                      ? <ChevronUp className="h-5 w-5" />
                      : <ChevronDown className="h-5 w-5" />
                    }
                  </button>
                </div>

                {/* Milestone Metadata */}
                <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                  <span className="flex items-center">
                    <Calendar className="h-4 w-4 mr-1" />
                    Hafta {milestone.week_number}
                  </span>
                  <span className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    {milestone.estimated_hours} saat
                  </span>
                  <span className="flex items-center">
                    <Target className="h-4 w-4 mr-1" />
                    {milestone.skill_focus}
                  </span>
                </div>

                {/* Progress Bar */}
                {milestone.status === 'in_progress' && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span>İlerleme</span>
                      <span>{milestone.progress}%</span>
                    </div>
                    <ProgressBar 
                      value={milestone.progress} 
                      variant={getProgressVariant(milestone.progress)}
                    />
                  </div>
                )}

                {/* Expanded Content */}
                {expandedMilestone === milestone.id && (
                  <div className="mt-4 space-y-4 pt-4 border-t">
                    {/* Objective */}
                    <div>
                      <h5 className="font-medium text-sm text-gray-700 mb-2">Hedef</h5>
                      <p className="text-sm text-gray-600">{milestone.objective}</p>
                    </div>

                    {/* Activities */}
                    {milestone.activities.length > 0 && (
                      <div>
                        <h5 className="font-medium text-sm text-gray-700 mb-2">Aktiviteler</h5>
                        <ul className="space-y-2">
                          {milestone.activities.map((activity, index) => (
                            <li key={index} className="flex items-start">
                              <div className={`w-5 h-5 rounded-full border-2 mr-3 mt-0.5 flex-shrink-0 ${
                                milestone.completed_activities?.includes(index)
                                  ? 'bg-green-500 border-green-500'
                                  : 'border-gray-300'
                              }`}>
                                {milestone.completed_activities?.includes(index) && (
                                  <CheckCircle className="h-3 w-3 text-white m-auto" />
                                )}
                              </div>
                              <div className="flex-1">
                                <p className={`text-sm ${
                                  milestone.completed_activities?.includes(index)
                                    ? 'text-gray-500 line-through'
                                    : 'text-gray-700'
                                }`}>
                                  {activity.title}
                                </p>
                                <p className="text-xs text-gray-500">{activity.duration}</p>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Resources */}
                    {milestone.resources.length > 0 && (
                      <div>
                        <h5 className="font-medium text-sm text-gray-700 mb-2">Kaynaklar</h5>
                        <div className="space-y-2">
                          {milestone.resources.map((resource, index) => (
                            <a
                              key={index}
                              href={resource.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
                            >
                              <BookOpen className="h-4 w-4 text-gray-500 mr-2" />
                              <span className="text-sm text-blue-600 hover:text-blue-800">
                                {resource.title}
                              </span>
                              <Badge variant="outline" size="sm" className="ml-auto">
                                {resource.type}
                              </Badge>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-end space-x-2 mt-4">
                  {milestone.status === 'pending' && (
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleStart(milestone.id)}
                      disabled={startMutation.isPending}
                    >
                      <Play className="mr-2 h-4 w-4" />
                      Başla
                    </Button>
                  )}
                  
                  {milestone.status === 'in_progress' && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowHelpModal(milestone.id)}
                      >
                        <HelpCircle className="mr-2 h-4 w-4" />
                        Yardım İste
                      </Button>
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleComplete(milestone.id)}
                        disabled={completeMutation.isPending || milestone.progress < 100}
                      >
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Tamamlandı
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Completed Milestones */}
      {completedMilestones.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold flex items-center">
            <CheckCircle className="mr-2 h-5 w-5 text-green-600" />
            Tamamlanan Hedefler ({completedMilestones.length})
          </h3>
          <div className="space-y-2">
            {completedMilestones.map((milestone) => (
              <Card key={milestone.id} className="p-4 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <div>
                      <h4 className="font-medium">{milestone.title}</h4>
                      <p className="text-sm text-gray-600">
                        Hafta {milestone.week_number} • {milestone.estimated_hours} saat
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-500">
                    {milestone.completed_at && new Date(milestone.completed_at).toLocaleDateString('tr-TR')}
                  </p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {milestones.length === 0 && (
        <Card className="p-12">
          <div className="text-center">
            <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Henüz öğrenme hedefi yok
            </h3>
            <p className="text-gray-600">
              Koçunuz size özel öğrenme hedefleri belirlediğinde burada görünecek.
            </p>
          </div>
        </Card>
      )}

      {/* Help Modal */}
      {showHelpModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">
              Yardım İste
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Bu hedefle ilgili yaşadığınız zorluğu açıklayın:
            </p>
            <textarea
              value={helpMessage}
              onChange={(e) => setHelpMessage(e.target.value)}
              placeholder="Örn: Aktiviteleri anlamakta zorlanıyorum..."
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
            <div className="flex justify-end space-x-2 mt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setShowHelpModal(null);
                  setHelpMessage('');
                }}
              >
                İptal
              </Button>
              <Button
                variant="primary"
                onClick={() => handleRequestHelp(showHelpModal)}
                disabled={!helpMessage.trim() || helpMutation.isPending}
              >
                {helpMutation.isPending ? 'Gönderiliyor...' : 'Gönder'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}