import { ChevronRight, Home } from 'lucide-react';
import React from 'react';
import { Link } from 'react-router-dom';

import { useBreadcrumbs } from '@/hooks/useBreadcrumbs';
import { cn } from '@/lib/utils';

export interface BreadcrumbsProps {
  className?: string;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ className }) => {
  const breadcrumbs = useBreadcrumbs();

  // Don't show breadcrumbs if we're on the dashboard
  if (breadcrumbs.length <= 1 && breadcrumbs[0]?.isActive) {
    return null;
  }

  return (
    <nav
      aria-label="Breadcrumb"
      className={cn(
        'flex items-center space-x-1 text-sm text-gray-600 dark:text-gray-400',
        className
      )}
    >
      {breadcrumbs.map((breadcrumb, index) => (
        <React.Fragment key={breadcrumb.path}>
          {index > 0 && (
            <ChevronRight 
              className="h-4 w-4 text-gray-400 dark:text-gray-600 mx-1 flex-shrink-0" 
              aria-hidden="true"
            />
          )}
          
          {breadcrumb.isActive ? (
            <span className="font-medium text-gray-900 dark:text-gray-100 flex items-center">
              {index === 0 && (
                <Home 
                  className="h-4 w-4 mr-1 flex-shrink-0" 
                  aria-hidden="true"
                />
              )}
              <span className="truncate max-w-xs">{breadcrumb.label}</span>
            </span>
          ) : (
            <Link
              to={breadcrumb.path}
              className="hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center group"
            >
              {index === 0 && (
                <Home 
                  className="h-4 w-4 mr-1 flex-shrink-0 group-hover:text-primary" 
                  aria-hidden="true"
                />
              )}
              <span className="truncate max-w-xs hover:underline">
                {breadcrumb.label}
              </span>
            </Link>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumbs;