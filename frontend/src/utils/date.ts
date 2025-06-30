import {
  format,
  formatRelative,
  formatDistanceToNow as formatDistanceToNowFn,
  parseISO,
} from 'date-fns';

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'dd MMM yyyy');
  } catch (error) {
    console.error('Date formatting error:', error);
    return '-';
  }
}

export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'dd MMM yyyy HH:mm');
  } catch (error) {
    console.error('DateTime formatting error:', error);
    return '-';
  }
}

export function formatRelativeDate(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatRelative(dateObj, new Date());
  } catch (error) {
    console.error('Relative date formatting error:', error);
    return '-';
  }
}

export function formatDistanceFromNow(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNowFn(dateObj, { addSuffix: true });
  } catch (error) {
    console.error('Distance date formatting error:', error);
    return '-';
  }
}

// Alias for consistency with component usage
export { formatDistanceFromNow as formatDistanceToNow };

export function formatShortDate(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'dd/MM/yyyy');
  } catch (error) {
    console.error('Short date formatting error:', error);
    return '-';
  }
}

export function formatTime(date: string | Date | null | undefined): string {
  if (!date) return '-';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'HH:mm');
  } catch (error) {
    console.error('Time formatting error:', error);
    return '-';
  }
}
