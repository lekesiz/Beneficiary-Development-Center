# Enhanced Breadcrumb Functionality

## Overview

The `useBreadcrumbs` hook has been enhanced to intelligently fetch and display actual names for dynamic route segments instead of showing raw IDs. This provides a much better user experience by showing meaningful breadcrumb trails.

## Key Features

### 1. **Intelligent Cache Checking**
- Before making any API calls, the hook checks React Query's cache
- If data is already cached from previous page visits, it's used immediately
- This prevents unnecessary API calls and provides instant breadcrumb updates

### 2. **Dynamic Segment Detection**
The hook automatically detects and handles these dynamic segments:
- `:programId` or `:id` in program routes → Fetches program title
- `:courseId` or `:id` in course routes → Fetches course title
- `:beneficiaryId`, `:id`, or `:studentId` in beneficiary routes → Fetches full name
- `:id` in evaluation routes → Fetches evaluation title
- `:id` in learning path routes → Fetches learning path title

### 3. **Graceful Loading States**
- While fetching data, the breadcrumb shows the ID (e.g., "Program 123")
- The `isLoading` flag in the Breadcrumb interface indicates loading state
- UI can show loading indicators while preserving navigation structure

### 4. **Error Handling**
- If an API call fails, the breadcrumb falls back to showing the ID
- Errors are logged to console but don't break the breadcrumb navigation
- Users can still navigate using the breadcrumb trail

### 5. **Performance Optimizations**
- Uses React Query's `fetchQuery` with proper cache keys
- Sets `staleTime` to 5 minutes to avoid frequent refetches
- Leverages existing query hooks to benefit from real-time updates
- Batches API calls when multiple entities need to be fetched

## Implementation Details

### Cache Key Structure
```typescript
// Program: ['programs', 'detail', programId, includeCoursesFlag]
// Course: ['courses', 'detail', courseId, includeSessionsFlag]
// Beneficiary: ['beneficiaries', 'detail', beneficiaryId]
// Evaluation: ['evaluations', 'detail', evaluationId, includeQuestionsFlag]
// Learning Path: ['learning-paths', 'detail', learningPathId]
```

### Dynamic Label Generation
```typescript
// Before: /programs/123 → "Program 123"
// After: /programs/123 → "Digital Marketing Masterclass"

// Before: /courses/456/edit → "Edit Course 456"
// After: /courses/456/edit → "Edit Advanced SEO Techniques"
```

## Usage Example

```typescript
import { useBreadcrumbs } from '@/hooks/useBreadcrumbs';

function BreadcrumbComponent() {
  const breadcrumbs = useBreadcrumbs();

  return (
    <nav>
      {breadcrumbs.map((crumb, index) => (
        <span key={crumb.path}>
          {index > 0 && ' / '}
          {crumb.isActive ? (
            <span>{crumb.label}</span>
          ) : (
            <a href={crumb.path}>{crumb.label}</a>
          )}
          {crumb.isLoading && <LoadingSpinner />}
        </span>
      ))}
    </nav>
  );
}
```

## Benefits

1. **Better UX**: Users see meaningful names instead of cryptic IDs
2. **Performance**: Leverages React Query cache to minimize API calls
3. **Resilient**: Handles errors gracefully with fallbacks
4. **Real-time**: Updates automatically when cached data changes
5. **Progressive**: Shows IDs immediately, then enhances with names

## Future Enhancements

1. Add support for custom entity types
2. Implement breadcrumb-specific cache warming strategies
3. Add configuration for custom label formatting
4. Support for nested resource breadcrumbs (e.g., session within course)