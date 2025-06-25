/**
 * API exports
 */
export { default as programsApi } from './programs';
export { default as coursesApi } from './courses';
export { default as beneficiariesApi } from './beneficiaries';
export { default as evaluationsApi } from './evaluations';

// Re-export all types
export type * from '../types/program';
export type * from '../types/course';
export type * from '../types/evaluation';
