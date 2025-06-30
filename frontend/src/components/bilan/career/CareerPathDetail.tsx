import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Menu,
  MenuItem
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Add as AddIcon,
  CheckCircle as CheckIcon,
  RadioButtonUnchecked as PendingIcon,
  Schedule as ScheduleIcon,
  Edit as EditIcon,
  MoreVert as MoreIcon
} from '@mui/icons-material';
import { careerApi } from '../../../api/bilan';
import type { CareerPath, CareerMilestone } from '../../../types/bilan';

const CareerPathDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [careerPath, setCareerPath] = useState<CareerPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedMilestone, setSelectedMilestone] = useState<CareerMilestone | null>(null);
  const [milestoneForm, setMilestoneForm] = useState({
    title: '',
    description: '',
    targetDate: ''
  });

  useEffect(() => {
    fetchCareerPath();
  }, [id]);

  const fetchCareerPath = async () => {
    try {
      setLoading(true);
      const response = await careerApi.getCareerPath(Number(id));
      setCareerPath(response.data);
    } catch (err) {
      console.error('Error fetching career path:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMilestone = async () => {
    try {
      await careerApi.addCareerMilestone(Number(id), {
        title: milestoneForm.title,
        description: milestoneForm.description,
        target_date: milestoneForm.targetDate,
        order: (careerPath?.milestones?.length || 0) + 1
      });
      setDialogOpen(false);
      setMilestoneForm({ title: '', description: '', targetDate: '' });
      fetchCareerPath();
    } catch (err) {
      console.error('Error adding milestone:', err);
    }
  };

  const handleCompleteMilestone = async (milestoneId: number) => {
    try {
      await careerApi.completeMilestone(milestoneId);
      fetchCareerPath();
      handleMenuClose();
    } catch (err) {
      console.error('Error completing milestone:', err);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, milestone: CareerMilestone) => {
    setAnchorEl(event.currentTarget);
    setSelectedMilestone(milestone);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedMilestone(null);
  };

  if (loading || !careerPath) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        Loading...
      </Box>
    );
  }

  const completedMilestones = careerPath.milestones?.filter(m => m.status === 'completed').length || 0;
  const totalMilestones = careerPath.milestones?.length || 0;

  return (
    <Box p={3}>
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/bilan/career')}
        sx={{ mb: 2 }}
      >
        Back to Career Dashboard
      </Button>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="start">
            <Box>
              <Typography variant="h4" gutterBottom>
                {careerPath.targetJobTitle}
              </Typography>
              {careerPath.targetIndustry && (
                <Typography variant="body1" color="textSecondary" gutterBottom>
                  Industry: {careerPath.targetIndustry}
                </Typography>
              )}
              {careerPath.currentRole && (
                <Typography variant="body2" color="textSecondary">
                  Current Role: {careerPath.currentRole}
                </Typography>
              )}
            </Box>
            <Chip
              label={careerPath.careerStatus.replace('_', ' ')}
              color="primary"
              size="large"
            />
          </Box>

          <Box mt={3}>
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body1">Overall Progress</Typography>
              <Typography variant="body1">{careerPath.progressPercentage}%</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={careerPath.progressPercentage}
              sx={{ height: 10, borderRadius: 5 }}
            />
          </Box>

          <Grid container spacing={3} mt={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="textSecondary">
                Milestones Completed
              </Typography>
              <Typography variant="h5">
                {completedMilestones} / {totalMilestones}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="textSecondary">
                Started
              </Typography>
              <Typography variant="h5">
                {new Date(careerPath.createdAt).toLocaleDateString()}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="textSecondary">
                Estimated Completion
              </Typography>
              <Typography variant="h5">
                {careerPath.estimatedCompletion 
                  ? new Date(careerPath.estimatedCompletion).toLocaleDateString()
                  : 'Not Set'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5">Career Milestones</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setDialogOpen(true)}
            >
              Add Milestone
            </Button>
          </Box>

          {!careerPath.milestones || careerPath.milestones.length === 0 ? (
            <Alert severity="info">
              No milestones defined yet. Add milestones to track your progress.
            </Alert>
          ) : (
            <Timeline position="alternate">
              {careerPath.milestones
                .sort((a, b) => a.order - b.order)
                .map((milestone, index) => (
                  <TimelineItem key={milestone.id}>
                    <TimelineOppositeContent color="text.secondary">
                      {milestone.targetDate && (
                        <Box>
                          <Typography variant="body2">
                            Target: {new Date(milestone.targetDate).toLocaleDateString()}
                          </Typography>
                          {milestone.completedDate && (
                            <Typography variant="body2" color="success.main">
                              Completed: {new Date(milestone.completedDate).toLocaleDateString()}
                            </Typography>
                          )}
                        </Box>
                      )}
                    </TimelineOppositeContent>
                    <TimelineSeparator>
                      <TimelineDot
                        color={milestone.status === 'completed' ? 'success' : 
                               milestone.status === 'in_progress' ? 'primary' : 'grey'}
                      >
                        {milestone.status === 'completed' ? <CheckIcon /> :
                         milestone.status === 'in_progress' ? <ScheduleIcon /> :
                         <PendingIcon />}
                      </TimelineDot>
                      {index < careerPath.milestones.length - 1 && <TimelineConnector />}
                    </TimelineSeparator>
                    <TimelineContent>
                      <Card variant="outlined">
                        <CardContent>
                          <Box display="flex" justifyContent="space-between" alignItems="start">
                            <Box>
                              <Typography variant="h6" gutterBottom>
                                {milestone.title}
                              </Typography>
                              <Typography variant="body2" color="textSecondary" paragraph>
                                {milestone.description}
                              </Typography>
                              <Chip
                                label={milestone.status.replace('_', ' ')}
                                size="small"
                                color={milestone.status === 'completed' ? 'success' :
                                       milestone.status === 'in_progress' ? 'primary' : 'default'}
                              />
                            </Box>
                            <IconButton
                              size="small"
                              onClick={(e) => handleMenuOpen(e, milestone)}
                            >
                              <MoreIcon />
                            </IconButton>
                          </Box>
                        </CardContent>
                      </Card>
                    </TimelineContent>
                  </TimelineItem>
                ))}
            </Timeline>
          )}
        </CardContent>
      </Card>

      {/* Add Milestone Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Milestone</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Milestone Title"
            value={milestoneForm.title}
            onChange={(e) => setMilestoneForm({ ...milestoneForm, title: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={milestoneForm.description}
            onChange={(e) => setMilestoneForm({ ...milestoneForm, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
            required
          />
          <TextField
            fullWidth
            label="Target Date"
            type="date"
            value={milestoneForm.targetDate}
            onChange={(e) => setMilestoneForm({ ...milestoneForm, targetDate: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleAddMilestone}
            variant="contained"
            disabled={!milestoneForm.title || !milestoneForm.description}
          >
            Add Milestone
          </Button>
        </DialogActions>
      </Dialog>

      {/* Milestone Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {selectedMilestone?.status !== 'completed' && (
          <MenuItem onClick={() => handleCompleteMilestone(selectedMilestone!.id)}>
            <CheckIcon sx={{ mr: 1 }} /> Mark as Complete
          </MenuItem>
        )}
        <MenuItem onClick={handleMenuClose}>
          <EditIcon sx={{ mr: 1 }} /> Edit
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default CareerPathDetail;