import React from 'react';

import { useBreadcrumbs } from '../hooks/useBreadcrumbs';

/**
 * Example component demonstrating the enhanced breadcrumb functionality
 * 
 * The breadcrumb hook now:
 * 1. Detects dynamic segments (e.g., :programId, :courseId)
 * 2. Checks React Query cache first to avoid unnecessary API calls
 * 3. Fetches entity names only when needed
 * 4. Shows loading states gracefully (ID while loading, then name)
 * 5. Falls back to ID if fetch fails
 */
export const BreadcrumbExample: React.FC = () => {
  const breadcrumbs = useBreadcrumbs();

  return (
    <nav aria-label="Breadcrumb">
      <ol style={{ display: 'flex', listStyle: 'none', padding: 0, gap: '8px' }}>
        {breadcrumbs.map((crumb, index) => (
          <li key={crumb.path} style={{ display: 'flex', alignItems: 'center' }}>
            {index > 0 && <span style={{ margin: '0 8px' }}>/</span>}
            {crumb.isActive ? (
              <span style={{ fontWeight: 'bold' }}>
                {crumb.isLoading ? (
                  <>
                    {crumb.label}
                    <span style={{ fontSize: '0.8em', marginLeft: '4px' }}>
                      (loading...)
                    </span>
                  </>
                ) : (
                  crumb.label
                )}
              </span>
            ) : (
              <a 
                href={crumb.path} 
                style={{ 
                  textDecoration: 'none', 
                  color: crumb.isLoading ? '#999' : '#0066cc' 
                }}
              >
                {crumb.label}
              </a>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

/**
 * Usage example:
 * 
 * URL: /programs/123/courses/456/edit
 * 
 * Without caching (first visit):
 * Dashboard / Programs / Program 123 (loading...) / Course 456 (loading...) / Edit Course 456 (loading...)
 * 
 * After data loads:
 * Dashboard / Programs / Digital Marketing Masterclass / Advanced SEO Techniques / Edit Advanced SEO Techniques
 * 
 * With caching (subsequent visits):
 * Dashboard / Programs / Digital Marketing Masterclass / Advanced SEO Techniques / Edit Advanced SEO Techniques
 * (No loading states, instant display of names)
 * 
 * Error handling:
 * If API call fails, falls back to showing IDs:
 * Dashboard / Programs / Program 123 / Course 456 / Edit Course 456
 */