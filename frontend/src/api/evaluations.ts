/**
 * Evaluations API client
 */
import apiClient from './client';

// Types for API requests and responses
export interface Evaluation {
  id: number;
  uuid: string;
  title: string;
  description?: string;
  instructions?: string;
  course_id?: number;
  program_id?: number;
  created_by: number;
  status: 'draft' | 'active' | 'archived' | 'completed';
  total_questions: number;
  total_points: number;
  passing_score: number;
  time_limit_minutes?: number;
  max_attempts: number;
  shuffle_questions: boolean;
  show_results_immediately: boolean;
  allow_review: boolean;
  is_adaptive: boolean;
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
  question_type: 'multiple_choice' | 'true_false' | 'short_answer' | 'essay' | 'matching' | 'ordering' | 'fill_in_blank';
  difficulty_level: 'easy' | 'medium' | 'hard';
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
  status: 'in_progress' | 'completed' | 'abandoned' | 'timed_out';
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
  difficulty_level: 'easy' | 'medium' | 'hard';
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer' | 'essay' | 'matching' | 'ordering' | 'fill_in_blank';
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
  is_adaptive?: boolean;
  available_from?: string;
  available_until?: string;
  evaluation_metadata?: Record<string, any>;
  tags?: string[];
}

export interface UpdateEvaluationRequest extends Partial<CreateEvaluationRequest> {}

export interface CreateQuestionRequest {
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer' | 'essay' | 'matching' | 'ordering' | 'fill_in_blank';
  difficulty_level?: 'easy' | 'medium' | 'hard';
  points?: number;
  order_index?: number;
  question_data: Record<string, any>;
  is_required?: boolean;
  explanation?: string;
  hints?: string[];
  question_metadata?: Record<string, any>;
  tags?: string[];
}

export interface UpdateQuestionRequest extends Partial<CreateQuestionRequest> {}

export interface SaveResponseRequest {
  question_id: number;
  response_data: Record<string, any>;
}

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

export interface AdaptiveQuestionResponse {
  complete: boolean;
  message?: string;
  next_action?: string;
  question?: Question & {
    adaptive_metadata: {
      difficulty_adjusted: boolean;
      current_difficulty: 'easy' | 'medium' | 'hard';
      question_number: number;
    };
  };
}

export interface LearningInsights {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  performance_metrics: {
    overall_score: number;
    accuracy_percentage: number;
    time_efficiency: number;
    consistency_score: number;
  };
  visual_indicators: {
    trend: 'improving' | 'declining' | 'stable';
    level: 'expert' | 'proficient' | 'developing' | 'novice' | 'beginner';
  };
  attempt_summary: {
    evaluation_title: string;
    score: string;
    percentage: string;
    passed: boolean;
    duration: string;
    questions_answered: string;
  };
}

const EVALUATIONS_BASE_URL = '/evaluations';

