import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemAvatar,
  Avatar,
  Paper,
  IconButton,
  Tooltip,
  CircularProgress,
  Badge
} from '@mui/material';
import {
  School as SchoolIcon,
  TrendingUp as ProgressIcon,
  Timer as TimerIcon,
  EmojiEvents as TrophyIcon,
  Group as MentorIcon,
  Psychology as AIIcon,
  PlayCircle as PlayIcon,
  Assignment as AssignmentIcon,
  Star as StarIcon
} from '@mui/icons-material';
import { learningApi } from '../../../api/bilan';
import { useAuth } from '../../../contexts/AuthContext';
import type { PersonalizedLearningPath, AdvancedLearningContent, MentorshipMatch } from '../../../types/bilan';

const LearningDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [learningPaths, setLearningPaths] = useState<PersonalizedLearningPath[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [progress, setProgress] = useState<any>(null);
  const [activeMentorship, setActiveMentorship] = useState<MentorshipMatch | null>(null);

  useEffect(() => {
    fetchLearningData();
  }, []);

  const fetchLearningData = async () => {
    try {
      setLoading(true);
      const [pathsRes, recommendationsRes, progressRes] = await Promise.all([
        learningApi.getLearningPaths(),
        learningApi.getRecommendations(),
        learningApi.getLearningProgress()
      ]);

      setLearningPaths(pathsRes.data);
      setRecommendations(recommendationsRes.data);
      setProgress(progressRes.data);

      // Check for active mentorship
      // Would need to add this endpoint
    } catch (err) {
      console.error('Error fetching learning data:', err);
    } finally {
      setLoading(false);
    }
  };

  const activePath = learningPaths.find(p => p.status === 'ACTIVE');
  const totalLearningHours = learningPaths.reduce((total, path) => total + (path.totalTimeSpent || 0), 0) / 60;
  const totalSkillsAcquired = learningPaths.reduce((total, path) => total + (path.skillsAcquired?.length || 0), 0);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Advanced Learning Center
      </Typography>

      {/* Learning Overview */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <SchoolIcon color="primary" />
                <Typography variant="h6">Active Paths</Typography>
              </Box>
              <Typography variant="h3">
                {learningPaths.filter(p => p.status === 'ACTIVE').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <ProgressIcon color="success" />
                <Typography variant="h6">Avg Progress</Typography>
              </Box>
              <Typography variant="h3">
                {activePath ? `${activePath.overallProgress}%` : '0%'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TimerIcon color="warning" />
                <Typography variant="h6">Learning Hours</Typography>
              </Box>
              <Typography variant="h3">
                {totalLearningHours.toFixed(0)}h
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TrophyIcon color="error" />
                <Typography variant="h6">Skills Acquired</Typography>
              </Box>
              <Typography variant="h3">
                {totalSkillsAcquired}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Active Learning Path */}
      {activePath ? (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="start">
              <Box>
                <Typography variant="h5" gutterBottom>
                  {activePath.title}
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {activePath.description}
                </Typography>
                <Box display="flex" gap={1} mb={2}>
                  <Chip
                    label={`Target: ${activePath.targetRole}`}
                    color="primary"
                    size="small"
                  />
                  <Chip
                    label={`${activePath.weeklyHoursCommitment}h/week`}
                    size="small"
                  />
                  <Chip
                    label={activePath.pacePreference}
                    size="small"
                  />
                </Box>
              </Box>
              <Button
                variant="contained"
                startIcon={<PlayIcon />}
                onClick={() => navigate(`/bilan/learning/paths/${activePath.id}`)}
              >
                Continue Learning
              </Button>
            </Box>

            <Box mt={3}>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">Overall Progress</Typography>
                <Typography variant="body2">{activePath.overallProgress}%</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={activePath.overallProgress}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>

            <Grid container spacing={2} mt={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="textSecondary">
                  Last Activity
                </Typography>
                <Typography>
                  {activePath.lastActivityDate 
                    ? new Date(activePath.lastActivityDate).toLocaleDateString()
                    : 'Not started'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="textSecondary">
                  Estimated Completion
                </Typography>
                <Typography>
                  {activePath.targetCompletionDate 
                    ? new Date(activePath.targetCompletionDate).toLocaleDateString()
                    : 'Not set'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="textSecondary">
                  Skills Focus
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                  {activePath.skillGoals.slice(0, 3).map(skill => (
                    <Chip key={skill} label={skill} size="small" />
                  ))}
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      ) : (
        <Paper sx={{ p: 3, mb: 3, textAlign: 'center' }}>
          <SchoolIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Active Learning Path
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            Create a personalized learning path based on your career goals
          </Typography>
          <Button
            variant="contained"
            startIcon={<SchoolIcon />}
            onClick={() => navigate('/bilan/learning/paths/new')}
          >
            Create Learning Path
          </Button>
        </Paper>
      )}

      <Grid container spacing={3}>
        {/* AI Recommendations */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AIIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI Recommendations
              </Typography>
              
              {recommendations.length === 0 ? (
                <Typography variant="body2" color="textSecondary">
                  No recommendations available
                </Typography>
              ) : (
                <List>
                  {recommendations.slice(0, 3).map((rec, index) => (
                    <ListItem key={index} divider={index < 2}>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: getContentColor(rec.type) }}>
                          {getContentIcon(rec.type)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={rec.title}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {rec.provider} • {rec.duration} min
                            </Typography>
                            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                              <Rating value={rec.rating} readOnly size="small" />
                              <Chip
                                label={rec.difficulty}
                                size="small"
                                color={rec.difficulty === 'BEGINNER' ? 'success' : 'default'}
                              />
                            </Box>
                          </Box>
                        }
                      />
                      <IconButton
                        edge="end"
                        onClick={() => learningApi.markRecommendationViewed(rec.id)}
                      >
                        <PlayIcon />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              )}
              
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/bilan/learning/content')}
              >
                Browse All Content
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Mentorship */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <MentorIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Mentorship
              </Typography>
              
              {activeMentorship ? (
                <Box>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Avatar src={activeMentorship.mentor?.avatarUrl}>
                      {activeMentorship.mentor?.firstName?.charAt(0)}
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle1">
                        {activeMentorship.mentor?.fullName}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Active since {new Date(activeMentorship.startDate!).toLocaleDateString()}
                      </Typography>
                    </Box>
                    <Chip label="Active" color="success" size="small" sx={{ ml: 'auto' }} />
                  </Box>
                  
                  <Box mb={2}>
                    <Typography variant="body2" color="textSecondary">
                      Sessions Completed
                    </Typography>
                    <Typography variant="h6">
                      {activeMentorship.totalSessions || 0}
                    </Typography>
                  </Box>
                  
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => navigate(`/bilan/learning/mentorship/${activeMentorship.id}`)}
                  >
                    View Mentorship Details
                  </Button>
                </Box>
              ) : (
                <Box textAlign="center" py={3}>
                  <MentorIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="body2" color="textSecondary" paragraph>
                    Connect with experienced professionals in your field
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/bilan/learning/mentorship/find')}
                  >
                    Find a Mentor
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Learning Tools */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Learning Tools & Resources
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Paper
                    variant="outlined"
                    sx={{ p: 2, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}
                    onClick={() => navigate('/bilan/learning/simulations')}
                  >
                    <Box display="flex" alignItems="center" gap={2}>
                      <Avatar sx={{ bgcolor: 'primary.light' }}>
                        <AssignmentIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle1">Job Simulations</Typography>
                        <Typography variant="body2" color="textSecondary">
                          Practice real-world scenarios
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Paper
                    variant="outlined"
                    sx={{ p: 2, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}
                    onClick={() => navigate('/bilan/learning/progress')}
                  >
                    <Box display="flex" alignItems="center" gap={2}>
                      <Avatar sx={{ bgcolor: 'success.light' }}>
                        <ProgressIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle1">Progress Tracking</Typography>
                        <Typography variant="body2" color="textSecondary">
                          Monitor your development
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Paper
                    variant="outlined"
                    sx={{ p: 2, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}
                    onClick={() => navigate('/bilan/learning/achievements')}
                  >
                    <Box display="flex" alignItems="center" gap={2}>
                      <Avatar sx={{ bgcolor: 'warning.light' }}>
                        <TrophyIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle1">Achievements</Typography>
                        <Typography variant="body2" color="textSecondary">
                          View your accomplishments
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  function getContentColor(type: string) {
    switch (type) {
      case 'VIDEO':
        return 'error.main';
      case 'ARTICLE':
        return 'info.main';
      case 'COURSE':
        return 'primary.main';
      case 'EXERCISE':
        return 'success.main';
      default:
        return 'grey.500';
    }
  }

  function getContentIcon(type: string) {
    switch (type) {
      case 'VIDEO':
        return '🎥';
      case 'ARTICLE':
        return '📄';
      case 'COURSE':
        return '🎓';
      case 'EXERCISE':
        return '💪';
      case 'QUIZ':
        return '❓';
      case 'PROJECT':
        return '🚀';
      default:
        return '📚';
    }
  }
};

// Add Rating component if not imported
const Rating: React.FC<{ value: number; readOnly?: boolean; size?: 'small' | 'medium' | 'large' }> = ({ value, readOnly, size }) => {
  return (
    <Box display="flex" gap={0.5}>
      {[1, 2, 3, 4, 5].map(star => (
        <StarIcon
          key={star}
          sx={{
            fontSize: size === 'small' ? 16 : 20,
            color: star <= value ? 'warning.main' : 'action.disabled'
          }}
        />
      ))}
    </Box>
  );
};

export default LearningDashboard;