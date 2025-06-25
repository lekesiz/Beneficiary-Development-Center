/**
 * Evaluation types
 */

export type EvaluationStatus = 'draft' | 'active' | 'archived' | 'completed';
export type QuestionType =
  | 'multiple_choice'
  | 'true_false'
  | 'short_answer'
  | 'essay'
  | 'matching'
  | 'ordering'
  | 'fill_in_blank';
export type EvaluationDifficultyLevel = 'easy' | 'medium' | 'hard';
export type AttemptStatus =
  | 'in_progress'
  | 'completed'
  | 'abandoned'
  | 'timed_out';

export interface Evaluation {
  id: number;
  uuid: string;
  title: string;
  description?: string;
  instructions?: string;
  course_id?: number;
  program_id?: number;
  created_by: number;
  status: EvaluationStatus;
  total_questions: number;
  total_points: number;
  passing_score: number;
  time_limit_minutes?: number;
  max_attempts: number;
  shuffle_questions: boolean;
  show_results_immediately: boolean;
  allow_review: boolean;
  available_from?: string;
  available_until?: string;
  evaluation_metadata: Record<string, any>;
  tags: string[];
  is_available: boolean;
  duration_display: string;
  created_at: string;
  updated_at: string;
  course_title?: string;
  program_title?: string;
  creator_name?: string;
  questions?: Question[];
}

export interface Question {
  id: number;
  uuid: string;
  evaluation_id: number;
  question_text: string;
  question_type: QuestionType;
  difficulty_level: EvaluationDifficultyLevel;
  points: number;
  order_index: number;
  question_data: Record<string, any>;
  is_required: boolean;
  explanation?: string;
  hints: string[];
  question_metadata: Record<string, any>;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface EvaluationAttempt {
  id: number;
  uuid: string;
  evaluation_id: number;
  user_id: number;
  attempt_number: number;
  status: AttemptStatus;
  started_at: string;
  completed_at?: string;
  time_spent_minutes?: number;
  total_questions: number;
  questions_answered: number;
  total_points: number;
  score_earned: number;
  percentage_score: number;
  passed: boolean;
  time_limit_minutes?: number;
  passing_score: number;
  attempt_metadata: Record<string, any>;
  duration_display: string;
  is_completed: boolean;
  is_in_progress: boolean;
  user_name?: string;
  evaluation_title?: string;
  responses?: QuestionResponse[];
}

export interface QuestionResponse {
  id: number;
  uuid: string;
  attempt_id: number;
  question_id: number;
  response_data: Record<string, any>;
  is_correct?: boolean;
  points_earned: number;
  time_spent_seconds?: number;
  answered_at: string;
  ai_feedback?: string;
  ai_score?: number;
  response_metadata: Record<string, any>;
}

export interface QuestionBank {
  id: number;
  uuid: string;
  title: string;
  description?: string;
  subject?: string;
  topic?: string;
  difficulty_level: EvaluationDifficultyLevel;
  question_text: string;
  question_type: QuestionType;
  points: number;
  question_data: Record<string, any>;
  explanation?: string;
  hints: string[];
  usage_count: number;
  last_used_at?: string;
  created_by: number;
  question_metadata: Record<string, any>;
  tags: string[];
  created_at: string;
  updated_at: string;
}

// Form types
export interface CreateEvaluationRequest {
  title: string;
  description?: string;
  instructions?: string;
  course_id?: number;
  program_id?: number;
  time_limit_minutes?: number;
  max_attempts?: number;
  passing_score?: number;
  shuffle_questions?: boolean;
  show_results_immediately?: boolean;
  allow_review?: boolean;
  available_from?: string;
  available_until?: string;
  evaluation_metadata?: Record<string, any>;
  tags?: string[];
}

export interface UpdateEvaluationRequest
  extends Partial<CreateEvaluationRequest> {}

export interface CreateQuestionRequest {
  question_text: string;
  question_type: QuestionType;
  difficulty_level?: EvaluationDifficultyLevel;
  points?: number;
  order_index?: number;
  question_data: Record<string, any>;
  is_required?: boolean;
  explanation?: string;
  hints?: string[];
  question_metadata?: Record<string, any>;
  tags?: string[];
}

export type UpdateQuestionRequest = Partial<CreateQuestionRequest>

export interface SaveResponseRequest {
  question_id: number;
  response_data: Record<string, any>;
}

// Filter and response types
export interface EvaluationFilters {
  page?: number;
  per_page?: number;
  status?: string;
  course_id?: number;
  program_id?: number;
  search?: string;
  sort_by?: string;
  sort_desc?: boolean;
}

export interface EvaluationsResponse {
  evaluations: Evaluation[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_prev: boolean;
    has_next: boolean;
  };
}

export interface EvaluationStatistics {
  total_evaluations: number;
  active_evaluations: number;
  total_attempts: number;
  average_score: number;
  pass_rate: number;
}

// Question type specific data structures
export interface MultipleChoiceData {
  options: string[];
  correct_answer: string;
  allow_multiple?: boolean;
}

export interface TrueFalseData {
  correct_answer: boolean;
}

export interface ShortAnswerData {
  correct_answers: string[];
  case_sensitive?: boolean;
  max_length?: number;
}

export interface EssayData {
  max_words?: number;
  min_words?: number;
  grading_rubric?: string;
}

export interface MatchingData {
  pairs: { left: string; right: string }[];
  shuffle_options?: boolean;
}

export interface OrderingData {
  items: string[];
  correct_order: number[];
}

export interface FillInBlankData {
  text_with_blanks: string;
  answers: { blank_index: number; correct_answers: string[] }[];
  case_sensitive?: boolean;
}