export const evaluationsApi = {
  /**
   * Get all evaluations with optional filters
   */
  getAll: async (filters?: EvaluationFilters): Promise<EvaluationsResponse> => {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    
    const response = await apiClient.get<EvaluationsResponse>(
      `${EVALUATIONS_BASE_URL}?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get evaluation by ID
   */
  getById: async (id: number, includeQuestions = false): Promise<Evaluation> => {
    const params = includeQuestions ? '?include_questions=true' : '';
    const response = await apiClient.get<Evaluation>(`${EVALUATIONS_BASE_URL}/${id}${params}`);
    return response.data;
  },

  /**
   * Create new evaluation
   */
  create: async (data: CreateEvaluationRequest): Promise<Evaluation> => {
    const response = await apiClient.post<Evaluation>(EVALUATIONS_BASE_URL, data);
    return response.data;
  },

  /**
   * Update evaluation
   */
  update: async (id: number, data: UpdateEvaluationRequest): Promise<Evaluation> => {
    const response = await apiClient.put<Evaluation>(`${EVALUATIONS_BASE_URL}/${id}`, data);
    return response.data;
  },

  /**
   * Delete evaluation
   */
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`${EVALUATIONS_BASE_URL}/${id}`);
  },

  /**
   * Activate evaluation
   */
  activate: async (id: number): Promise<Evaluation> => {
    const response = await apiClient.post<Evaluation>(`${EVALUATIONS_BASE_URL}/${id}/activate`);
    return response.data;
  },

  /**
   * Archive evaluation
   */
  archive: async (id: number): Promise<Evaluation> => {
    const response = await apiClient.post<Evaluation>(`${EVALUATIONS_BASE_URL}/${id}/archive`);
    return response.data;
  },

  /**
   * Get evaluation statistics
   */
  getStatistics: async (): Promise<EvaluationStatistics> => {
    const response = await apiClient.get<EvaluationStatistics>(`${EVALUATIONS_BASE_URL}/statistics`);
    return response.data;
  },

  // Question management
  questions: {
    /**
     * Get all questions for an evaluation
     */
    getAll: async (evaluationId: number): Promise<Question[]> => {
      const response = await apiClient.get<Question[]>(`${EVALUATIONS_BASE_URL}/${evaluationId}/questions`);
      return response.data;
    },

    /**
     * Create new question
     */
    create: async (evaluationId: number, data: CreateQuestionRequest): Promise<Question> => {
      const response = await apiClient.post<Question>(`${EVALUATIONS_BASE_URL}/${evaluationId}/questions`, data);
      return response.data;
    },

    /**
     * Update question
     */
    update: async (evaluationId: number, questionId: number, data: UpdateQuestionRequest): Promise<Question> => {
      const response = await apiClient.put<Question>(`${EVALUATIONS_BASE_URL}/${evaluationId}/questions/${questionId}`, data);
      return response.data;
    },

    /**
     * Delete question
     */
    delete: async (evaluationId: number, questionId: number): Promise<void> => {
      await apiClient.delete(`${EVALUATIONS_BASE_URL}/${evaluationId}/questions/${questionId}`);
    },

    /**
     * Reorder question
     */
    reorder: async (evaluationId: number, questionId: number, orderIndex: number): Promise<Question> => {
      const response = await apiClient.post<Question>(
        `${EVALUATIONS_BASE_URL}/${evaluationId}/questions/${questionId}/reorder`,
        { order_index: orderIndex }
      );
      return response.data;
    }
  },

  // Adaptive evaluation API calls
  adaptive: {
    /**
     * Get next question using AI-powered adaptive logic
     */
    getNextQuestion: async (evaluationId: number, attemptId: number, currentIndex?: number): Promise<AdaptiveQuestionResponse> => {
      const params = new URLSearchParams({
        attempt_id: attemptId.toString(),
        ...(currentIndex !== undefined && { current_index: currentIndex.toString() })
      });
      
      const response = await apiClient.get<AdaptiveQuestionResponse>(
        `${EVALUATIONS_BASE_URL}/${evaluationId}/next-question?${params}`
      );
      return response.data;
    },

    /**
     * Get AI-powered learning insights
     */
    getLearningInsights: async (evaluationId: number, attemptId: number): Promise<LearningInsights> => {
      const response = await apiClient.get<LearningInsights>(
        `${EVALUATIONS_BASE_URL}/${evaluationId}/attempts/${attemptId}/insights`
      );
      return response.data;
    }
  },

  // Attempt management
  attempts: {
    /**
     * Start new evaluation attempt
     */
    start: async (evaluationId: number): Promise<EvaluationAttempt> => {
      const response = await apiClient.post<EvaluationAttempt>(`${EVALUATIONS_BASE_URL}/${evaluationId}/attempts`);
      return response.data;
    },

    /**
     * Get evaluation attempt
     */
    getById: async (evaluationId: number, attemptId: number): Promise<EvaluationAttempt> => {
      const response = await apiClient.get<EvaluationAttempt>(`${EVALUATIONS_BASE_URL}/${evaluationId}/attempts/${attemptId}`);
      return response.data;
    },

    /**
     * Submit evaluation attempt
     */
    submit: async (evaluationId: number, attemptId: number): Promise<EvaluationAttempt> => {
      const response = await apiClient.post<EvaluationAttempt>(`${EVALUATIONS_BASE_URL}/${evaluationId}/attempts/${attemptId}/submit`);
      return response.data;
    },

    /**
     * Get current user's attempts for an evaluation
     */
    getMy: async (evaluationId: number): Promise<EvaluationAttempt[]> => {
      const response = await apiClient.get<EvaluationAttempt[]>(`${EVALUATIONS_BASE_URL}/${evaluationId}/my-attempts`);
      return response.data;
    },

    /**
     * Save question response
     */
    saveResponse: async (evaluationId: number, attemptId: number, data: SaveResponseRequest): Promise<QuestionResponse> => {
      const response = await apiClient.post<QuestionResponse>(
        `${EVALUATIONS_BASE_URL}/${evaluationId}/attempts/${attemptId}/responses`,
        data
      );
      return response.data;
    }
  }
};

export default evaluationsApi;