import React, { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
// Lazy load all Bilan components
const BilanDashboard = lazy(() => import('../components/bilan/BilanDashboard'));
// 360° Assessment Components
const AssessmentList = lazy(() => import('../components/bilan/assessments/AssessmentList'));
const AssessmentDetail = lazy(() => import('../components/bilan/assessments/AssessmentDetail'));
const CreateAssessment = lazy(() => import('../components/bilan/assessments/CreateAssessment'));
const AssessmentQuestions = lazy(() => import('../components/bilan/assessments/AssessmentQuestions'));
// Career Intelligence Components
const CareerDashboard = lazy(() => import('../components/bilan/career/CareerDashboard'));
const CareerPathDetail = lazy(() => import('../components/bilan/career/CareerPathDetail'));
// Legal Compliance Components
const ComplianceDashboard = lazy(() => import('../components/bilan/compliance/ComplianceDashboard'));
const SessionManagement = lazy(() => import('../components/bilan/compliance/SessionManagement'));
// Advanced Learning Components
const LearningDashboard = lazy(() => import('../components/bilan/learning/LearningDashboard'));
const LearningPathDetail = lazy(() => import('../components/bilan/learning/LearningPathDetail'));
const BilanRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Main Dashboard */}
      <Route path="/" element={<BilanDashboard />} />
      {/* 360° Assessment Routes */}
      <Route path="/assessments" element={<AssessmentList />} />
      <Route path="/assessments/new" element={<CreateAssessment />} />
      <Route path="/assessments/:id" element={<AssessmentDetail />} />
      <Route path="/assessments/:id/questions" element={<AssessmentQuestions />} />
      <Route path="/assessments/:id/invite" element={
        <div>Invite Evaluators Component</div>
      } />
      <Route path="/assessments/:id/responses/:responseId" element={
        <div>Response Detail Component</div>
      } />
      {/* Career Intelligence Routes */}
      <Route path="/career" element={<CareerDashboard />} />
      <Route path="/career/paths/new" element={
        <div>Create Career Path Component</div>
      } />
      <Route path="/career/paths/:id" element={<CareerPathDetail />} />
      <Route path="/career/paths/:id/milestones" element={<CareerPathDetail />} />
      <Route path="/career/market" element={<div>Job Market Component</div>} />
      <Route path="/career/opportunities" element={<div>Job Opportunities Component</div>} />
      <Route path="/career/skills" element={<div>Skills Analysis Component</div>} />
      <Route path="/career/documents" element={<div>Career Documents Component</div>} />
      <Route path="/career/insights" element={<div>Career Insights Component</div>} />
      {/* Legal Compliance Routes */}
      <Route path="/compliance" element={<ComplianceDashboard />} />
      <Route path="/compliance/sessions" element={<SessionManagement />} />
      <Route path="/compliance/sessions/new" element={<SessionManagement />} />
      <Route path="/compliance/sessions/:id" element={<div>Session Detail Component</div>} />
      <Route path="/compliance/reports" element={<div>Compliance Reports Component</div>} />
      <Route path="/compliance/gdpr" element={<div>GDPR Management Component</div>} />
      <Route path="/compliance/gdpr/consent" element={<div>Consent Management Component</div>} />
      <Route path="/compliance/data-retention" element={<div>Data Retention Component</div>} />
      {/* Advanced Learning Routes */}
      <Route path="/learning" element={<LearningDashboard />} />
      <Route path="/learning/paths/new" element={<div>Create Learning Path Component</div>} />
      <Route path="/learning/paths/:id" element={<LearningPathDetail />} />
      <Route path="/learning/content" element={<div>Content Browser Component</div>} />
      <Route path="/learning/mentorship/find" element={<div>Find Mentor Component</div>} />
      <Route path="/learning/mentorship/:id" element={<div>Mentorship Detail Component</div>} />
      <Route path="/learning/simulations" element={<div>Job Simulations Component</div>} />
      <Route path="/learning/progress" element={<div>Learning Progress Component</div>} />
      <Route path="/learning/achievements" element={<div>Achievements Component</div>} />
      {/* Beneficiary Detail View (for consultants) */}
      <Route path="/beneficiary/:id" element={<div>Beneficiary Detail Component</div>} />
      {/* Catch all - redirect to main dashboard */}
      <Route path="*" element={<Navigate to="/bilan" replace />} />
    </Routes>
  );
};
export default BilanRoutes;