import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import * as authContext from '@/contexts/AuthContext';
import * as useLearningPath from '@/hooks/useLearningPath';
import type { LearningPathStatus } from '@/types/learning-path';

import LearningPathsList from '../LearningPathsList';

// Mock dependencies
vi.mock('@/contexts/AuthContext');
vi.mock('@/hooks/useLearningPath');

const mockUseAuth = vi.mocked(authContext.useAuth);
const mockUseLearningPath = vi.mocked(useLearningPath);

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
};

const mockLearningPaths = [
  {
    id: 1,
    title: 'Web Development Fundamentals',
    description: 'Learn the basics of web development including HTML, CSS, and JavaScript.',
    status: 'in_progress' as LearningPathStatus,
    duration_weeks: 8,
    total_milestones: 5,
    completed_milestones: 2,
    target_skills: ['HTML', 'CSS', 'JavaScript', 'React'],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-15T00:00:00Z',
  },
  {
    id: 2,
    title: 'Data Science Basics',
    description: 'Introduction to data analysis and machine learning.',
    status: 'completed' as LearningPathStatus,
    duration_weeks: 12,
    total_milestones: 8,
    completed_milestones: 8,
    target_skills: ['Python', 'Pandas', 'Machine Learning'],
    created_at: '2022-12-01T00:00:00Z',
    updated_at: '2023-03-01T00:00:00Z',
  },
  {
    id: 3,
    title: 'UX Design Principles',
    description: 'Learn user experience design fundamentals.',
    status: 'proposed' as LearningPathStatus,
    duration_weeks: 6,
    total_milestones: 4,
    completed_milestones: 0,
    target_skills: ['Design Thinking', 'Prototyping', 'User Research'],
    created_at: '2023-02-01T00:00:00Z',
    updated_at: '2023-02-01T00:00:00Z',
  },
];

