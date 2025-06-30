import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  Tooltip,
  Menu,
  Paper
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Edit as EditIcon,
  MoreVert as MoreIcon,
  Timer as TimerIcon,
  CalendarToday as CalendarIcon,
  LocationOn as LocationIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { complianceApi } from '../../../api/bilan';
import { useAuth } from '../../../contexts/AuthContext';
import type { BilanSession, BilanPhase, SessionStatus } from '../../../types/bilan';

const SessionManagement: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [sessions, setSessions] = useState<BilanSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [activeSession, setActiveSession] = useState<BilanSession | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedSession, setSelectedSession] = useState<BilanSession | null>(null);
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false);
  const [sessionForm, setSessionForm] = useState({
    beneficiaryId: user?.id || 0,
    consultantId: 0,
    phase: BilanPhase.PRELIMINARY,
    scheduledStart: new Date(),
    scheduledEnd: new Date(Date.now() + 2 * 60 * 60 * 1000), // 2 hours later
    location: '',
    isRemote: false,
    contractNumber: '',
    gdprConsentGiven: false
  });
  const [completionForm, setCompletionForm] = useState({
    durationMinutes: 120,
    sessionNotes: ''
  });

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await complianceApi.getSessions();
      setSessions(response.data.items);
      
      // Find active session
      const active = response.data.items.find(s => s.status === 'IN_PROGRESS');
      setActiveSession(active || null);
    } catch (err) {
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSession = async () => {
    try {
      await complianceApi.createSession({
        beneficiary_id: sessionForm.beneficiaryId,
        consultant_id: sessionForm.consultantId,
        phase: sessionForm.phase,
        scheduled_start: sessionForm.scheduledStart.toISOString(),
        scheduled_end: sessionForm.scheduledEnd.toISOString(),
        location: sessionForm.location,
        is_remote: sessionForm.isRemote,
        contract_number: sessionForm.contractNumber,
        gdpr_consent_given: sessionForm.gdprConsentGiven
      });
      setDialogOpen(false);
      fetchSessions();
    } catch (err) {
      console.error('Error creating session:', err);
    }
  };

  const handleStartSession = async (sessionId: number) => {
    try {
      await complianceApi.startSession(sessionId);
      fetchSessions();
      handleMenuClose();
    } catch (err) {
      console.error('Error starting session:', err);
    }
  };

  const handleCompleteSession = async () => {
    if (!selectedSession) return;
    
    try {
      await complianceApi.completeSession(selectedSession.id, {
        duration_minutes: completionForm.durationMinutes,
        session_notes: completionForm.sessionNotes
      });
      setCompleteDialogOpen(false);
      fetchSessions();
      handleMenuClose();
    } catch (err) {
      console.error('Error completing session:', err);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, session: BilanSession) => {
    setAnchorEl(event.currentTarget);
    setSelectedSession(session);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedSession(null);
  };

  const getStatusColor = (status: SessionStatus): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    switch (status) {
      case SessionStatus.SCHEDULED:
        return 'info';
      case SessionStatus.IN_PROGRESS:
        return 'warning';
      case SessionStatus.COMPLETED:
        return 'success';
      case SessionStatus.CANCELLED:
        return 'error';
      default:
        return 'default';
    }
  };

  const getPhaseIcon = (phase: BilanPhase) => {
    switch (phase) {
      case BilanPhase.PRELIMINARY:
        return '🎯';
      case BilanPhase.INVESTIGATION:
        return '🔍';
      case BilanPhase.CONCLUSION:
        return '📋';
      default:
        return '📄';
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box p={3}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">Session Management</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setDialogOpen(true)}
            disabled={!!activeSession}
          >
            Schedule Session
          </Button>
        </Box>

        {activeSession && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            Session in progress: {activeSession.phase} phase started at{' '}
            {new Date(activeSession.actualStart!).toLocaleTimeString()}
          </Alert>
        )}

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Phase</TableCell>
                <TableCell>Date & Time</TableCell>
                <TableCell>Beneficiary</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sessions.map(session => (
                <TableRow key={session.id}>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="h6">{getPhaseIcon(session.phase)}</Typography>
                      {session.phase}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        {new Date(session.scheduledStart).toLocaleDateString()}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {new Date(session.scheduledStart).toLocaleTimeString()} - 
                        {new Date(session.scheduledEnd).toLocaleTimeString()}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <PersonIcon fontSize="small" />
                      {session.beneficiary?.fullName || 'N/A'}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LocationIcon fontSize="small" />
                      {session.isRemote ? 'Remote' : session.location || 'TBD'}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={session.status}
                      color={getStatusColor(session.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {session.durationMinutes ? (
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <TimerIcon fontSize="small" />
                        {session.durationMinutes} min
                      </Box>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, session)}
                    >
                      <MoreIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Create Session Dialog */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Schedule New Session</DialogTitle>
          <DialogContent>
            <FormControl fullWidth margin="normal">
              <InputLabel>Phase</InputLabel>
              <Select
                value={sessionForm.phase}
                onChange={(e) => setSessionForm({ ...sessionForm, phase: e.target.value as BilanPhase })}
                label="Phase"
              >
                <MenuItem value={BilanPhase.PRELIMINARY}>
                  {getPhaseIcon(BilanPhase.PRELIMINARY)} Preliminary
                </MenuItem>
                <MenuItem value={BilanPhase.INVESTIGATION}>
                  {getPhaseIcon(BilanPhase.INVESTIGATION)} Investigation
                </MenuItem>
                <MenuItem value={BilanPhase.CONCLUSION}>
                  {getPhaseIcon(BilanPhase.CONCLUSION)} Conclusion
                </MenuItem>
              </Select>
            </FormControl>

            <DateTimePicker
              label="Start Date & Time"
              value={sessionForm.scheduledStart}
              onChange={(value) => value && setSessionForm({ ...sessionForm, scheduledStart: value })}
              slotProps={{ textField: { fullWidth: true, margin: 'normal' } }}
            />

            <DateTimePicker
              label="End Date & Time"
              value={sessionForm.scheduledEnd}
              onChange={(value) => value && setSessionForm({ ...sessionForm, scheduledEnd: value })}
              slotProps={{ textField: { fullWidth: true, margin: 'normal' } }}
            />

            <TextField
              fullWidth
              label="Contract Number"
              value={sessionForm.contractNumber}
              onChange={(e) => setSessionForm({ ...sessionForm, contractNumber: e.target.value })}
              margin="normal"
              required
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={sessionForm.isRemote}
                  onChange={(e) => setSessionForm({ ...sessionForm, isRemote: e.target.checked })}
                />
              }
              label="Remote Session"
              sx={{ mt: 2 }}
            />

            {!sessionForm.isRemote && (
              <TextField
                fullWidth
                label="Location"
                value={sessionForm.location}
                onChange={(e) => setSessionForm({ ...sessionForm, location: e.target.value })}
                margin="normal"
              />
            )}

            <FormControlLabel
              control={
                <Checkbox
                  checked={sessionForm.gdprConsentGiven}
                  onChange={(e) => setSessionForm({ ...sessionForm, gdprConsentGiven: e.target.checked })}
                />
              }
              label="GDPR Consent Obtained"
              sx={{ mt: 2 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleCreateSession}
              variant="contained"
              disabled={!sessionForm.contractNumber || !sessionForm.gdprConsentGiven}
            >
              Schedule Session
            </Button>
          </DialogActions>
        </Dialog>

        {/* Complete Session Dialog */}
        <Dialog open={completeDialogOpen} onClose={() => setCompleteDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Complete Session</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Duration (minutes)"
              type="number"
              value={completionForm.durationMinutes}
              onChange={(e) => setCompletionForm({ ...completionForm, durationMinutes: parseInt(e.target.value) })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Session Notes"
              value={completionForm.sessionNotes}
              onChange={(e) => setCompletionForm({ ...completionForm, sessionNotes: e.target.value })}
              margin="normal"
              multiline
              rows={4}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCompleteDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleCompleteSession}
              variant="contained"
            >
              Complete Session
            </Button>
          </DialogActions>
        </Dialog>

        {/* Actions Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          {selectedSession?.status === SessionStatus.SCHEDULED && (
            <MenuItem onClick={() => handleStartSession(selectedSession.id)}>
              <StartIcon sx={{ mr: 1 }} /> Start Session
            </MenuItem>
          )}
          {selectedSession?.status === SessionStatus.IN_PROGRESS && (
            <MenuItem onClick={() => {
              setCompleteDialogOpen(true);
              handleMenuClose();
            }}>
              <StopIcon sx={{ mr: 1 }} /> Complete Session
            </MenuItem>
          )}
          <MenuItem onClick={() => {
            navigate(`/bilan/compliance/sessions/${selectedSession?.id}`);
            handleMenuClose();
          }}>
            <EditIcon sx={{ mr: 1 }} /> View Details
          </MenuItem>
        </Menu>
      </Box>
    </LocalizationProvider>
  );
};

export default SessionManagement;