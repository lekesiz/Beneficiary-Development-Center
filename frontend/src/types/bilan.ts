// Types for Bilan de Compétence System

// Enums
export enum AssessmentType {
  SELF = 'SELF',
  PEER = 'PEER',
  MANAGER = 'MANAGER',
  SUBORDINATE = 'SUBORDINATE',
  CLIENT = 'CLIENT',
  OTHER = 'OTHER'
}

export enum AssessmentStatus {
  DRAFT = 'DRAFT',
  SENT = 'SENT',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED'
}

export enum BilanPhase {
  PRELIMINARY = 'PRELIMINARY',
  INVESTIGATION = 'INVESTIGATION',
  CONCLUSION = 'CONCLUSION'
}

export enum SessionStatus {
  SCHEDULED = 'SCHEDULED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED'
}

export enum CareerStatus {
  EXPLORING = 'EXPLORING',
  PLANNING = 'PLANNING',
  TRANSITIONING = 'TRANSITIONING',
  ESTABLISHED = 'ESTABLISHED'
}

export enum LearningStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  PAUSED = 'PAUSED',
  COMPLETED = 'COMPLETED'
}

// 360° Assessment Types
export interface Assessment {
  id: number;
  title: string;
  description?: string;
  assessmentType: AssessmentType;
  beneficiaryId: number;
  beneficiary?: User;
  status: AssessmentStatus;
  completionRate: number;
  averageScore?: number;
  questions?: AssessmentQuestion[];
  invitations?: AssessmentInvitation[];
  responses?: AssessmentResponse[];
  createdAt: string;
  updatedAt: string;
}

export interface AssessmentQuestion {
  id: number;
  question: string;
  category: string;
  competencyId?: number;
  competency?: Competency;
  isRequired: boolean;
  order: number;
}

export interface AssessmentInvitation {
  id: number;
  assessmentId: number;
  evaluatorEmail: string;
  evaluatorName: string;
  evaluatorType: AssessmentType;
  token: string;
  sentAt?: string;
  completedAt?: string;
  reminderCount: number;
  lastReminderAt?: string;
}

export interface AssessmentResponse {
  id: number;
  assessmentId: number;
  invitationId?: number;
  evaluatorType: AssessmentType;
  evaluatorName: string;
  completedAt?: string;
  averageRating?: number;
  questionResponses?: AssessmentQuestionResponse[];
}

export interface AssessmentQuestionResponse {
  id: number;
  responseId: number;
  questionId: number;
  rating: number;
  comment?: string;
}

export interface Competency {
  id: number;
  name: string;
  description?: string;
  category: string;
  isCore: boolean;
}

// Career Intelligence Types
export interface JobMarketData {
  id: number;
  jobTitle: string;
  industry: string;
  location: string;
  averageSalary?: number;
  salaryRange?: { min: number; max: number };
  demandLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY_HIGH';
  growthRate?: number;
  requiredSkills: string[];
  emergingSkills: string[];
  typicalExperience: string;
  educationLevel: string;
  dataDate: string;
  source: string;
}

export interface CareerPath {
  id: number;
  userId: number;
  targetJobTitle: string;
  targetIndustry?: string;
  currentRole?: string;
  careerStatus: CareerStatus;
  progressPercentage: number;
  estimatedCompletion?: string;
  milestones?: CareerMilestone[];
  createdAt: string;
  updatedAt: string;
}

export interface CareerMilestone {
  id: number;
  careerPathId: number;
  title: string;
  description: string;
  targetDate?: string;
  completedDate?: string;
  status: 'pending' | 'in_progress' | 'completed';
  order: number;
}

export interface SkillGapAnalysis {
  id: number;
  userId: number;
  targetJobId?: number;
  currentSkills: Record<string, number>;
  requiredSkills: Record<string, number>;
  skillGaps: string[];
  criticalGaps: string[];
  prioritySkills: string[];
  recommendedCourses?: string[];
  analysisDate: string;
}

export interface JobOpportunity {
  id: number;
  userId: number;
  jobTitle: string;
  companyName: string;
  location: string;
  salaryRange?: { min: number; max: number };
  jobUrl?: string;
  description?: string;
  matchScore: number;
  matchingSkills?: string[];
  missingSkills?: string[];
  applicationStatus?: 'saved' | 'applied' | 'interviewing' | 'rejected' | 'accepted';
  appliedDate?: string;
  notes?: string;
}

