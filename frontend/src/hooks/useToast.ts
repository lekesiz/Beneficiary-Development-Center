/**
 * Toast notification hook
 * Simple implementation - can be replaced with a proper toast library
 */
import { useCallback } from 'react';

export const useToast = () => {
  const toast = useCallback(
    (message: string, type: 'success' | 'error' | 'info' = 'info') => {
      // Simple console log for now - replace with actual toast library
      console.log(`[${type.toUpperCase()}] ${message}`);

      // You can integrate with libraries like:
      // - react-hot-toast
      // - react-toastify
      // - sonner
      // etc.
    },
    []
  );

  return {
    success: (message: string) => toast(message, 'success'),
    error: (message: string) => toast(message, 'error'),
    info: (message: string) => toast(message, 'info'),
  };
};
