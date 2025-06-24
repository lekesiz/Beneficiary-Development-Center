import React, { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import LoadingScreen from '@/components/common/LoadingScreen'
import AuthLayout from '@/components/layouts/AuthLayout'
import DashboardLayout from '@/components/layouts/DashboardLayout'

// Lazy load pages
const Login = lazy(() => import('@/pages/auth/Login'))
const Register = lazy(() => import('@/pages/auth/Register'))
const ForgotPassword = lazy(() => import('@/pages/auth/ForgotPassword'))
const ResetPassword = lazy(() => import('@/pages/auth/ResetPassword'))

const Dashboard = lazy(() => import('@/pages/dashboard/Dashboard'))
const BeneficiaryList = lazy(() => import('@/pages/beneficiaries/BeneficiaryList'))
const BeneficiaryDetail = lazy(() => import('@/pages/beneficiaries/BeneficiaryDetail'))
const BeneficiaryForm = lazy(() => import('@/pages/beneficiaries/BeneficiaryForm'))
const ProgramList = lazy(() => import('@/pages/programs/ProgramList'))
const ProgramDetail = lazy(() => import('@/pages/programs/ProgramDetail'))
const ProgramForm = lazy(() => import('@/pages/programs/ProgramForm'))
const CourseList = lazy(() => import('@/pages/courses/CourseList'))
const CourseDetail = lazy(() => import('@/pages/courses/CourseDetail'))
const CourseForm = lazy(() => import('@/pages/courses/CourseForm'))
const CourseSessionForm = lazy(() => import('@/pages/courses/CourseSessionForm'))
const CourseReorder = lazy(() => import('@/pages/courses/CourseReorder'))
const EvaluationList = lazy(() => import('@/pages/evaluations/EvaluationList'))
const TakeEvaluation = lazy(() => import('@/pages/evaluations/TakeEvaluation'))
const TakeEvaluationAdaptive = lazy(() => import('@/pages/evaluations/TakeEvaluationAdaptive'))
const EvaluationResults = lazy(() => import('@/pages/evaluations/EvaluationResults'))
const LearningPathPage = lazy(() => import('@/pages/learning-paths/LearningPathPage'))
const MyDevelopmentReport = lazy(() => import('@/pages/reports/MyDevelopmentReport'))
const CoachDashboard = lazy(() => import('@/pages/coach/CoachDashboard'))
const StudentProfile = lazy(() => import('@/pages/coach/StudentProfile'))
const Profile = lazy(() => import('@/pages/settings/Profile'))
const Settings = lazy(() => import('@/pages/settings/Settings'))

// Protected Route component
interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRoles?: string[]
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRoles }) => {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return <LoadingScreen />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (requiredRoles && user) {
    const hasRequiredRole = requiredRoles.some(role => 
      user.roles?.some(userRole => userRole.name === role)
    )
    
    if (!hasRequiredRole) {
      return <Navigate to="/unauthorized" replace />
    }
  }

  return <>{children}</>
}

const AppRoutes: React.FC = () => {
  const { isAuthenticated } = useAuth()

  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        {/* Public routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
          <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />
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
          
          {/* Beneficiary routes */}
          <Route path="/beneficiaries" element={<BeneficiaryList />} />
          <Route path="/beneficiaries/new" element={<BeneficiaryForm />} />
          <Route path="/beneficiaries/:id" element={<BeneficiaryDetail />} />
          <Route path="/beneficiaries/:id/edit" element={<BeneficiaryForm />} />
          
          {/* Program routes */}
          <Route path="/programs" element={<ProgramList />} />
          <Route path="/programs/new" element={<ProgramForm />} />
          <Route path="/programs/:id" element={<ProgramDetail />} />
          <Route path="/programs/:id/edit" element={<ProgramForm />} />
          
          {/* Course routes */}
          <Route path="/courses" element={<CourseList />} />
          <Route path="/courses/new" element={<CourseForm />} />
          <Route path="/courses/:id" element={<CourseDetail />} />
          <Route path="/courses/:id/edit" element={<CourseForm />} />
          <Route path="/courses/:courseId/sessions/new" element={<CourseSessionForm />} />
          
          {/* Program course management */}
          <Route path="/programs/:programId/courses/reorder" element={<CourseReorder />} />
          
          {/* Evaluation routes */}
          <Route path="/evaluations" element={<EvaluationList />} />
          <Route path="/evaluations/:id/take" element={<TakeEvaluation />} />
          <Route path="/evaluations/:id/take-adaptive" element={<TakeEvaluationAdaptive />} />
          <Route path="/evaluations/:id/results/:attemptId" element={<EvaluationResults />} />
          
          {/* Learning Path routes */}
          <Route path="/learning-paths/:id" element={<LearningPathPage />} />
          
          {/* Report routes */}
          <Route path="/reports/my-development" element={<MyDevelopmentReport />} />
          
          {/* Coach routes */}
          <Route path="/coach/dashboard" element={<CoachDashboard />} />
          <Route path="/coach/student/:studentId" element={<StudentProfile />} />
          
          {/* Settings routes */}
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* Catch all */}
        <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}

export default AppRoutes