import React, { useState, useEffect } from 'react';
import { Save, X, User, FileText, Tag, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select-new';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface Student {
  id: number;
  name: string;
  email: string;
}

interface Note {
  id?: number;
  student_id: number;
  title: string;
  content: string;
  category: string;
  priority: string;
  is_private: boolean;
  is_archived?: boolean;
}

interface NoteEditorProps {
  note?: Note | null;
  students: Student[];
  categories: string[];
  priorities: string[];
  onSubmit: (noteData: any) => void;
  onCancel: () => void;
}

export const NoteEditor: React.FC<NoteEditorProps> = ({
  note,
  students,
  categories,
  priorities,
  onSubmit,
  onCancel
}) => {
  const [formData, setFormData] = useState({
    student_id: '',
    title: '',
    content: '',
    category: 'general',
    priority: 'medium',
    is_private: false,
    is_archived: false
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (note) {
      setFormData({
        student_id: note.student_id.toString(),
        title: note.title,
        content: note.content,
        category: note.category,
        priority: note.priority,
        is_private: note.is_private,
        is_archived: note.is_archived || false
      });
    }
  }, [note]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.student_id) {
      newErrors.student_id = 'Please select a student';
    }

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must be less than 200 characters';
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Content is required';
    } else if (formData.content.length < 10) {
      newErrors.content = 'Content must be at least 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      const submitData = {
        ...formData,
        student_id: parseInt(formData.student_id),
        title: formData.title.trim(),
        content: formData.content.trim()
      };

      await onSubmit(submitData);
    } catch (error) {
      console.error('Error submitting note:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const selectedStudent = students.find(s => s.id.toString() === formData.student_id);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Student Selection */}
      <div className="space-y-2">
        <Label htmlFor="student" className="flex items-center gap-2">
          <User className="w-4 h-4" />
          Student *
        </Label>
        <Select
          value={formData.student_id}
          onValueChange={(value) => handleInputChange('student_id', value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select a student" />
          </SelectTrigger>
          <SelectContent>
            {students.map(student => (
              <SelectItem key={student.id} value={student.id.toString()}>
                <div className="flex flex-col">
                  <span className="font-medium">{student.name}</span>
                  <span className="text-sm text-gray-500">{student.email}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.student_id && (
          <p className="text-sm text-red-600">{errors.student_id}</p>
        )}
      </div>

      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="title" className="flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Title *
        </Label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => handleInputChange('title', e.target.value)}
          placeholder="Enter note title..."
          maxLength={200}
        />
        <div className="flex justify-between text-sm text-gray-500">
          {errors.title && <span className="text-red-600">{errors.title}</span>}
          <span className="ml-auto">{formData.title.length}/200</span>
        </div>
      </div>

      {/* Category and Priority */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="category" className="flex items-center gap-2">
            <Tag className="w-4 h-4" />
            Category
          </Label>
          <Select
            value={formData.category}
            onValueChange={(value) => handleInputChange('category', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {categories.map(category => (
                <SelectItem key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="priority" className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Priority
          </Label>
          <Select
            value={formData.priority}
            onValueChange={(value) => handleInputChange('priority', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {priorities.map(priority => (
                <SelectItem key={priority} value={priority}>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      priority === 'urgent' ? 'bg-red-500' :
                      priority === 'high' ? 'bg-orange-500' :
                      priority === 'medium' ? 'bg-yellow-500' :
                      'bg-gray-500'
                    }`} />
                    {priority.charAt(0).toUpperCase() + priority.slice(1)}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-2">
        <Label htmlFor="content">Content *</Label>
        <Textarea
          id="content"
          value={formData.content}
          onChange={(e) => handleInputChange('content', e.target.value)}
          placeholder="Enter your note content here..."
          rows={8}
          className="resize-none"
        />
        <div className="flex justify-between text-sm text-gray-500">
          {errors.content && <span className="text-red-600">{errors.content}</span>}
          <span className="ml-auto">{formData.content.length} characters</span>
        </div>
      </div>

      {/* Options */}
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="space-y-1">
            <Label htmlFor="is_private" className="font-medium">Private Note</Label>
            <p className="text-sm text-gray-600">
              Only you and administrators can view this note
            </p>
          </div>
          <Switch
            id="is_private"
            checked={formData.is_private}
            onCheckedChange={(checked) => handleInputChange('is_private', checked)}
          />
        </div>

        {note && (
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="space-y-1">
              <Label htmlFor="is_archived" className="font-medium">Archive Note</Label>
              <p className="text-sm text-gray-600">
                Archived notes are hidden from the main view
              </p>
            </div>
            <Switch
              id="is_archived"
              checked={formData.is_archived}
              onCheckedChange={(checked) => handleInputChange('is_archived', checked)}
            />
          </div>
        )}
      </div>

      {/* Selected Student Info */}
      {selectedStudent && (
        <Alert>
          <User className="w-4 h-4" />
          <AlertDescription>
            Creating note for: <strong>{selectedStudent.name}</strong> ({selectedStudent.email})
          </AlertDescription>
        </Alert>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          <X className="w-4 h-4 mr-2" />
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
          className="min-w-[120px]"
        >
          {isSubmitting ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Saving...
            </div>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              {note ? 'Update' : 'Create'} Note
            </>
          )}
        </Button>
      </div>
    </form>
  );
};