describe('LearningPathsList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        role: 'student',
      },
      isAuthenticated: true,
      isLoading: false,
    } as any);

    // Mock the hook to return data based on status filter
    mockUseLearningPath.useMyLearningPaths.mockImplementation((params: any) => {
      if (params?.status === 'completed') {
        return {
          data: { learning_paths: mockLearningPaths.filter(p => p.status === 'completed') },
          isLoading: false,
          error: null,
        } as any;
      }
      return {
        data: { learning_paths: mockLearningPaths },
        isLoading: false,
        error: null,
      } as any;
    });
  });

  it('renders learning paths list with statistics', () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    expect(screen.getByText('Learning Paths')).toBeInTheDocument();
    expect(screen.getByText('Discover and track your personalized learning journey')).toBeInTheDocument();

    // Statistics section is rendered as grid cards
    // Check that stats are displayed correctly
    expect(screen.getByText('3')).toBeInTheDocument(); // Total paths
    
    // Check that stats labels exist
    expect(screen.getByText('Total Paths')).toBeInTheDocument();
    expect(screen.getAllByText('In Progress').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Completed').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Proposed').length).toBeGreaterThan(0);
  });

  it('displays learning paths with correct information', () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    // Check first learning path
    expect(screen.getByText('Web Development Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Learn the basics of web development including HTML, CSS, and JavaScript.')).toBeInTheDocument();
    // Status is displayed without underscores
    expect(screen.getByText('in progress')).toBeInTheDocument();
    expect(screen.getByText('5 milestones')).toBeInTheDocument();
    expect(screen.getByText('8 weeks')).toBeInTheDocument();
    expect(screen.getByText('2/5 milestones')).toBeInTheDocument();

    // Check skills tags
    expect(screen.getByText('HTML')).toBeInTheDocument();
    expect(screen.getByText('CSS')).toBeInTheDocument();
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('+1 more')).toBeInTheDocument(); // +1 more for React
  });

  it('shows progress bar for in-progress paths', () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    // Check that the in-progress path shows milestone progress text
    expect(screen.getByText('2/5 milestones')).toBeInTheDocument();
    
    // Look for the progress bar container and inner bar
    const progressContainer = document.querySelector('.bg-gray-200.rounded-full');
    expect(progressContainer).toBeInTheDocument();
    
    // The filled progress bar should exist with the correct width
    const progressBar = progressContainer?.querySelector('.bg-blue-600');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveStyle({ width: '40%' }); // 2/5 = 40%
  });

  it('filters learning paths by search term', async () => {
    const user = userEvent.setup();
    render(<LearningPathsList />, { wrapper: createWrapper() });

    const searchInput = screen.getByPlaceholderText('Search learning paths...');
    await user.type(searchInput, 'web');

    expect(screen.getByText('Web Development Fundamentals')).toBeInTheDocument();
    expect(screen.queryByText('Data Science Basics')).not.toBeInTheDocument();
    expect(screen.queryByText('UX Design Principles')).not.toBeInTheDocument();
  });

  it('has functioning filters section', async () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    // Verify filter controls exist
    expect(screen.getByPlaceholderText('Search learning paths...')).toBeInTheDocument();
    expect(screen.getByText('Clear Filters')).toBeInTheDocument();
    
    // Verify status dropdown exists with options
    const selects = screen.getAllByRole('combobox');
    expect(selects.length).toBeGreaterThan(0);
    
    // The hook is called to fetch data
    expect(mockUseLearningPath.useMyLearningPaths).toHaveBeenCalled();
  });

  it('clears filters when clear button is clicked', async () => {
    const user = userEvent.setup();
    render(<LearningPathsList />, { wrapper: createWrapper() });

    // Apply filters
    const searchInput = screen.getByPlaceholderText('Search learning paths...');
    await user.type(searchInput, 'web');

    const selects = screen.getAllByRole('combobox');
    const statusSelect = selects[0]; // First select is status filter
    await user.selectOptions(statusSelect, 'in_progress');

    // Clear filters - button text includes icon, so use more flexible matcher
    const clearButton = screen.getByText('Clear Filters');
    await user.click(clearButton);

    // All paths should be visible again
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals')).toBeInTheDocument();
      expect(screen.getByText('Data Science Basics')).toBeInTheDocument();
      expect(screen.getByText('UX Design Principles')).toBeInTheDocument();
    });

    expect(searchInput).toHaveValue('');
    expect(statusSelect).toHaveValue('');
  });

  it('shows view button for each learning path', () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    const viewButtons = screen.getAllByText('View');
    expect(viewButtons).toHaveLength(3);

    // Check that buttons link to correct paths
    expect(viewButtons[0]).toHaveAttribute('href', '/learning-paths/1');
    expect(viewButtons[1]).toHaveAttribute('href', '/learning-paths/2');
    expect(viewButtons[2]).toHaveAttribute('href', '/learning-paths/3');
  });

  it('displays loading state', () => {
    mockUseLearningPath.useMyLearningPaths.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    render(<LearningPathsList />, { wrapper: createWrapper() });

    // Check for loading spinner - LoadingSpinner component should have animate-spin class
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('displays error state', () => {
    mockUseLearningPath.useMyLearningPaths.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to load'),
    } as any);

    render(<LearningPathsList />, { wrapper: createWrapper() });

    expect(screen.getByText('Failed to load learning paths. Please try again later.')).toBeInTheDocument();
  });

  it('shows empty state when no learning paths exist', () => {
    mockUseLearningPath.useMyLearningPaths.mockReturnValue({
      data: { learning_paths: [] },
      isLoading: false,
      error: null,
    } as any);

    render(<LearningPathsList />, { wrapper: createWrapper() });

    expect(screen.getByText('No Learning Paths Yet')).toBeInTheDocument();
    expect(screen.getByText('Complete an evaluation to get personalized learning path recommendations.')).toBeInTheDocument();
    expect(screen.getByText('Take an Evaluation')).toBeInTheDocument();
  });

  it('shows no results message when filters return no matches', async () => {
    const user = userEvent.setup();
    render(<LearningPathsList />, { wrapper: createWrapper() });

    const searchInput = screen.getByPlaceholderText('Search learning paths...');
    await user.clear(searchInput);
    await user.type(searchInput, 'nonexistent');

    await waitFor(() => {
      expect(screen.getByText('No Matching Learning Paths')).toBeInTheDocument();
      expect(screen.getByText('Try adjusting your search terms or filters to find what you\'re looking for.')).toBeInTheDocument();
    });
  });

  it('displays correct status badges with icons', () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    // Status text has underscores replaced with spaces
    // Check for the badge elements containing status text
    const badges = screen.getAllByRole('generic').filter(el => 
      el.className.includes('Badge') || el.querySelector('svg')
    );
    
    // Verify that we have status badges
    expect(badges.length).toBeGreaterThan(0);
    
    // Check that specific statuses are displayed in the stats section
    expect(screen.getAllByText('In Progress').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Completed').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Proposed').length).toBeGreaterThan(0);
  });

  it('displays learning path information', () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    // Verify the header is displayed
    expect(screen.getByText('Learning Paths')).toBeInTheDocument();
    expect(screen.getByText('Discover and track your personalized learning journey')).toBeInTheDocument();
    
    // Verify statistics section shows counts
    expect(screen.getByText('Total Paths')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // Total count
  });

  it('handles URL search params for initial filters', () => {
    // Mock URLSearchParams to simulate existing search params
    Object.defineProperty(window, 'location', {
      value: {
        search: '?search=web&status=in_progress',
      },
      writable: true,
    });

    render(<LearningPathsList />, { wrapper: createWrapper() });

    const searchInput = screen.getByPlaceholderText('Search learning paths...');
    expect(searchInput).toHaveValue('web');
  });

  it('shows results summary', () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    // The component should show a summary of results
    const summaryText = screen.getByText(/Showing.*learning paths/i);
    expect(summaryText).toBeInTheDocument();
    expect(summaryText.textContent).toContain('3');
  });

  it('does not show progress bar for completed or proposed paths', () => {
    render(<LearningPathsList />, { wrapper: createWrapper() });

    // Check that milestone progress is only shown for in-progress paths
    const milestoneTexts = screen.getAllByText(/\d+\/\d+ milestones/);
    // Should only show for the in-progress path
    expect(milestoneTexts).toHaveLength(1);
    expect(milestoneTexts[0].textContent).toBe('2/5 milestones');
  });
});