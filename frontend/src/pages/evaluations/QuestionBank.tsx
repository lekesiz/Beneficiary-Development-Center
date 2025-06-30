import { ColumnDef, PaginationState, SortingState } from '@tanstack/react-table';
import {
  Plus,
  Search,
  Filter,
  Edit,
  Trash2,
  Copy,
  Eye,
  MoreHorizontal,
  BookOpen,
  Clock,
  Target,
  Hash,
} from 'lucide-react';
import * as React from 'react';
import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Modal } from '@/components/ui/Modal';
import type { QuestionBank } from '@/types/evaluation';

// Mock data for demonstration - this would come from a real API
const mockQuestionBankData = {
  questions: [
    {
      id: 1,
      uuid: 'uuid1',
      title: 'Temel Matematik Sorusu',
      description: 'Toplama işlemi',
      subject: 'Matematik',
      topic: 'Temel İşlemler',
      difficulty_level: 'easy' as const,
      question_text: '5 + 3 = ?',
      question_type: 'multiple_choice' as const,
      points: 1,
      question_data: {
        options: ['6', '7', '8', '9'],
        correct_answer: '8',
      },
      explanation: '5 + 3 = 8',
      hints: ['Toplama işlemi yapın'],
      usage_count: 15,
      last_used_at: '2024-01-15T10:30:00Z',
      created_by: 1,
      question_metadata: {},
      tags: ['matematik', 'toplama'],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-15T10:30:00Z',
    },
    {
      id: 2,
      uuid: 'uuid2',
      title: 'Türkçe Gramer Sorusu',
      description: 'Fiillerin çekimi',
      subject: 'Türkçe',
      topic: 'Gramer',
      difficulty_level: 'medium' as const,
      question_text: 'Aşağıdaki cümlede fiil hangisidir?',
      question_type: 'multiple_choice' as const,
      points: 2,
      question_data: {
        options: ['koşmak', 'hızlı', 'çocuk', 'park'],
        correct_answer: 'koşmak',
      },
      explanation: 'Koşmak bir fiildir, hareket bildirir.',
      hints: ['Hareket bildiren kelimeleri düşünün'],
      usage_count: 8,
      last_used_at: '2024-01-10T14:20:00Z',
      created_by: 1,
      question_metadata: {},
      tags: ['türkçe', 'gramer', 'fiil'],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-10T14:20:00Z',
    },
  ],
  pagination: {
    page: 1,
    per_page: 20,
    total: 2,
    pages: 1,
    has_prev: false,
    has_next: false,
  },
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

  return <Badge variant="outline">{labels[type as keyof typeof labels] || type}</Badge>;
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

// Actions dropdown component
const ActionsDropdown: React.FC<{
  question: QuestionBank;
  onView: (id: number) => void;
  onEdit: (id: number) => void;
  onCopy: (id: number) => void;
  onDelete: (id: number) => void;
}> = ({ question, onView, onEdit, onCopy, onDelete }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button onClick={() => setIsOpen(!isOpen)} className="p-2 hover:bg-gray-100 rounded-md">
        <MoreHorizontal className="h-4 w-4" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white border rounded-md shadow-lg z-10">
          <button
            onClick={() => {
              onView(question.id);
              setIsOpen(false);
            }}
            className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100"
          >
            <Eye className="mr-2 h-4 w-4" />
            Preview
          </button>
          <button
            onClick={() => {
              onEdit(question.id);
              setIsOpen(false);
            }}
            className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100"
          >
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </button>
          <button
            onClick={() => {
              onCopy(question.id);
              setIsOpen(false);
            }}
            className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100"
          >
            <Copy className="mr-2 h-4 w-4" />
            Copy
          </button>
          <hr className="my-1" />
          <button
            onClick={() => {
              onDelete(question.id);
              setIsOpen(false);
            }}
            className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </button>
        </div>
      )}
    </div>
  );
};

