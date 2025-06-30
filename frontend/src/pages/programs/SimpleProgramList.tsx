import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Eye, Edit, Trash2, BookOpen, Calendar, Users, Clock } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const mockPrograms = [
  {
    id: 1,
    title: 'Digital Literacy Training',
    description: 'Basic computer skills and internet usage',
    status: 'active',
    startDate: '2024-02-01',
    endDate: '2024-04-30',
    participants: 25,
    coordinator: 'Jane Smith',
    category: 'Technology',
  },
  {
    id: 2,
    title: 'Entrepreneurship Bootcamp',
    description: 'Business skills and startup fundamentals',
    status: 'upcoming',
    startDate: '2024-03-15',
    endDate: '2024-05-15',
    participants: 30,
    coordinator: 'Mike Wilson',
    category: 'Business',
  },
  {
    id: 3,
    title: 'Language Skills Development',
    description: 'English language proficiency program',
    status: 'completed',
    startDate: '2023-09-01',
    endDate: '2023-12-20',
    participants: 20,
    coordinator: 'Sarah Johnson',
    category: 'Education',
  },
];

export default function SimpleProgramList() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const canCreate = user?.primaryRole === 'admin' || user?.primaryRole === 'trainer';
  const canEdit = user?.primaryRole === 'admin' || user?.primaryRole === 'trainer';
  const canDelete = user?.primaryRole === 'admin';

  const filteredPrograms = mockPrograms.filter(program => {
    const matchesSearch = program.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         program.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || program.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const statusColors = {
    active: 'bg-green-100 text-green-800 border-green-200',
    upcoming: 'bg-blue-100 text-blue-800 border-blue-200',
    completed: 'bg-gray-100 text-gray-800 border-gray-200',
    cancelled: 'bg-red-100 text-red-800 border-red-200',
  };

  const categoryColors = {
    Technology: 'bg-purple-100 text-purple-800',
    Business: 'bg-indigo-100 text-indigo-800',
    Education: 'bg-yellow-100 text-yellow-800',
    Health: 'bg-pink-100 text-pink-800',
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Programs</h1>
          <p className="text-gray-600">Manage training and development programs</p>
        </div>
        
        {canCreate && (
          <button
            onClick={() => navigate('/programs/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Create Program
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search programs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="upcoming">Upcoming</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {/* Programs Grid */}
      {filteredPrograms.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No programs found</h3>
          <p className="text-gray-500 mb-6">
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your filters'
              : 'Get started by creating your first program'}
          </p>
          {canCreate && !searchTerm && statusFilter === 'all' && (
            <button
              onClick={() => navigate('/programs/new')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create First Program
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPrograms.map((program) => (
            <div
              key={program.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              {/* Program Header */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {program.title}
                    </h3>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {program.description}
                    </p>
                  </div>
                  <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full border ${statusColors[program.status as keyof typeof statusColors]}`}>
                    {program.status}
                  </span>
                </div>

                {/* Program Details */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span>{program.startDate} - {program.endDate}</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="h-4 w-4 mr-2" />
                    <span>{program.participants} participants</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="h-4 w-4 mr-2" />
                    <span>Coordinator: {program.coordinator}</span>
                  </div>
                </div>

                {/* Category Tag */}
                <div className="mb-4">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${categoryColors[program.category as keyof typeof categoryColors]}`}>
                    {program.category}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => navigate(`/programs/${program.id}`)}
                    className="flex-1 px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    View Details
                  </button>
                  
                  {canEdit && (
                    <button
                      onClick={() => navigate(`/programs/${program.id}/edit`)}
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                      title="Edit"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                  )}
                  
                  {canDelete && (
                    <button
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this program?')) {
                          console.log('Delete program:', program.id);
                        }
                      }}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600">Total Programs</p>
          <p className="text-2xl font-bold text-gray-900">{mockPrograms.length}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600">Active Programs</p>
          <p className="text-2xl font-bold text-green-600">
            {mockPrograms.filter(p => p.status === 'active').length}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600">Total Participants</p>
          <p className="text-2xl font-bold text-blue-600">
            {mockPrograms.reduce((sum, p) => sum + p.participants, 0)}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600">Completion Rate</p>
          <p className="text-2xl font-bold text-purple-600">85%</p>
        </div>
      </div>

      {/* Development Notice */}
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>Note:</strong> This is a simplified view with mock data. Full API integration will be enabled once authentication is configured.
        </p>
      </div>
    </div>
  );
}