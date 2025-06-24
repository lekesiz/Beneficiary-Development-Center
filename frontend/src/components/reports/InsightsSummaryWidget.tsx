import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
  ChevronRight,
  Brain,
  Zap
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useInsightsSummary } from '@/hooks/useReports';
import { LineChart, Line, ResponsiveContainer, Tooltip } from 'recharts';

export const InsightsSummaryWidget: React.FC = () => {
  const navigate = useNavigate();
  const { data: summary, isLoading, error } = useInsightsSummary();
  
  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center">
          <LoadingSpinner size="sm" />
        </div>
      </Card>
    );
  }
  
  if (error || !summary) {
    return null;
  }
  
  const getTrendIcon = () => {
    if (!summary.performance_trend || summary.performance_trend.length < 2) {
      return <Minus className="h-5 w-5 text-gray-500" />;
    }
    
    const recent = summary.performance_trend[summary.performance_trend.length - 1].score;
    const previous = summary.performance_trend[summary.performance_trend.length - 2].score;
    
    if (recent > previous) {
      return <TrendingUp className="h-5 w-5 text-green-600" />;
    } else if (recent < previous) {
      return <TrendingDown className="h-5 w-5 text-red-600" />;
    }
    return <Minus className="h-5 w-5 text-gray-500" />;
  };
  
  const getRiskBadge = (riskScore: string) => {
    switch (riskScore) {
      case 'Low':
        return <Badge variant="success" size="sm">Düşük Risk</Badge>;
      case 'Medium':
        return <Badge variant="warning" size="sm">Orta Risk</Badge>;
      case 'High':
        return <Badge variant="danger" size="sm">Yüksek Risk</Badge>;
      default:
        return <Badge size="sm">Bilinmiyor</Badge>;
    }
  };
  
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center">
          <Brain className="mr-2 h-5 w-5 text-purple-600" />
          AI Öğrenme Özeti
        </h3>
        {getTrendIcon()}
      </div>
      
      {/* Performance Overview */}
      <div className="space-y-4">
        {/* Mini Chart */}
        {summary.performance_trend && summary.performance_trend.length > 0 && (
          <div className="h-16">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary.performance_trend}>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-gray-800 text-white p-2 rounded text-xs">
                          {payload[0].value}%
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
        
        {/* Summary Text */}
        <p className="text-sm text-gray-700 line-clamp-2">
          {summary.progress_summary}
        </p>
        
        {/* Scores */}
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">
              {summary.summary_score.performance_index}
            </p>
            <p className="text-xs text-gray-600">Performans İndeksi</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-lg font-bold">
              {summary.summary_score.completion_rate}
            </p>
            <p className="text-xs text-gray-600">Tamamlama</p>
          </div>
        </div>
        
        {/* Risk Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Risk Durumu:</span>
          {getRiskBadge(summary.summary_score.risk_score)}
        </div>
        
        {/* Immediate Actions */}
        {summary.immediate_actions && summary.immediate_actions.length > 0 && (
          <div className="pt-3 border-t">
            <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
              <Zap className="mr-1 h-4 w-4 text-orange-500" />
              Hızlı Aksiyonlar
            </h4>
            <ul className="space-y-1">
              {summary.immediate_actions.slice(0, 2).map((action, index) => (
                <li key={index} className="text-xs text-gray-600 flex items-start">
                  <ChevronRight className="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" />
                  <span className="line-clamp-1">{action}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* View Full Report Button */}
        <Button 
          size="sm" 
          variant="outline" 
          className="w-full"
          onClick={() => navigate('/reports/my-development')}
        >
          Detaylı Raporu Görüntüle
          <ChevronRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
      
      {/* Last Updated */}
      {summary.generated_at && (
        <p className="text-xs text-gray-500 text-center mt-4">
          Son güncelleme: {new Date(summary.generated_at).toLocaleTimeString('tr-TR', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </p>
      )}
    </Card>
  );
};