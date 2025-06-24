import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'primary';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  className,
  showLabel = false,
  size = 'md',
  variant = 'default'
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };
  
  const variantClasses = {
    default: 'bg-blue-600',
    primary: 'bg-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    danger: 'bg-red-600'
  };
  
  const getVariantByValue = () => {
    if (variant !== 'default') return variant;
    if (percentage >= 80) return 'success';
    if (percentage >= 50) return 'default';
    if (percentage >= 30) return 'warning';
    return 'danger';
  };
  
  const currentVariant = getVariantByValue();
  
  return (
    <div className={cn('relative', className)}>
      <div className={cn(
        'w-full bg-gray-200 rounded-full overflow-hidden',
        sizeClasses[size]
      )}>
        <div
          className={cn(
            'h-full rounded-full transition-all duration-300 ease-out',
            variantClasses[currentVariant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn(
            'font-medium',
            size === 'sm' ? 'text-xs' : 'text-sm',
            percentage > 50 ? 'text-white' : 'text-gray-700'
          )}>
            {percentage.toFixed(0)}%
          </span>
        </div>
      )}
    </div>
  );
};