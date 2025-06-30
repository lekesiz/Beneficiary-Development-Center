import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Eye, Edit, Trash2, Users, Search, Filter } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

// Mock data for testing
const mockBeneficiaries = [
  {
    id: 1,
    full_name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+90 555 123 4567',
    status: 'active',
    assigned_trainer: 'Jane Smith',
    created_at: '2024-01-15',
    tags: ['New', 'Priority'],
  },
  {
    id: 2,
    full_name: 'Sarah Johnson',
    email: 'sarah.j@example.com',
    phone: '+90 555 234 5678',
    status: 'inactive',
    assigned_trainer: 'Mike Wilson',
    created_at: '2024-01-10',
    tags: ['Follow-up'],
  },
  {
    id: 3,
    full_name: 'Ahmed Hassan',
    email: 'ahmed.h@example.com',
    phone: '+90 555 345 6789',
    status: 'active',
    assigned_trainer: 'Jane Smith',
    created_at: '2024-01-08',
    tags: ['Active', 'Training'],
  },
];

export default function SimpleBeneficiaryList() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const canCreate = user?.primaryRole === 'admin' || user?.primaryRole === 'trainer';
  const canEdit = user?.primaryRole === 'admin' || user?.primaryRole === 'trainer';
  const canDelete = user?.primaryRole === 'admin';

  const filteredBeneficiaries = mockBeneficiaries.filter(beneficiary => {
    const matchesSearch = beneficiary.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         beneficiary.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || beneficiary.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const statusColors = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    completed: 'bg-blue-100 text-blue-800',
    suspended: 'bg-red-100 text-red-800',
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Beneficiaries</h1>
          <p className="text-gray-600">Manage and track your beneficiaries</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Export
          </button>
          
          {canCreate && (
            <button
              onClick={() => navigate('/beneficiaries/new')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Beneficiary
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search beneficiaries..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="completed">Completed</option>
          <option value="suspended">Suspended</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredBeneficiaries.length === 0 ? (
          <div className="p-12 text-center">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No beneficiaries found</h3>
            <p className="text-gray-500 mb-6">
              {searchTerm || statusFilter !== 'all' 
                ? 'Try adjusting your filters'
                : 'Get started by adding your first beneficiary'}
            </p>
            {canCreate && !searchTerm && statusFilter === 'all' && (
              <button
                onClick={() => navigate('/beneficiaries/new')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add First Beneficiary
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trainer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tags
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredBeneficiaries.map((beneficiary) => (
                  <tr key={beneficiary.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{beneficiary.full_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{beneficiary.email}</div>
                      <div className="text-sm text-gray-500">{beneficiary.phone}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusColors[beneficiary.status as keyof typeof statusColors]}`}>
                        {beneficiary.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {beneficiary.assigned_trainer}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex gap-1">
                        {beneficiary.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {beneficiary.created_at}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => navigate(`/beneficiaries/${beneficiary.id}`)}
                          className="text-gray-600 hover:text-gray-900"
                          title="View details"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        
                        {canEdit && (
                          <button
                            onClick={() => navigate(`/beneficiaries/${beneficiary.id}/edit`)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                        )}
                        
                        {canDelete && (
                          <button
                            onClick={() => {
                              if (confirm('Are you sure you want to delete this beneficiary?')) {
                                console.log('Delete beneficiary:', beneficiary.id);
                              }
                            }}
                            className="text-red-600 hover:text-red-900"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Development Notice */}
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>Note:</strong> This is a simplified view with mock data. API integration will be enabled once JWT authentication is properly configured.
        </p>
      </div>
    </div>
  );
}