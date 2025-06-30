import apiClient from './client';

export interface CoachNote {
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

export interface CreateNoteData {
  student_id: number;
  title: string;
  content: string;
  category?: string;
  priority?: string;
  is_private?: boolean;
}

export interface UpdateNoteData {
  title: string;
  content: string;
  category?: string;
  priority?: string;
  is_private?: boolean;
  is_archived?: boolean;
}

export interface NotesResponse {
  notes: CoachNote[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters: {
    student_id?: number;
    coach_id?: number;
    category?: string;
    priority?: string;
    is_archived?: boolean;
    search?: string;
  };
}

export const coachNotesApi = {
  // Get notes with filtering and pagination
  async getNotes(queryParams?: string): Promise<NotesResponse> {
    const url = queryParams ? `/coach-notes?${queryParams}` : '/coach-notes';
    const response = await apiClient.get(url);
    return response.data;
  },

  // Get a specific note by ID
  async getNote(id: number): Promise<{ note: CoachNote }> {
    const response = await apiClient.get(`/coach-notes/${id}`);
    return response.data;
  },

  // Create a new note
  async createNote(data: CreateNoteData): Promise<{ note: CoachNote; message: string }> {
    const response = await apiClient.post('/coach-notes', data);
    return response.data;
  },

  // Update an existing note
  async updateNote(id: number, data: UpdateNoteData): Promise<{ note: CoachNote; message: string }> {
    const response = await apiClient.put(`/coach-notes/${id}`, data);
    return response.data;
  },

  // Delete a note
  async deleteNote(id: number): Promise<{ message: string }> {
    const response = await apiClient.delete(`/coach-notes/${id}`);
    return response.data;
  },

  // Get available categories
  async getCategories(): Promise<{ categories: string[] }> {
    const response = await apiClient.get('/coach-notes/categories');
    return response.data;
  },

  // Get available priorities
  async getPriorities(): Promise<{ priorities: string[] }> {
    const response = await apiClient.get('/coach-notes/priorities');
    return response.data;
  },

  // Get notes for a specific student
  async getStudentNotes(studentId: number): Promise<{
    student: { id: number; name: string; email: string };
    notes: CoachNote[];
    total_notes: number;
  }> {
    const response = await apiClient.get(`/coach-notes/student/${studentId}`);
    return response.data;
  },

  // Get notes by a specific coach (admin only)
  async getCoachNotes(coachId: number): Promise<{
    coach: { id: number; name: string; email: string };
    notes: CoachNote[];
    total_notes: number;
  }> {
    const response = await apiClient.get(`/coach-notes/coach/${coachId}`);
    return response.data;
  }
};