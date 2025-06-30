/**
 * Toast notification hook using react-hot-toast
 */
import toast from 'react-hot-toast';

export const useToast = () => {
  return {
    success: (message: string) => toast.success(message, {
      duration: 4000,
      position: 'top-right',
      style: {
        background: '#10B981',
        color: '#fff',
      },
    }),
    error: (message: string) => toast.error(message, {
      duration: 4000,
      position: 'top-right',
      style: {
        background: '#EF4444',
        color: '#fff',
      },
    }),
    info: (message: string) => toast(message, {
      duration: 4000,
      position: 'top-right',
      icon: 'ℹ️',
      style: {
        background: '#3B82F6',
        color: '#fff',
      },
    }),
  };
};
