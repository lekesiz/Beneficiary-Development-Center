import * as React from 'react';
import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import LoadingScreen from '@/components/common/LoadingScreen';
import AuthLayout from '@/components/layouts/AuthLayout';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { useAuth } from '@/contexts/AuthContext';
import { ROLES } from '@/utils/permissions';

// Lazy load pages
const Login = lazy(() => import('@/pages/auth/Login'));
const Register = lazy(() => import('@/pages/auth/Register'));
const ForgotPassword = lazy(() => import('@/pages/auth/ForgotPassword'));
const ResetPassword = lazy(() => import('@/pages/auth/ResetPassword'));

const Dashboard = lazy(() => import('@/pages/dashboard/SimpleDashboard'));
const BeneficiaryList = lazy(() => import('@/pages/beneficiaries/SimpleBeneficiaryList'));
const BeneficiaryDetail = lazy(() => import('@/pages/beneficiaries/BeneficiaryDetail'));
const BeneficiaryForm = lazy(() => import('@/pages/beneficiaries/SimpleBeneficiaryForm'));
const ProgramList = lazy(() => import('@/pages/programs/SimpleProgramList'));
const ProgramDetail = lazy(() => import('@/pages/programs/ProgramDetail'));
const ProgramForm = lazy(() => import('@/pages/programs/ProgramForm'));
const CourseList = lazy(() => import('@/pages/courses/CourseList'));
const CourseDetail = lazy(() => import('@/pages/courses/CourseDetail'));
const CourseForm = lazy(() => import('@/pages/courses/CourseForm'));
const CourseSessionForm = lazy(() => import('@/pages/courses/CourseSessionForm'));
const CourseReorder = lazy(() => import('@/pages/courses/CourseReorder'));
const EvaluationList = lazy(() => import('@/pages/evaluations/EvaluationList'));
const TakeEvaluation = lazy(() => import('@/pages/evaluations/TakeEvaluation'));
const TakeEvaluationAdaptive = lazy(() => import('@/pages/evaluations/TakeEvaluationAdaptive'));
const EvaluationResults = lazy(() => import('@/pages/evaluations/EvaluationResults'));
const LearningPathsList = lazy(() => import('@/pages/learning-paths/LearningPathsList'));
const LearningPathPage = lazy(() => import('@/pages/learning-paths/LearningPathPage'));
const ReportsList = lazy(() => import('@/pages/reports/ReportsList'));
const MyDevelopmentReport = lazy(() => import('@/pages/reports/MyDevelopmentReport'));
const CoachDashboard = lazy(() => import('@/pages/coach/CoachDashboard'));
const StudentProfile = lazy(() => import('@/pages/coach/StudentProfile'));
const SessionsList = lazy(() => import('@/pages/sessions/SessionsList'));
const Profile = lazy(() => import('@/pages/settings/Profile'));
const Settings = lazy(() => import('@/pages/settings/Settings'));

// Coach Notes
const CoachNotesManager = lazy(() => import('@/components/coach-notes/CoachNotesManager'));

// Chat
const ChatLayout = lazy(() => import('@/components/chat/ChatLayout'));

// Bilan de Compétence
const BilanLayout = lazy(() => import('@/components/bilan/BilanLayout'));
const BilanRoutes = lazy(() => import('./BilanRoutes'));

// Error pages
const NotFound = lazy(() => import('@/pages/errors/NotFound'));
const Unauthorized = lazy(() => import('@/pages/errors/Unauthorized'));
const ServerError = lazy(() => import('@/pages/errors/ServerError'));

// Test pages
const TestAuth = lazy(() => import('@/pages/TestAuth'));
const TestRoleAccess = lazy(() => import('@/pages/TestRoleAccess'));
const TestRealtime = lazy(() => import('@/pages/TestRealtime'));
const TestDashboard = lazy(() => import('@/pages/TestDashboard'));
const DesignTest = lazy(() => import('@/pages/auth/DesignTest'));

// Protected Route component
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRoles }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  console.log('ProtectedRoute check:', { isAuthenticated, isLoading, user: user?.email });

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRoles && user) {
    const hasRequiredRole = requiredRoles.some((role) =>
      user.roles?.some((userRole) => userRole.name === role)
    );

    if (!hasRequiredRole) {
      return <Navigate to="/403" replace />;
    }
  }

  return <>{children}</>;
};

