import * as React from 'react';

import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { cn } from '@/lib/utils';

interface FormSkeletonProps {
  sections?: number;
  fieldsPerSection?: number;
  showHeader?: boolean;
  className?: string;
}

export const FormSkeleton: React.FC<FormSkeletonProps> = ({
  sections = 3,
  fieldsPerSection = 4,
  showHeader = true,
  className,
}) => {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      {showHeader && (
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-32" /> {/* Back button */}
            <div>
              <Skeleton className="h-8 w-48 mb-2" /> {/* Title */}
              <Skeleton className="h-4 w-64" /> {/* Description */}
            </div>
          </div>
        </div>
      )}

      {/* Form sections */}
      {Array.from({ length: sections }).map((_, sectionIndex) => (
        <Card key={`section-${sectionIndex}`} className="p-6">
          {/* Section title */}
          <Skeleton className="h-6 w-40 mb-4" />
          
          {/* Form fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Array.from({ length: fieldsPerSection }).map((_, fieldIndex) => (
              <div
                key={`field-${sectionIndex}-${fieldIndex}`}
                className={fieldIndex === 0 ? 'md:col-span-2' : ''}
              >
                <div className="space-y-2">
                  {/* Label */}
                  <Skeleton className="h-4 w-24" />
                  {/* Input field */}
                  <Skeleton className="h-10 w-full" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      ))}

      {/* Action buttons */}
      <div className="flex justify-end space-x-4">
        <Skeleton className="h-10 w-24" /> {/* Cancel button */}
        <Skeleton className="h-10 w-32" /> {/* Submit button */}
      </div>
    </div>
  );
};