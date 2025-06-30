import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, FileText, User, Calendar, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select-new';
import { useToast } from '@/hooks/useToast';
import { coachNotesApi } from '@/api/coachNotes';
import { NoteEditor } from './NoteEditor';
import { NotesList } from './NotesList';

interface CoachNote {
  id: number;
  student_id: number;
  coach_id: number;
  title: string;
  content: string;
  category: string;
  priority: string;
  is_private: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  student_name: string;
  coach_name: string;
}

interface Student {
  id: number;
  name: string;
  email: string;
}

interface Filters {
  search: string;
  category: string;
  priority: string;
  student_id: string;
  is_archived: boolean;
}

export const CoachNotesManager: React.FC = () => {
  const [notes, setNotes] = useState<CoachNote[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [priorities, setPriorities] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingNote, setEditingNote] = useState<CoachNote | null>(null);
  const [filters, setFilters] = useState<Filters>({
    search: '',
    category: '',
    priority: '',
    student_id: '',
    is_archived: false
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  const { error: toastError, success: toastSuccess } = useToast();

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadNotes();
  }, [filters, currentPage]);

  const loadInitialData = async () => {
    try {
      const [categoriesRes, prioritiesRes, studentsRes] = await Promise.all([
        coachNotesApi.getCategories(),
        coachNotesApi.getPriorities(),
        // Assuming we have a students API endpoint
        fetch('/api/v1/users?role=student', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'X-Tenant-ID': '1'
          }
        }).then(res => res.json())
      ]);

      setCategories(categoriesRes.categories);
      setPriorities(prioritiesRes.priorities);
      setStudents(studentsRes.users || []);
    } catch (error) {
      toastError('Failed to load initial data');
      console.error('Error loading initial data:', error);
    }
  };

  const loadNotes = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: '10'
      });

      // Add filters to params
      if (filters.search) params.append('search', filters.search);
      if (filters.category) params.append('category', filters.category);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.student_id) params.append('student_id', filters.student_id);
      if (filters.is_archived) params.append('is_archived', 'true');

      const response = await coachNotesApi.getNotes(params.toString());
      setNotes(response.notes);
      setTotalPages(response.pagination?.pages || 0);
    } catch (error) {
      toastError('Failed to load notes');
      console.error('Error loading notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNote = () => {
    setEditingNote(null);
    setIsEditorOpen(true);
  };

  const handleEditNote = (note: CoachNote) => {
    setEditingNote(note);
    setIsEditorOpen(true);
  };

  const handleNoteSubmit = async (noteData: any) => {
    try {
      if (editingNote) {
        await coachNotesApi.updateNote(editingNote.id, noteData);
        toastSuccess('Note updated successfully');
      } else {
        await coachNotesApi.createNote(noteData);
        toastSuccess('Note created successfully');
      }
      
      setIsEditorOpen(false);
      setEditingNote(null);
      loadNotes();
    } catch (error) {
      toastError('Failed to save note');
      console.error('Error saving note:', error);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
      await coachNotesApi.deleteNote(noteId);
      toastSuccess('Note deleted successfully');
      loadNotes();
    } catch (error) {
      toastError('Failed to delete note');
      console.error('Error deleting note:', error);
    }
  };

  const handleFilterChange = (key: keyof Filters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      priority: '',
      student_id: '',
      is_archived: false
    });
    setCurrentPage(1);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'destructive';
      case 'high': return 'warning';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'default';
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'progress': 'success',
      'observation': 'info',
      'recommendation': 'warning',
      'concern': 'destructive',
      'achievement': 'success',
      'behavior': 'secondary',
      'skill_development': 'info',
      'goal_setting': 'default',
      'feedback': 'default',
      'general': 'default'
    };
    return colors[category] || 'default';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Coach Notes</h1>
          <p className="text-gray-600 mt-1">Manage student progress notes and observations</p>
        </div>
        
        <Dialog open={isEditorOpen} onOpenChange={setIsEditorOpen}>
          <DialogTrigger asChild>
            <Button onClick={handleCreateNote} className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Create Note
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingNote ? 'Edit Note' : 'Create New Note'}
              </DialogTitle>
            </DialogHeader>
            <NoteEditor
              note={editingNote}
              students={students}
              categories={categories}
              priorities={priorities}
              onSubmit={handleNoteSubmit}
              onCancel={() => setIsEditorOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Notes</p>
                <p className="text-2xl font-bold text-gray-900">{notes.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <User className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Students</p>
                <p className="text-2xl font-bold text-gray-900">{students.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <AlertCircle className="w-8 h-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">High Priority</p>
                <p className="text-2xl font-bold text-gray-900">
                  {notes.filter(n => n.priority === 'high' || n.priority === 'urgent').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Calendar className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">This Week</p>
                <p className="text-2xl font-bold text-gray-900">
                  {notes.filter(n => {
                    const noteDate = new Date(n.created_at);
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    return noteDate >= weekAgo;
                  }).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Filter className="w-5 h-5" />
              Filters
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              {showFilters ? 'Hide' : 'Show'} Filters
            </Button>
          </div>
        </CardHeader>
        
        {showFilters && (
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Search notes..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="pl-10"
                />
              </div>

              <Select
                value={filters.student_id}
                onValueChange={(value) => handleFilterChange('student_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select student" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All students</SelectItem>
                  {students.map(student => (
                    <SelectItem key={student.id} value={student.id.toString()}>
                      {student.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select
                value={filters.category}
                onValueChange={(value) => handleFilterChange('category', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All categories</SelectItem>
                  {categories.map(category => (
                    <SelectItem key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select
                value={filters.priority}
                onValueChange={(value) => handleFilterChange('priority', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All priorities</SelectItem>
                  {priorities.map(priority => (
                    <SelectItem key={priority} value={priority}>
                      {priority.charAt(0).toUpperCase() + priority.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Notes List */}
      <NotesList
        notes={notes}
        loading={loading}
        onEdit={handleEditNote}
        onDelete={handleDeleteNote}
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
        getPriorityColor={getPriorityColor}
        getCategoryColor={getCategoryColor}
      />
    </div>
  );
};

export default CoachNotesManager;