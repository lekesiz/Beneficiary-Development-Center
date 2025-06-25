import { FileText, BarChart3, TrendingUp, Users } from 'lucide-react';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/Form';
import { useAuth } from '@/contexts/AuthContext';

interface ReportCard {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  path: string;
  requiredRoles?: string[];
  badge?: string;
}

export default function ReportsList() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const reports: ReportCard[] = [
    {
      id: 'my-development',
      title: 'My Development Report',
      description: 'View your personal learning progress, skill development, and achievement summary.',
      icon: <TrendingUp className="h-6 w-6" />,
      path: '/reports/my-development',
      badge: 'Personal',
    },
    {
      id: 'program-analytics',
      title: 'Program Analytics',
      description: 'Comprehensive analysis of program effectiveness, completion rates, and participant outcomes.',
      icon: <BarChart3 className="h-6 w-6" />,
      path: '/reports/program-analytics',
      requiredRoles: ['admin', 'manager', 'instructor'],
      badge: 'Analytics',
    },
    {
      id: 'beneficiary-overview',
      title: 'Beneficiary Overview',
      description: 'Statistical overview of all beneficiaries including demographics, progress, and status distribution.',
      icon: <Users className="h-6 w-6" />,
      path: '/reports/beneficiary-overview',
      requiredRoles: ['admin', 'manager', 'trainer'],
      badge: 'Overview',
    },
    {
      id: 'evaluation-insights',
      title: 'Evaluation Insights',
      description: 'Detailed analysis of evaluation performance, learning path effectiveness, and assessment outcomes.',
      icon: <FileText className="h-6 w-6" />,
      path: '/reports/evaluation-insights',
      requiredRoles: ['admin', 'manager', 'instructor'],
      badge: 'Insights',
    },
  ];

  const availableReports = reports.filter((report) => {
    if (!user) return false; // No user, no access to any reports
    if (!report.requiredRoles) return true;
    return report.requiredRoles.some((role) =>
      user?.roles?.some((userRole) => userRole.name === role)
    );
  });

  const handleReportClick = (report: ReportCard) => {
    navigate(report.path);
  };

  const getBadgeColor = (badge: string) => {
    const colors = {
      Personal: 'bg-blue-100 text-blue-800',
      Analytics: 'bg-green-100 text-green-800',
      Overview: 'bg-purple-100 text-purple-800',
      Insights: 'bg-orange-100 text-orange-800',
    };
    return colors[badge as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="container mx-auto py-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="mt-2 text-gray-600">
            Access comprehensive reports and analytics to track progress and performance.
          </p>
        </div>

        {/* Reports Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {availableReports.map((report) => (
            <div
              key={report.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer group"
              onClick={() => handleReportClick(report)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0 p-2 bg-gray-50 rounded-lg group-hover:bg-gray-100 transition-colors">
                    {report.icon}
                  </div>
                  {report.badge && (
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBadgeColor(
                        report.badge
                      )}`}
                    >
                      {report.badge}
                    </span>
                  )}
                </div>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                {report.title}
              </h3>
              
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {report.description}
              </p>

              <div className="flex items-center justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  className="group-hover:bg-blue-50 group-hover:border-blue-200 transition-colors"
                >
                  View Report
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {availableReports.length === 0 && (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Reports Available
            </h3>
            <p className="text-gray-600">
              You don't have access to any reports at this time. Contact your administrator for access.
            </p>
          </div>
        )}

        {/* Quick Actions */}
        {user?.roles?.some((role) => ['admin', 'manager'].includes(role.name)) && (
          <div className="mt-12 bg-gray-50 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Actions
            </h2>
            <div className="flex flex-wrap gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/reports/export')}
              >
                Export All Data
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/reports/schedule')}
              >
                Schedule Reports
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/reports/custom')}
              >
                Create Custom Report
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}