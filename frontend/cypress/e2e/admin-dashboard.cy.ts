describe('Admin Dashboard - End to End', () => {
  beforeEach(() => {
    // Login as admin
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('BDC Platform').should('be.visible');
  });

  it('displays all dashboard statistics and charts correctly', () => {
    // 1. Verify dashboard header
    cy.contains('h1', 'Dashboard').should('be.visible');
    cy.contains('Welcome back').should('be.visible');
    
    // 2. Check statistics cards
    cy.get('[data-testid="stats-card"]').should('have.length', 4);
    
    // Total Beneficiaries
    cy.get('[data-testid="stats-card-beneficiaries"]').within(() => {
      cy.contains('Total Beneficiaries').should('be.visible');
      cy.get('[data-testid="stats-value"]').should('exist');
      cy.get('[data-testid="stats-trend"]').should('exist');
      cy.contains(/\+\d+%|−\d+%/).should('be.visible'); // Trend percentage
    });

    // Active Programs
    cy.get('[data-testid="stats-card-programs"]').within(() => {
      cy.contains('Active Programs').should('be.visible');
      cy.get('[data-testid="stats-value"]').should('exist');
      cy.get('[data-testid="stats-trend"]').should('exist');
    });

    // Total Courses
    cy.get('[data-testid="stats-card-courses"]').within(() => {
      cy.contains('Total Courses').should('be.visible');
      cy.get('[data-testid="stats-value"]').should('exist');
      cy.get('[data-testid="stats-trend"]').should('exist');
    });

    // Completion Rate
    cy.get('[data-testid="stats-card-completion"]').within(() => {
      cy.contains('Completion Rate').should('be.visible');
      cy.get('[data-testid="stats-value"]').should('contain', '%');
      cy.get('[data-testid="stats-trend"]').should('exist');
    });

    // 3. Verify charts are rendered
    // Enrollment Trends Chart
    cy.get('[data-testid="enrollment-trends-chart"]').should('be.visible');
    cy.contains('h3', 'Enrollment Trends').should('be.visible');
    cy.get('[data-testid="chart-legend"]').within(() => {
      cy.contains('New Enrollments').should('be.visible');
      cy.contains('Completions').should('be.visible');
    });

    // Program Distribution Chart
    cy.get('[data-testid="program-distribution-chart"]').should('be.visible');
    cy.contains('h3', 'Program Distribution').should('be.visible');
    
    // Performance Overview Chart
    cy.get('[data-testid="performance-overview-chart"]').should('be.visible');
    cy.contains('h3', 'Performance Overview').should('be.visible');

    // 4. Check recent activities
    cy.get('[data-testid="recent-activities"]').should('be.visible');
    cy.contains('h3', 'Recent Activities').should('be.visible');
    cy.get('[data-testid="activity-item"]').should('have.length.greaterThan', 0);
    
    // Activity items should have timestamp and description
    cy.get('[data-testid="activity-item"]').first().within(() => {
      cy.get('[data-testid="activity-time"]').should('be.visible');
      cy.get('[data-testid="activity-description"]').should('be.visible');
      cy.get('[data-testid="activity-icon"]').should('be.visible');
    });

    // 5. Check quick actions
    cy.get('[data-testid="quick-actions"]').should('be.visible');
    cy.contains('h3', 'Quick Actions').should('be.visible');
    
    cy.get('[data-testid="quick-action-add-beneficiary"]').should('be.visible');
    cy.get('[data-testid="quick-action-create-program"]').should('be.visible');
    cy.get('[data-testid="quick-action-generate-report"]').should('be.visible');
    cy.get('[data-testid="quick-action-view-analytics"]').should('be.visible');
  });

  it('allows filtering dashboard data by date range', () => {
    // Check date range selector
    cy.get('[data-testid="date-range-selector"]').should('be.visible');
    cy.get('[data-testid="date-range-selector"]').click();
    
    // Select predefined ranges
    cy.contains('button', 'Last 7 days').click();
    cy.wait(500); // Wait for data refresh
    cy.contains('Showing data for: Last 7 days').should('be.visible');
    
    cy.get('[data-testid="date-range-selector"]').click();
    cy.contains('button', 'Last 30 days').click();
    cy.wait(500);
    cy.contains('Showing data for: Last 30 days').should('be.visible');
    
    // Custom date range
    cy.get('[data-testid="date-range-selector"]').click();
    cy.contains('button', 'Custom Range').click();
    
    cy.get('input[name="start_date"]').type('2024-01-01');
    cy.get('input[name="end_date"]').type('2024-06-30');
    cy.contains('button', 'Apply').click();
    
    cy.wait(500);
    cy.contains('Showing data for: Jan 1 - Jun 30, 2024').should('be.visible');
  });

  it('provides drill-down functionality from statistics', () => {
    // Click on Total Beneficiaries card
    cy.get('[data-testid="stats-card-beneficiaries"]').click();
    
    // Should navigate to beneficiaries page with context
    cy.url().should('include', '/beneficiaries');
    cy.contains('Filtered by: Dashboard Overview').should('be.visible');
    
    // Navigate back
    cy.go('back');
    
    // Click on Active Programs card
    cy.get('[data-testid="stats-card-programs"]').click();
    cy.url().should('include', '/programs');
    cy.get('select[name="status"]').should('have.value', 'active');
  });

  it('displays real-time notifications', () => {
    // Check notification bell
    cy.get('[data-testid="notification-bell"]').should('be.visible');
    cy.get('[data-testid="notification-count"]').should('be.visible');
    
    // Click notification bell
    cy.get('[data-testid="notification-bell"]').click();
    
    // Notification panel should open
    cy.get('[data-testid="notification-panel"]').should('be.visible');
    cy.contains('h3', 'Notifications').should('be.visible');
    
    // Check notification items
    cy.get('[data-testid="notification-item"]').should('have.length.greaterThan', 0);
    
    cy.get('[data-testid="notification-item"]').first().within(() => {
      cy.get('[data-testid="notification-title"]').should('be.visible');
      cy.get('[data-testid="notification-time"]').should('be.visible');
      cy.contains('button', 'Mark as read').should('be.visible');
    });
    
    // Mark notification as read
    cy.get('[data-testid="notification-item"]').first().within(() => {
      cy.contains('button', 'Mark as read').click();
    });
    
    // Notification count should decrease
    cy.get('[data-testid="notification-count"]').then($count => {
      const initialCount = parseInt($count.text());
      cy.get('[data-testid="notification-count"]').should('contain', initialCount - 1);
    });
  });

  it('shows program performance metrics', () => {
    // Navigate to program performance section
    cy.get('[data-testid="program-performance-section"]').scrollIntoView();
    cy.contains('h3', 'Program Performance').should('be.visible');
    
    // Check program cards
    cy.get('[data-testid="program-card"]').should('have.length.greaterThan', 0);
    
    cy.get('[data-testid="program-card"]').first().within(() => {
      cy.get('[data-testid="program-name"]').should('be.visible');
      cy.get('[data-testid="program-enrollment"]').should('be.visible');
      cy.get('[data-testid="program-completion-rate"]').should('be.visible');
      cy.get('[data-testid="program-satisfaction"]').should('be.visible');
      
      // Progress bars
      cy.get('[data-testid="enrollment-progress"]').should('be.visible');
      cy.get('[data-testid="completion-progress"]').should('be.visible');
    });
  });

  it('allows exporting dashboard data', () => {
    // Export button
    cy.get('[data-testid="export-dashboard"]').should('be.visible');
    cy.get('[data-testid="export-dashboard"]').click();
    
    // Export options modal
    cy.contains('Export Dashboard Data').should('be.visible');
    
    // Select export format
    cy.get('input[type="radio"][value="pdf"]').check();
    cy.contains('Include charts and visualizations').should('be.visible');
    cy.get('input[name="include_charts"]').check();
    
    // Select sections to export
    cy.contains('Select sections to export:').should('be.visible');
    cy.get('input[name="export_statistics"]').should('be.checked');
    cy.get('input[name="export_charts"]').check();
    cy.get('input[name="export_activities"]').check();
    
    // Export
    cy.contains('button', 'Export').click();
    cy.contains('Dashboard exported successfully').should('be.visible');
  });

  it('provides quick insights and recommendations', () => {
    // Insights section
    cy.get('[data-testid="insights-section"]').scrollIntoView();
    cy.contains('h3', 'Insights & Recommendations').should('be.visible');
    
    // Check insight cards
    cy.get('[data-testid="insight-card"]').should('have.length.greaterThan', 0);
    
    cy.get('[data-testid="insight-card"]').first().within(() => {
      cy.get('[data-testid="insight-icon"]').should('be.visible');
      cy.get('[data-testid="insight-title"]').should('be.visible');
      cy.get('[data-testid="insight-description"]').should('be.visible');
      cy.contains('button', 'Take Action').should('be.visible');
    });
    
    // Click on insight action
    cy.get('[data-testid="insight-card"]').first().within(() => {
      cy.contains('button', 'Take Action').click();
    });
    
    // Should navigate to relevant page
    cy.url().should('not.include', '/dashboard');
  });

  it('handles data refresh and loading states', () => {
    // Refresh button
    cy.get('[data-testid="refresh-dashboard"]').should('be.visible');
    
    // Mock slow API response
    cy.intercept('GET', '/api/v1/dashboard/stats', (req) => {
      req.reply((res) => {
        res.delay(1000); // 1 second delay
        res.send({
          statusCode: 200,
          body: {
            beneficiaries: { total: 150, trend: 12 },
            programs: { active: 8, trend: 5 },
            courses: { total: 24, trend: -3 },
            completion_rate: { value: 78, trend: 8 }
          }
        });
      });
    }).as('dashboardStats');
    
    // Click refresh
    cy.get('[data-testid="refresh-dashboard"]').click();
    
    // Should show loading state
    cy.get('[data-testid="dashboard-loading"]').should('be.visible');
    cy.contains('Refreshing dashboard...').should('be.visible');
    
    // Wait for data
    cy.wait('@dashboardStats');
    
    // Loading state should disappear
    cy.get('[data-testid="dashboard-loading"]').should('not.exist');
    cy.contains('Dashboard updated').should('be.visible');
  });

  it('displays system health and status', () => {
    // System status widget
    cy.get('[data-testid="system-status"]').should('be.visible');
    cy.contains('h3', 'System Status').should('be.visible');
    
    // Check status indicators
    cy.get('[data-testid="status-api"]').within(() => {
      cy.contains('API').should('be.visible');
      cy.get('[data-testid="status-indicator"]').should('have.class', 'bg-green-500');
      cy.contains('Operational').should('be.visible');
    });
    
    cy.get('[data-testid="status-database"]').within(() => {
      cy.contains('Database').should('be.visible');
      cy.get('[data-testid="status-indicator"]').should('have.class', 'bg-green-500');
      cy.contains('Operational').should('be.visible');
    });
    
    cy.get('[data-testid="status-storage"]').within(() => {
      cy.contains('Storage').should('be.visible');
      cy.get('[data-testid="status-indicator"]').should('exist');
      cy.contains(/\d+% used/).should('be.visible');
    });
  });

  it('allows customizing dashboard layout', () => {
    // Customize button
    cy.get('[data-testid="customize-dashboard"]').should('be.visible');
    cy.get('[data-testid="customize-dashboard"]').click();
    
    // Customization modal
    cy.contains('Customize Dashboard').should('be.visible');
    
    // Widget toggles
    cy.contains('Show/Hide Widgets').should('be.visible');
    cy.get('input[name="show_statistics"]').should('be.checked');
    cy.get('input[name="show_charts"]').should('be.checked');
    cy.get('input[name="show_activities"]').should('be.checked');
    
    // Hide activities
    cy.get('input[name="show_activities"]').uncheck();
    
    // Save changes
    cy.contains('button', 'Save Layout').click();
    cy.contains('Dashboard layout saved').should('be.visible');
    
    // Activities should be hidden
    cy.get('[data-testid="recent-activities"]').should('not.exist');
    
    // Reset layout
    cy.get('[data-testid="customize-dashboard"]').click();
    cy.contains('button', 'Reset to Default').click();
    cy.contains('Dashboard layout reset').should('be.visible');
    
    // Activities should be visible again
    cy.get('[data-testid="recent-activities"]').should('be.visible');
  });
});

describe('Admin Dashboard - Mobile Responsive', () => {
  beforeEach(() => {
    cy.viewport('iphone-x');
    
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
  });

  it('displays properly on mobile devices', () => {
    // Stats cards should stack vertically
    cy.get('[data-testid="stats-card"]').should('be.visible');
    cy.get('[data-testid="stats-grid"]').should('have.css', 'grid-template-columns', '1fr');
    
    // Charts should be scrollable
    cy.get('[data-testid="charts-container"]').scrollIntoView();
    cy.get('[data-testid="charts-container"]').should('have.css', 'overflow-x', 'auto');
    
    // Quick actions should be accessible
    cy.get('[data-testid="quick-actions"]').scrollIntoView();
    cy.get('[data-testid="quick-actions"]').should('be.visible');
    
    // Mobile menu should work
    cy.get('[data-testid="mobile-menu-toggle"]').click();
    cy.get('[data-testid="mobile-menu"]').should('be.visible');
  });
});