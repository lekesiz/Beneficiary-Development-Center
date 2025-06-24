import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Activity,
  BookOpen,
  Calendar,
  ChevronRight,
  MessageSquare,
  Download,
  Eye
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Form';
import { useAddCoachNote } from '@/hooks/useReportsOverview';
import type { StudentReportSummary } from '@/hooks/useReportsOverview';

interface StudentReportRowProps {
  summary: StudentReportSummary;
  onSelect: (selected: boolean) => void;
  isSelected: boolean;
  onViewDetails: (studentId: number) => void;
}

export const StudentReportRow: React.FC<StudentReportRowProps> = ({
  summary,
  onSelect,
  isSelected,
  onViewDetails
}) => {
  const navigate = useNavigate();
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [noteText, setNoteText] = useState('');
  const addNoteMutation = useAddCoachNote();
  
  const getRiskBadge = () => {
    switch (summary.risk_score) {
      case 'High':
        return <Badge variant="danger" size="sm">Yüksek Risk</Badge>;
      case 'Medium':
        return <Badge variant="warning" size="sm">Orta Risk</Badge>;
      case 'Low':
        return <Badge variant="success" size="sm">Düşük Risk</Badge>;
      default:
        return <Badge variant="outline" size="sm">Bilinmiyor</Badge>;
    }
  };
  
  const getPerformanceColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getPerformanceIcon = () => {
    if (summary.performance_index >= 70) {
      return <TrendingUp className="h-4 w-4 text-green-600" />;
    } else if (summary.performance_index >= 40) {
      return <Activity className="h-4 w-4 text-yellow-600" />;
    }
    return <TrendingDown className="h-4 w-4 text-red-600" />;
  };
  
  const handleAddNote = async () => {
    if (!noteText.trim()) return;
    
    try {
      await addNoteMutation.mutateAsync({
        studentId: summary.student_id,
        note: noteText
      });
      setNoteText('');
      setShowNoteModal(false);
    } catch (error) {
      console.error('Failed to add note:', error);
    }
  };
  
  const formatLastActivity = (date: string | null) => {
    if (!date) return 'Aktivite yok';
    
    const activityDate = new Date(date);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - activityDate.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Bugün';
    if (diffDays === 1) return 'Dün';
    if (diffDays < 7) return `${diffDays} gün önce`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} hafta önce`;
    return activityDate.toLocaleDateString('tr-TR');
  };
  
  return (
    <>
      <tr className={`
        hover:bg-gray-50 transition-colors
        ${summary.needs_attention ? 'bg-red-50' : ''}
        ${isSelected ? 'bg-blue-50' : ''}
      `}>
        {/* Checkbox */}
        <td className="px-6 py-4 whitespace-nowrap">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => onSelect(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </td>
        
        {/* Student Info */}
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center">
            <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="h-5 w-5 text-gray-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-900">
                {summary.student_name}
              </div>
              <div className="text-sm text-gray-500">
                {summary.student_email}
              </div>
            </div>
          </div>
        </td>
        
        {/* Performance Score */}
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center space-x-2">
            {getPerformanceIcon()}
            <span className={`text-lg font-semibold ${getPerformanceColor(summary.performance_index)}`}>
              {summary.performance_index}
            </span>
          </div>
        </td>
        
        {/* Risk Level */}
        <td className="px-6 py-4 whitespace-nowrap">
          {getRiskBadge()}
        </td>
        
        {/* Progress Summary */}
        <td className="px-6 py-4">
          <div className="text-sm text-gray-900">
            {summary.progress_summary}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            <span className="inline-flex items-center">
              <BookOpen className="h-3 w-3 mr-1" />
              {summary.active_learning_paths} aktif plan
            </span>
            <span className="mx-2">•</span>
            <span>%{summary.completion_rate} tamamlama</span>
          </div>
        </td>
        
        {/* Enrollments */}
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm text-gray-900">
            {summary.enrollments.length > 0 ? (
              <div className="space-y-1">
                {summary.enrollments.slice(0, 2).map((enrollment, index) => (
                  <div key={index} className="text-xs">
                    <span className="font-medium">
                      {enrollment.type === 'program' ? 'P:' : 'K:'}
                    </span>
                    <span className="ml-1 text-gray-600">
                      {enrollment.name.length > 20 
                        ? enrollment.name.substring(0, 20) + '...' 
                        : enrollment.name}
                    </span>
                  </div>
                ))}
                {summary.enrollments.length > 2 && (
                  <div className="text-xs text-gray-500">
                    +{summary.enrollments.length - 2} daha
                  </div>
                )}
              </div>
            ) : (
              <span className="text-gray-500">Kayıt yok</span>
            )}
          </div>
        </td>
        
        {/* Last Activity */}
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="h-4 w-4 mr-1" />
            {formatLastActivity(summary.last_activity)}
          </div>
        </td>
        
        {/* Actions */}
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <div className="flex items-center justify-end space-x-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setShowNoteModal(true)}
              title="Not ekle"
            >
              <MessageSquare className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="primary"
              onClick={() => navigate(`/coach/student/${summary.student_id}`)}
            >
              <Eye className="h-4 w-4 mr-1" />
              Profil
            </Button>
          </div>
        </td>
      </tr>
      
      {/* Note Modal */}
      {showNoteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">
              {summary.student_name} için Not Ekle
            </h3>
            <textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder="Öğrenci hakkında gözlem veya önerinizi yazın..."
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
            <div className="flex justify-end space-x-2 mt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setShowNoteModal(false);
                  setNoteText('');
                }}
              >
                İptal
              </Button>
              <Button
                onClick={handleAddNote}
                disabled={!noteText.trim() || addNoteMutation.isPending}
              >
                {addNoteMutation.isPending ? 'Kaydediliyor...' : 'Kaydet'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};