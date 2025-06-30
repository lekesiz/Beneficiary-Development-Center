import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Tabs,
  Tab,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondary,
  IconButton,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  Rating,
  Avatar
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  Person as PersonIcon,
  QuestionAnswer as QuestionIcon
} from '@mui/icons-material';
import { assessmentApi } from '../../../api/bilan';
import type { 
  Assessment, 
  AssessmentQuestion, 
  AssessmentInvitation, 
  AssessmentResponse 
} from '../../../types/bilan';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`assessment-tabpanel-${index}`}
      aria-labelledby={`assessment-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

const AssessmentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [invitations, setInvitations] = useState<AssessmentInvitation[]>([]);
  const [responses, setResponses] = useState<AssessmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState(0);

  useEffect(() => {
    if (id) {
      fetchAssessmentData();
    }
  }, [id]);

  const fetchAssessmentData = async () => {
    try {
      setLoading(true);
      const [assessmentRes, questionsRes, invitationsRes, responsesRes] = await Promise.all([
        assessmentApi.getAssessment(Number(id)),
        assessmentApi.getAssessmentQuestions(Number(id)),
        assessmentApi.getAssessmentInvitations(Number(id)),
        assessmentApi.getAssessmentResponses(Number(id))
      ]);

      setAssessment(assessmentRes.data);
      setQuestions(questionsRes.data);
      setInvitations(invitationsRes.data);
      setResponses(responsesRes.data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load assessment details');
    } finally {
      setLoading(false);
    }
  };

  const handleResendInvitation = async (invitationId: number) => {
    // TODO: Implement resend invitation
    console.log('Resend invitation:', invitationId);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !assessment) {
    return (
      <Box p={3}>
        <Alert severity="error">{error || 'Assessment not found'}</Alert>
        <Button onClick={() => navigate('/bilan/assessments')} sx={{ mt: 2 }}>
          Back to Assessments
        </Button>
      </Box>
    );
  }

  const completedInvitations = invitations.filter(inv => inv.completedAt);
  const pendingInvitations = invitations.filter(inv => !inv.completedAt);

  return (
    <Box p={3}>
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/bilan/assessments')}
        sx={{ mb: 2 }}
      >
        Back to Assessments
      </Button>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="start">
            <Box>
              <Typography variant="h4" gutterBottom>
                {assessment.title}
              </Typography>
              {assessment.description && (
                <Typography variant="body1" color="textSecondary" paragraph>
                  {assessment.description}
                </Typography>
              )}
              <Box display="flex" gap={2} alignItems="center">
                <Chip 
                  label={assessment.assessmentType}
                  color="primary"
                  size="small"
                />
                <Chip 
                  label={assessment.status}
                  color={assessment.status === 'COMPLETED' ? 'success' : 'default'}
                  size="small"
                />
                <Typography variant="body2" color="textSecondary">
                  Created: {new Date(assessment.createdAt).toLocaleDateString()}
                </Typography>
              </Box>
            </Box>
            <Box>
              {assessment.status === 'DRAFT' && (
                <Button
                  variant="contained"
                  startIcon={<SendIcon />}
                  onClick={() => navigate(`/bilan/assessments/${id}/invite`)}
                >
                  Send Invitations
                </Button>
              )}
            </Box>
          </Box>

          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h3" align="center">
                  {assessment.completionRate}%
                </Typography>
                <Typography variant="body2" color="textSecondary" align="center">
                  Completion Rate
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h3" align="center">
                  {assessment.averageScore?.toFixed(1) || '-'}
                </Typography>
                <Typography variant="body2" color="textSecondary" align="center">
                  Average Score
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h3" align="center">
                  {responses.length}/{invitations.length}
                </Typography>
                <Typography variant="body2" color="textSecondary" align="center">
                  Responses
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <Tabs
          value={tab}
          onChange={(_, newValue) => setTab(newValue)}
          indicatorColor="primary"
          textColor="primary"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label={`Questions (${questions.length})`} />
          <Tab label={`Invitations (${invitations.length})`} />
          <Tab label={`Responses (${responses.length})`} />
        </Tabs>

        <TabPanel value={tab} index={0}>
          {questions.length === 0 ? (
            <Box textAlign="center" py={4}>
              <QuestionIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="textSecondary">
                No questions added yet
              </Typography>
              <Button
                variant="contained"
                sx={{ mt: 2 }}
                onClick={() => navigate(`/bilan/assessments/${id}/questions`)}
              >
                Add Questions
              </Button>
            </Box>
          ) : (
            <List>
              {questions.map((question, index) => (
                <React.Fragment key={question.id}>
                  <ListItem>
                    <ListItemText
                      primary={`${index + 1}. ${question.question}`}
                      secondary={
                        <Box display="flex" gap={1} mt={1}>
                          <Chip label={question.category} size="small" />
                          {question.isRequired && (
                            <Chip label="Required" size="small" color="error" />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < questions.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </TabPanel>

        <TabPanel value={tab} index={1}>
          {invitations.length === 0 ? (
            <Box textAlign="center" py={4}>
              <PersonIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="textSecondary">
                No invitations sent yet
              </Typography>
              <Button
                variant="contained"
                sx={{ mt: 2 }}
                onClick={() => navigate(`/bilan/assessments/${id}/invite`)}
              >
                Send Invitations
              </Button>
            </Box>
          ) : (
            <>
              {pendingInvitations.length > 0 && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Pending ({pendingInvitations.length})
                  </Typography>
                  <List>
                    {pendingInvitations.map(invitation => (
                      <ListItem
                        key={invitation.id}
                        secondaryAction={
                          <IconButton 
                            edge="end"
                            onClick={() => handleResendInvitation(invitation.id)}
                          >
                            <RefreshIcon />
                          </IconButton>
                        }
                      >
                        <ListItemText
                          primary={invitation.evaluatorName}
                          secondary={
                            <>
                              {invitation.evaluatorEmail} • {invitation.evaluatorType}
                              <br />
                              Sent: {new Date(invitation.sentAt!).toLocaleDateString()}
                              {invitation.reminderCount > 0 && (
                                <Chip 
                                  label={`${invitation.reminderCount} reminders sent`}
                                  size="small"
                                  sx={{ ml: 1 }}
                                />
                              )}
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}

              {completedInvitations.length > 0 && (
                <>
                  <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                    Completed ({completedInvitations.length})
                  </Typography>
                  <List>
                    {completedInvitations.map(invitation => (
                      <ListItem key={invitation.id}>
                        <ListItemText
                          primary={invitation.evaluatorName}
                          secondary={
                            <>
                              {invitation.evaluatorEmail} • {invitation.evaluatorType}
                              <br />
                              Completed: {new Date(invitation.completedAt!).toLocaleDateString()}
                            </>
                          }
                        />
                        <Chip label="Completed" color="success" size="small" />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </>
          )}
        </TabPanel>

        <TabPanel value={tab} index={2}>
          {responses.length === 0 ? (
            <Box textAlign="center" py={4}>
              <AssessmentIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="textSecondary">
                No responses received yet
              </Typography>
            </Box>
          ) : (
            <List>
              {responses.map(response => (
                <ListItem key={response.id} sx={{ alignItems: 'flex-start' }}>
                  <Avatar sx={{ mr: 2, mt: 1 }}>
                    {response.evaluatorName.charAt(0)}
                  </Avatar>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1">
                          {response.evaluatorName}
                        </Typography>
                        <Chip 
                          label={response.evaluatorType} 
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Box mt={1}>
                        <Typography variant="body2" color="textSecondary">
                          Completed: {response.completedAt ? new Date(response.completedAt).toLocaleDateString() : 'In Progress'}
                        </Typography>
                        {response.averageRating && (
                          <Box display="flex" alignItems="center" gap={1} mt={1}>
                            <Typography variant="body2">Average Rating:</Typography>
                            <Rating 
                              value={response.averageRating} 
                              readOnly 
                              size="small" 
                            />
                            <Typography variant="body2">
                              ({response.averageRating.toFixed(1)})
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    }
                  />
                  <Button
                    size="small"
                    onClick={() => navigate(`/bilan/assessments/${id}/responses/${response.id}`)}
                  >
                    View Details
                  </Button>
                </ListItem>
              ))}
            </List>
          )}
        </TabPanel>
      </Card>
    </Box>
  );
};

export default AssessmentDetail;