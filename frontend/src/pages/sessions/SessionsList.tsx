/**
 * Sessions List Page
 * Shows all upcoming sessions/appointments for the user
 */

import { Calendar, Clock, MapPin, Globe, User, BookOpen, Filter } from 'lucide-react';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';

import { Badge } from '../../components/ui/Badge';
import { CalendarButton } from '../../components/ui/CalendarButton';
import { Card } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Form';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { useSessions } from '../../hooks/useSessions';
import type { CourseSession } from '../../types/course';
import { formatSessionDateTime, isSessionPast } from '../../utils/calendar';

interface SessionWithCourse extends CourseSession {
  course?: {
    id: number;
    title: string;
    code: string;
    program_id: number;
  };
}

export const SessionsList: React.FC = () => {
  const { user } = useAuth();
  const [showPast, setShowPast] = useState(false);
  const [filterInstructor, setFilterInstructor] = useState<number | null>(null);

  // This hook would need to be created to fetch all sessions
  const {
    data: sessions,
    isLoading,
    error,
  } = useSessions({
    include_past: showPast,
    instructor_id: filterInstructor,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">Oturumlar yüklenirken hata oluştu.</div>
      </Card>
    );
  }

  const upcomingSessions = sessions?.filter((s: SessionWithCourse) => !isSessionPast(s)) || [];
  const pastSessions = sessions?.filter((s: SessionWithCourse) => isSessionPast(s)) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Oturumlar</h1>
          <p className="text-gray-600">Tüm kurs oturumlarınızı görüntüleyin</p>
        </div>
        <div className="flex items-center gap-4">
          <Button
            variant={showPast ? 'outline' : 'primary'}
            size="sm"
            onClick={() => setShowPast(!showPast)}
          >
            <Filter className="h-4 w-4 mr-2" />
            {showPast ? 'Tümünü Göster' : 'Sadece Gelecek'}
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Calendar className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{upcomingSessions.length}</div>
              <div className="text-sm text-gray-600">Gelecek Oturum</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Clock className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {upcomingSessions.length > 0
                  ? Math.ceil(
                      (new Date(upcomingSessions[0].session_date).getTime() - Date.now()) /
                        (1000 * 60 * 60 * 24)
                    )
                  : '-'}
              </div>
              <div className="text-sm text-gray-600">Sonraki Oturuma Gün</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BookOpen className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {new Set(sessions?.map((s: SessionWithCourse) => s.course?.id)).size}
              </div>
              <div className="text-sm text-gray-600">Farklı Kurs</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Sessions List */}
      {upcomingSessions.length === 0 && !showPast ? (
        <EmptyState
          icon={Calendar}
          title="Yaklaşan oturum yok"
          description="Henüz planlanmış bir oturumunuz bulunmuyor."
        />
      ) : (
        <div className="space-y-4">
          {/* Upcoming Sessions */}
          {upcomingSessions.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold mb-4">Yaklaşan Oturumlar</h2>
              <div className="grid grid-cols-1 gap-4">
                {upcomingSessions.map((session: SessionWithCourse) => (
                  <SessionCard key={session.id} session={session} isPast={false} />
                ))}
              </div>
            </div>
          )}

          {/* Past Sessions */}
          {showPast && pastSessions.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold mb-4 text-gray-600">Geçmiş Oturumlar</h2>
              <div className="grid grid-cols-1 gap-4">
                {pastSessions.map((session: SessionWithCourse) => (
                  <SessionCard key={session.id} session={session} isPast={true} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Session Card Component
const SessionCard: React.FC<{
  session: SessionWithCourse;
  isPast: boolean;
}> = ({ session, isPast }) => {
  return (
    <Card className={`p-6 ${isPast ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold mb-1">{session.title}</h3>
              {session.course && (
                <Link
                  to={`/courses/${session.course.id}`}
                  className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block"
                >
                  {session.course.title} ({session.course.code})
                </Link>
              )}

              <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{formatSessionDateTime(session)}</span>
                </div>

                {session.is_online ? (
                  <div className="flex items-center gap-1">
                    <Globe className="h-4 w-4" />
                    <span>Online</span>
                  </div>
                ) : (
                  session.location && (
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      <span>{session.location}</span>
                      {session.room_number && ` - ${session.room_number}`}
                    </div>
                  )
                )}

                {session.instructor_name && (
                  <div className="flex items-center gap-1">
                    <User className="h-4 w-4" />
                    <span>{session.instructor_name}</span>
                  </div>
                )}
              </div>

              {session.description && (
                <p className="text-sm text-gray-600 mb-3">{session.description}</p>
              )}

              <div className="flex items-center gap-2">
                {session.is_cancelled ? (
                  <Badge color="red">İptal Edildi</Badge>
                ) : isPast ? (
                  <Badge color="gray">Tamamlandı</Badge>
                ) : (
                  <Badge color="green">Yaklaşıyor</Badge>
                )}

                {!session.is_mandatory && <Badge variant="outline">Opsiyonel</Badge>}
              </div>
            </div>
          </div>
        </div>

        {!isPast && !session.is_cancelled && session.course && (
          <CalendarButton
            session={session}
            courseTitle={session.course.title}
            programId={session.course.program_id}
            courseId={session.course.id}
            variant="outline"
          />
        )}
      </div>

      {/* Online Link */}
      {session.is_online && session.online_link && !isPast && !session.is_cancelled && (
        <div className="mt-4 pt-4 border-t">
          <a
            href={session.online_link}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800"
          >
            <Globe className="h-4 w-4" />
            Oturuma Katıl
          </a>
        </div>
      )}
    </Card>
  );
};

export default SessionsList;