const AppRoutes: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        {/* Public routes */}
        <Route element={<AuthLayout />}>
          <Route
            path="/login"
            element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />}
          />
          <Route
            path="/register"
            element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />}
          />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password/:token" element={<ResetPassword />} />
        </Route>

        {/* Protected routes */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />

          {/* Beneficiary routes - Admin & Trainer only */}
          <Route path="/beneficiaries" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <BeneficiaryList />
            </ProtectedRoute>
          } />
          <Route path="/beneficiaries/new" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <BeneficiaryForm />
            </ProtectedRoute>
          } />
          <Route path="/beneficiaries/:id" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <BeneficiaryDetail />
            </ProtectedRoute>
          } />
          <Route path="/beneficiaries/:id/edit" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <BeneficiaryForm />
            </ProtectedRoute>
          } />

          {/* Program routes - Admin & Trainer only */}
          <Route path="/programs" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <ProgramList />
            </ProtectedRoute>
          } />
          <Route path="/programs/new" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <ProgramForm />
            </ProtectedRoute>
          } />
          <Route path="/programs/:id" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <ProgramDetail />
            </ProtectedRoute>
          } />
          <Route path="/programs/:id/edit" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <ProgramForm />
            </ProtectedRoute>
          } />

          {/* Course routes - Admin & Trainer only */}
          <Route path="/courses" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <CourseList />
            </ProtectedRoute>
          } />
          <Route path="/courses/new" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <CourseForm />
            </ProtectedRoute>
          } />
          <Route path="/courses/:id" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <CourseDetail />
            </ProtectedRoute>
          } />
          <Route path="/courses/:id/edit" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <CourseForm />
            </ProtectedRoute>
          } />
          <Route path="/courses/:courseId/sessions/new" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <CourseSessionForm />
            </ProtectedRoute>
          } />

          {/* Program course management - Admin & Trainer only */}
          <Route path="/programs/:programId/courses/reorder" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <CourseReorder />
            </ProtectedRoute>
          } />

          {/* Evaluation routes - All authenticated users */}
          <Route path="/evaluations" element={<EvaluationList />} />
          <Route path="/evaluations/:id/take" element={<TakeEvaluation />} />
          <Route path="/evaluations/:id/take-adaptive" element={<TakeEvaluationAdaptive />} />
          <Route path="/evaluations/:id/results/:attemptId" element={<EvaluationResults />} />

          {/* Learning Path routes - All authenticated users */}
          <Route path="/learning-paths" element={<LearningPathsList />} />
          <Route path="/learning-paths/:id" element={<LearningPathPage />} />

          {/* Report routes - Admin & Trainer access to reports list, all users to own reports */}
          <Route path="/reports" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <ReportsList />
            </ProtectedRoute>
          } />
          <Route path="/reports/my-development" element={<MyDevelopmentReport />} />

          {/* Coach routes - Admin & Trainer only */}
          <Route path="/coach/dashboard" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <CoachDashboard />
            </ProtectedRoute>
          } />
          <Route path="/coach/student/:studentId" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <StudentProfile />
            </ProtectedRoute>
          } />

          {/* Sessions/Appointments routes */}
          <Route path="/sessions" element={<SessionsList />} />

          {/* Coach Notes - Admin & Trainer only */}
          <Route path="/coach-notes" element={
            <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.TRAINER]}>
              <CoachNotesManager />
            </ProtectedRoute>
          } />

          {/* Chat routes */}
          <Route path="/chat" element={<ChatLayout />} />
          <Route path="/chat/:conversationId" element={<ChatLayout />} />

          {/* Settings routes */}
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* Bilan de Compétence routes */}
        <Route
          path="/bilan/*"
          element={
            <ProtectedRoute>
              <BilanLayout />
            </ProtectedRoute>
          }
        >
          <Route path="*" element={<BilanRoutes />} />
        </Route>

        {/* Error routes */}
        <Route path="/404" element={<NotFound />} />
        <Route path="/403" element={<Unauthorized />} />
        <Route path="/500" element={<ServerError />} />
        
        {/* Test routes */}
        <Route path="/test" element={<TestDashboard />} />
        <Route path="/test-auth" element={<TestAuth />} />
        <Route path="/test-roles" element={<TestRoleAccess />} />
        <Route path="/test-realtime" element={<TestRealtime />} />
        <Route path="/design-test" element={<DesignTest />} />

        {/* Catch all */}
        <Route
          path="/"
          element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;
