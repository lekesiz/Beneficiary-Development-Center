import { useQueryClient } from '@tanstack/react-query';
import { useMemo, useEffect, useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';

import { useBeneficiary, beneficiaryKeys } from './useBeneficiaries';
import { useCourse, courseQueryKeys } from './useCourses';
import { useEvaluation, evaluationQueryKeys } from './useEvaluations';
import { useProgram, programQueryKeys } from './usePrograms';

export interface Breadcrumb {
  label: string;
  path: string;
  isActive: boolean;
  isLoading?: boolean;
}

// Route name mappings
const routeLabels: Record<string, string> = {
  '/': 'Dashboard',
  '/dashboard': 'Dashboard',
  '/programs': 'Programs',
  '/programs/new': 'New Program',
  '/programs/:id': 'Program Details',
  '/programs/:id/edit': 'Edit Program',
  '/programs/:programId/courses/reorder': 'Reorder Courses',
  '/courses': 'Courses',
  '/courses/new': 'New Course',
  '/courses/:id': 'Course Details',
  '/courses/:id/edit': 'Edit Course',
  '/courses/:courseId/sessions/new': 'New Session',
  '/beneficiaries': 'Beneficiaries',
  '/beneficiaries/new': 'New Beneficiary',
  '/beneficiaries/:id': 'Beneficiary Details',
  '/beneficiaries/:id/edit': 'Edit Beneficiary',
  '/evaluations': 'Evaluations',
  '/evaluations/:id/take': 'Take Evaluation',
  '/evaluations/:id/take-adaptive': 'Take Adaptive Evaluation',
  '/evaluations/:id/results/:attemptId': 'Evaluation Results',
  '/learning-paths': 'Learning Paths',
  '/learning-paths/new': 'New Learning Path',
  '/learning-paths/:id': 'Learning Path Details',
  '/learning-paths/:id/edit': 'Edit Learning Path',
  '/reports': 'Reports',
  '/reports/my-development': 'My Development Report',
  '/coach/dashboard': 'Coach Dashboard',
  '/coach/student/:studentId': 'Student Profile',
  '/settings': 'Settings',
  '/profile': 'Profile',
};

// Dynamic segment patterns
const dynamicSegmentPatterns = {
  programId: /^(id|programId)$/,
  courseId: /^(id|courseId)$/,
  beneficiaryId: /^(id|studentId)$/,
  evaluationId: /^id$/,
  learningPathId: /^id$/,
};

// Dynamic label generators for specific routes
const dynamicLabels: Record<string, (params: any, data?: any) => string> = {
  '/programs/:id': (params, data) => data?.title || `Program ${params.id}`,
  '/programs/:id/edit': (params, data) => `Edit ${data?.title || 'Program'}`,
  '/programs/:programId/courses/reorder': (params, data) =>
    `Reorder Courses - ${data?.title || 'Program'}`,
  '/courses/:id': (params, data) => data?.title || `Course ${params.id}`,
  '/courses/:id/edit': (params, data) => `Edit ${data?.title || 'Course'}`,
  '/courses/:courseId/sessions/new': (params, data) => `New Session - ${data?.title || 'Course'}`,
  '/beneficiaries/:id': (params, data) => data?.full_name || `Beneficiary ${params.id}`,
  '/beneficiaries/:id/edit': (params, data) => `Edit ${data?.full_name || 'Beneficiary'}`,
  '/learning-paths/:id': (params, data) => data?.title || `Learning Path ${params.id}`,
  '/learning-paths/:id/edit': (params, data) => `Edit ${data?.title || 'Learning Path'}`,
  '/evaluations/:id/take': (params, data) => `Take ${data?.title || 'Evaluation'}`,
  '/evaluations/:id/take-adaptive': (params, data) =>
    `Take ${data?.title || 'Evaluation'} (Adaptive)`,
  '/evaluations/:id/results/:attemptId': (params, data) =>
    `Results - ${data?.title || 'Evaluation'}`,
  '/coach/student/:studentId': (params, data) => data?.full_name || `Student ${params.studentId}`,
};

// Interface for cached entity data
interface CachedEntityData {
  program?: any;
  course?: any;
  beneficiary?: any;
  evaluation?: any;
  learningPath?: any;
}

// Hook to fetch dynamic data for breadcrumbs with caching
function useDynamicBreadcrumbData() {
  const location = useLocation();
  const params = useParams();
  const queryClient = useQueryClient();
  const [cachedData, setCachedData] = useState<CachedEntityData>({});
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});

  // Determine which IDs we need based on the current path and params
  const idsToFetch = useMemo(() => {
    const ids: Record<string, number> = {};

    // Check for program ID
    if (location.pathname.includes('/programs')) {
      const id = Number(params.id || params.programId);
      if (id) ids.programId = id;
    } else if (params.programId) {
      ids.programId = Number(params.programId);
    }

    // Check for course ID
    if (location.pathname.includes('/courses')) {
      const id = Number(params.id || params.courseId);
      if (id) ids.courseId = id;
    } else if (params.courseId) {
      ids.courseId = Number(params.courseId);
    }

    // Check for beneficiary ID
    if (location.pathname.includes('/beneficiaries')) {
      const id = Number(params.id);
      if (id) ids.beneficiaryId = id;
    } else if (location.pathname.includes('/coach/student')) {
      const id = Number(params.studentId);
      if (id) ids.beneficiaryId = id;
    }

    // Check for evaluation ID
    if (location.pathname.includes('/evaluations')) {
      const id = Number(params.id);
      if (id) ids.evaluationId = id;
    }

    // Check for learning path ID
    if (location.pathname.includes('/learning-paths')) {
      const id = Number(params.id);
      if (id) ids.learningPathId = id;
    }

    return ids;
  }, [location.pathname, params]);

  // Check cache and fetch data if needed
  useEffect(() => {
    const fetchData = async () => {
      const newData: CachedEntityData = {};
      const newLoadingStates: Record<string, boolean> = {};

      // Check and fetch program data
      if (idsToFetch.programId) {
        const cacheKey = programQueryKeys.detail(idsToFetch.programId, false);
        const cachedProgram = queryClient.getQueryData(cacheKey);

        if (cachedProgram) {
          newData.program = cachedProgram;
        } else {
          newLoadingStates.program = true;
          try {
            const data = await queryClient.fetchQuery({
              queryKey: cacheKey,
              queryFn: async () => {
                const { programsApi } = await import('../api/programs');
                return programsApi.getById(idsToFetch.programId, false);
              },
              staleTime: 5 * 60 * 1000,
            });
            newData.program = data;
          } catch (error) {
            console.error('Failed to fetch program:', error);
          }
          newLoadingStates.program = false;
        }
      }

      // Check and fetch course data
      if (idsToFetch.courseId) {
        const cacheKey = courseQueryKeys.detail(idsToFetch.courseId, false);
        const cachedCourse = queryClient.getQueryData(cacheKey);

        if (cachedCourse) {
          newData.course = cachedCourse;
        } else {
          newLoadingStates.course = true;
          try {
            const data = await queryClient.fetchQuery({
              queryKey: cacheKey,
              queryFn: async () => {
                const { coursesApi } = await import('../api/courses');
                return coursesApi.getById(idsToFetch.courseId, false);
              },
              staleTime: 5 * 60 * 1000,
            });
            newData.course = data;
          } catch (error) {
            console.error('Failed to fetch course:', error);
          }
          newLoadingStates.course = false;
        }
      }

      // Check and fetch beneficiary data
      if (idsToFetch.beneficiaryId) {
        const cacheKey = beneficiaryKeys.detail(idsToFetch.beneficiaryId);
        const cachedBeneficiary = queryClient.getQueryData(cacheKey);

        if (cachedBeneficiary) {
          newData.beneficiary = cachedBeneficiary;
        } else {
          newLoadingStates.beneficiary = true;
          try {
            const data = await queryClient.fetchQuery({
              queryKey: cacheKey,
              queryFn: async () => {
                const { beneficiariesApi } = await import('../api/beneficiaries');
                return beneficiariesApi.getById(idsToFetch.beneficiaryId);
              },
              staleTime: 5 * 60 * 1000,
            });
            newData.beneficiary = data;
          } catch (error) {
            console.error('Failed to fetch beneficiary:', error);
          }
          newLoadingStates.beneficiary = false;
        }
      }

      // Check and fetch evaluation data
      if (idsToFetch.evaluationId) {
        const cacheKey = evaluationQueryKeys.detail(idsToFetch.evaluationId, false);
        const cachedEvaluation = queryClient.getQueryData(cacheKey);

        if (cachedEvaluation) {
          newData.evaluation = cachedEvaluation;
        } else {
          newLoadingStates.evaluation = true;
          try {
            const data = await queryClient.fetchQuery({
              queryKey: cacheKey,
              queryFn: async () => {
                const { evaluationsApi } = await import('../api/evaluations');
                return evaluationsApi.getById(idsToFetch.evaluationId, false);
              },
              staleTime: 5 * 60 * 1000,
            });
            newData.evaluation = data;
          } catch (error) {
            console.error('Failed to fetch evaluation:', error);
          }
          newLoadingStates.evaluation = false;
        }
      }

      // Check and fetch learning path data
      if (idsToFetch.learningPathId) {
        const cacheKey = ['learning-paths', 'detail', idsToFetch.learningPathId] as const;
        const cachedLearningPath = queryClient.getQueryData(cacheKey);

        if (cachedLearningPath) {
          newData.learningPath = cachedLearningPath;
        } else {
          newLoadingStates.learningPath = true;
          try {
            const data = await queryClient.fetchQuery({
              queryKey: cacheKey,
              queryFn: async () => {
                const apiClient = (await import('../api/client')).default;
                const response = await apiClient.get(
                  `/api/learning-paths/${idsToFetch.learningPathId}`
                );
                return response.data;
              },
              staleTime: 5 * 60 * 1000,
            });
            newData.learningPath = data;
          } catch (error) {
            console.error('Failed to fetch learning path:', error);
          }
          newLoadingStates.learningPath = false;
        }
      }

      setCachedData(newData);
      setLoadingStates(newLoadingStates);
    };

    fetchData();
  }, [idsToFetch, queryClient]);

  // Use React Query hooks for real-time updates (these will use cached data if available)
  const { data: programData, isLoading: programLoading } = useProgram(
    idsToFetch.programId || 0,
    false
  );

  const { data: courseData, isLoading: courseLoading } = useCourse(idsToFetch.courseId || 0, false);

  const { data: beneficiaryData, isLoading: beneficiaryLoading } = useBeneficiary(
    idsToFetch.beneficiaryId || 0,
    !!idsToFetch.beneficiaryId
  );

  const { data: evaluationData, isLoading: evaluationLoading } = useEvaluation(
    idsToFetch.evaluationId || 0,
    false
  );

  return {
    data: {
      program: programData || cachedData.program,
      course: courseData || cachedData.course,
      beneficiary: beneficiaryData || cachedData.beneficiary,
      evaluation: evaluationData || cachedData.evaluation,
      learningPath: cachedData.learningPath,
    },
    loading: {
      program: programLoading || loadingStates.program,
      course: courseLoading || loadingStates.course,
      beneficiary: beneficiaryLoading || loadingStates.beneficiary,
      evaluation: evaluationLoading || loadingStates.evaluation,
      learningPath: loadingStates.learningPath,
    },
  };
}

