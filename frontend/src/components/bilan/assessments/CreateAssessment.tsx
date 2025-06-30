import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Alert,
  Grid
} from '@mui/material';
import { ArrowBack as BackIcon, Save as SaveIcon } from '@mui/icons-material';
import { assessmentApi } from '../../../api/bilan';
import { useAuth } from '../../../contexts/AuthContext';
import type { AssessmentType } from '../../../types/bilan';

const assessmentTypes = [
  { value: AssessmentType.SELF, label: 'Self Assessment', icon: '👤' },
  { value: AssessmentType.PEER, label: 'Peer Assessment', icon: '👥' },
  { value: AssessmentType.MANAGER, label: 'Manager Assessment', icon: '👔' },
  { value: AssessmentType.SUBORDINATE, label: 'Subordinate Assessment', icon: '👨‍💼' },
  { value: AssessmentType.CLIENT, label: 'Client Assessment', icon: '🤝' },
  { value: AssessmentType.OTHER, label: 'Other', icon: '📋' }
];

const CreateAssessment: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assessmentType: AssessmentType.SELF,
    beneficiaryId: user?.id || 0
  });

  const steps = ['Basic Information', 'Select Type', 'Review & Create'];

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      handleSubmit();
    } else {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await assessmentApi.createAssessment({
        title: formData.title,
        description: formData.description,
        assessment_type: formData.assessmentType,
        beneficiary_id: formData.beneficiaryId
      });
      navigate(`/bilan/assessments/${response.data.id}/questions`);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create assessment');
    } finally {
      setLoading(false);
    }
  };

  const isStepValid = () => {
    switch (activeStep) {
      case 0:
        return formData.title.trim() !== '';
      case 1:
        return true;
      case 2:
        return true;
      default:
        return false;
    }
  };

  return (
    <Box p={3}>
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/bilan/assessments')}
        sx={{ mb: 2 }}
      >
        Back to Assessments
      </Button>

      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Create New Assessment
          </Typography>

          <Stepper activeStep={activeStep} sx={{ mt: 3, mb: 4 }}>
            {steps.map(label => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {activeStep === 0 && (
            <Box>
              <TextField
                fullWidth
                label="Assessment Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                margin="normal"
                required
                helperText="Give your assessment a clear, descriptive title"
              />
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                margin="normal"
                multiline
                rows={4}
                helperText="Explain the purpose and scope of this assessment"
              />
            </Box>
          )}

          {activeStep === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Select Assessment Type
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Choose the type of feedback you want to collect
              </Typography>
              <Grid container spacing={2}>
                {assessmentTypes.map(type => (
                  <Grid item xs={12} sm={6} md={4} key={type.value}>
                    <Card
                      variant={formData.assessmentType === type.value ? 'elevation' : 'outlined'}
                      sx={{
                        cursor: 'pointer',
                        border: formData.assessmentType === type.value ? 2 : 1,
                        borderColor: formData.assessmentType === type.value ? 'primary.main' : 'divider'
                      }}
                      onClick={() => setFormData({ ...formData, assessmentType: type.value })}
                    >
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h2">{type.icon}</Typography>
                        <Typography variant="subtitle1">{type.label}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {activeStep === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Review Your Assessment
              </Typography>
              <Card variant="outlined" sx={{ p: 2, mb: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Title
                    </Typography>
                    <Typography variant="body1">{formData.title}</Typography>
                  </Grid>
                  {formData.description && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="textSecondary">
                        Description
                      </Typography>
                      <Typography variant="body1">{formData.description}</Typography>
                    </Grid>
                  )}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Assessment Type
                    </Typography>
                    <Typography variant="body1">
                      {assessmentTypes.find(t => t.value === formData.assessmentType)?.icon}{' '}
                      {assessmentTypes.find(t => t.value === formData.assessmentType)?.label}
                    </Typography>
                  </Grid>
                </Grid>
              </Card>
              <Alert severity="info">
                After creating the assessment, you'll be able to add questions and invite evaluators.
              </Alert>
            </Box>
          )}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
            >
              Back
            </Button>
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={!isStepValid() || loading}
              startIcon={activeStep === steps.length - 1 ? <SaveIcon /> : null}
            >
              {activeStep === steps.length - 1 ? 'Create Assessment' : 'Next'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CreateAssessment;