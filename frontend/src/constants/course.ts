/**
 * Course related constants
 */
import { CourseStatus, CourseFormat, DifficultyLevel } from '../types/course';

export const COURSE_STATUS_OPTIONS = [
  { value: CourseStatus.DRAFT, label: 'Taslak', color: 'gray' },
  { value: CourseStatus.PUBLISHED, label: 'Yayınlandı', color: 'green' },
  { value: CourseStatus.ARCHIVED, label: 'Arşivlendi', color: 'gray' },
];

export const COURSE_FORMAT_OPTIONS = [
  { value: CourseFormat.LECTURE, label: 'Ders', icon: '👨‍🏫' },
  { value: CourseFormat.WORKSHOP, label: 'Atölye', icon: '🔨' },
  { value: CourseFormat.PRACTICAL, label: 'Pratik', icon: '⚡' },
  { value: CourseFormat.ONLINE, label: 'Online', icon: '💻' },
  { value: CourseFormat.SELF_PACED, label: 'Kendi Hızında', icon: '🎯' },
  { value: CourseFormat.HYBRID, label: 'Hibrit', icon: '🔄' },
];

export const DIFFICULTY_LEVEL_OPTIONS = [
  { value: DifficultyLevel.BEGINNER, label: 'Başlangıç', color: 'green', order: 1 },
  { value: DifficultyLevel.INTERMEDIATE, label: 'Orta', color: 'yellow', order: 2 },
  { value: DifficultyLevel.ADVANCED, label: 'İleri', color: 'orange', order: 3 },
  { value: DifficultyLevel.EXPERT, label: 'Uzman', color: 'red', order: 4 },
];

export const ASSESSMENT_TYPE_OPTIONS = [
  { value: 'quiz', label: 'Quiz', icon: '❓' },
  { value: 'project', label: 'Proje', icon: '🚀' },
  { value: 'presentation', label: 'Sunum', icon: '📊' },
  { value: 'exam', label: 'Sınav', icon: '📝' },
  { value: 'assignment', label: 'Ödev', icon: '📋' },
  { value: 'portfolio', label: 'Portfolyo', icon: '💼' },
];

export const COURSE_DEFAULTS = {
  STATUS: CourseStatus.DRAFT,
  FORMAT: CourseFormat.LECTURE,
  DIFFICULTY_LEVEL: DifficultyLevel.BEGINNER,
  DURATION_HOURS: 1,
  DURATION_WEEKS: 1,
  MIN_PARTICIPANTS: 1,
  HAS_ASSESSMENT: false,
  PASSING_SCORE: 70,
  MAX_ATTEMPTS: 3,
  ORDER_INDEX: 0,
};

export const COURSE_VALIDATION = {
  TITLE_MIN_LENGTH: 1,
  TITLE_MAX_LENGTH: 200,
  SUBTITLE_MAX_LENGTH: 300,
  DESCRIPTION_MAX_LENGTH: 2000,
  DURATION_HOURS_MIN: 0.5,
  DURATION_HOURS_MAX: 200,
  DURATION_WEEKS_MIN: 1,
  DURATION_WEEKS_MAX: 52,
  MIN_PARTICIPANTS_MIN: 1,
  MAX_PARTICIPANTS_MIN: 1,
  PASSING_SCORE_MIN: 0,
  PASSING_SCORE_MAX: 100,
  MAX_ATTEMPTS_MIN: 1,
  MAX_ATTEMPTS_MAX: 10,
  CONTENT_URL_MAX_LENGTH: 500,
  VIDEO_URL_MAX_LENGTH: 500,
  THUMBNAIL_URL_MAX_LENGTH: 500,
};

export const SESSION_DEFAULTS = {
  DURATION_HOURS: 2,
  IS_ONLINE: false,
  IS_MANDATORY: true,
};

export const SESSION_VALIDATION = {
  TITLE_MIN_LENGTH: 1,
  TITLE_MAX_LENGTH: 200,
  DESCRIPTION_MAX_LENGTH: 1000,
  DURATION_HOURS_MIN: 0.5,
  DURATION_HOURS_MAX: 12,
  LOCATION_MAX_LENGTH: 200,
  ROOM_NUMBER_MAX_LENGTH: 50,
  ONLINE_LINK_MAX_LENGTH: 500,
  MATERIALS_URL_MAX_LENGTH: 500,
};