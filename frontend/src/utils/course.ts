/**
 * Course utility functions
 */
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

import {
  COURSE_STATUS_OPTIONS,
  COURSE_FORMAT_OPTIONS,
  DIFFICULTY_LEVEL_OPTIONS,
  ASSESSMENT_TYPE_OPTIONS,
} from '../constants/course';
import type { Course, CourseStatus, DifficultyLevel } from '../types/course';

/**
 * Get course status display information
 */
export const getCourseStatusInfo = (status: CourseStatus) => {
  return (
    COURSE_STATUS_OPTIONS.find((option) => option.value === status) || {
      value: status,
      label: status,
      color: 'gray',
    }
  );
};

/**
 * Get course format display information
 */
export const getCourseFormatInfo = (format: string) => {
  return (
    COURSE_FORMAT_OPTIONS.find((option) => option.value === format) || {
      value: format,
      label: format,
      icon: '📋',
    }
  );
};

/**
 * Get difficulty level display information
 */
export const getDifficultyLevelInfo = (level: DifficultyLevel) => {
  return (
    DIFFICULTY_LEVEL_OPTIONS.find((option) => option.value === level) || {
      value: level,
      label: level,
      color: 'gray',
      order: 0,
    }
  );
};

/**
 * Get assessment type display information
 */
export const getAssessmentTypeInfo = (type: string) => {
  return (
    ASSESSMENT_TYPE_OPTIONS.find((option) => option.value === type) || {
      value: type,
      label: type,
      icon: '📋',
    }
  );
};

/**
 * Format course duration for display
 */
export const formatCourseDuration = (hours: number) => {
  if (hours < 1) {
    const minutes = Math.round(hours * 60);
    return `${minutes} dakika`;
  }

  if (hours === 1) return '1 saat';
  if (hours < 24) return `${hours} saat`;

  const days = Math.round(hours / 24);
  return `${days} gün`;
};

/**
 * Format course total duration including weeks
 */
export const formatCourseTotalDuration = (course: Course) => {
  const hourText = formatCourseDuration(course.total_duration_hours);

  if (course.duration_weeks && course.duration_weeks > 1) {
    return `${hourText} (${course.duration_weeks} hafta)`;
  }

  return hourText;
};

/**
 * Calculate completion rate color
 */
export const getCompletionRateColor = (rate: number) => {
  if (rate >= 80) return 'green';
  if (rate >= 60) return 'yellow';
  if (rate >= 40) return 'orange';
  return 'red';
};

/**
 * Get assessment score color
 */
export const getAssessmentScoreColor = (score: number, passingScore = 70) => {
  if (score >= passingScore + 20) return 'green';
  if (score >= passingScore + 10) return 'blue';
  if (score >= passingScore) return 'yellow';
  return 'red';
};

/**
 * Check if course is available for enrollment
 */
export const isCourseAvailable = (course: Course) => {
  return course.status === 'published' && course.is_available;
};

/**
 * Get available spots text for course
 */
export const getCourseAvailableSpotsText = (course: Course) => {
  const available = course.available_spots || 0;

  if (available === 0) return 'Yer kalmadı';
  if (available === 1) return '1 yer kaldı';
  return `${available} yer kaldı`;
};

/**
 * Calculate course difficulty score for sorting
 */
export const getCourseDifficultyScore = (level: DifficultyLevel) => {
  const info = getDifficultyLevelInfo(level);
  return info.order;
};

/**
 * Format prerequisites list
 */
export const formatPrerequisites = (prerequisites: string[]) => {
  if (!prerequisites || prerequisites.length === 0) {
    return 'Ön koşul yok';
  }

  if (prerequisites.length === 1) {
    return prerequisites[0];
  }

  return (
    prerequisites.slice(0, -1).join(', ') +
    ' ve ' +
    prerequisites[prerequisites.length - 1]
  );
};

/**
 * Format objectives list
 */
export const formatObjectives = (objectives: string[]) => {
  if (!objectives || objectives.length === 0) {
    return [];
  }

  return objectives.map((objective, index) => ({
    id: index,
    text: objective,
  }));
};

/**
 * Check if course has sessions
 */
export const courseHasSessions = (course: Course) => {
  return course.sessions && course.sessions.length > 0;
};

/**
 * Get next session date
 */
export const getNextSessionDate = (course: Course) => {
  if (!courseHasSessions(course)) return null;

  const now = new Date();
  const futureSessions = course
    .sessions!.filter((session) => new Date(session.session_date) > now)
    .sort(
      (a, b) =>
        new Date(a.session_date).getTime() - new Date(b.session_date).getTime()
    );

  return futureSessions.length > 0 ? futureSessions[0].session_date : null;
};

/**
 * Format session date for display
 */
export const formatSessionDate = (dateString: string, includeTime = true) => {
  const date = new Date(dateString);

  if (includeTime) {
    return format(date, 'dd MMMM yyyy, HH:mm', { locale: tr });
  }

  return format(date, 'dd MMMM yyyy', { locale: tr });
};

/**
 * Sort courses by various criteria
 */
export const sortCourses = (
  courses: Course[],
  sortBy: string,
  sortOrder: 'asc' | 'desc' = 'asc'
) => {
  const sorted = [...courses].sort((a, b) => {
    let comparison = 0;

    switch (sortBy) {
      case 'title':
        comparison = a.title.localeCompare(b.title, 'tr');
        break;
      case 'order_index':
        comparison = a.order_index - b.order_index;
        break;
      case 'difficulty_level':
        comparison =
          getCourseDifficultyScore(a.difficulty_level) -
          getCourseDifficultyScore(b.difficulty_level);
        break;
      case 'duration_hours':
        comparison = a.duration_hours - b.duration_hours;
        break;
      case 'created_at':
        comparison =
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        break;
      case 'participant_count':
        comparison = (a.participant_count || 0) - (b.participant_count || 0);
        break;
      case 'completion_rate':
        comparison = (a.completion_rate || 0) - (b.completion_rate || 0);
        break;
      default:
        return 0;
    }

    return sortOrder === 'desc' ? -comparison : comparison;
  });

  return sorted;
};

/**
 * Filter courses by search term
 */
export const filterCourses = (courses: Course[], searchTerm: string) => {
  if (!searchTerm.trim()) return courses;

  const term = searchTerm.toLowerCase().trim();

  return courses.filter(
    (course) =>
      course.title.toLowerCase().includes(term) ||
      course.subtitle?.toLowerCase().includes(term) ||
      course.description?.toLowerCase().includes(term) ||
      course.code.toLowerCase().includes(term) ||
      course.tags.some((tag) => tag.toLowerCase().includes(term))
  );
};
