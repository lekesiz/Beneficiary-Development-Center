import { MessageSquare, Plus, Edit2, Trash2, Save, X } from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { useAddCoachNote } from '@/hooks/useStudentProfile';
import { formatDate } from '@/utils/date';

interface CoachNote {
  id: number;
  student_id: number;
  coach_id: number;
  note: string;
  category: string;
  created_at: string;
}

interface CoachNotesSectionProps {
  studentId: number;
  notes: CoachNote[];
}

export default function CoachNotesSection({
  studentId,
  notes,
}: CoachNotesSectionProps) {
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [newNote, setNewNote] = useState('');
  const [newCategory, setNewCategory] = useState<string>('general');
  const addNoteMutation = useAddCoachNote();

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    try {
      await addNoteMutation.mutateAsync({
        studentId,
        note: newNote,
        category: newCategory,
      });

      setNewNote('');
      setNewCategory('general');
      setIsAddingNote(false);
    } catch (error) {
      console.error('Failed to add note:', error);
    }
  };

  const getCategoryBadgeVariant = (category: string) => {
    switch (category) {
      case 'academic':
        return 'primary';
      case 'behavioral':
        return 'warning';
      case 'other':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'academic':
        return 'Akademik';
      case 'behavioral':
        return 'Davranışsal';
      case 'other':
        return 'Diğer';
      default:
        return 'Genel';
    }
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center">
          <MessageSquare className="mr-2 h-5 w-5" />
          Koç Notları
        </h3>
        {!isAddingNote && (
          <Button size="sm" onClick={() => setIsAddingNote(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Not Ekle
          </Button>
        )}
      </div>

      {/* Add Note Form */}
      {isAddingNote && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Kategori
              </label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="general">Genel</option>
                <option value="academic">Akademik</option>
                <option value="behavioral">Davranışsal</option>
                <option value="other">Diğer</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Not
              </label>
              <textarea
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Öğrenci hakkında gözlem veya öneri yazın..."
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setIsAddingNote(false);
                  setNewNote('');
                  setNewCategory('general');
                }}
              >
                <X className="mr-2 h-4 w-4" />
                İptal
              </Button>
              <Button
                size="sm"
                onClick={handleAddNote}
                disabled={!newNote.trim() || addNoteMutation.isPending}
              >
                <Save className="mr-2 h-4 w-4" />
                Kaydet
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Notes List */}
      {notes.length > 0 ? (
        <div className="space-y-3">
          {notes.map((note) => (
            <div key={note.id} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <Badge
                      variant={getCategoryBadgeVariant(note.category)}
                      size="sm"
                    >
                      {getCategoryLabel(note.category)}
                    </Badge>
                    <span className="ml-2 text-sm text-gray-500">
                      {formatDate(note.created_at)}
                    </span>
                  </div>
                  <p className="text-gray-700 whitespace-pre-wrap">
                    {note.note}
                  </p>
                </div>
                {/* In a real app, you'd add edit/delete functionality here */}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">Henüz not eklenmemiş</p>
          {!isAddingNote && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsAddingNote(true)}
              className="mt-3"
            >
              İlk Notu Ekle
            </Button>
          )}
        </div>
      )}
    </Card>
  );
}
