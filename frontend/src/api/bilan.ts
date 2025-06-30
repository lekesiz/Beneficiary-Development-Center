import apiClient from './client';
import type { 
  BilanDashboard, 
  BilanTimeline, 
  BilanProgress, 
  BilanRecommendations,
  Assessment,
  AssessmentQuestion,
  AssessmentInvitation,
  AssessmentResponse,
  Competency,
  JobMarketData,
  CareerPath,
  CareerMilestone,
  SkillGapAnalysis,
  JobOpportunity,
  BilanSession,
  TimeLog,
  CertifiedConsultant,
  ComplianceCheck,
  PersonalizedLearningPath,
  AdvancedLearningContent,
  MentorshipMatch
} from '../types/bilan';

// Dashboard API
export const bilanDashboardApi = {
  getDashboard: () => 
    apiClient.get<BilanDashboard>('/api/v1/bilan/dashboard'),
  
  getTimeline: (beneficiaryId: number) => 
    apiClient.get<BilanTimeline>(`/api/v1/bilan/timeline/${beneficiaryId}`),
  
  getProgress: (beneficiaryId: number) => 
    apiClient.get<BilanProgress>(`/api/v1/bilan/progress/${beneficiaryId}`),
  
  getRecommendations: (beneficiaryId: number) => 
    apiClient.get<BilanRecommendations>(`/api/v1/bilan/recommendations/${beneficiaryId}`)
};

// 360° Assessment API
export const assessmentApi = {
  // Assessments
  getAssessments: (params?: { page?: number; per_page?: number; status?: string }) => 
    apiClient.get<{ items: Assessment[]; pagination: any }>('/api/v1/assessments', { params }),
  
  createAssessment: (data: Partial<Assessment>) => 
    apiClient.post<Assessment>('/api/v1/assessments', data),
  
  getAssessment: (id: number) => 
    apiClient.get<Assessment>(`/api/v1/assessments/${id}`),
  
  updateAssessment: (id: number, data: Partial<Assessment>) => 
    apiClient.put<Assessment>(`/api/v1/assessments/${id}`, data),
  
  completeAssessment: (id: number) => 
    apiClient.post<Assessment>(`/api/v1/assessments/${id}/complete`),
  
  // Questions
  getAssessmentQuestions: (assessmentId: number) => 
    apiClient.get<AssessmentQuestion[]>(`/api/v1/assessments/${assessmentId}/questions`),
  
  addAssessmentQuestions: (assessmentId: number, questions: Partial<AssessmentQuestion>[]) => 
    apiClient.post<AssessmentQuestion[]>(`/api/v1/assessments/${assessmentId}/questions`, { questions }),
  
  // Invitations & Responses
  getAssessmentInvitations: (assessmentId: number) => 
    apiClient.get<AssessmentInvitation[]>(`/api/v1/assessments/${assessmentId}/invitations`),
  
  sendAssessmentInvitations: (assessmentId: number, invitations: Array<{
    evaluator_email: string;
    evaluator_name: string;
    evaluator_type: string;
  }>) => 
    apiClient.post<AssessmentInvitation[]>(`/api/v1/assessments/${assessmentId}/invitations`, { invitations }),
  
  getAssessmentResponses: (assessmentId: number) => 
    apiClient.get<AssessmentResponse[]>(`/api/v1/assessments/${assessmentId}/responses`),
  
  submitAssessmentResponse: (assessmentId: number, responses: Array<{
    question_id: number;
    rating: number;
    comment?: string;
  }>) => 
    apiClient.post<AssessmentResponse>(`/api/v1/assessments/${assessmentId}/submit`, { responses }),
  
  // Public Access
  getPublicAssessment: (token: string) => 
    apiClient.get<Assessment>(`/api/v1/assessments/public/${token}`),
  
  submitPublicAssessment: (token: string, data: {
    evaluator_name: string;
    responses: Array<{
      question_id: number;
      rating: number;
      comment?: string;
    }>;
  }) => 
    apiClient.post<AssessmentResponse>(`/api/v1/assessments/public/${token}/submit`, data),
  
  // Reference Data
  getCompetencies: () => 
    apiClient.get<Competency[]>('/api/v1/assessments/competencies')
};

