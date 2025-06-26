import { CheckCircle, Clock, Target, TrendingUp, Filter, Search, Eye, Calendar, User } from 'lucide-react';
import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input, Select } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAuth } from '@/contexts/AuthContext';
import { useMyLearningPaths } from '@/hooks/useLearningPath';
import { LearningPathStatus } from '@/types/learning-path';

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'proposed', label: 'Proposed' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

const getStatusColor = (status: LearningPathStatus): string => {
  switch (status) {
    case 'draft':
      return 'gray';
    case 'proposed':
      return 'blue';
    case 'accepted':
      return 'green';
    case 'in_progress':
      return 'orange';
    case 'completed':
      return 'green';
    case 'cancelled':
      return 'red';
    default:
      return 'gray';
  }
};

const getStatusIcon = (status: LearningPathStatus) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-4 w-4" />;
    case 'in_progress':
      return <Clock className="h-4 w-4" />;
    case 'proposed':
      return <Target className="h-4 w-4" />;
    default:
      return <TrendingUp className="h-4 w-4" />;
  }
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export default function LearningPathsList() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || '');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');

  // Fetch learning paths with filters
  const { data: learningPathsData, isLoading, error } = useMyLearningPaths({
    status: statusFilter as LearningPathStatus,
  });

  const learningPaths = learningPathsData?.learning_paths || [];

  // Filter paths by search term
  const filteredPaths = learningPaths.filter(path =>
    path.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    path.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Update URL params when filters change
  const updateFilters = (newSearchTerm?: string, newStatus?: string) => {
    const params = new URLSearchParams();
    
    if (newSearchTerm !== undefined ? newSearchTerm : searchTerm) {
      params.set('search', newSearchTerm !== undefined ? newSearchTerm : searchTerm);
    }
    
    if (newStatus !== undefined ? newStatus : statusFilter) {
      params.set('status', newStatus !== undefined ? newStatus : statusFilter);
    }
    
    setSearchParams(params);
  };

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    updateFilters(value, undefined);
  };

  const handleStatusChange = (value: string) => {
    setStatusFilter(value);
    updateFilters(undefined, value);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
    setSearchParams({});
  };

  // Calculate summary statistics
  const stats = {
    total: learningPaths.length,
    inProgress: learningPaths.filter(p => p.status === 'in_progress').length,
    completed: learningPaths.filter(p => p.status === 'completed').length,
    proposed: learningPaths.filter(p => p.status === 'proposed').length,
  };

  if (error) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6">
          <div className="text-center text-red-600">
            <p>Failed to load learning paths. Please try again later.</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Learning Paths</h1>
          <p className="text-gray-600">
            Discover and track your personalized learning journey
          </p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Target className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Paths</p>
              <p className="text-xl font-semibold">{stats.total}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Clock className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="text-xl font-semibold">{stats.inProgress}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-xl font-semibold">{stats.completed}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Proposed</p>
              <p className="text-xl font-semibold">{stats.proposed}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search learning paths..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          
          <div className="w-full md:w-48">
            <Select
              value={statusFilter}
              onChange={(e) => handleStatusChange(e.target.value)}
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          </div>

          {(searchTerm || statusFilter) && (
            <Button variant="outline" onClick={clearFilters}>
              <Filter className="h-4 w-4 mr-2" />
              Clear Filters
            </Button>
          )}
        </div>
      </Card>

      {/* Learning Paths List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredPaths.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <Target className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {learningPaths.length === 0 ? 'No Learning Paths Yet' : 'No Matching Learning Paths'}
            </h3>
            <p className="text-gray-600 mb-6">
              {learningPaths.length === 0
                ? 'Complete an evaluation to get personalized learning path recommendations.'
                : 'Try adjusting your search terms or filters to find what you\'re looking for.'}
            </p>
            {learningPaths.length === 0 && (
              <Button asChild>
                <Link to="/evaluations">
                  <Target className="h-4 w-4 mr-2" />
                  Take an Evaluation
                </Link>
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredPaths.map((path) => (
            <Card key={path.id} className="p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {path.title}
                    </h3>
                    <Badge
                      variant={getStatusColor(path.status) as any}
                      className="flex items-center space-x-1"
                    >
                      {getStatusIcon(path.status)}
                      <span>{path.status.replace('_', ' ')}</span>
                    </Badge>
                  </div>

                  {path.description && (
                    <p className="text-gray-600 mb-4 line-clamp-2">
                      {path.description}
                    </p>
                  )}

                  <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-4">
                    <div className="flex items-center space-x-1">
                      <Target className="h-4 w-4" />
                      <span>{path.total_milestones || 0} milestones</span>
                    </div>
                    
                    {path.duration_weeks && (
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-4 w-4" />
                        <span>{path.duration_weeks} weeks</span>
                      </div>
                    )}

                    <div className="flex items-center space-x-1">
                      <User className="h-4 w-4" />
                      <span>Created {formatDate(path.created_at)}</span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {path.status === 'in_progress' && path.completed_milestones !== undefined && path.total_milestones && (
                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600">Progress</span>
                        <span className="text-gray-900 font-medium">
                          {path.completed_milestones}/{path.total_milestones} milestones
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{
                            width: `${(path.completed_milestones / path.total_milestones) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Resources and Skills */}
                  <div className="flex flex-wrap gap-2">
                    {path.target_skills?.slice(0, 3).map((skill, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {path.target_skills && path.target_skills.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{path.target_skills.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex space-x-2 ml-4">
                  <Button asChild variant="outline" size="sm">
                    <Link to={`/learning-paths/${path.id}`}>
                      <Eye className="h-4 w-4 mr-2" />
                      View
                    </Link>
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Results Summary */}
      {!isLoading && filteredPaths.length > 0 && (
        <div className="text-center text-sm text-gray-500">
          Showing {filteredPaths.length} of {learningPaths.length} learning paths
        </div>
      )}
    </div>
  );
}