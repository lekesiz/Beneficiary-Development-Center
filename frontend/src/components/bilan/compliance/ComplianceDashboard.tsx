import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  LinearProgress,
  Paper,
  Avatar,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Gavel as GavelIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Timer as TimerIcon,
  Description as DocumentIcon,
  Security as SecurityIcon,
  Person as PersonIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { complianceApi } from '../../../api/bilan';
import { useAuth } from '../../../contexts/AuthContext';
import type { BilanSession, CertifiedConsultant, ComplianceCheck } from '../../../types/bilan';

const ComplianceDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [sessions, setSessions] = useState<BilanSession[]>([]);
  const [consultant, setConsultant] = useState<CertifiedConsultant | null>(null);
  const [complianceStats, setComplianceStats] = useState<any>(null);

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    try {
      setLoading(true);
      const [sessionsRes, statsRes] = await Promise.all([
        complianceApi.getSessions(),
        complianceApi.getComplianceStatistics()
      ]);
      
      setSessions(sessionsRes.data.items);
      setComplianceStats(statsRes.data);

      // Check if user is a certified consultant
      if (user?.role === 'consultant' || user?.role === 'admin') {
        const consultantsRes = await complianceApi.getCertifiedConsultants();
        const userConsultant = consultantsRes.data.find(c => c.userId === user.id);
        setConsultant(userConsultant || null);
      }
    } catch (err) {
      console.error('Error fetching compliance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPhaseProgress = () => {
    const phases = ['PRELIMINARY', 'INVESTIGATION', 'CONCLUSION'];
    const completedPhases = sessions
      .filter(s => s.status === 'COMPLETED')
      .map(s => s.phase);
    const uniqueCompleted = [...new Set(completedPhases)];
    return (uniqueCompleted.length / phases.length) * 100;
  };

  const getTotalHours = () => {
    return sessions.reduce((total, session) => total + (session.durationMinutes || 0), 0) / 60;
  };

  const isCompliant = () => {
    const totalHours = getTotalHours();
    const phaseProgress = getPhaseProgress();
    return totalHours >= 24 && phaseProgress === 100;
  };

  if (loading) {
    return (
      <Box p={3}>
        <Typography variant="h4" gutterBottom>Loading...</Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Legal Compliance Center
      </Typography>

      {/* Consultant Certification Card */}
      {consultant && (
        <Card sx={{ mb: 3, bgcolor: consultant.isActive ? 'success.light' : 'warning.light' }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <PersonIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">
                    Certified Consultant
                  </Typography>
                  <Typography variant="body2">
                    Certificate: {consultant.certificationNumber}
                  </Typography>
                  <Typography variant="body2">
                    Expires: {new Date(consultant.expiryDate).toLocaleDateString()}
                  </Typography>
                </Box>
              </Box>
              <Box textAlign="right">
                <Chip
                  label={consultant.isActive ? 'Active' : 'Inactive'}
                  color={consultant.isActive ? 'success' : 'warning'}
                />
                <Typography variant="body2" mt={1}>
                  {consultant.currentBilansCount} / {consultant.maxConcurrentBilans} Active Bilans
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Compliance Overview */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <GavelIcon color="primary" />
                <Typography variant="h6">Compliance Status</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={2}>
                {isCompliant() ? (
                  <CheckIcon color="success" sx={{ fontSize: 40 }} />
                ) : (
                  <WarningIcon color="warning" sx={{ fontSize: 40 }} />
                )}
                <Typography variant="h5">
                  {isCompliant() ? 'Compliant' : 'In Progress'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TimerIcon color="primary" />
                <Typography variant="h6">Total Hours</Typography>
              </Box>
              <Typography variant="h4">
                {getTotalHours().toFixed(1)}h
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min((getTotalHours() / 24) * 100, 100)}
                sx={{ mt: 1 }}
              />
              <Typography variant="body2" color="textSecondary" mt={1}>
                {getTotalHours() < 24 ? `${(24 - getTotalHours()).toFixed(1)}h remaining` : 'Requirement met'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <ScheduleIcon color="primary" />
                <Typography variant="h6">Phase Progress</Typography>
              </Box>
              <Typography variant="h4">
                {getPhaseProgress().toFixed(0)}%
              </Typography>
              <Box display="flex" gap={0.5} mt={2}>
                {['PRELIMINARY', 'INVESTIGATION', 'CONCLUSION'].map(phase => {
                  const isCompleted = sessions.some(s => s.phase === phase && s.status === 'COMPLETED');
                  return (
                    <Chip
                      key={phase}
                      label={phase.slice(0, 4)}
                      size="small"
                      color={isCompleted ? 'success' : 'default'}
                    />
                  );
                })}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <DocumentIcon color="primary" />
                <Typography variant="h6">Sessions</Typography>
              </Box>
              <Typography variant="h4">
                {sessions.length}
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                {sessions.filter(s => s.status === 'COMPLETED').length} completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box display="flex" gap={2} mb={3}>
        <Button
          variant="contained"
          startIcon={<ScheduleIcon />}
          onClick={() => navigate('/bilan/compliance/sessions/new')}
        >
          Schedule Session
        </Button>
        <Button
          variant="outlined"
          startIcon={<DocumentIcon />}
          onClick={() => navigate('/bilan/compliance/reports')}
        >
          Generate Reports
        </Button>
        <Button
          variant="outlined"
          startIcon={<SecurityIcon />}
          onClick={() => navigate('/bilan/compliance/gdpr')}
        >
          GDPR & Privacy
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Recent Sessions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Sessions
              </Typography>
              {sessions.length === 0 ? (
                <Alert severity="info">No sessions scheduled yet</Alert>
              ) : (
                <List>
                  {sessions.slice(0, 5).map((session, index) => (
                    <React.Fragment key={session.id}>
                      <ListItem
                        button
                        onClick={() => navigate(`/bilan/compliance/sessions/${session.id}`)}
                      >
                        <ListItemIcon>
                          <Avatar sx={{ bgcolor: getPhaseColor(session.phase) }}>
                            {session.phase.charAt(0)}
                          </Avatar>
                        </ListItemIcon>
                        <ListItemText
                          primary={`${session.phase} Phase`}
                          secondary={
                            <Box>
                              <Typography variant="body2">
                                {new Date(session.scheduledStart).toLocaleDateString()} • 
                                {session.durationMinutes ? ` ${session.durationMinutes} min` : ' Scheduled'}
                              </Typography>
                              <Chip
                                label={session.status}
                                size="small"
                                color={getStatusColor(session.status)}
                                sx={{ mt: 0.5 }}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < sessions.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance Requirements */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">
                  Legal Requirements
                </Typography>
                <Tooltip title="French Labor Code L6313-1">
                  <IconButton size="small">
                    <InfoIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <List>
                <ListItem>
                  <ListItemIcon>
                    {getTotalHours() >= 24 ? (
                      <CheckIcon color="success" />
                    ) : (
                      <WarningIcon color="warning" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="Minimum 24 hours duration"
                    secondary={`Current: ${getTotalHours().toFixed(1)} hours`}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    {getPhaseProgress() === 100 ? (
                      <CheckIcon color="success" />
                    ) : (
                      <WarningIcon color="warning" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="All 3 phases completed"
                    secondary={`Progress: ${getPhaseProgress().toFixed(0)}%`}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    {sessions.some(s => s.gdprConsentGiven) ? (
                      <CheckIcon color="success" />
                    ) : (
                      <WarningIcon color="warning" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="GDPR consent obtained"
                    secondary="Data protection compliance"
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon>
                    {sessions.some(s => s.contractNumber) ? (
                      <CheckIcon color="success" />
                    ) : (
                      <WarningIcon color="warning" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary="Contract established"
                    secondary="Written agreement required"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Data Retention Policy */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Data Retention & Privacy
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              All Bilan de Compétence data is retained for 6 years in compliance with French labor law.
              Beneficiaries have the right to access, modify, and delete their personal data.
            </Alert>
            <Box display="flex" gap={2}>
              <Button
                variant="outlined"
                onClick={() => navigate('/bilan/compliance/gdpr/consent')}
              >
                Manage Consents
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/bilan/compliance/data-retention')}
              >
                View Retention Policy
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );

  function getPhaseColor(phase: string) {
    switch (phase) {
      case 'PRELIMINARY':
        return 'info.main';
      case 'INVESTIGATION':
        return 'warning.main';
      case 'CONCLUSION':
        return 'success.main';
      default:
        return 'grey.500';
    }
  }

  function getStatusColor(status: string) {
    switch (status) {
      case 'SCHEDULED':
        return 'info';
      case 'IN_PROGRESS':
        return 'warning';
      case 'COMPLETED':
        return 'success';
      case 'CANCELLED':
        return 'error';
      default:
        return 'default';
    }
  }
};

export default ComplianceDashboard;