// Career Intelligence API
export const careerApi = {
  // Market Intelligence
  searchMarketData: (params: { 
    job_title?: string; 
    location?: string; 
    industry?: string;
    page?: number;
    per_page?: number;
  }) => 
    apiClient.get<{ items: JobMarketData[]; pagination: any }>('/api/v1/career/market-data', { params }),
  
  getMarketData: (id: number) => 
    apiClient.get<JobMarketData>(`/api/v1/career/market-data/${id}`),
  
  // Career Planning
  getCareerPaths: () => 
    apiClient.get<CareerPath[]>('/api/v1/career/paths'),
  
  createCareerPath: (data: Partial<CareerPath>) => 
    apiClient.post<CareerPath>('/api/v1/career/paths', data),
  
  getCareerPath: (id: number) => 
    apiClient.get<CareerPath>(`/api/v1/career/paths/${id}`),
  
  addCareerMilestone: (pathId: number, milestone: Partial<CareerMilestone>) => 
    apiClient.post<CareerMilestone>(`/api/v1/career/paths/${pathId}/milestones`, milestone),
  
  completeMilestone: (milestoneId: number) => 
    apiClient.post<CareerMilestone>(`/api/v1/career/milestones/${milestoneId}/complete`),
  
  // Skills Analysis
  createSkillGapAnalysis: (data: { target_job_id: number }) => 
    apiClient.post<SkillGapAnalysis>('/api/v1/career/skill-gap-analysis', data),
  
  getSkillGapAnalysis: (id: number) => 
    apiClient.get<SkillGapAnalysis>(`/api/v1/career/skill-gap-analysis/${id}`),
  
  // Job Opportunities
  getJobOpportunities: (params?: { page?: number; per_page?: number }) => 
    apiClient.get<{ items: JobOpportunity[]; pagination: any }>('/api/v1/career/opportunities', { params }),
  
  searchJobOpportunities: (criteria: { 
    job_title: string; 
    location?: string; 
    salary_min?: number; 
    skills?: string[];
  }) => 
    apiClient.post<{ items: JobOpportunity[]; pagination: any }>('/api/v1/career/opportunities/search', criteria),
  
  markJobApplied: (id: number) => 
    apiClient.post<JobOpportunity>(`/api/v1/career/opportunities/${id}/apply`),
  
  // Documents
  getCareerDocuments: () => 
    apiClient.get<any[]>('/api/v1/career/documents'),
  
  uploadCareerDocument: (formData: FormData) => 
    apiClient.post<any>('/api/v1/career/documents', formData),
  
  // Insights
  getCareerInsights: () => 
    apiClient.get<any>('/api/v1/career/insights')
};

// Legal Compliance API
export const complianceApi = {
  // Session Management
  getSessions: (params?: { page?: number; per_page?: number; status?: string }) => 
    apiClient.get<{ items: BilanSession[]; pagination: any }>('/api/v1/compliance/sessions', { params }),
  
  createSession: (data: Partial<BilanSession>) => 
    apiClient.post<BilanSession>('/api/v1/compliance/sessions', data),
  
  getSession: (id: number) => 
    apiClient.get<BilanSession>(`/api/v1/compliance/sessions/${id}`),
  
  startSession: (id: number) => 
    apiClient.post<BilanSession>(`/api/v1/compliance/sessions/${id}/start`),
  
  completeSession: (id: number, data: { duration_minutes: number; session_notes?: string }) => 
    apiClient.post<BilanSession>(`/api/v1/compliance/sessions/${id}/complete`, data),
  
  // Time Tracking
  createTimeLog: (data: Partial<TimeLog>) => 
    apiClient.post<TimeLog>('/api/v1/compliance/time-logs', data),
  
  // Consultants
  getCertifiedConsultants: () => 
    apiClient.get<CertifiedConsultant[]>('/api/v1/compliance/consultants'),
  
  registerConsultant: (data: {
    certification_number: string;
    certification_body: string;
    certification_date: string;
    expiry_date: string;
    specializations?: string[];
  }) => 
    apiClient.post<CertifiedConsultant>('/api/v1/compliance/consultants/register', data),
  
  // Compliance Monitoring
  checkCompliance: (sessionId: number) => 
    apiClient.post<ComplianceCheck>(`/api/v1/compliance/check/${sessionId}`),
  
  getComplianceStatistics: () => 
    apiClient.get<any>('/api/v1/compliance/statistics'),
  
  // GDPR & Privacy
  recordGDPRConsent: (data: { consent_type: string; consent_given: boolean }) => 
    apiClient.post<any>('/api/v1/compliance/gdpr/consent', data),
  
  getGDPRConsents: () => 
    apiClient.get<any[]>('/api/v1/compliance/gdpr/consent'),
  
  withdrawGDPRConsent: (id: number) => 
    apiClient.post<any>(`/api/v1/compliance/gdpr/consent/${id}/withdraw`),
  
  // Reports
  generateSynthesisReport: (beneficiaryId: number) => 
    apiClient.post<any>(`/api/v1/compliance/reports/synthesis/${beneficiaryId}`),
  
  validateReport: (id: number) => 
    apiClient.post<any>(`/api/v1/compliance/reports/${id}/validate`),
  
  // Data Retention
  getDataRetentionPolicies: () => 
    apiClient.get<any>('/api/v1/compliance/data-retention')
};

