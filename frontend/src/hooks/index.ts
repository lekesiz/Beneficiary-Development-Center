/**
 * Hooks exports
 */
// Program hooks
export {
  usePrograms,
  useProgram,
  useProgramStatistics,
  useCreateProgram,
  useUpdateProgram,
  useDeleteProgram,
  useUpdateProgramStatus,
  useAddCourseToProgram,
  programQueryKeys
} from './usePrograms';

// Course hooks
export {
  useCourses,
  useCourse,
  useCourseStatistics,
  useCreateCourse,
  useUpdateCourse,
  useDeleteCourse,
  useAddSession,
  useDuplicateCourse,
  useReorderCourse,
  courseQueryKeys
} from './useCourses';

// Beneficiary hooks
export {
  useBeneficiaries,
  useBeneficiary,
  useCreateBeneficiary,
  useUpdateBeneficiary,
  useDeleteBeneficiary,
  useAddNote,
  useAddTag,
  useRemoveTag,
  useAssignTrainer,
  useBeneficiaryStatistics
} from './useBeneficiaries';

// Evaluation hooks
export {
  useEvaluations,
  useEvaluation,
  useEvaluationQuestions,
  useEvaluationStatistics,
  useMyEvaluationAttempts,
  useEvaluationAttempt,
  useCreateEvaluation,
  useUpdateEvaluation,
  useDeleteEvaluation,
  useActivateEvaluation,
  useArchiveEvaluation,
  useCreateQuestion,
  useUpdateQuestion,
  useDeleteQuestion,
  useReorderQuestion,
  useStartEvaluationAttempt,
  useSubmitEvaluationAttempt,
  useSaveQuestionResponse,
  evaluationQueryKeys
} from './useEvaluations';