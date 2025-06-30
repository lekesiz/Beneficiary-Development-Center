import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  LinearProgress, 
  Chip,
  Button,
  Alert,
  Skeleton,
  Paper
} from '@mui/material';
import { 
  Assessment as AssessmentIcon,
  TrendingUp as CareerIcon,
  Gavel as ComplianceIcon,
  School as LearningIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { useBilanDashboard } from '../../hooks/useBilanDashboard';
import { useAuth } from '../../contexts/AuthContext';
import type { BilanDashboard } from '../../types/bilan';

const BilanDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { dashboard, loading, error, refetch } = useBilanDashboard();

  useEffect(() => {
    refetch();
  }, []);

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading dashboard: {error}
          <Button onClick={refetch} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      </Box>
    );
  }

  if (!dashboard) {
    return null;
  }

  const isConsultant = user?.role === 'consultant' || user?.role === 'admin';

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Bilan de Compétence Dashboard
      </Typography>

      {/* Overview Section */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Bilan Status
              </Typography>
              <Typography variant="h5">
                {dashboard.overview.bilanStatus.replace('_', ' ').toUpperCase()}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={dashboard.overview.completionPercentage} 
                sx={{ mt: 2 }}
              />
              <Typography variant="body2" color="textSecondary" mt={1}>
                {dashboard.overview.completionPercentage.toFixed(0)}% Complete
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Hours
              </Typography>
              <Typography variant="h5">
                {dashboard.overview.totalHoursCompleted.toFixed(1)}h
              </Typography>
              <Typography variant="body2" color="textSecondary">
                of 24h minimum
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Sessions
              </Typography>
              <Typography variant="h5">
                {dashboard.overview.activeSessions}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Next Session
              </Typography>
              {dashboard.compliance.nextSession ? (
                <>
                  <Typography variant="body1">
                    {new Date(dashboard.compliance.nextSession.date).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {dashboard.compliance.nextSession.phase}
                  </Typography>
                </>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No upcoming sessions
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Consultant Info */}
      {isConsultant && dashboard.consultantInfo && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Consultant Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="textSecondary">
                  Certification
                </Typography>
                <Typography>
                  {dashboard.consultantInfo.certificationNumber}
                  {dashboard.consultantInfo.certificationValid ? (
                    <CheckIcon color="success" sx={{ ml: 1, fontSize: 16 }} />
                  ) : (
                    <WarningIcon color="error" sx={{ ml: 1, fontSize: 16 }} />
                  )}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="textSecondary">
                  Bilans Completed
                </Typography>
                <Typography>{dashboard.consultantInfo.bilansCompleted}</Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="textSecondary">
                  Current Bilans
                </Typography>
                <Typography>
                  {dashboard.consultantInfo.currentBilans} / {dashboard.consultantInfo.maxBilans}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="textSecondary">
                  Average Rating
                </Typography>
                <Typography>
                  {dashboard.consultantInfo.averageRating?.toFixed(1) || 'N/A'} / 5.0
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Assessments */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AssessmentIcon sx={{ mr: 1 }} />
                <Typography variant="h6">360° Assessments</Typography>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="h4">{dashboard.assessments.total}</Typography>
                  <Typography variant="body2" color="textSecondary">Total</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="h4" color="success.main">
                    {dashboard.assessments.completed}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">Completed</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="h4" color="warning.main">
                    {dashboard.assessments.pending}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">Pending</Typography>
                </Grid>
              </Grid>

              {dashboard.assessments.averageScore > 0 && (
                <Box mt={2}>
                  <Typography variant="body2" color="textSecondary">
                    Average Score: {dashboard.assessments.averageScore.toFixed(1)}/5
                  </Typography>
                </Box>
              )}

              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/bilan/assessments')}
              >
                View All Assessments
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Career Intelligence */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <CareerIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Career Intelligence</Typography>
              </Box>

              {dashboard.career.currentPath ? (
                <>
                  <Typography variant="body1" gutterBottom>
                    Target: {dashboard.career.currentPath.targetRole}
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={dashboard.career.currentPath.progress} 
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="textSecondary">
                    {dashboard.career.currentPath.progress}% Progress
                  </Typography>
                  <Typography variant="body2" color="textSecondary" mt={1}>
                    {dashboard.career.currentPath.milestonesCompleted} milestones completed
                  </Typography>
                </>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No career path defined yet
                </Typography>
              )}

              <Box mt={2}>
                <Typography variant="body2" color="textSecondary">
                  {dashboard.career.skillGaps} skill gaps identified
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboard.career.jobMatches} job matches found
                </Typography>
              </Box>

              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/bilan/career')}
              >
                Explore Career Options
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Legal Compliance */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <ComplianceIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Legal Compliance</Typography>
              </Box>

              {dashboard.compliance.contractNumber && (
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Contract: {dashboard.compliance.contractNumber}
                </Typography>
              )}

              <Box mt={2}>
                <Typography variant="body2" gutterBottom>Phases Completed:</Typography>
                <Box display="flex" gap={1} flexWrap="wrap">
                  {['PRELIMINARY', 'INVESTIGATION', 'CONCLUSION'].map(phase => (
                    <Chip
                      key={phase}
                      label={phase}
                      size="small"
                      color={dashboard.compliance.phasesCompleted.includes(phase) ? 'success' : 'default'}
                    />
                  ))}
                </Box>
              </Box>

              <Typography variant="body2" color="textSecondary" mt={2}>
                {dashboard.compliance.totalSessions} sessions completed
              </Typography>

              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/bilan/compliance')}
              >
                View Compliance Details
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Learning System */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <LearningIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Advanced Learning</Typography>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="h4">{dashboard.learning.activePaths}</Typography>
                  <Typography variant="body2" color="textSecondary">Active Paths</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h4">{dashboard.learning.skillsAcquired}</Typography>
                  <Typography variant="body2" color="textSecondary">Skills Acquired</Typography>
                </Grid>
              </Grid>

              <Box mt={2}>
                <Typography variant="body2" color="textSecondary">
                  Average Progress: {dashboard.learning.averageProgress.toFixed(0)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Learning Hours: {dashboard.learning.totalLearningHours.toFixed(1)}h
                </Typography>
                {dashboard.learning.mentorshipActive && (
                  <Chip label="Mentorship Active" size="small" color="primary" sx={{ mt: 1 }} />
                )}
              </Box>

              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/bilan/learning')}
              >
                Continue Learning
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions Required */}
      {dashboard.actionsRequired.length > 0 && (
        <Paper sx={{ mt: 3, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Actions Required
          </Typography>
          {dashboard.actionsRequired.map((action, index) => (
            <Alert 
              key={index} 
              severity={action.priority === 'high' ? 'warning' : 'info'}
              sx={{ mb: 1 }}
              action={
                <Button 
                  size="small"
                  onClick={() => handleAction(action.action)}
                >
                  Take Action
                </Button>
              }
            >
              {action.message}
            </Alert>
          ))}
        </Paper>
      )}

      {/* Active Beneficiaries (for consultants) */}
      {isConsultant && dashboard.activeBeneficiaries && dashboard.activeBeneficiaries.length > 0 && (
        <Paper sx={{ mt: 3, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Active Beneficiaries
          </Typography>
          <Grid container spacing={2}>
            {dashboard.activeBeneficiaries.map(beneficiary => (
              <Grid item xs={12} md={6} key={beneficiary.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1">{beneficiary.name}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      Phase: {beneficiary.phase}
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={beneficiary.progress} 
                      sx={{ mt: 1, mb: 1 }}
                    />
                    <Button 
                      size="small"
                      onClick={() => navigate(`/bilan/beneficiary/${beneficiary.id}`)}
                    >
                      View Details
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Recent Activities */}
      {dashboard.recentActivities.length > 0 && (
        <Paper sx={{ mt: 3, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Recent Activities
          </Typography>
          {dashboard.recentActivities.map((activity, index) => (
            <Box key={index} mb={1}>
              <Box display="flex" alignItems="center">
                <ScheduleIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                <Typography variant="body2" color="textSecondary">
                  {new Date(activity.date).toLocaleDateString()}
                </Typography>
                <Typography variant="body2" sx={{ ml: 2 }}>
                  {activity.description}
                </Typography>
              </Box>
            </Box>
          ))}
        </Paper>
      )}
    </Box>
  );

  function handleAction(action: string) {
    switch (action) {
      case 'complete_assessment':
        navigate('/bilan/assessments');
        break;
      case 'prepare_session':
        navigate('/bilan/sessions');
        break;
      case 'continue_learning':
        navigate('/bilan/learning');
        break;
      case 'validate_sessions':
        navigate('/bilan/compliance/sessions');
        break;
      case 'generate_reports':
        navigate('/bilan/compliance/reports');
        break;
      default:
        break;
    }
  }
};

const DashboardSkeleton: React.FC = () => (
  <Box p={3}>
    <Skeleton variant="text" width={300} height={40} />
    <Grid container spacing={3} mt={1}>
      {[1, 2, 3, 4].map(i => (
        <Grid item xs={12} md={3} key={i}>
          <Skeleton variant="rectangular" height={120} />
        </Grid>
      ))}
    </Grid>
    <Grid container spacing={3} mt={1}>
      {[1, 2, 3, 4].map(i => (
        <Grid item xs={12} md={6} key={i}>
          <Skeleton variant="rectangular" height={200} />
        </Grid>
      ))}
    </Grid>
  </Box>
);

export default BilanDashboard;