// Advanced Learning API
export const learningApi = {
  // Content Discovery
  browseContent: (params?: { 
    type?: string; 
    skill?: string; 
    difficulty?: string;
    page?: number;
    per_page?: number;
  }) => 
    apiClient.get<{ items: AdvancedLearningContent[]; pagination: any }>('/api/v1/learning/content', { params }),
  
  getContent: (id: number) => 
    apiClient.get<AdvancedLearningContent>(`/api/v1/learning/content/${id}`),
  
  // Learning Paths
  getLearningPaths: () => 
    apiClient.get<PersonalizedLearningPath[]>('/api/v1/learning/paths'),
  
  createLearningPath: (data: Partial<PersonalizedLearningPath>) => 
    apiClient.post<PersonalizedLearningPath>('/api/v1/learning/paths', data),
  
  getLearningPath: (id: number) => 
    apiClient.get<PersonalizedLearningPath>(`/api/v1/learning/paths/${id}`),
  
  activateLearningPath: (id: number) => 
    apiClient.post<PersonalizedLearningPath>(`/api/v1/learning/paths/${id}/activate`),
  
  completeContent: (pathId: number, contentId: number, data: { time_spent: number; score?: number }) => 
    apiClient.post<any>(`/api/v1/learning/paths/${pathId}/content/${contentId}/complete`, data),
  
  // Mentorship
  findAvailableMentors: (params?: { skills?: string[]; availability?: string }) => 
    apiClient.get<any[]>('/api/v1/learning/mentorship/available', { params }),
  
  requestMentorship: (data: { mentor_id: number; message: string; goals: string[] }) => 
    apiClient.post<MentorshipMatch>('/api/v1/learning/mentorship/request', data),
  
  acceptMentorship: (id: number) => 
    apiClient.post<MentorshipMatch>(`/api/v1/learning/mentorship/${id}/accept`),
  
  createMentorshipSession: (matchId: number, data: {
    scheduled_date: string;
    duration_minutes: number;
    topic: string;
  }) => 
    apiClient.post<any>(`/api/v1/learning/mentorship/${matchId}/sessions`, data),
  
  // Job Simulations
  getSimulations: (params?: { role?: string; difficulty?: string }) => 
    apiClient.get<any[]>('/api/v1/learning/simulations', { params }),
  
  startSimulation: (id: number) => 
    apiClient.post<any>(`/api/v1/learning/simulations/${id}/start`),
  
  completeSimulation: (simulationId: number, attemptId: number, data: {
    score: number;
    time_taken: number;
    responses: any;
  }) => 
    apiClient.post<any>(`/api/v1/learning/simulations/${simulationId}/attempts/${attemptId}/complete`, data),
  
  // Recommendations & Progress
  getRecommendations: () => 
    apiClient.get<any[]>('/api/v1/learning/recommendations'),
  
  markRecommendationViewed: (id: number) => 
    apiClient.post<any>(`/api/v1/learning/recommendations/${id}/view`),
  
  getLearningProgress: () => 
    apiClient.get<any>('/api/v1/learning/progress/summary')
};