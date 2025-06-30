import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Collapse,
  Avatar
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  PlayCircle as PlayIcon,
  CheckCircle as CheckIcon,
  Lock as LockIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Timer as TimerIcon,
  Flag as FlagIcon,
  EmojiEvents as TrophyIcon
} from '@mui/icons-material';
import { learningApi } from '../../../api/bilan';
import type { PersonalizedLearningPath, AdvancedLearningContent, AdvancedLearningMilestone } from '../../../types/bilan';

const LearningPathDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [learningPath, setLearningPath] = useState<PersonalizedLearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedMilestone, setExpandedMilestone] = useState<number | null>(null);
  const [completeDialog, setCompleteDialog] = useState<{ open: boolean; content: AdvancedLearningContent | null }>({
    open: false,
    content: null
  });
  const [completionForm, setCompletionForm] = useState({
    timeSpent: 30,
    score: 0
  });

  useEffect(() => {
    fetchLearningPath();
  }, [id]);

  const fetchLearningPath = async () => {
    try {
      setLoading(true);
      const response = await learningApi.getLearningPath(Number(id));
      setLearningPath(response.data);
    } catch (err) {
      console.error('Error fetching learning path:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteContent = async () => {
    if (!completeDialog.content) return;

    try {
      await learningApi.completeContent(
        Number(id),
        completeDialog.content.id,
        {
          time_spent: completionForm.timeSpent,
          score: completionForm.score
        }
      );
      setCompleteDialog({ open: false, content: null });
      fetchLearningPath();
    } catch (err) {
      console.error('Error completing content:', err);
    }
  };

  const handleToggleMilestone = (milestoneId: number) => {
    setExpandedMilestone(expandedMilestone === milestoneId ? null : milestoneId);
  };

  if (loading || !learningPath) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        Loading...
      </Box>
    );
  }

  const completedContent = learningPath.contentItems?.filter(c => c.completionRate === 100).length || 0;
  const totalContent = learningPath.contentItems?.length || 0;

  return (
    <Box p={3}>
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/bilan/learning')}
        sx={{ mb: 2 }}
      >
        Back to Learning Dashboard
      </Button>

      {/* Path Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="start">
            <Box>
              <Typography variant="h4" gutterBottom>
                {learningPath.title}
              </Typography>
              <Typography variant="body1" color="textSecondary" paragraph>
                {learningPath.description}
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                <Chip label={`Target: ${learningPath.targetRole}`} color="primary" />
                <Chip label={learningPath.learningStyle || 'Mixed'} />
                <Chip label={`${learningPath.weeklyHoursCommitment}h/week`} />
                <Chip 
                  label={learningPath.status} 
                  color={learningPath.status === 'ACTIVE' ? 'success' : 'default'}
                />
              </Box>
            </Box>
            {learningPath.status === 'DRAFT' && (
              <Button
                variant="contained"
                onClick={() => learningApi.activateLearningPath(learningPath.id)}
              >
                Activate Path
              </Button>
            )}
          </Box>

          <Box mt={3}>
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body1">Overall Progress</Typography>
              <Typography variant="body1">{learningPath.overallProgress}%</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={learningPath.overallProgress}
              sx={{ height: 12, borderRadius: 6 }}
            />
          </Box>

          <Grid container spacing={3} mt={2}>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="textSecondary">
                Content Completed
              </Typography>
              <Typography variant="h6">
                {completedContent} / {totalContent}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="textSecondary">
                Time Invested
              </Typography>
              <Typography variant="h6">
                {((learningPath.totalTimeSpent || 0) / 60).toFixed(1)}h
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="textSecondary">
                Skills Acquired
              </Typography>
              <Typography variant="h6">
                {learningPath.skillsAcquired?.length || 0}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="textSecondary">
                Est. Completion
              </Typography>
              <Typography variant="h6">
                {learningPath.targetCompletionDate 
                  ? new Date(learningPath.targetCompletionDate).toLocaleDateString()
                  : 'Not set'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Skill Goals */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Skill Goals
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {learningPath.skillGoals.map((skill, index) => (
              <Chip
                key={index}
                label={skill}
                color={learningPath.skillsAcquired?.includes(skill) ? 'success' : 'default'}
                icon={learningPath.skillsAcquired?.includes(skill) ? <CheckIcon /> : undefined}
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Learning Milestones */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Learning Milestones
          </Typography>
          
          {(!learningPath.milestones || learningPath.milestones.length === 0) ? (
            <Alert severity="info">
              No milestones defined for this learning path
            </Alert>
          ) : (
            <Stepper orientation="vertical">
              {learningPath.milestones
                .sort((a, b) => a.order - b.order)
                .map((milestone) => (
                  <Step key={milestone.id} active={milestone.status === 'in_progress'} completed={milestone.status === 'completed'}>
                    <StepLabel
                      StepIconComponent={() => (
                        <Avatar
                          sx={{
                            bgcolor: milestone.status === 'completed' ? 'success.main' :
                                   milestone.status === 'in_progress' ? 'primary.main' : 'grey.400',
                            width: 32,
                            height: 32
                          }}
                        >
                          {milestone.status === 'completed' ? <CheckIcon /> :
                           milestone.status === 'in_progress' ? milestone.order : <LockIcon />}
                        </Avatar>
                      )}
                    >
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Typography variant="subtitle1">{milestone.title}</Typography>
                        <IconButton
                          size="small"
                          onClick={() => handleToggleMilestone(milestone.id)}
                        >
                          {expandedMilestone === milestone.id ? <CollapseIcon /> : <ExpandIcon />}
                        </IconButton>
                      </Box>
                    </StepLabel>
                    <StepContent>
                      <Collapse in={expandedMilestone === milestone.id}>
                        <Box>
                          <Typography variant="body2" color="textSecondary" paragraph>
                            {milestone.description}
                          </Typography>
                          
                          {milestone.requiredSkills.length > 0 && (
                            <Box mb={2}>
                              <Typography variant="caption" color="textSecondary">
                                Required Skills:
                              </Typography>
                              <Box display="flex" gap={0.5} mt={0.5}>
                                {milestone.requiredSkills.map(skill => (
                                  <Chip key={skill} label={skill} size="small" />
                                ))}
                              </Box>
                            </Box>
                          )}

                          {milestone.targetDate && (
                            <Typography variant="body2" color="textSecondary">
                              Target: {new Date(milestone.targetDate).toLocaleDateString()}
                            </Typography>
                          )}
                        </Box>
                      </Collapse>
                    </StepContent>
                  </Step>
                ))}
            </Stepper>
          )}
        </CardContent>
      </Card>

      {/* Learning Content */}
      {learningPath.contentItems && learningPath.contentItems.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Learning Content
            </Typography>
            <List>
              {learningPath.contentItems.map((content, index) => (
                <ListItem
                  key={content.id}
                  divider={index < learningPath.contentItems!.length - 1}
                >
                  <ListItemIcon>
                    <Avatar sx={{ bgcolor: getContentColor(content.type) }}>
                      {getContentIcon(content.type)}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={content.title}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {content.provider} • {content.duration} min • {content.difficulty}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                          {content.completionRate === 100 && (
                            <Chip label="Completed" size="small" color="success" />
                          )}
                          {content.isFree ? (
                            <Chip label="Free" size="small" color="primary" />
                          ) : (
                            <Chip label={`$${content.price}`} size="small" />
                          )}
                          {content.rating && (
                            <Typography variant="caption">
                              ⭐ {content.rating.toFixed(1)}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    {content.completionRate === 100 ? (
                      <CheckIcon color="success" />
                    ) : (
                      <IconButton
                        edge="end"
                        onClick={() => setCompleteDialog({ open: true, content })}
                      >
                        <PlayIcon />
                      </IconButton>
                    )}
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Complete Content Dialog */}
      <Dialog open={completeDialog.open} onClose={() => setCompleteDialog({ open: false, content: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Complete Learning Content</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            {completeDialog.content?.title}
          </Typography>
          <TextField
            fullWidth
            label="Time Spent (minutes)"
            type="number"
            value={completionForm.timeSpent}
            onChange={(e) => setCompletionForm({ ...completionForm, timeSpent: parseInt(e.target.value) })}
            margin="normal"
          />
          {completeDialog.content?.type === 'QUIZ' && (
            <TextField
              fullWidth
              label="Score (%)"
              type="number"
              value={completionForm.score}
              onChange={(e) => setCompletionForm({ ...completionForm, score: parseInt(e.target.value) })}
              margin="normal"
              inputProps={{ min: 0, max: 100 }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompleteDialog({ open: false, content: null })}>
            Cancel
          </Button>
          <Button onClick={handleCompleteContent} variant="contained">
            Mark Complete
          </Button>
        </DialogActions>
      </Dialog>
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
      case 'QUIZ':
        return 'warning.main';
      case 'PROJECT':
        return 'secondary.main';
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

export default LearningPathDetail;