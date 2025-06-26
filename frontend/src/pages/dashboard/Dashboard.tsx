import { Users, BookOpen, ClipboardCheck, TrendingUp } from 'lucide-react';

import { useBeneficiaryStatistics } from '@/hooks/useBeneficiaries';

export default function Dashboard() {
  const { data: statsData, isLoading } = useBeneficiaryStatistics();
  const stats = statsData?.data.statistics;

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Beneficiaries</p>
              <p className="text-2xl font-bold">{stats?.total || 0}</p>
            </div>
            <Users className="h-8 w-8 text-primary" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Programs</p>
              <p className="text-2xl font-bold">0</p>
            </div>
            <BookOpen className="h-8 w-8 text-primary" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Evaluations</p>
              <p className="text-2xl font-bold">0</p>
            </div>
            <ClipboardCheck className="h-8 w-8 text-primary" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold">0%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-primary" />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border rounded-lg hover:bg-gray-50">
            Add New Beneficiary
          </button>
          <button className="p-4 border rounded-lg hover:bg-gray-50">
            Create Program
          </button>
          <button className="p-4 border rounded-lg hover:bg-gray-50">
            Schedule Evaluation
          </button>
        </div>
      </div>
    </div>
  );
}
