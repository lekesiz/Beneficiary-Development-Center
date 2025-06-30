import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  DragIndicator as DragIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { assessmentApi } from '../../../api/bilan';
import type { AssessmentQuestion, Competency } from '../../../types/bilan';

const categories = [
  'Communication',
  'Leadership',
  'Technical Skills',
  'Problem Solving',
  'Teamwork',
  'Innovation',
  'Customer Focus',
  'Adaptability',
  'Time Management',
  'Strategic Thinking'
];

const AssessmentQuestions: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [competencies, setCompetencies] = useState<Competency[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<AssessmentQuestion | null>(null);
  const [formData, setFormData] = useState({
    question: '',
    category: '',
    competencyId: null as number | null,
    isRequired: true
  });

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [questionsRes, competenciesRes] = await Promise.all([
        assessmentApi.getAssessmentQuestions(Number(id)),
        assessmentApi.getCompetencies()
      ]);
      setQuestions(questionsRes.data);
      setCompetencies(competenciesRes.data);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    const items = Array.from(questions);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    // Update order property
    const updatedItems = items.map((item, index) => ({
      ...item,
      order: index + 1
    }));

    setQuestions(updatedItems);
  };

  const handleAddQuestion = () => {
    setEditingQuestion(null);
    setFormData({
      question: '',
      category: '',
      competencyId: null,
      isRequired: true
    });
    setDialogOpen(true);
  };

  const handleEditQuestion = (question: AssessmentQuestion) => {
    setEditingQuestion(question);
    setFormData({
      question: question.question,
      category: question.category,
      competencyId: question.competencyId || null,
      isRequired: question.isRequired
    });
    setDialogOpen(true);
  };

  const handleSaveQuestion = async () => {
    if (editingQuestion) {
      // Update existing question
      const updatedQuestions = questions.map(q =>
        q.id === editingQuestion.id
          ? {
              ...q,
              question: formData.question,
              category: formData.category,
              competencyId: formData.competencyId,
              isRequired: formData.isRequired
            }
          : q
      );
      setQuestions(updatedQuestions);
    } else {
      // Add new question
      const newQuestion: Partial<AssessmentQuestion> = {
        question: formData.question,
        category: formData.category,
        competencyId: formData.competencyId || undefined,
        isRequired: formData.isRequired,
        order: questions.length + 1
      };
      
      try {
        const response = await assessmentApi.addAssessmentQuestions(Number(id), [newQuestion]);
        setQuestions([...questions, ...response.data]);
      } catch (err) {
        console.error('Error adding question:', err);
      }
    }
    
    setDialogOpen(false);
  };

  const handleDeleteQuestion = (questionId: number) => {
    setQuestions(questions.filter(q => q.id !== questionId));
  };

  const handleSaveAll = async () => {
    try {
      // Save all questions with their current order
      await assessmentApi.addAssessmentQuestions(Number(id), questions);
      navigate(`/bilan/assessments/${id}/invite`);
    } catch (err) {
      console.error('Error saving questions:', err);
    }
  };

  return (
    <Box p={3}>
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate(`/bilan/assessments/${id}`)}
        sx={{ mb: 2 }}
      >
        Back to Assessment
      </Button>

      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5">
              Assessment Questions
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddQuestion}
            >
              Add Question
            </Button>
          </Box>

          {questions.length === 0 ? (
            <Alert severity="info">
              No questions added yet. Add questions to build your assessment.
            </Alert>
          ) : (
            <DragDropContext onDragEnd={handleDragEnd}>
              <Droppable droppableId="questions">
                {(provided) => (
                  <List {...provided.droppableProps} ref={provided.innerRef}>
                    {questions.map((question, index) => (
                      <Draggable
                        key={question.id}
                        draggableId={String(question.id)}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <ListItem
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            sx={{
                              mb: 1,
                              bgcolor: snapshot.isDragging ? 'action.hover' : 'background.paper',
                              border: 1,
                              borderColor: 'divider',
                              borderRadius: 1
                            }}
                          >
                            <Box {...provided.dragHandleProps} sx={{ mr: 2 }}>
                              <DragIcon color="action" />
                            </Box>
                            <ListItemText
                              primary={
                                <Box display="flex" alignItems="center" gap={1}>
                                  <Typography variant="body1">
                                    {index + 1}. {question.question}
                                  </Typography>
                                  {question.isRequired && (
                                    <Chip label="Required" size="small" color="error" />
                                  )}
                                </Box>
                              }
                              secondary={
                                <Box display="flex" gap={1} mt={1}>
                                  <Chip label={question.category} size="small" />
                                  {question.competency && (
                                    <Chip
                                      label={question.competency.name}
                                      size="small"
                                      color="primary"
                                    />
                                  )}
                                </Box>
                              }
                            />
                            <ListItemSecondaryAction>
                              <IconButton
                                edge="end"
                                onClick={() => handleEditQuestion(question)}
                                sx={{ mr: 1 }}
                              >
                                <EditIcon />
                              </IconButton>
                              <IconButton
                                edge="end"
                                onClick={() => handleDeleteQuestion(question.id)}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </List>
                )}
              </Droppable>
            </DragDropContext>
          )}

          <Box display="flex" justifyContent="flex-end" gap={2} mt={3}>
            <Button
              variant="outlined"
              onClick={() => navigate(`/bilan/assessments/${id}`)}
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSaveAll}
              disabled={questions.length === 0}
            >
              Save & Continue
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingQuestion ? 'Edit Question' : 'Add Question'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Question"
            value={formData.question}
            onChange={(e) => setFormData({ ...formData, question: e.target.value })}
            margin="normal"
            multiline
            rows={3}
            required
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Category</InputLabel>
            <Select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value as string })}
              label="Category"
            >
              {categories.map(category => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Autocomplete
            options={competencies}
            getOptionLabel={(option) => option.name}
            value={competencies.find(c => c.id === formData.competencyId) || null}
            onChange={(_, value) => setFormData({ ...formData, competencyId: value?.id || null })}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Competency (Optional)"
                margin="normal"
                fullWidth
              />
            )}
          />

          <FormControlLabel
            control={
              <Checkbox
                checked={formData.isRequired}
                onChange={(e) => setFormData({ ...formData, isRequired: e.target.checked })}
              />
            }
            label="Required question"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveQuestion}
            variant="contained"
            disabled={!formData.question || !formData.category}
          >
            {editingQuestion ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AssessmentQuestions;