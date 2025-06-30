/**
 * Program utility functions
 */
import { format, isAfter, isBefore, isWithinInterval } from 'date-fns';

import {
  PROGRAM_STATUS_OPTIONS,
  PROGRAM_TYPE_OPTIONS,
  CURRENCY_OPTIONS,
} from '../constants/program';
import type { Program, ProgramStatus } from '../types/program';

/**
 * Format program dates for display
 */
export const formatProgramDate = (dateString: string, formatStr = 'dd MMMM yyyy') => {
  return format(new Date(dateString), formatStr);
};

/**
 * Get program duration in human readable format
 */
export const getProgramDurationText = (program: Program) => {
  const days = program.duration_days;

  if (days === 1) return '1 day';
  if (days < 7) return `${days} days`;
  if (days < 30) {
    const weeks = Math.ceil(days / 7);
    return `${weeks} week${weeks > 1 ? 's' : ''}`;
  }

  const months = Math.ceil(days / 30);
  return `${months} month${months > 1 ? 's' : ''}`;
};

/**
 * Get program status display information
 */
export const getProgramStatusInfo = (status: ProgramStatus) => {
  return (
    PROGRAM_STATUS_OPTIONS.find((option) => option.value === status) || {
      value: status,
      label: status,
      color: 'gray',
    }
  );
};

/**
 * Get program type display information
 */
export const getProgramTypeInfo = (type: string) => {
  return (
    PROGRAM_TYPE_OPTIONS.find((option) => option.value === type) || {
      value: type,
      label: type,
      icon: '📋',
    }
  );
};

/**
 * Get currency display information
 */
export const getCurrencyInfo = (currency: string) => {
  return (
    CURRENCY_OPTIONS.find((option) => option.value === currency) || {
      value: currency,
      label: currency,
      symbol: currency,
    }
  );
};

/**
 * Format program price for display
 */
export const formatProgramPrice = (price: number, currency: string) => {
  const currencyInfo = getCurrencyInfo(currency);
  const amount = price / 100; // Convert from cents

  if (amount === 0) return 'Free';

  return `${amount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} ${currencyInfo.symbol}`;
};

/**
 * Check if program enrollment is currently open
 */
export const isProgramEnrollmentOpen = (program: Program) => {
  if (program.status !== 'published') return false;

  const now = new Date();

  if (program.enrollment_start && program.enrollment_end) {
    return isWithinInterval(now, {
      start: new Date(program.enrollment_start),
      end: new Date(program.enrollment_end),
    });
  }

  // If no enrollment dates, check if before program start
  return isBefore(now, new Date(program.start_date));
};

/**
 * Check if program is currently active
 */
export const isProgramActive = (program: Program) => {
  if (program.status !== 'active') return false;

  const now = new Date();
  return isWithinInterval(now, {
    start: new Date(program.start_date),
    end: new Date(program.end_date),
  });
};

/**
 * Check if program is upcoming
 */
export const isProgramUpcoming = (program: Program) => {
  const now = new Date();
  return (
    ['published', 'active'].includes(program.status) && isAfter(new Date(program.start_date), now)
  );
};

/**
 * Check if program has ended
 */
export const isProgramPast = (program: Program) => {
  const now = new Date();
  return isAfter(now, new Date(program.end_date));
};

/**
 * Get enrollment period text
 */
export const getEnrollmentPeriodText = (program: Program) => {
  if (!program.enrollment_start || !program.enrollment_end) {
    return 'Until program starts';
  }

  const start = formatProgramDate(program.enrollment_start, 'dd MMM');
  const end = formatProgramDate(program.enrollment_end, 'dd MMM yyyy');

  return `${start} - ${end}`;
};

/**
 * Get program phase (upcoming, active, past)
 */
export const getProgramPhase = (program: Program): 'upcoming' | 'active' | 'past' => {
  if (isProgramPast(program)) return 'past';
  if (isProgramActive(program)) return 'active';
  return 'upcoming';
};

/**
 * Calculate enrollment percentage
 */
export const calculateEnrollmentPercentage = (program: Program) => {
  if (!program.enrollment_count) return 0;
  return Math.round((program.enrollment_count / program.max_participants) * 100);
};

/**
 * Get available spots text
 */
export const getAvailableSpotsText = (program: Program) => {
  const available = program.available_spots || 0;

  if (available === 0) return 'No spots left';
  if (available === 1) return '1 spot left';
  return `${available} spots left`;
};

/**
 * Sort programs by various criteria
 */
export const sortPrograms = (
  programs: Program[],
  sortBy: string,
  sortOrder: 'asc' | 'desc' = 'asc'
) => {
  const sorted = [...programs].sort((a, b) => {
    let comparison = 0;

    switch (sortBy) {
      case 'title':
        comparison = a.title.localeCompare(b.title);
        break;
      case 'start_date':
        comparison = new Date(a.start_date).getTime() - new Date(b.start_date).getTime();
        break;
      case 'created_at':
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        break;
      case 'enrollment_count':
        comparison = (a.enrollment_count || 0) - (b.enrollment_count || 0);
        break;
      case 'duration':
        comparison = a.duration_days - b.duration_days;
        break;
      default:
        return 0;
    }

    return sortOrder === 'desc' ? -comparison : comparison;
  });

  return sorted;
};