// Legal Compliance Types
export interface BilanSession {
  id: number;
  beneficiaryId: number;
  beneficiary?: User;
  consultantId: number;
  consultant?: User;
  phase: BilanPhase;
  status: SessionStatus;
  contractNumber: string;
  scheduledStart: string;
  scheduledEnd: string;
  actualStart?: string;
  actualEnd?: string;
  durationMinutes?: number;
  location?: string;
  isRemote: boolean;
  sessionNotes?: string;
  validatedByConsultant: boolean;
  validatedByBeneficiary: boolean;
  gdprConsentGiven: boolean;
  gdprConsentDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TimeLog {
  id: number;
  sessionId: number;
  userId: number;
  activityType: string;
  startTime: string;
  endTime?: string;
  durationMinutes?: number;
  description?: string;
  billable: boolean;
}

export interface CertifiedConsultant {
  id: number;
  userId: number;
  user?: User;
  certificationNumber: string;
  certificationBody: string;
  certificationDate: string;
  expiryDate: string;
  specializations?: string[];
  bilansCompleted: number;
  averageRating?: number;
  currentBilansCount: number;
  maxConcurrentBilans: number;
  isActive: boolean;
}

export interface ComplianceCheck {
  id: number;
  sessionId: number;
  checkType: string;
  status: 'PASSED' | 'FAILED' | 'WARNING';
  details?: Record<string, any>;
  checkedAt: string;
  checkedBy?: number;
}

// Advanced Learning Types
export interface PersonalizedLearningPath {
  id: number;
  userId: number;
  user?: User;
  title: string;
  description?: string;
  targetRole?: string;
  skillGoals: string[];
  status: LearningStatus;
  learningStyle?: 'visual' | 'auditory' | 'kinesthetic' | 'reading';
  pacePreference?: 'slow' | 'moderate' | 'fast';
  weeklyHoursCommitment?: number;
  estimatedDuration?: number;
  startDate?: string;
  targetCompletionDate?: string;
  completedDate?: string;
  overallProgress: number;
  totalTimeSpent?: number;
  lastActivityDate?: string;
  adaptationEnabled: boolean;
  contentItems?: AdvancedLearningContent[];
  milestones?: AdvancedLearningMilestone[];
  skillsAcquired?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface AdvancedLearningContent {
  id: number;
  title: string;
  type: 'VIDEO' | 'ARTICLE' | 'COURSE' | 'EXERCISE' | 'QUIZ' | 'PROJECT';
  provider: string;
  url?: string;
  duration?: number;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  skills: string[];
  prerequisites?: string[];
  language: string;
  isFree: boolean;
  price?: number;
  rating?: number;
  completionRate?: number;
  metadata?: Record<string, any>;
}

export interface AdvancedLearningMilestone {
  id: number;
  pathId: number;
  title: string;
  description?: string;
  requiredSkills: string[];
  assessmentCriteria?: string[];
  targetDate?: string;
  completedDate?: string;
  status: 'pending' | 'in_progress' | 'completed';
  order: number;
}

export interface MentorshipMatch {
  id: number;
  menteeId: number;
  mentee?: User;
  mentorId: number;
  mentor?: User;
  status: 'PENDING' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  matchScore?: number;
  matchingCriteria?: Record<string, any>;
  startDate?: string;
  endDate?: string;
  totalSessions?: number;
  feedback?: string;
}

// Dashboard Types
export interface BilanDashboard {
  user: {
    id: number;
    name: string;
    role: string;
    email: string;
  };
  overview: {
    bilanStatus: string;
    totalHoursCompleted: number;
    activeSessions: number;
    completionPercentage: number;
  };
  assessments: {
    total: number;
    completed: number;
    pending: number;
    averageScore: number;
    recent: Array<{
      id: number;
      title: string;
      type: string;
      status: string;
      completionRate: number;
    }>;
  };
  career: {
    currentPath?: {
      id: number;
      targetRole: string;
      progress: number;
      milestonesCompleted: number;
    };
    skillGaps: number;
    prioritySkills: string[];
    jobMatches: number;
  };
  compliance: {
    contractNumber?: string;
    phasesCompleted: string[];
    phasesRemaining: string[];
    totalSessions: number;
    nextSession?: {
      id: number;
      date: string;
      phase: string;
      consultantName: string;
    };
  };
  learning: {
    activePaths: number;
    averageProgress: number;
    totalLearningHours: number;
    skillsAcquired: number;
    mentorshipActive: boolean;
  };
  actionsRequired: Array<{
    type: string;
    priority: string;
    message: string;
    action: string;
  }>;
  recentActivities: Array<{
    type: string;
    date: string;
    description: string;
  }>;
  // Additional fields for consultants
  consultantInfo?: {
    certificationNumber: string;
    certificationValid: boolean;
    bilansCompleted: number;
    currentBilans: number;
    maxBilans: number;
    averageRating?: number;
  };
  activeBeneficiaries?: Array<{
    id: number;
    name: string;
    phase: string;
    nextSession?: string;
    progress: number;
  }>;
  upcomingSessions?: Array<{
    id: number;
    beneficiaryName: string;
    date: string;
    phase: string;
    duration: number;
  }>;
  complianceAlerts?: Array<{
    type: string;
    severity: string;
    message: string;
  }>;
}

export interface BilanTimeline {
  timeline: Array<{
    type: string;
    date: string;
    title: string;
    description: string;
    status: string;
  }>;
}

export interface BilanProgress {
  overallCompletion: number;
  phases: Record<string, {
    completed: boolean;
    hours: number;
  }>;
  assessments: {
    total: number;
    completed: number;
    averageScore: number;
    byType: Record<string, number>;
  };
  careerPlanning: {
    status: string;
    progressPercentage: number;
    milestonesCompleted: number;
    totalMilestones: number;
    estimatedCompletion?: string;
  };
  learning: {
    pathsCreated: number;
    activePaths: number;
    averageProgress: number;
    totalHours: number;
  };
  compliance: {
    hoursCompleted: number;
    hoursRequired: number;
    isCompliant: boolean;
    missingElements: string[];
  };
}

export interface BilanRecommendations {
  immediateActions: Array<{
    action: string;
    reason: string;
    priority: string;
  }>;
  skillDevelopment: Array<{
    skill: string;
    currentLevel: number;
    requiredLevel: number;
    priority: string;
  }>;
  careerOpportunities: Array<{
    jobTitle: string;
    company: string;
    matchScore: number;
    keyMatchingSkills: string[];
  }>;
  learningSuggestions: string[];
}

// Import User type from existing types
import type { User } from './user';