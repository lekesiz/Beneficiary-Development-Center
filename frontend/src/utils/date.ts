import {
  format,
  formatRelative,
  formatDistanceToNow,
  parseISO,
 tr } from 'date-fns';

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'dd MMM yyyy', { locale: tr });
  } catch (error) {
    console.error('Date formatting error:', error);
    return '-';
  }
}

export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'dd MMM yyyy HH:mm', { locale: tr });
  } catch (error) {
    console.error('DateTime formatting error:', error);
    return '-';
  }
}

export function formatRelativeDate(
  date: string | Date | null | undefined
): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatRelative(dateObj, new Date(), { locale: tr });
  } catch (error) {
    console.error('Relative date formatting error:', error);
    return '-';
  }
}

export function formatDistanceFromNow(
  date: string | Date | null | undefined
): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true, locale: tr });
  } catch (error) {
    console.error('Distance date formatting error:', error);
    return '-';
  }
}

// Alias for consistency with component usage
export const formatDistanceToNow = formatDistanceFromNow;

export function formatShortDate(
  date: string | Date | null | undefined
): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'dd/MM/yyyy', { locale: tr });
  } catch (error) {
    console.error('Short date formatting error:', error);
    return '-';
  }
}

export function formatTime(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'HH:mm', { locale: tr });
  } catch (error) {
    console.error('Time formatting error:', error);
    return '-';
  }
}
