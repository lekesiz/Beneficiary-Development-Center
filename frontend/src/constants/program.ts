/**
 * Program related constants
 */
import { ProgramStatus, ProgramType } from '../types/program';

export const PROGRAM_STATUS_OPTIONS = [
  { value: ProgramStatus.DRAFT, label: 'Taslak', color: 'gray' },
  { value: ProgramStatus.PUBLISHED, label: 'Yayınlandı', color: 'blue' },
  { value: ProgramStatus.ACTIVE, label: 'Aktif', color: 'green' },
  { value: ProgramStatus.COMPLETED, label: 'Tamamlandı', color: 'purple' },
  { value: ProgramStatus.ARCHIVED, label: 'Arşivlendi', color: 'gray' },
];

export const PROGRAM_TYPE_OPTIONS = [
  { value: ProgramType.TRAINING, label: 'Eğitim', icon: '🎓' },
  { value: ProgramType.WORKSHOP, label: 'Atölye', icon: '🔨' },
  { value: ProgramType.CERTIFICATION, label: 'Sertifika', icon: '📜' },
  { value: ProgramType.BOOTCAMP, label: 'Bootcamp', icon: '⚡' },
  { value: ProgramType.MENTORSHIP, label: 'Mentorluk', icon: '🤝' },
  { value: ProgramType.OTHER, label: 'Diğer', icon: '📋' },
];

export const CURRENCY_OPTIONS = [
  { value: 'EUR', label: 'Euro (€)', symbol: '€' },
  { value: 'USD', label: 'Dolar ($)', symbol: '$' },
  { value: 'TRY', label: 'Türk Lirası (₺)', symbol: '₺' },
  { value: 'GBP', label: 'İngiliz Sterlini (£)', symbol: '£' },
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