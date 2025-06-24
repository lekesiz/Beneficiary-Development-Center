import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  User,
  TrendingUp,
  AlertCircle,
  Shield,
  Calendar,
  Award,
  Activity,
  BookOpen,
  MessageSquare,
  Download,
  ChevronLeft,
  ChevronRight,
  Plus,
  Edit,
  Trash2
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { useStudentProfile, useAddCoachNote, useExportStudentProfile } from '@/hooks/useStudentProfile';
import { formatDate } from '@/utils/date';
import PerformanceTrendChart from '@/components/charts/PerformanceTrendChart';
import SkillDistributionChart from '@/components/charts/SkillDistributionChart';
import CoachNotesSection from '@/components/profile/CoachNotesSection';
import LearningPathUpdatesSection from '@/components/learning-path/LearningPathUpdatesSection';

export default function StudentProfile() {
  const { studentId } = useParams<{ studentId: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'overview' | 'activities' | 'analysis' | 'insights' | 'learning-path' | 'notes'>('overview');
  
  const { data: profile, isLoading, error } = useStudentProfile(Number(studentId));
  const exportMutation = useExportStudentProfile();
  
  if (isLoading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex justify-center items-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }
  
  if (error || !profile) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">Öğrenci profili yüklenemedi.</p>
          <Button
            onClick={() => navigate('/coach/dashboard')}
            className="mt-4"
          >
            Listeye Dön
          </Button>
        </div>
      </div>
    );
  }
  
  const handleExport = async (format: 'json' | 'pdf' = 'json') => {
    try {
      await exportMutation.mutateAsync({ 
        studentId: Number(studentId), 
        format 
      });
    } catch (error) {
      console.error('Export failed:', error);
    }
  };
  
  const getRiskBadgeVariant = (risk: string) => {
    switch (risk) {
      case 'High': return 'danger';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };
  
  const getMasteryBadgeVariant = (level: string) => {
    switch (level) {
      case 'Expert': return 'success';
      case 'Proficient': return 'primary';
      case 'Intermediate': return 'warning';
      case 'Beginner': return 'default';
      default: return 'default';
    }
  };
  
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/coach/dashboard')}
            size="sm"
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Listeye Dön
          </Button>
          
          <div>
            <h1 className="text-2xl font-bold flex items-center">
              <User className="mr-2 h-6 w-6" />
              {profile.student_info.name}
            </h1>
            <p className="text-gray-600">{profile.student_info.email}</p>
          </div>
        </div>
        
        <Button
          onClick={() => handleExport('json')}
          disabled={exportMutation.isPending}
        >
          <Download className="mr-2 h-4 w-4" />
          Raporu İndir
        </Button>
      </div>
      
      {/* Student Info Card */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-gray-600">Kayıt Tarihi</p>
            <p className="font-medium">{formatDate(profile.student_info.registration_date)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Son Giriş</p>
            <p className="font-medium">
              {profile.student_info.last_login 
                ? formatDate(profile.student_info.last_login)
                : 'Henüz giriş yapmadı'
              }
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Durum</p>
            <Badge variant={profile.student_info.status === 'active' ? 'success' : 'default'}>
              {profile.student_info.status === 'active' ? 'Aktif' : 'Pasif'}
            </Badge>
          </div>
          <div>
            <p className="text-sm text-gray-600">Öğrenme Stili</p>
            <p className="font-medium capitalize">{profile.student_info.learning_style}</p>
          </div>
        </div>
      </Card>
      
      {/* Development Scores */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Performans İndeksi</p>
              <p className="text-2xl font-bold">{profile.development_scores.performance_index}</p>
              <ProgressBar 
                value={profile.development_scores.performance_index} 
                className="mt-2"
              />
            </div>
            <TrendingUp className="h-8 w-8 text-blue-600 opacity-80" />
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Katılım Skoru</p>
              <p className="text-2xl font-bold">{profile.development_scores.engagement_score}</p>
              <ProgressBar 
                value={profile.development_scores.engagement_score} 
                className="mt-2"
                variant="warning"
              />
            </div>
            <Activity className="h-8 w-8 text-yellow-600 opacity-80" />
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tamamlama Oranı</p>
              <p className="text-2xl font-bold">{profile.development_scores.completion_rate}%</p>
              <ProgressBar 
                value={profile.development_scores.completion_rate} 
                className="mt-2"
                variant="success"
              />
            </div>
            <Award className="h-8 w-8 text-green-600 opacity-80" />
          </div>
        </Card>
        
        <Card className={`p-4 border-${getRiskBadgeVariant(profile.development_scores.risk_score)}-200`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Risk Skoru</p>
              <Badge 
                variant={getRiskBadgeVariant(profile.development_scores.risk_score)}
                size="lg"
                className="mt-1"
              >
                {profile.development_scores.risk_score === 'High' ? 'Yüksek' :
                 profile.development_scores.risk_score === 'Medium' ? 'Orta' : 'Düşük'}
              </Badge>
              {profile.development_scores.risk_factors.length > 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  {profile.development_scores.risk_factors.length} risk faktörü
                </p>
              )}
            </div>
            <Shield className="h-8 w-8 text-gray-600 opacity-80" />
          </div>
        </Card>
      </div>
      
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Genel Bakış
          </button>
          <button
            onClick={() => setActiveTab('activities')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'activities'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Aktiviteler
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analysis'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            AI Analizi
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'insights'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Öneriler
          </button>
          <button
            onClick={() => setActiveTab('learning-path')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'learning-path'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Öğrenme Yolu
          </button>
          <button
            onClick={() => setActiveTab('notes')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'notes'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Koç Notları
          </button>
        </nav>
      </div>
      
      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <>
            {/* Enrollments */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <BookOpen className="mr-2 h-5 w-5" />
                Kayıtlar
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600 mb-2">Programlar ({profile.enrollments.programs.length})</p>
                  {profile.enrollments.programs.length > 0 ? (
                    <div className="space-y-2">
                      {profile.enrollments.programs.map(program => (
                        <div key={program.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="font-medium">{program.title}</span>
                          <Badge variant={program.status === 'active' ? 'success' : 'default'} size="sm">
                            {program.status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">Program kaydı yok</p>
                  )}
                </div>
                
                <div>
                  <p className="text-sm text-gray-600 mb-2">Kurslar ({profile.enrollments.courses.length})</p>
                  {profile.enrollments.courses.length > 0 ? (
                    <div className="space-y-2">
                      {profile.enrollments.courses.map(course => (
                        <div key={course.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="font-medium">{course.title}</span>
                          <Badge variant={course.status === 'active' ? 'success' : 'default'} size="sm">
                            {course.status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">Kurs kaydı yok</p>
                  )}
                </div>
              </div>
            </Card>
            
            {/* Visualizations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Performans Trendi</h3>
                <PerformanceTrendChart data={profile.visualization_data.performance_trend} />
              </Card>
              
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Beceri Dağılımı</h3>
                <SkillDistributionChart data={profile.visualization_data.skill_distribution} />
              </Card>
            </div>
          </>
        )}
        
        {activeTab === 'activities' && (
          <div className="space-y-6">
            {/* Recent Evaluations */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Son Değerlendirmeler</h3>
              {profile.recent_activities.recent_evaluations.length > 0 ? (
                <div className="space-y-3">
                  {profile.recent_activities.recent_evaluations.map(evaluation => (
                    <div key={evaluation.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{evaluation.evaluation_title}</h4>
                          <p className="text-sm text-gray-600">
                            {formatDate(evaluation.completed_at!)} • {evaluation.duration_minutes} dakika
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold">{evaluation.score}%</p>
                          <Badge variant={evaluation.passed ? 'success' : 'danger'} size="sm">
                            {evaluation.passed ? 'Başarılı' : 'Başarısız'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Henüz değerlendirme tamamlanmamış</p>
              )}
            </Card>
            
            {/* Recent Learning Sessions */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Son Öğrenme Oturumları</h3>
              {profile.recent_activities.recent_sessions.length > 0 ? (
                <div className="space-y-3">
                  {profile.recent_activities.recent_sessions.map(session => (
                    <div key={session.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{session.milestone_title}</h4>
                          <p className="text-sm text-gray-600">
                            {session.path_title} • Hafta {session.week_number}
                          </p>
                          <p className="text-sm text-gray-600">
                            {formatDate(session.updated_at!)}
                          </p>
                        </div>
                        <div className="text-right">
                          <ProgressBar value={session.progress!} className="w-24" />
                          <Badge variant="default" size="sm" className="mt-1">
                            {session.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Henüz öğrenme oturumu yok</p>
              )}
            </Card>
          </div>
        )}
        
        {activeTab === 'analysis' && (
          <div className="space-y-6">
            {/* AI Analysis */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">AI Gelişim Analizi</h3>
              
              <div className="space-y-6">
                {/* Strengths */}
                <div>
                  <h4 className="font-medium text-green-700 mb-2">Güçlü Yönler</h4>
                  <ul className="space-y-1">
                    {profile.ai_analysis.strengths.map((strength, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-green-500 mr-2">•</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* Weaknesses */}
                <div>
                  <h4 className="font-medium text-red-700 mb-2">Gelişim Alanları</h4>
                  <ul className="space-y-1">
                    {profile.ai_analysis.weaknesses.map((weakness, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-red-500 mr-2">•</span>
                        <span>{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* Recommendations */}
                <div>
                  <h4 className="font-medium text-blue-700 mb-2">Öneriler</h4>
                  <ul className="space-y-1">
                    {profile.ai_analysis.recommendations.map((recommendation, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        <span>{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* Learning Pattern & Motivation */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">Öğrenme Modeli</p>
                    <p className="font-medium">{profile.ai_analysis.learning_pattern}</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">Motivasyon Seviyesi</p>
                    <p className="font-medium">{profile.ai_analysis.motivation_level}</p>
                  </div>
                </div>
              </div>
            </Card>
            
            {/* Next Steps */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Sonraki Adımlar</h3>
              
              {profile.next_recommendations.next_evaluation && (
                <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-1">Önerilen Değerlendirme</h4>
                  <p className="text-sm">
                    {profile.next_recommendations.next_evaluation.type === 'remedial' ? 'Telafi' : 'İleri Seviye'} - 
                    {' '}{profile.next_recommendations.next_evaluation.focus}
                  </p>
                  <p className="text-sm text-blue-600">
                    Önerilen Tarih: {formatDate(profile.next_recommendations.next_evaluation.suggested_date)}
                  </p>
                </div>
              )}
              
              <div className="space-y-2">
                {profile.next_recommendations.action_items.map((item, index) => (
                  <div key={index} className="flex items-center p-3 bg-gray-50 rounded">
                    <Calendar className="h-4 w-4 text-gray-500 mr-3" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}
        
        {activeTab === 'insights' && (
          <div className="space-y-6">
            {/* Alerts Section */}
            {profile.ai_analysis.alerts && profile.ai_analysis.alerts.length > 0 && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <AlertCircle className="mr-2 h-5 w-5 text-red-500" />
                  Sistem Uyarıları
                </h3>
                <div className="space-y-3">
                  {profile.ai_analysis.alerts
                    .sort((a, b) => {
                      const priorityOrder = { high: 0, medium: 1, low: 2 };
                      return priorityOrder[a.priority] - priorityOrder[b.priority];
                    })
                    .map((alert, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border-l-4 ${
                          alert.type === 'danger'
                            ? 'bg-red-50 border-red-500'
                            : 'bg-yellow-50 border-yellow-500'
                        }`}
                      >
                        <div className="flex items-start">
                          <AlertCircle 
                            className={`h-5 w-5 mt-0.5 mr-3 ${
                              alert.type === 'danger' ? 'text-red-600' : 'text-yellow-600'
                            }`} 
                          />
                          <div className="flex-1">
                            <p className={`font-medium ${
                              alert.type === 'danger' ? 'text-red-800' : 'text-yellow-800'
                            }`}>
                              {alert.message}
                            </p>
                            <Badge 
                              variant={alert.priority === 'high' ? 'danger' : alert.priority === 'medium' ? 'warning' : 'default'}
                              size="sm"
                              className="mt-2"
                            >
                              {alert.priority === 'high' ? 'Yüksek Öncelik' : 
                               alert.priority === 'medium' ? 'Orta Öncelik' : 'Düşük Öncelik'}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </Card>
            )}
            
            {/* Interventions Section */}
            {profile.ai_analysis.interventions && profile.ai_analysis.interventions.length > 0 && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Shield className="mr-2 h-5 w-5 text-blue-600" />
                  Müdahale Önerileri
                </h3>
                <div className="space-y-4">
                  {profile.ai_analysis.interventions
                    .sort((a, b) => {
                      const priorityOrder = { critical: 0, high: 1, medium: 2 };
                      return priorityOrder[a.priority] - priorityOrder[b.priority];
                    })
                    .map((intervention, index) => (
                      <Card 
                        key={index} 
                        className={`p-5 ${
                          intervention.priority === 'critical' 
                            ? 'border-red-200 bg-red-50' 
                            : intervention.priority === 'high' 
                            ? 'border-orange-200 bg-orange-50' 
                            : 'border-gray-200'
                        }`}
                      >
                        <div className="space-y-3">
                          <div className="flex items-start justify-between">
                            <h4 className="font-semibold text-lg">{intervention.title}</h4>
                            <div className="flex items-center space-x-2">
                              <Badge 
                                variant={
                                  intervention.type === 'immediate' ? 'danger' :
                                  intervention.type === 'short_term' ? 'warning' : 'default'
                                }
                                size="sm"
                              >
                                {intervention.type === 'immediate' ? 'Acil' :
                                 intervention.type === 'short_term' ? 'Kısa Vadeli' : 'Uzun Vadeli'}
                              </Badge>
                              <Badge 
                                variant={
                                  intervention.priority === 'critical' ? 'danger' :
                                  intervention.priority === 'high' ? 'warning' : 'default'
                                }
                                size="sm"
                              >
                                {intervention.priority === 'critical' ? 'Kritik' :
                                 intervention.priority === 'high' ? 'Yüksek' : 'Orta'} Öncelik
                              </Badge>
                            </div>
                          </div>
                          
                          <p className="text-gray-700">{intervention.description}</p>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <p className="text-sm font-medium text-gray-600">Beklenen Etki:</p>
                              <p className="text-sm bg-green-100 text-green-800 p-2 rounded">
                                {intervention.expected_impact}
                              </p>
                            </div>
                            <div className="space-y-2">
                              <p className="text-sm font-medium text-gray-600">Zaman Çizelgesi:</p>
                              <p className="text-sm bg-blue-100 text-blue-800 p-2 rounded flex items-center">
                                <Calendar className="h-4 w-4 mr-1" />
                                {intervention.timeline}
                              </p>
                            </div>
                          </div>
                          
                          {intervention.action_items.length > 0 && (
                            <div className="space-y-2">
                              <p className="text-sm font-medium text-gray-600">Yapılacaklar:</p>
                              <ul className="space-y-1">
                                {intervention.action_items.map((item, itemIndex) => (
                                  <li key={itemIndex} className="flex items-start text-sm">
                                    <ChevronRight className="h-4 w-4 text-gray-400 mt-0.5 mr-2 flex-shrink-0" />
                                    <span>{item}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </Card>
                    ))}
                </div>
              </Card>
            )}
            
            {/* No Alerts or Interventions */}
            {(!profile.ai_analysis.alerts || profile.ai_analysis.alerts.length === 0) && 
             (!profile.ai_analysis.interventions || profile.ai_analysis.interventions.length === 0) && (
              <Card className="p-12">
                <div className="text-center">
                  <Shield className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Müdahale Gerektirmiyor
                  </h3>
                  <p className="text-gray-600">
                    Öğrenci şu anda sağlıklı bir gelişim gösteriyor. 
                    Düzenli takip devam ettirilmeli.
                  </p>
                </div>
              </Card>
            )}
          </div>
        )}
        
        {activeTab === 'learning-path' && (
          <LearningPathUpdatesSection studentId={Number(studentId!)} />
        )}
        
        {activeTab === 'notes' && (
          <CoachNotesSection 
            studentId={Number(studentId!)}
            notes={profile.coach_notes}
          />
        )}
      </div>
    </div>
  );
}