// Filters component
const QuestionFilters: React.FC<{
  filters: any;
  onFiltersChange: (filters: any) => void;
}> = ({ filters, onFiltersChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center px-4 py-2 border rounded-md hover:bg-gray-50"
      >
        <Filter className="mr-2 h-4 w-4" />
        Filter
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white border rounded-md shadow-lg z-10 p-4">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Topic</label>
              <input
                type="text"
                value={filters.subject || ''}
                onChange={(e) =>
                  onFiltersChange({
                    ...filters,
                    subject: e.target.value || undefined,
                  })
                }
                placeholder="Search topic..."
                className="w-full p-2 border rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Subtopic</label>
              <input
                type="text"
                value={filters.topic || ''}
                onChange={(e) =>
                  onFiltersChange({
                    ...filters,
                    topic: e.target.value || undefined,
                  })
                }
                placeholder="Search subtopic..."
                className="w-full p-2 border rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Question Type</label>
              <select
                value={filters.question_type || ''}
                onChange={(e) =>
                  onFiltersChange({
                    ...filters,
                    question_type: e.target.value || undefined,
                  })
                }
                className="w-full p-2 border rounded-md"
              >
                <option value="">All</option>
                <option value="multiple_choice">Multiple Choice</option>
                <option value="true_false">True/False</option>
                <option value="short_answer">Short Answer</option>
                <option value="essay">Essay</option>
                <option value="matching">Matching</option>
                <option value="ordering">Ordering</option>
                <option value="fill_in_blank">Fill in the Blank</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Difficulty</label>
              <select
                value={filters.difficulty_level || ''}
                onChange={(e) =>
                  onFiltersChange({
                    ...filters,
                    difficulty_level: e.target.value || undefined,
                  })
                }
                className="w-full p-2 border rounded-md"
              >
                <option value="">All</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Sort By</label>
              <select
                value={filters.sort_by || 'created_at'}
                onChange={(e) => onFiltersChange({ ...filters, sort_by: e.target.value })}
                className="w-full p-2 border rounded-md"
              >
                <option value="created_at">Creation Date</option>
                <option value="title">Title</option>
                <option value="usage_count">Usage Count</option>
                <option value="subject">Topic</option>
                <option value="difficulty_level">Difficulty</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="sort_desc"
                checked={filters.sort_desc || false}
                onChange={(e) => onFiltersChange({ ...filters, sort_desc: e.target.checked })}
                className="mr-2"
              />
              <label htmlFor="sort_desc" className="text-sm">
                Descending order
              </label>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t">
            <button
              onClick={() => setIsOpen(false)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Apply
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default function QuestionBank() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    page: 1,
    per_page: 20,
    sort_by: 'created_at',
    sort_desc: true,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    questionId?: number;
  }>({
    isOpen: false,
  });
  const [previewModal, setPreviewModal] = useState<{
    isOpen: boolean;
    question?: QuestionBank;
  }>({
    isOpen: false,
  });

  // For now using mock data - would use actual API hook
  const questionsData = mockQuestionBankData;
  const isLoading = false;

  // Pagination state
  const pagination: PaginationState = {
    pageIndex: (filters.page || 1) - 1,
    pageSize: filters.per_page || 20,
  };

  // Sorting state
  const sorting: SortingState = filters.sort_by
    ? [
        {
          id: filters.sort_by,
          desc: filters.sort_desc || false,
        },
      ]
    : [];

  // Table columns
  const columns: ColumnDef<QuestionBank>[] = useMemo(
    () => [
      {
        accessorKey: 'title',
        header: 'Title',
        cell: ({ row }) => (
          <div className="flex flex-col">
            <span className="font-medium">{row.original.title}</span>
            <span className="text-sm text-gray-500 truncate max-w-xs">
              {row.original.question_text}
            </span>
          </div>
        ),
      },
      {
        accessorKey: 'subject',
        header: 'Topic',
        cell: ({ row }) => (
          <div className="flex flex-col">
            <span className="font-medium">{row.original.subject}</span>
            {row.original.topic && (
              <span className="text-sm text-gray-500">{row.original.topic}</span>
            )}
          </div>
        ),
      },
      {
        accessorKey: 'question_type',
        header: 'Type',
        cell: ({ row }) => <QuestionTypeBadge type={row.original.question_type} />,
      },
      {
        accessorKey: 'difficulty_level',
        header: 'Difficulty',
        cell: ({ row }) => <DifficultyBadge level={row.original.difficulty_level} />,
      },
      {
        accessorKey: 'points',
        header: 'Points',
        cell: ({ row }) => row.original.points,
      },
      {
        accessorKey: 'usage_count',
        header: 'Usage',
        cell: ({ row }) => (
          <div className="flex items-center">
            <Hash className="mr-1 h-4 w-4 text-gray-400" />
            {row.original.usage_count}
          </div>
        ),
      },
      {
        accessorKey: 'last_used_at',
        header: 'Last Used',
        cell: ({ row }) =>
          row.original.last_used_at
            ? new Date(row.original.last_used_at).toLocaleDateString('en-US')
            : 'Never',
      },
      {
        accessorKey: 'tags',
        header: 'Tags',
        cell: ({ row }) => (
          <div className="flex flex-wrap gap-1">
            {row.original.tags.slice(0, 2).map((tag, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
            {row.original.tags.length > 2 && (
              <Badge variant="outline" className="text-xs">
                +{row.original.tags.length - 2}
              </Badge>
            )}
          </div>
        ),
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => (
          <ActionsDropdown
            question={row.original}
            onView={(id) =>
              setPreviewModal({
                isOpen: true,
                question: questionsData.questions.find((q) => q.id === id),
              })
            }
            onEdit={(id) => navigate(`/question-bank/${id}/edit`)}
            onCopy={(id) => navigate(`/question-bank/${id}/copy`)}
            onDelete={(id) => setDeleteModal({ isOpen: true, questionId: id })}
          />
        ),
      },
    ],
    [navigate, questionsData.questions]
  );

  // Handle pagination change
  const handlePaginationChange = (newPagination: PaginationState) => {
    setFilters((prev) => ({
      ...prev,
      page: newPagination.pageIndex + 1,
      per_page: newPagination.pageSize,
    }));
  };

  // Handle sorting change
  const handleSortingChange = (newSorting: SortingState) => {
    const sort = newSorting[0];
    setFilters((prev) => ({
      ...prev,
      sort_by: sort?.id,
      sort_desc: sort?.desc,
    }));
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Question Bank</h1>
          <p className="text-gray-600">Manage reusable questions</p>
        </div>
        <button
          onClick={() => navigate('/question-bank/create')}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Question
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center">
            <BookOpen className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Questions</p>
              <p className="text-2xl font-bold">{questionsData.pagination.total}</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Easy Questions</p>
              <p className="text-2xl font-bold">
                {questionsData.questions.filter((q) => q.difficulty_level === 'easy').length}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Medium Questions</p>
              <p className="text-2xl font-bold">
                {questionsData.questions.filter((q) => q.difficulty_level === 'medium').length}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Hard Questions</p>
              <p className="text-2xl font-bold">
                {questionsData.questions.filter((q) => q.difficulty_level === 'hard').length}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters and Search */}
      <div className="flex justify-between items-center">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search in question bank..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-md"
            />
          </div>
        </div>
        <QuestionFilters filters={filters} onFiltersChange={setFilters} />
      </div>

      {/* Data Table */}
      <Card>
        <DataTable
          columns={columns}
          data={questionsData.questions}
          loading={isLoading}
          pageCount={questionsData.pagination?.pages}
          pagination={pagination}
          onPaginationChange={handlePaginationChange}
          sorting={sorting}
          onSortingChange={handleSortingChange}
        />
      </Card>

      {/* Preview Modal */}
      <Modal
        isOpen={previewModal.isOpen}
        onClose={() => setPreviewModal({ isOpen: false })}
        title="Question Preview"
        size="lg"
      >
        {previewModal.question && (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
              <QuestionTypeBadge type={previewModal.question.question_type} />
              <DifficultyBadge level={previewModal.question.difficulty_level} />
              <span className="text-sm text-gray-500">{previewModal.question.points} points</span>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Question:</h3>
              <p className="text-gray-800">{previewModal.question.question_text}</p>
            </div>

            {previewModal.question.question_type === 'multiple_choice' && (
              <div>
                <h3 className="font-semibold mb-2">Options:</h3>
                <div className="space-y-2">
                  {previewModal.question.question_data.options?.map(
                    (option: string, index: number) => (
                      <div key={index} className="flex items-center space-x-2">
                        <span className="w-6 h-6 border rounded-full flex items-center justify-center text-xs">
                          {String.fromCharCode(65 + index)}
                        </span>
                        <span
                          className={
                            option === previewModal.question.question_data.correct_answer
                              ? 'text-green-600 font-medium'
                              : ''
                          }
                        >
                          {option}
                        </span>
                        {option === previewModal.question.question_data.correct_answer && (
                          <Badge variant="success" className="text-xs">
                            Correct
                          </Badge>
                        )}
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {previewModal.question.explanation && (
              <div>
                <h3 className="font-semibold mb-2">Explanation:</h3>
                <p className="text-blue-800 bg-blue-50 p-3 rounded">
                  {previewModal.question.explanation}
                </p>
              </div>
            )}

            {previewModal.question.tags.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Tags:</h3>
                <div className="flex flex-wrap gap-2">
                  {previewModal.question.tags.map((tag, index) => (
                    <Badge key={index} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false })}
        title="Delete Question"
      >
        <div className="space-y-4">
          <p>
            Are you sure you want to delete this question from the question bank? This action cannot
            be undone.
          </p>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => setDeleteModal({ isOpen: false })}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                // Handle delete
                setDeleteModal({ isOpen: false });
              }}
            >
              Delete
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
