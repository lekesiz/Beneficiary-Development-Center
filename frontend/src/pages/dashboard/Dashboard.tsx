import { useState } from 'react';
import { 
  Users, 
  BookOpen, 
  ClipboardCheck, 
  TrendingUp,
  Plus,
  Calendar,
  ArrowUp,
  ArrowDown,
  Activity,
  Award,
  Target,
  Sparkles
} from 'lucide-react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useBeneficiaryStatistics } from '@/hooks/useBeneficiaries';
import { useDashboardData } from '@/hooks/useDashboard';
import { cn } from '@/lib/utils';

// Stat Card Component
const StatCard = ({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  trendValue, 
  color = 'primary' 
}: {
  title: string;
  value: string | number;
  icon: any;
  trend?: 'up' | 'down';
  trendValue?: string;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
}) => {
  const colorClasses = {
    primary: 'text-primary bg-primary/10',
    success: 'text-success bg-success/10',
    warning: 'text-warning bg-warning/10',
    danger: 'text-destructive bg-destructive/10',
    info: 'text-info bg-info/10',
  };

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <div className="flex items-baseline space-x-2">
              <p className="text-3xl font-bold tracking-tight">{value}</p>
              {trend && (
                <span className={cn(
                  'flex items-center text-sm font-medium',
                  trend === 'up' ? 'text-success' : 'text-destructive'
                )}>
                  {trend === 'up' ? (
                    <ArrowUp className="h-3 w-3 mr-0.5" />
                  ) : (
                    <ArrowDown className="h-3 w-3 mr-0.5" />
                  )}
                  {trendValue}
                </span>
              )}
            </div>
          </div>
          <div className={cn(
            'p-3 rounded-xl',
            colorClasses[color]
          )}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Activity Item Component
const ActivityItem = ({ 
  title, 
  description, 
  time, 
  type 
}: {
  title: string;
  description: string;
  time: string;
  type: 'beneficiary' | 'program' | 'evaluation';
}) => {
  const typeConfig = {
    beneficiary: { icon: Users, color: 'text-primary' },
    program: { icon: BookOpen, color: 'text-success' },
    evaluation: { icon: ClipboardCheck, color: 'text-warning' },
  };

  const { icon: Icon, color } = typeConfig[type];

  return (
    <div className="flex space-x-3 pb-4 last:pb-0">
      <div className={cn('p-2 rounded-full bg-muted', color)}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 space-y-1">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
        <p className="text-xs text-muted-foreground">{time}</p>
      </div>
    </div>
  );
};

export default function Dashboard() {
  const { data: statsData, isLoading: beneficiaryStatsLoading } = useBeneficiaryStatistics();
  const { stats, activities, events, isLoading: dashboardLoading, refetch } = useDashboardData();
  
  const isLoading = beneficiaryStatsLoading || dashboardLoading;
  
  // Use real data from API, fallback to beneficiary stats for backward compatibility
  const recentActivities = activities || [];
  const upcomingEvents = events || [];

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's an overview of your development center.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Beneficiaries"
          value={stats?.total_beneficiaries || statsData?.data.statistics?.total || 0}
          icon={Users}
          trend="up"
          trendValue={stats?.beneficiary_growth || "12%"}
          color="primary"
        />
        <StatCard
          title="Active Programs"
          value={stats?.active_programs || 8}
          icon={BookOpen}
          trend="up"
          trendValue={stats?.program_growth || "2"}
          color="success"
        />
        <StatCard
          title="Evaluations"
          value={stats?.completed_evaluations || 45}
          icon={ClipboardCheck}
          trend="up"
          trendValue={stats?.evaluation_growth || "8%"}
          color="warning"
        />
        <StatCard
          title="Success Rate"
          value={`${stats?.completion_rate || 87}%`}
          icon={TrendingUp}
          trend="up"
          trendValue={stats?.completion_growth || "3%"}
          color="info"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Performance Overview */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Performance Overview</CardTitle>
            <CardDescription>
              Track the progress and success metrics across all programs
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Target className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Program Completion Rate</span>
                  </div>
                  <span className="text-sm font-medium">78%</span>
                </div>
                <Progress value={78} className="h-2" />
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Award className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Skill Certification Rate</span>
                  </div>
                  <span className="text-sm font-medium">92%</span>
                </div>
                <Progress value={92} className="h-2" />
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Active Engagement</span>
                  </div>
                  <span className="text-sm font-medium">85%</span>
                </div>
                <Progress value={85} className="h-2" />
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t">
              <div className="text-center">
                <p className="text-2xl font-bold">156</p>
                <p className="text-xs text-muted-foreground">Certificates Issued</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">89%</p>
                <p className="text-xs text-muted-foreground">Job Placement</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">4.8</p>
                <p className="text-xs text-muted-foreground">Avg. Rating</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest updates from your center</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <ActivityItem key={activity.id} {...activity} />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Section */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and operations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              <Button variant="outline" className="justify-start" leftIcon={<Plus className="h-4 w-4" />}>
                Add Beneficiary
              </Button>
              <Button variant="outline" className="justify-start" leftIcon={<BookOpen className="h-4 w-4" />}>
                Create Program
              </Button>
              <Button variant="outline" className="justify-start" leftIcon={<Calendar className="h-4 w-4" />}>
                Schedule Event
              </Button>
              <Button variant="outline" className="justify-start" leftIcon={<ClipboardCheck className="h-4 w-4" />}>
                New Evaluation
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Upcoming Events */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Upcoming Events</CardTitle>
              <CardDescription>Scheduled programs and activities</CardDescription>
            </div>
            <Button variant="ghost" size="sm">
              View all
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {upcomingEvents.map((event) => (
                <div key={event.id} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{event.title}</p>
                    <p className="text-xs text-muted-foreground">{event.date}</p>
                  </div>
                  <Badge variant="secondary">
                    {event.participants} participants
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights */}
      <Card className="border-primary/20 bg-gradient-to-r from-primary/5 to-primary/10">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle>AI Insights</CardTitle>
          </div>
          <CardDescription>
            Intelligent recommendations based on your center's performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <p className="text-sm font-medium">Recommendation</p>
              <p className="text-xs text-muted-foreground">
                Consider increasing capacity for the Web Development program - 95% completion rate with high demand.
              </p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Optimization</p>
              <p className="text-xs text-muted-foreground">
                Schedule Python workshops on Tuesdays for 23% better attendance based on historical data.
              </p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Alert</p>
              <p className="text-xs text-muted-foreground">
                3 beneficiaries in Data Analytics need additional support - engagement dropped below 60%.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}