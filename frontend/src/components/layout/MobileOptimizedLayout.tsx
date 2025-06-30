import React from 'react';
import { cn } from '@/lib/utils';

interface MobileOptimizedLayoutProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '7xl' | 'full';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const maxWidthClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
  '7xl': 'max-w-7xl',
  full: 'max-w-full',
};

const paddingClasses = {
  none: '',
  sm: 'px-4 py-4 sm:px-6 sm:py-6',
  md: 'px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10',
  lg: 'px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-12',
};

export const MobileOptimizedLayout: React.FC<MobileOptimizedLayoutProps> = ({
  children,
  className,
  maxWidth = '7xl',
  padding = 'md',
}) => {
  return (
    <div className={cn(
      "min-h-screen bg-slate-50",
      paddingClasses[padding],
      className
    )}>
      <div className={cn(
        "mx-auto",
        maxWidthClasses[maxWidth]
      )}>
        {children}
      </div>
    </div>
  );
};

// Responsive Container Component
export const ResponsiveContainer: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className }) => {
  return (
    <div className={cn(
      "w-full",
      // Responsive padding
      "px-4 sm:px-6 lg:px-8",
      // Max width with responsive breakpoints
      "mx-auto max-w-7xl",
      className
    )}>
      {children}
    </div>
  );
};

// Mobile-First Grid Component
export const ResponsiveGrid: React.FC<{
  children: React.ReactNode;
  cols?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ 
  children, 
  cols = { default: 1, sm: 2, lg: 3, xl: 4 },
  gap = 'md',
  className 
}) => {
  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8',
  };

  const colClasses = [
    cols.default && `grid-cols-${cols.default}`,
    cols.sm && `sm:grid-cols-${cols.sm}`,
    cols.md && `md:grid-cols-${cols.md}`,
    cols.lg && `lg:grid-cols-${cols.lg}`,
    cols.xl && `xl:grid-cols-${cols.xl}`,
  ].filter(Boolean).join(' ');

  return (
    <div className={cn(
      "grid",
      gapClasses[gap],
      colClasses,
      className
    )}>
      {children}
    </div>
  );
};

// Mobile-Optimized Card Component
export const MobileCard: React.FC<{
  children: React.ReactNode;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
}> = ({ children, className, padding = 'md' }) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div className={cn(
      "bg-white rounded-lg shadow-sm border border-slate-200",
      paddingClasses[padding],
      // Hover effect for non-touch devices
      "hover:shadow-md transition-shadow duration-200",
      // Touch-friendly tap highlight
      "active:scale-[0.99] transition-transform",
      className
    )}>
      {children}
    </div>
  );
};

// Mobile-Optimized Button Component
export const MobileButton: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  className?: string;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}> = ({ 
  children, 
  onClick, 
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className,
  disabled = false,
  type = 'button'
}) => {
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800',
    secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200 active:bg-slate-300',
    ghost: 'bg-transparent text-slate-700 hover:bg-slate-100 active:bg-slate-200',
  };

  const sizeClasses = {
    sm: 'h-9 px-3 text-sm',
    md: 'h-11 px-4 text-base',
    lg: 'h-12 px-6 text-lg',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "inline-flex items-center justify-center font-medium rounded-lg",
        "transition-all duration-200",
        "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        // Touch-friendly minimum size
        "min-h-[44px] min-w-[44px]",
        variantClasses[variant],
        sizeClasses[size],
        fullWidth && "w-full",
        className
      )}
    >
      {children}
    </button>
  );
};