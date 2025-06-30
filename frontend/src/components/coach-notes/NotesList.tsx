import React from 'react';
import { Edit, Trash2, EyeOff, Calendar, User, FileText, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/Skeleton';
import { formatDistance } from 'date-fns';

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

interface NotesListProps {
  notes: CoachNote[];
  loading: boolean;
  onEdit: (note: CoachNote) => void;
  onDelete: (noteId: number) => void;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  getPriorityColor: (priority: string) => string;
  getCategoryColor: (category: string) => string;
}

export const NotesList: React.FC<NotesListProps> = ({
  notes,
  loading,
  onEdit,
  onDelete,
  currentPage,
  totalPages,
  onPageChange,
  getPriorityColor,
  getCategoryColor
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return formatDistance(date, new Date(), { addSuffix: true });
  };

  const truncateContent = (content: string, maxLength: number = 150) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Skeleton className="h-6 w-1/3" />
                  <div className="flex gap-2">
                    <Skeleton className="h-6 w-16" />
                    <Skeleton className="h-6 w-16" />
                  </div>
                </div>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
                <div className="flex items-center justify-between">
                  <Skeleton className="h-4 w-24" />
                  <div className="flex gap-2">
                    <Skeleton className="h-8 w-8 rounded" />
                    <Skeleton className="h-8 w-8 rounded" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (notes.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No notes found</h3>
          <p className="text-gray-600">
            No coach notes match your current filters. Try adjusting your search criteria.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Notes Grid */}
      <div className="space-y-4">
        {notes.map((note) => (
          <Card key={note.id} className="hover:shadow-md transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
                        {note.title}
                      </h3>
                      {note.is_private && (
                        <div className="flex items-center gap-1 text-orange-600">
                          <EyeOff className="w-4 h-4" />
                          <span className="text-xs font-medium">Private</span>
                        </div>
                      )}
                      {note.is_archived && (
                        <Badge variant="secondary" className="text-xs">
                          Archived
                        </Badge>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        <span>{note.student_name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(note.created_at)}</span>
                      </div>
                      <span>by {note.coach_name}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <Badge variant={getPriorityColor(note.priority)} className="text-xs">
                      {note.priority}
                    </Badge>
                    <Badge variant={getCategoryColor(note.category)} className="text-xs">
                      {note.category.replace('_', ' ')}
                    </Badge>
                  </div>
                </div>

                {/* Content */}
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 leading-relaxed">
                    {truncateContent(note.content)}
                  </p>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="text-xs text-gray-500">
                    {note.created_at !== note.updated_at && (
                      <span>Updated {formatDate(note.updated_at)}</span>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onEdit(note)}
                      className="flex items-center gap-1"
                    >
                      <Edit className="w-3 h-3" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onDelete(note.id)}
                      className="flex items-center gap-1 text-red-600 hover:text-red-700 hover:border-red-300"
                    >
                      <Trash2 className="w-3 h-3" />
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Page {currentPage} of {totalPages}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="flex items-center gap-1"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Button>
            
            {/* Page numbers */}
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }

                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => onPageChange(pageNum)}
                    className="w-8 h-8 p-0"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="flex items-center gap-1"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};