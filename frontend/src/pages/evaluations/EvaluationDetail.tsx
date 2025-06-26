import {
  ArrowLeft,
  Edit,
  Play,
  Archive,
  Trash2,
  Clock,
  FileText,
  Users,
  Calendar,
  Plus,
  MoreHorizontal,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Modal } from '@/components/ui/Modal';
import {
  useEvaluation,
  useEvaluationQuestions,
  useDeleteEvaluation,
  useActivateEvaluation,
  useArchiveEvaluation,
} from '@/hooks/useEvaluations';
import type { Question } from '@/types/evaluation';

// Status badge component
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const variants = {
    draft: 'secondary',
    active: 'success',
    archived: 'warning',
    completed: 'default',
  } as const;

  const labels = {
    draft: 'Draft',
    active: 'Active',
    archived: 'Archived',
    completed: 'Completed',
  };

  return (
    <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>
      {labels[status as keyof typeof labels] || status}
    </Badge>
  );
};

// Question type badge
const QuestionTypeBadge: React.FC<{ type: string }> = ({ type }) => {
  const labels = {
    multiple_choice: 'Multiple Choice',
    true_false: 'True/False',
    short_answer: 'Short Answer',
    essay: 'Essay',
    matching: 'Matching',
    ordering: 'Ordering',
    fill_in_blank: 'Fill in the Blank',
  };

  return (
    <Badge variant="outline">
      {labels[type as keyof typeof labels] || type}
    </Badge>
  );
};

// Difficulty badge
const DifficultyBadge: React.FC<{ level: string }> = ({ level }) => {
  const variants = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger',
  } as const;

  const labels = {
    easy: 'Easy',
    medium: 'Medium',
    hard: 'Hard',
  };

  return (
    <Badge variant={variants[level as keyof typeof variants] || 'secondary'}>
      {labels[level as keyof typeof labels] || level}
    </Badge>
  );
};

