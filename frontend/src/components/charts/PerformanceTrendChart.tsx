import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface PerformanceTrendData {
  week: string;
  score: number | null;
  attempts: number;
}

interface PerformanceTrendChartProps {
  data: PerformanceTrendData[];
}

export default function PerformanceTrendChart({ data }: PerformanceTrendChartProps) {
  // Filter out weeks with no data and prepare for display
  const chartData = data.map(item => ({
    ...item,
    score: item.score ?? 0,
    hasData: item.score !== null
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          {data.hasData ? (
            <>
              <p className="text-sm text-blue-600">Puan: {data.score.toFixed(1)}%</p>
              <p className="text-sm text-gray-600">Deneme: {data.attempts}</p>
            </>
          ) : (
            <p className="text-sm text-gray-500">Veri yok</p>
          )}
        </div>
      );
    }
    return null;
  };

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    
    if (!payload.hasData) {
      return null;
    }
    
    return (
      <circle 
        cx={cx} 
        cy={cy} 
        r={4} 
        fill="#3B82F6" 
        stroke="#fff" 
        strokeWidth={2}
      />
    );
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            dataKey="week" 
            tick={{ fontSize: 12 }}
            stroke="#6B7280"
          />
          <YAxis 
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            stroke="#6B7280"
            label={{ 
              value: 'Performans (%)', 
              angle: -90, 
              position: 'insideLeft',
              style: { fontSize: 12, fill: '#6B7280' }
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={<CustomDot />}
            connectNulls={false}
            name="Performans"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}