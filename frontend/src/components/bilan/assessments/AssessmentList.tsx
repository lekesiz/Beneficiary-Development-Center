import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Grid,
  IconButton,
  Menu,
  MenuItem,
  LinearProgress,
  Skeleton,
  Alert,
  Fab
} from '@mui/material';
import {
  MoreVert as MoreIcon,
  Add as AddIcon,
  Send as SendIcon,
  Assessment as AssessmentIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { assessmentApi } from '../../../api/bilan';
import type { Assessment, AssessmentStatus, AssessmentType } from '../../../types/bilan';

const AssessmentList: React.FC = () => {
  const navigate = useNavigate();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);

  useEffect(() => {
    fetchAssessments();
  }, []);

  const fetchAssessments = async () => {
    try {
      setLoading(true);
      const response = await assessmentApi.getAssessments();
      setAssessments(response.data.items);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load assessments');
    } finally {
      setLoading(false);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, assessment: Assessment) => {
    setAnchorEl(event.currentTarget);
    setSelectedAssessment(assessment);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedAssessment(null);
  };

  const handleComplete = async () => {
    if (!selectedAssessment) return;
    
    try {
      await assessmentApi.completeAssessment(selectedAssessment.id);
      await fetchAssessments();
      handleMenuClose();
    } catch (err: any) {
      console.error('Error completing assessment:', err);
    }
  };

  const getStatusColor = (status: AssessmentStatus) => {
    switch (status) {
      case AssessmentStatus.DRAFT:
        return 'default';
      case AssessmentStatus.SENT:
        return 'warning';
      case AssessmentStatus.IN_PROGRESS:
        return 'info';
      case AssessmentStatus.COMPLETED:
        return 'success';
      default:
        return 'default';
    }
  };

  const getTypeIcon = (type: AssessmentType) => {
    switch (type) {
      case AssessmentType.SELF:
        return '👤';
      case AssessmentType.PEER:
        return '👥';
      case AssessmentType.MANAGER:
        return '👔';
      case AssessmentType.SUBORDINATE:
        return '👨‍💼';
      case AssessmentType.CLIENT:
        return '🤝';
      default:
        return '📋';
    }
  };

  if (loading) {
    return (
      <Box p={3}>
        <Grid container spacing={3}>
          {[1, 2, 3].map(i => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Skeleton variant="rectangular" height={200} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">360° Assessments</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/bilan/assessments/new')}
        >
          Create Assessment
        </Button>
      </Box>

      {assessments.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <AssessmentIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No assessments yet
            </Typography>
            <Typography variant="body2" color="textSecondary" mb={3}>
              Create your first 360° assessment to gather feedback
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/bilan/assessments/new')}
            >
              Create Assessment
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {assessments.map(assessment => (
            <Grid item xs={12} md={6} lg={4} key={assessment.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start">
                    <Box>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Typography variant="h5">
                          {getTypeIcon(assessment.assessmentType)}
                        </Typography>
                        <Chip
                          label={assessment.status}
                          size="small"
                          color={getStatusColor(assessment.status)}
                        />
                      </Box>
                      <Typography variant="h6" gutterBottom>
                        {assessment.title}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, assessment)}
                    >
                      <MoreIcon />
                    </IconButton>
                  </Box>

                  {assessment.description && (
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      {assessment.description}
                    </Typography>
                  )}

                  <Box mb={2}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2" color="textSecondary">
                        Completion
                      </Typography>
                      <Typography variant="body2">
                        {assessment.completionRate}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={assessment.completionRate}
                    />
                  </Box>

                  {assessment.averageScore !== undefined && (
                    <Typography variant="body2" color="textSecondary">
                      Average Score: {assessment.averageScore.toFixed(1)}/5
                    </Typography>
                  )}

                  <Box display="flex" gap={1} mt={2}>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => navigate(`/bilan/assessments/${assessment.id}`)}
                    >
                      View Details
                    </Button>
                    {assessment.status === AssessmentStatus.DRAFT && (
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<SendIcon />}
                        onClick={() => navigate(`/bilan/assessments/${assessment.id}/invite`)}
                      >
                        Send Invites
                      </Button>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          navigate(`/bilan/assessments/${selectedAssessment?.id}/edit`);
          handleMenuClose();
        }}>
          <EditIcon sx={{ mr: 1 }} /> Edit
        </MenuItem>
        {selectedAssessment?.status !== AssessmentStatus.COMPLETED && (
          <MenuItem onClick={handleComplete}>
            <AssessmentIcon sx={{ mr: 1 }} /> Mark Complete
          </MenuItem>
        )}
        <MenuItem onClick={handleMenuClose} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} /> Delete
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default AssessmentList;