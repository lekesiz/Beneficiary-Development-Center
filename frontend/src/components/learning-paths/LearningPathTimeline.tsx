import { Calendar, Clock, CheckCircle, Circle, Lock } from 'lucide-react';
import * as React from 'react';

import type { WeeklySchedule, LearningMilestone } from '@/types/learning-path';

interface LearningPathTimelineProps {
  weeklySchedule: WeeklySchedule;
  milestones: LearningMilestone[];
  startDate?: string;
}

export const LearningPathTimeline: React.FC<LearningPathTimelineProps> = ({
  weeklySchedule,
  milestones,
  startDate,
}) => {
  const weeks = Object.keys(weeklySchedule).sort();
  const days = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
  ];
  const dayNames = {
    monday: 'Pazartesi',
    tuesday: 'Salı',
    wednesday: 'Çarşamba',
    thursday: 'Perşembe',
    friday: 'Cuma',
    saturday: 'Cumartesi',
    sunday: 'Pazar',
  };

  // Group milestones by week
  const milestonesByWeek = milestones.reduce((acc, milestone) => {
    const weekKey = `week_${milestone.week_number}`;
    if (!acc[weekKey]) acc[weekKey] = [];
    acc[weekKey].push(milestone);
    return acc;
  }, {} as Record<string, LearningMilestone[]>);

  // Get week start date
  const getWeekStartDate = (weekNumber: number) => {
    if (!startDate) return null;
    const start = new Date(startDate);
    start.setDate(start.getDate() + (weekNumber - 1) * 7);
    return start;
  };

  return (
    <div className="space-y-6">
      {weeks.map((weekKey, weekIndex) => {
        const weekNumber = parseInt(weekKey.split('_')[1]);
        const weekStart = getWeekStartDate(weekNumber);
        const weekMilestones = milestonesByWeek[weekKey] || [];
        const isCurrentWeek = false; // This would be calculated based on current date
        const isPastWeek = false; // This would be calculated based on current date

        return (
          <div key={weekKey} className="relative">
            {/* Week Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div
                  className={`
                  w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
                  ${
                    isPastWeek
                      ? 'bg-green-100 text-green-700'
                      : isCurrentWeek
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700'
                  }
                `}
                >
                  {weekNumber}
                </div>
                <div>
                  <h4 className="font-semibold">Hafta {weekNumber}</h4>
                  {weekStart && (
                    <p className="text-sm text-gray-600">
                      {weekStart.toLocaleDateString('tr-TR', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                      })}{' '}
                      başlangıç
                    </p>
                  )}
                </div>
              </div>

              {/* Week Status */}
              <div className="flex items-center space-x-2">
                {weekMilestones.map((milestone) => (
                  <div
                    key={milestone.id}
                    className={`
                      px-3 py-1 rounded-full text-xs font-medium
                      ${
                        milestone.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : milestone.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-700'
                      }
                    `}
                  >
                    {milestone.title.length > 20
                      ? milestone.title.substring(0, 20) + '...'
                      : milestone.title}
                  </div>
                ))}
              </div>
            </div>

            {/* Weekly Schedule Grid */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="grid grid-cols-7 gap-2">
                {days.map((day) => {
                  const daySchedule = weeklySchedule[weekKey]?.[day];
                  const hasActivities =
                    daySchedule && daySchedule.activities.length > 0;

                  return (
                    <div
                      key={day}
                      className={`
                        p-3 rounded-md text-center
                        ${
                          hasActivities
                            ? 'bg-white border border-gray-200'
                            : 'bg-gray-100'
                        }
                      `}
                    >
                      <p className="text-xs font-medium text-gray-700 mb-1">
                        {dayNames[day as keyof typeof dayNames]}
                      </p>

                      {hasActivities ? (
                        <div className="space-y-1">
                          <Clock className="h-4 w-4 mx-auto text-blue-600" />
                          <p className="text-xs text-gray-600">
                            {daySchedule.duration}
                          </p>
                          <div className="mt-2">
                            {daySchedule.activities.map((activity, index) => (
                              <p
                                key={index}
                                className="text-xs text-gray-700 truncate"
                              >
                                {activity}
                              </p>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="py-4">
                          <Circle className="h-4 w-4 mx-auto text-gray-400" />
                          <p className="text-xs text-gray-400 mt-1">Boş</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Week Summary */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-gray-500" />
                    <span className="text-gray-600">
                      Toplam:{' '}
                      {
                        Object.values(weeklySchedule[weekKey] || {}).filter(
                          (d) => d.activities.length > 0
                        ).length
                      }{' '}
                      gün aktif
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span className="text-gray-600">
                      ~
                      {weekMilestones.reduce(
                        (sum, m) => sum + m.estimated_hours,
                        0
                      )}{' '}
                      saat
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Connecting Line (except for last week) */}
            {weekIndex < weeks.length - 1 && (
              <div className="absolute left-5 top-14 bottom-0 w-0.5 bg-gray-300" />
            )}
          </div>
        );
      })}
    </div>
  );
};
