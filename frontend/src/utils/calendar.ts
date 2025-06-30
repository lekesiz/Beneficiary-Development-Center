/**
 * Calendar utilities for handling calendar downloads
 */

import type { CourseSession } from '../types/course';

/**
 * Download calendar file for a session
 * @param session - The session to download calendar for
 * @param courseTitle - The course title
 * @param programId - The program ID
 * @param courseId - The course ID
 */
export const downloadSessionCalendar = async (
  session: CourseSession,
  courseTitle: string,
  programId: number,
  courseId: number
) => {
  try {
    // Get user's timezone
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Construct the download URL
    const url = `/api/v1/programs/${programId}/courses/${courseId}/sessions/${
      session.id
    }/calendar?timezone=${encodeURIComponent(timezone)}`;

    // Create a temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = `session_${session.uuid || session.id}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error downloading calendar file:', error);
    throw new Error('Failed to download calendar file');
  }
};

/**
 * Open session in user's default calendar app (for web-based calendars)
 * @param session - The session to add to calendar
 * @param courseTitle - The course title
 */
export const openInCalendar = (
  session: CourseSession,
  courseTitle: string,
  calendarType: 'google' | 'outlook' | 'apple'
) => {
  const title = encodeURIComponent(`${courseTitle}: ${session.title}`);
  const details = encodeURIComponent(session.description || '');
  const location = encodeURIComponent(
    session.is_online ? session.online_link || 'Online' : session.location || ''
  );

  // Parse session date
  const startDate = new Date(session.session_date);
  const endDate = new Date(startDate.getTime() + session.duration_hours * 60 * 60 * 1000);

  // Format dates for calendar URLs
  const formatDateForGoogle = (date: Date) => {
    return date
      .toISOString()
      .replace(/[-:]/g, '')
      .replace(/\.\d{3}/, '');
  };

  const formatDateForOutlook = (date: Date) => {
    return date.toISOString();
  };

  let url = '';

  switch (calendarType) {
    case 'google':
      // Google Calendar URL format
      url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${formatDateForGoogle(
        startDate
      )}/${formatDateForGoogle(endDate)}&details=${details}&location=${location}`;
      break;

    case 'outlook':
      // Outlook Web Calendar URL format
      url = `https://outlook.live.com/calendar/0/deeplink/compose?subject=${title}&startdt=${formatDateForOutlook(
        startDate
      )}&enddt=${formatDateForOutlook(endDate)}&body=${details}&location=${location}`;
      break;

    case 'apple':
      // For Apple Calendar, we'll download the ICS file instead
      // as there's no direct web URL for Apple Calendar
      return downloadSessionCalendar(session, courseTitle, 0, 0);
  }

  if (url) {
    window.open(url, '_blank');
  }
};

/**
 * Check if a session is in the past
 * @param session - The session to check
 * @returns boolean indicating if the session is in the past
 */
export const isSessionPast = (session: CourseSession): boolean => {
  const sessionDate = new Date(session.session_date);
  const now = new Date();
  return sessionDate < now;
};

/**
 * Format session date and time for display
 * @param session - The session to format
 * @returns Formatted date and time string
 */
export const formatSessionDateTime = (session: CourseSession): string => {
  const date = new Date(session.session_date);
  const endDate = new Date(date.getTime() + session.duration_hours * 60 * 60 * 1000);

  const dateStr = date.toLocaleDateString('tr-TR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const timeStr = `${date.toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit',
  })} - ${endDate.toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit',
  })}`;

  return `${dateStr}, ${timeStr}`;
};
