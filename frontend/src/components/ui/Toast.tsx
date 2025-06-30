import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import * as React from 'react';

export interface ToastProps {
  id?: string;
  title: string;
  description?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  duration?: number;
  onClose?: () => void;
}

const variantStyles = {
  default: {
    container: 'bg-white border-gray-200',
    icon: null,
    iconColor: '',
  },
  success: {
    container: 'bg-green-50 border-green-200',
    icon: CheckCircle,
    iconColor: 'text-green-600',
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200',
    icon: AlertTriangle,
    iconColor: 'text-yellow-600',
  },
  danger: {
    container: 'bg-red-50 border-red-200',
    icon: AlertCircle,
    iconColor: 'text-red-600',
  },
  info: {
    container: 'bg-blue-50 border-blue-200',
    icon: Info,
    iconColor: 'text-blue-600',
  },
};

export const Toast: React.FC<ToastProps> = ({
  title,
  description,
  variant = 'default',
  onClose,
}) => {
  const styles = variantStyles[variant];
  const Icon = styles.icon;

  return (
    <div
      className={`max-w-sm w-full shadow-lg rounded-lg pointer-events-auto border ${styles.container}`}
    >
      <div className="p-4">
        <div className="flex items-start">
          {Icon && (
            <div className="flex-shrink-0">
              <Icon className={`h-5 w-5 ${styles.iconColor}`} />
            </div>
          )}
          <div className="ml-3 w-0 flex-1">
            <p className="text-sm font-medium text-gray-900">{title}</p>
            {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
          </div>
          {onClose && (
            <div className="ml-4 flex-shrink-0 flex">
              <button
                className="rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                onClick={onClose}
              >
                <span className="sr-only">Close</span>
                <X className="h-5 w-5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Toast container component
export const ToastContainer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="fixed inset-0 z-50 pointer-events-none flex items-end px-4 py-6 sm:items-start sm:p-6">
      <div className="w-full flex flex-col items-center space-y-4 sm:items-end">{children}</div>
    </div>
  );
};

// Toast context and hook
interface ToastContextType {
  addToast: (toast: Omit<ToastProps, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = React.useState<ToastProps[]>([]);

  const addToast = React.useCallback((toast: Omit<ToastProps, 'id'>) => {
    const id = Date.now().toString();
    const newToast = { ...toast, id };

    setToasts((prev) => [...prev, newToast]);

    // Auto remove after duration
    if (toast.duration !== 0) {
      setTimeout(() => {
        removeToast(id);
      }, toast.duration || 5000);
    }
  }, []);

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer>
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} onClose={() => removeToast(toast.id!)} />
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

// Convenience function for showing toasts
export const toast = (props: Omit<ToastProps, 'id'>) => {
  // This would need to be connected to the toast context
  // For now, it's a placeholder
  console.log('Toast:', props);
};