// Question card component
const QuestionCard: React.FC<{
  question: Question;
  index: number;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}> = ({ question, index, onEdit, onDelete }) => {
  const [showActions, setShowActions] = useState(false);

  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center space-x-2">
          <span className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full text-sm font-medium">
            {index + 1}
          </span>
          <QuestionTypeBadge type={question.question_type} />
          <DifficultyBadge level={question.difficulty_level} />
          <span className="text-sm text-gray-500">{question.points} points</span>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowActions(!showActions)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <MoreHorizontal className="h-4 w-4" />
          </button>

          {showActions && (
            <div className="absolute right-0 mt-2 w-32 bg-white border rounded-md shadow-lg z-10">
              <button
                onClick={() => {
                  onEdit(question.id);
                  setShowActions(false);
                }}
                className="flex items-center w-full px-3 py-2 text-sm hover:bg-gray-100"
              >
                <Edit className="mr-2 h-3 w-3" />
                Edit
              </button>
              <button
                onClick={() => {
                  onDelete(question.id);
                  setShowActions(false);
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                <Trash2 className="mr-2 h-3 w-3" />
                Delete
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-gray-800">{question.question_text}</p>

        {/* Show question data based on type */}
        {question.question_type === 'multiple_choice' &&
          question.question_data.options && (
            <div className="ml-4 space-y-1">
              {question.question_data.options.map(
                (option: string, idx: number) => (
                  <div key={idx} className="flex items-center space-x-2">
                    <span className="w-6 h-6 border rounded-full flex items-center justify-center text-xs">
                      {String.fromCharCode(65 + idx)}
                    </span>
                    <span
                      className={`text-sm ${
                        option === question.question_data.correct_answer
                          ? 'text-green-600 font-medium'
                          : 'text-gray-600'
                      }`}
                    >
                      {option}
                      {option === question.question_data.correct_answer && (
                        <CheckCircle className="inline ml-1 h-3 w-3" />
                      )}
                    </span>
                  </div>
                )
              )}
            </div>
          )}

        {question.question_type === 'true_false' && (
          <div className="ml-4">
            <span className="text-sm text-gray-600">
              Correct answer:
              <span className="ml-1 font-medium text-green-600">
                {question.question_data.correct_answer ? 'True' : 'False'}
              </span>
            </span>
          </div>
        )}

        {question.explanation && (
          <div className="mt-3 p-3 bg-blue-50 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>Explanation:</strong> {question.explanation}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default function EvaluationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    questionId?: number;
  }>({
    isOpen: false,
  });

  const evaluationId = parseInt(id!);

  // React Query hooks
  const {
    data: evaluation,
    isLoading,
    error,
  } = useEvaluation(evaluationId, true);
  const { data: questions, isLoading: questionsLoading } =
    useEvaluationQuestions(evaluationId);
  const deleteMutation = useDeleteEvaluation();
  const activateMutation = useActivateEvaluation();
  const archiveMutation = useArchiveEvaluation();

  // Handle actions
  const handleActivate = () => {
    activateMutation.mutate(evaluationId);
  };

  const handleArchive = () => {
    archiveMutation.mutate(evaluationId);
  };

  const handleDelete = () => {
    deleteMutation.mutate(evaluationId, {
      onSuccess: () => {
        navigate('/evaluations');
      },
    });
  };

  if (isLoading) {
    return (
      <div className="p-6 flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">Error loading evaluation.</p>
          <button
            onClick={() => navigate('/evaluations')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/evaluations')}
            className="p-2 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">{evaluation.title}</h1>
            <div className="flex items-center space-x-4 mt-1">
              <StatusBadge status={evaluation.status} />
              <span className="text-sm text-gray-500">
                {new Date(evaluation.created_at).toLocaleDateString('tr-TR')}{' '}
                created on
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {evaluation.status === 'draft' && (
            <button
              onClick={handleActivate}
              disabled={activateMutation.isPending}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              <Play className="mr-2 h-4 w-4" />
              {activateMutation.isPending
                ? 'Activating...'
                : 'Activate'}
            </button>
          )}

          {evaluation.status === 'active' && (
            <button
              onClick={handleArchive}
              disabled={archiveMutation.isPending}
              className="flex items-center px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50"
            >
              <Archive className="mr-2 h-4 w-4" />
              {archiveMutation.isPending ? 'Archiving...' : 'Archive'}
            </button>
          )}

          <button
            onClick={() => navigate(`/evaluations/${evaluationId}/edit`)}
            className="flex items-center px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            <Edit className="mr-2 h-4 w-4" />
            Düzenle
          </button>

          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Evaluation Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">General Information</h2>

            {evaluation.description && (
              <div className="mb-4">
                <h3 className="font-medium text-gray-700 mb-2">Description</h3>
                <p className="text-gray-600">{evaluation.description}</p>
              </div>
            )}

            {evaluation.instructions && (
              <div className="mb-4">
                <h3 className="font-medium text-gray-700 mb-2">Instructions</h3>
                <div className="p-3 bg-blue-50 rounded-md">
                  <p className="text-blue-800">{evaluation.instructions}</p>
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="text-center">
                <FileText className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Number of Questions</p>
                <p className="text-lg font-semibold">
                  {evaluation.total_questions}
                </p>
              </div>

              <div className="text-center">
                <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-green-600 font-bold text-sm">P</span>
                </div>
                <p className="text-sm text-gray-600">Total Points</p>
                <p className="text-lg font-semibold">
                  {evaluation.total_points}
                </p>
              </div>

              <div className="text-center">
                <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-yellow-600 font-bold text-sm">%</span>
                </div>
                <p className="text-sm text-gray-600">Passing Score</p>
                <p className="text-lg font-semibold">
                  {evaluation.passing_score}%
                </p>
              </div>

              <div className="text-center">
                <Clock className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Duration</p>
                <p className="text-lg font-semibold">
                  {evaluation.duration_display}
                </p>
              </div>
            </div>
          </Card>

          {/* Questions Section */}
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">
                Questions ({questions?.length || 0})
              </h2>
              <button
                onClick={() =>
                  navigate(`/evaluations/${evaluationId}/questions/create`)
                }
                className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
              >
                <Plus className="mr-1 h-4 w-4" />
                Add Question
              </button>
            </div>

            {questionsLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : questions && questions.length > 0 ? (
              <div className="space-y-4">
                {questions.map((question, index) => (
                  <QuestionCard
                    key={question.id}
                    question={question}
                    index={index}
                    onEdit={(id) =>
                      navigate(
                        `/evaluations/${evaluationId}/questions/${id}/edit`
                      )
                    }
                    onDelete={(id) =>
                      setDeleteModal({ isOpen: true, questionId: id })
                    }
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No questions added yet</p>
                <button
                  onClick={() =>
                    navigate(`/evaluations/${evaluationId}/questions/create`)
                  }
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Add First Question
                </button>
              </div>
            )}
          </Card>
        </div>

        {/* Right Column - Settings and Info */}
        <div className="space-y-6">
          {/* Settings */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Settings</h2>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Maximum Attempts</span>
                <span className="font-medium">{evaluation.max_attempts}</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Shuffle Questions</span>
                <span className="font-medium">
                  {evaluation.shuffle_questions ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-600" />
                  )}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">
                  Show Results Immediately
                </span>
                <span className="font-medium">
                  {evaluation.show_results_immediately ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-600" />
                  )}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">
                  Allow Review
                </span>
                <span className="font-medium">
                  {evaluation.allow_review ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-600" />
                  )}
                </span>
              </div>
            </div>
          </Card>

          {/* Availability */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Availability</h2>

            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Badge
                  variant={evaluation.is_available ? 'success' : 'secondary'}
                >
                  {evaluation.is_available ? 'Available' : 'Not Available'}
                </Badge>
              </div>

              {evaluation.available_from && (
                <div>
                  <span className="text-sm text-gray-600">Start:</span>
                  <p className="font-medium">
                    {new Date(evaluation.available_from).toLocaleString(
                      'tr-TR'
                    )}
                  </p>
                </div>
              )}

              {evaluation.available_until && (
                <div>
                  <span className="text-sm text-gray-600">End:</span>
                  <p className="font-medium">
                    {new Date(evaluation.available_until).toLocaleString(
                      'tr-TR'
                    )}
                  </p>
                </div>
              )}
            </div>
          </Card>

          {/* Course/Program Info */}
          {(evaluation.course_title || evaluation.program_title) && (
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">Related To</h2>

              <div className="space-y-2">
                {evaluation.program_title && (
                  <div>
                    <span className="text-sm text-gray-600">Program:</span>
                    <p className="font-medium">{evaluation.program_title}</p>
                  </div>
                )}

                {evaluation.course_title && (
                  <div>
                    <span className="text-sm text-gray-600">Kurs:</span>
                    <p className="font-medium">{evaluation.course_title}</p>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Delete Question Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false })}
        title="Delete Question"
      >
        <div className="space-y-4">
          <p>
            Are you sure you want to delete this question? This action cannot be undone.
          </p>
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setDeleteModal({ isOpen: false })}
              className="px-4 py-2 border rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                // Handle question delete
                setDeleteModal({ isOpen: false });
              }}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Sil
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
