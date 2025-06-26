import * as React from 'react';

import { Skeleton } from '@/components/ui/Skeleton';
import { cn } from '@/lib/utils';

interface DataTableSkeletonProps {
  columns?: number;
  rows?: number;
  showPagination?: boolean;
  className?: string;
}

export const DataTableSkeleton: React.FC<DataTableSkeletonProps> = ({
  columns = 5,
  rows = 10,
  showPagination = true,
  className,
}) => {
  return (
    <div className={cn('w-full', className)}>
      {/* Table */}
      <div className="rounded-md border">
        <div className="overflow-hidden">
          <table className="w-full">
            {/* Table Header */}
            <thead className="border-b bg-gray-50 dark:bg-gray-800">
              <tr>
                {Array.from({ length: columns }).map((_, index) => (
                  <th
                    key={`header-${index}`}
                    className="px-6 py-3 text-left"
                  >
                    <Skeleton className="h-4 w-24" />
                  </th>
                ))}
              </tr>
            </thead>
            
            {/* Table Body */}
            <tbody>
              {Array.from({ length: rows }).map((_, rowIndex) => (
                <tr
                  key={`row-${rowIndex}`}
                  className="border-b transition-colors hover:bg-gray-50/50 dark:hover:bg-gray-800/50"
                >
                  {Array.from({ length: columns }).map((_, colIndex) => (
                    <td
                      key={`cell-${rowIndex}-${colIndex}`}
                      className="px-6 py-4"
                    >
                      {/* Vary skeleton widths for more realistic appearance */}
                      {colIndex === 0 ? (
                        // First column - typically title/name
                        <div className="space-y-2">
                          <Skeleton className="h-4 w-32" />
                          <Skeleton className="h-3 w-24" />
                        </div>
                      ) : colIndex === columns - 1 ? (
                        // Last column - typically actions
                        <div className="flex items-center space-x-2">
                          <Skeleton className="h-8 w-8 rounded" />
                          <Skeleton className="h-8 w-8 rounded" />
                          <Skeleton className="h-8 w-8 rounded" />
                        </div>
                      ) : colIndex === 1 ? (
                        // Status badges
                        <Skeleton className="h-6 w-20 rounded-full" />
                      ) : (
                        // Regular cells
                        <Skeleton className="h-4 w-28" />
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {showPagination && (
        <div className="flex items-center justify-between px-2 py-4">
          <div className="flex items-center space-x-2">
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="flex items-center space-x-2">
            <Skeleton className="h-8 w-20 rounded" />
            <Skeleton className="h-8 w-8 rounded" />
            <Skeleton className="h-8 w-8 rounded" />
            <Skeleton className="h-8 w-8 rounded" />
            <Skeleton className="h-8 w-8 rounded" />
            <Skeleton className="h-8 w-20 rounded" />
          </div>
        </div>
      )}
    </div>
  );
};