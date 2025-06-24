import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/Form';
import { DevelopmentReport } from '@/components/reports/DevelopmentReport';
import { useAuth } from '@/contexts/AuthContext';

export default function MyDevelopmentReport() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [dateRange, setDateRange] = useState(30);
  
  if (!user) {
    return null;
  }
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">Gelişim Raporum</h1>
            <p className="text-gray-600">Kişisel performans ve öğrenme analizi</p>
          </div>
        </div>
        
        {/* Date Range Selector */}
        <div className="flex items-center space-x-2">
          <Calendar className="h-5 w-5 text-gray-500" />
          <select
            value={dateRange}
            onChange={(e) => setDateRange(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>Son 7 gün</option>
            <option value={30}>Son 30 gün</option>
            <option value={60}>Son 60 gün</option>
            <option value={90}>Son 90 gün</option>
          </select>
        </div>
      </div>
      
      {/* Development Report Component */}
      <DevelopmentReport
        userId={user.id}
        userName={`${user.first_name} ${user.last_name}`}
        dateRange={dateRange}
      />
    </div>
  );
}