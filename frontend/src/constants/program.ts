/**
 * Program related constants
 */
import { ProgramStatus, ProgramType } from '../types/program';

export const PROGRAM_STATUS_OPTIONS = [
  { value: ProgramStatus.DRAFT, label: 'Draft', color: 'gray' },
  { value: ProgramStatus.PUBLISHED, label: 'Published', color: 'blue' },
  { value: ProgramStatus.ACTIVE, label: 'Active', color: 'green' },
  { value: ProgramStatus.COMPLETED, label: 'Completed', color: 'purple' },
  { value: ProgramStatus.ARCHIVED, label: 'Archived', color: 'gray' },
];

export const PROGRAM_TYPE_OPTIONS = [
  { value: ProgramType.TRAINING, label: 'Training', icon: '🎓' },
  { value: ProgramType.WORKSHOP, label: 'Workshop', icon: '🔨' },
  { value: ProgramType.CERTIFICATION, label: 'Certification', icon: '📜' },
  { value: ProgramType.BOOTCAMP, label: 'Bootcamp', icon: '⚡' },
  { value: ProgramType.MENTORSHIP, label: 'Mentorship', icon: '🤝' },
  { value: ProgramType.OTHER, label: 'Other', icon: '📋' },
];

export const CURRENCY_OPTIONS = [
  { value: 'EUR', label: 'Euro (€)', symbol: '€' },
  { value: 'USD', label: 'Dollar ($)', symbol: '$' },
  { value: 'TRY', label: 'Turkish Lira (₺)', symbol: '₺' },
  { value: 'GBP', label: 'British Pound (£)', symbol: '£' },
];

export const PROGRAM_DEFAULTS = {
  MIN_PARTICIPANTS: 1,
  MAX_PARTICIPANTS: 50,
  CURRENCY: 'EUR',
  PRICE: 0,
  IS_ONLINE: false,
  IS_HYBRID: false,
  PROGRAM_TYPE: ProgramType.TRAINING,
  STATUS: ProgramStatus.DRAFT,
};

export const PROGRAM_VALIDATION = {
  TITLE_MIN_LENGTH: 1,
  TITLE_MAX_LENGTH: 200,
  DESCRIPTION_MAX_LENGTH: 2000,
  MIN_PARTICIPANTS_MIN: 1,
  MAX_PARTICIPANTS_MIN: 1,
  PRICE_MIN: 0,
  CURRENCY_LENGTH: 3,
  LOCATION_MAX_LENGTH: 200,
  ONLINE_LINK_MAX_LENGTH: 500,
  COVER_IMAGE_URL_MAX_LENGTH: 500,
};
