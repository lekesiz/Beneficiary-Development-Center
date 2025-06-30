export type LearningPathStatus =
  | 'draft'
  | 'proposed'
  | 'accepted'
  | 'in_progress'
  | 'completed'
  | 'cancelled';
export type MilestoneStatus = 'pending' | 'in_progress' | 'completed' | 'skipped';
export type LearningStyle = 'visual' | 'auditory' | 'kinesthetic' | 'reading' | 'mixed';
export type DifficultyAdjustment = 'easy' | 'balanced' | 'challenging';
export type ResourceType = 'video' | 'article' | 'exercise' | 'book' | 'course' | 'video_series';
export type ActivityType = 'practice' | 'study' | 'project';

export interface LearningResource {
  type: ResourceType;
  title: string;
  url?: string;
  duration?: string;
  description?: string;
  provider?: string;
  cost?: 'free' | 'paid';
  estimated_time?: string;
}

export interface LearningActivity {
  title: string;
  description: string;
  duration: string;
  type: ActivityType;
}

export interface WeeklyScheduleItem {
  activities: string[];
  duration: string;
}

export interface WeeklySchedule {
  [key: string]: {
    [day: string]: WeeklyScheduleItem;
  };
}

export interface ResourceCategory {
  category: string;
  items: LearningResource[];
}

export interface LearningMilestone {
  id: number;
  uuid: string;
  learning_path_id: number;
  title: string;
  description?: string;
  objective?: string;
  order_index: number;
  week_number: number;
  estimated_hours: number;
  status: MilestoneStatus;
  progress: number;
  started_at?: string;
  completed_at?: string;
  resources: LearningResource[];
  activities: LearningActivity[];
  assessment_criteria: string[];
  related_courses?: number[];
  related_topics?: string[];
  skill_focus?: string;
  user_notes?: string;
  feedback?: string;
  difficulty_rating?: number;
  created_at: string;
  updated_at: string;
}

export interface AIInsightsSummary {
  strengths_addressed: number;
  weaknesses_targeted: number;
  performance_level: string;
  recommendations_incorporated: number;
}

export interface LearningPath {
  id: number;
  uuid: string;
  user_id: number;
  evaluation_id: number;
  evaluation_attempt_id: number;
  title: string;
  description?: string;
  objective?: string;
  status: LearningPathStatus;
  accepted_by_user: boolean;
  accepted_at?: string;
  duration_weeks: number;
  estimated_hours_per_week: number;
  start_date?: string;
  end_date?: string;
  ai_insights_summary?: AIInsightsSummary;
  learning_style?: LearningStyle;
  difficulty_adjustment?: DifficultyAdjustment;
  overall_progress: number;
  completed_milestones: number;
  total_milestones: number;
  customization_notes?: string;
  feedback?: string;
  rating?: number;
  weekly_schedule: WeeklySchedule;
  resources: ResourceCategory[];
  prerequisites: string[];
  success_metrics?: string[];
  milestones: LearningMilestone[];
  created_at: string;
  updated_at: string;
}

export interface LearningPathCreateParams {
  evaluation_id: number;
  attempt_id: number;
}

export interface LearningPathUpdateParams {
  title?: string;
  description?: string;
  objective?: string;
  estimated_hours_per_week?: number;
  customization_notes?: string;
  weekly_schedule?: WeeklySchedule;
}

export interface MilestoneProgressParams {
  progress: number;
  notes?: string;
}

export interface LearningPathStatistics {
  total_paths: number;
  active_paths: number;
  completed_paths: number;
  total_milestones: number;
  completed_milestones: number;
  average_progress: number;
  by_status: {
    [key: string]: number;
  };
}
