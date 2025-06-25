import * as React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface SkillData {
  skill: string;
  total_focus: number;
  completed: number;
  in_progress: number;
  average_progress: number;
  mastery_level: string;
}

interface SkillDistributionChartProps {
  data: SkillData[];
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: SkillData;
  }>;
  label?: string;
}

interface BarProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  payload?: SkillData;
}

export default function SkillDistributionChart({
  data,
}: SkillDistributionChartProps) {
  // Take top 8 skills
  const chartData = data.slice(0, 8);

  const getMasteryColor = (level: string) => {
    switch (level) {
      case 'Expert':
        return '#10B981';
      case 'Proficient':
        return '#3B82F6';
      case 'Intermediate':
        return '#F59E0B';
      case 'Beginner':
        return '#6B7280';
      case 'Novice':
        return '#EF4444';
      default:
        return '#9CA3AF';
    }
  };

  const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          <p className="text-sm text-gray-600">
            Toplam Odak: {data.total_focus}
          </p>
          <p className="text-sm text-green-600">Tamamlanan: {data.completed}</p>
          <p className="text-sm text-yellow-600">
            Devam Eden: {data.in_progress}
          </p>
          <p className="text-sm text-blue-600">
            Ortalama İlerleme: {data.average_progress}%
          </p>
          <p className="text-sm font-medium mt-1">
            Ustalık:{' '}
            <span style={{ color: getMasteryColor(data.mastery_level) }}>
              {data.mastery_level}
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  const CustomBar = (props: BarProps) => {
    const { x, y, width, height, payload } = props;
    const color = getMasteryColor(payload.mastery_level);

    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={color}
          opacity={0.8}
        />
      </g>
    );
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="skill"
            tick={{ fontSize: 12 }}
            stroke="#6B7280"
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#6B7280"
            label={{
              value: 'İlerleme (%)',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12, fill: '#6B7280' },
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="average_progress"
            shape={<CustomBar />}
            name="Ortalama İlerleme"
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-3 mt-4">
        <div className="flex items-center text-xs">
          <div
            className="w-3 h-3 rounded mr-1"
            style={{ backgroundColor: '#10B981' }}
          />
          <span>Expert</span>
        </div>
        <div className="flex items-center text-xs">
          <div
            className="w-3 h-3 rounded mr-1"
            style={{ backgroundColor: '#3B82F6' }}
          />
          <span>Proficient</span>
        </div>
        <div className="flex items-center text-xs">
          <div
            className="w-3 h-3 rounded mr-1"
            style={{ backgroundColor: '#F59E0B' }}
          />
          <span>Intermediate</span>
        </div>
        <div className="flex items-center text-xs">
          <div
            className="w-3 h-3 rounded mr-1"
            style={{ backgroundColor: '#6B7280' }}
          />
          <span>Beginner</span>
        </div>
        <div className="flex items-center text-xs">
          <div
            className="w-3 h-3 rounded mr-1"
            style={{ backgroundColor: '#EF4444' }}
          />
          <span>Novice</span>
        </div>
      </div>
    </div>
  );
}
