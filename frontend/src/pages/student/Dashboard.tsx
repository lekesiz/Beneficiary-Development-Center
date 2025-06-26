import {
  Target,
  BookOpen,
  Award,
  TrendingUp,
  Calendar,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import LearningPathMilestones from '@/components/student/LearningPathMilestones';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { useAuth } from '@/contexts/AuthContext';
import { useStudentDashboard } from '@/hooks/useStudentDashboard';
import { formatDate } from '@/utils/date';

export default function StudentDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: dashboard, isLoading } = useStudentDashboard();

  if (isLoading || !dashboard) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Welcome, {user?.fullName}! 👋
        </h1>
        <p className="text-blue-100">
          Ready to continue your learning journey?
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Overall Progress
              </p>
              <p className="text-2xl font-bold">
                {dashboard.stats.overall_progress}%
              </p>
              <ProgressBar
                value={dashboard.stats.overall_progress}
                className="mt-2"
                variant="primary"
              />
            </div>
            <TrendingUp className="h-8 w-8 text-blue-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold">
                {dashboard.stats.completed_milestones}
              </p>
              <p className="text-xs text-gray-500">Milestones</p>
            </div>
            <Award className="h-8 w-8 text-green-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">This Week</p>
              <p className="text-2xl font-bold">
                {dashboard.stats.weekly_hours}s
              </p>
              <p className="text-xs text-gray-500">Study Hours</p>
            </div>
            <Clock className="h-8 w-8 text-purple-600 opacity-80" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Paths</p>
              <p className="text-2xl font-bold">
                {dashboard.stats.active_paths}
              </p>
              <p className="text-xs text-gray-500">Programs</p>
            </div>
            <Target className="h-8 w-8 text-orange-600 opacity-80" />
          </div>
        </Card>
      </div>

      {/* Alerts and Notifications */}
      {dashboard.alerts && dashboard.alerts.length > 0 && (
        <Card className="p-4 border-l-4 border-yellow-500">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-3 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-yellow-800 mb-2">Attention!</h3>
              <ul className="space-y-1">
                {dashboard.alerts.map((alert, index) => (
                  <li key={index} className="text-sm text-gray-700">
                    • {alert.message}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Learning Path Milestones - 2 columns */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <LearningPathMilestones />
          </Card>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Upcoming Evaluations */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Calendar className="mr-2 h-5 w-5" />
              Upcoming Evaluations
            </h3>
            {dashboard.upcoming_evaluations.length > 0 ? (
              <div className="space-y-3">
                {dashboard.upcoming_evaluations.map((evaluation) => (
                  <div
                    key={evaluation.id}
                    className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => navigate(`/evaluations/${evaluation.id}`)}
                  >
                    <h4 className="font-medium text-sm">{evaluation.title}</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {formatDate(evaluation.due_date)}
                    </p>
                    <Badge variant="warning" size="sm" className="mt-2">
                      {evaluation.type}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">
                No upcoming evaluations
              </p>
            )}
          </Card>

          {/* Recent Achievements */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Award className="mr-2 h-5 w-5" />
              Recent Achievements
            </h3>
            {dashboard.recent_achievements.length > 0 ? (
              <div className="space-y-3">
                {dashboard.recent_achievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className="flex items-center space-x-3"
                  >
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <Award className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-sm">{achievement.title}</p>
                      <p className="text-xs text-gray-500">
                        {formatDate(achievement.earned_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No achievements earned yet</p>
            )}
          </Card>

          {/* Quick Actions */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={() => navigate('/courses')}
              >
                <BookOpen className="mr-2 h-4 w-4" />
                Browse Courses
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={() => navigate('/evaluations')}
              >
                <Target className="mr-2 h-4 w-4" />
                Evaluations
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={() => navigate('/profile')}
              >
                <TrendingUp className="mr-2 h-4 w-4" />
                My Progress Report
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