export function useBreadcrumbs(): Breadcrumb[] {
  const location = useLocation();
  const params = useParams();
  const { data: dynamicData, loading } = useDynamicBreadcrumbData();

  return useMemo(() => {
    const breadcrumbs: Breadcrumb[] = [];
    const pathSegments = location.pathname.split('/').filter(Boolean);

    // Always add Dashboard as the first breadcrumb
    breadcrumbs.push({
      label: 'Dashboard',
      path: '/dashboard',
      isActive: location.pathname === '/dashboard' || location.pathname === '/',
    });

    // Build breadcrumbs from path segments
    let currentPath = '';

    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;

      // Skip dashboard since we already added it
      if (currentPath === '/dashboard') {
        return;
      }

      // Get label for this path
      let label = routeLabels[currentPath] || segment;
      let isLoading = false;

      // Check for dynamic labels based on current path
      if (currentPath.includes('/programs/') && params.id) {
        if (dynamicData.program) {
          label = dynamicData.program.title || dynamicData.program.name || 'Program';
        } else if (loading.program) {
          label = 'Loading...';
          isLoading = true;
        }
      } else if (currentPath.includes('/beneficiaries/') && params.id) {
        if (dynamicData.beneficiary) {
          label = `${dynamicData.beneficiary.first_name} ${dynamicData.beneficiary.last_name}` || 'Beneficiary';
        } else if (loading.beneficiary) {
          label = 'Loading...';
          isLoading = true;
        }
      } else if (currentPath.includes('/evaluations/') && params.id) {
        if (dynamicData.evaluation) {
          label = dynamicData.evaluation.title || 'Evaluation';
        } else if (loading.evaluation) {
          label = 'Loading...';
          isLoading = true;
        }
      }

      // Capitalize first letter of segment if no specific label found
      if (label === segment) {
        label = segment.charAt(0).toUpperCase() + segment.slice(1);
      }

      // Add breadcrumb
      const isActive = index === pathSegments.length - 1;
      breadcrumbs.push({
        label,
        path: currentPath,
        isActive,
        isLoading,
      });
    });

    return breadcrumbs;
  }, [location.pathname, params, dynamicData, loading]);
}
