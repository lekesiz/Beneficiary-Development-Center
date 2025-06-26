describe('Admin Dashboard - End to End', () => {
  beforeEach(() => {
    // Login as admin
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('admin123');
    cy.get('button[type="submit"]').click();
    
    // Wait for redirect to admin dashboard
    cy.url().should('include', '/admin/dashboard');
    cy.contains('Admin Dashboard').should('be.visible');
  });

  describe('Dashboard Overview', () => {
    it('displays key metrics and statistics', () => {
      // Check main stats cards
      cy.get('[data-testid="stats-card"]').should('have.length', 4);
      
      // Total Users
      cy.get('[data-testid="stats-card-users"]').within(() => {
        cy.contains('Total Users').should('be.visible');
        cy.get('[data-testid="stat-value"]').should('exist');
        cy.get('[data-testid="stat-change"]').should('exist'); // Growth percentage
      });

      // Active Programs
      cy.get('[data-testid="stats-card-programs"]').within(() => {
        cy.contains('Active Programs').should('be.visible');
        cy.get('[data-testid="stat-value"]').should('exist');
      });

      // Completion Rate
      cy.get('[data-testid="stats-card-completion"]').within(() => {
        cy.contains('Completion Rate').should('be.visible');
        cy.get('[data-testid="stat-value"]').should('contain', '%');
      });

      // Active Sessions
      cy.get('[data-testid="stats-card-sessions"]').within(() => {
        cy.contains('Active Sessions').should('be.visible');
        cy.get('[data-testid="stat-value"]').should('exist');
      });
    });

    it('shows activity charts and graphs', () => {
      // User growth chart
      cy.get('[data-testid="user-growth-chart"]').should('be.visible');
      cy.contains('User Growth').should('be.visible');
      
      // Program enrollment chart
      cy.get('[data-testid="enrollment-chart"]').should('be.visible');
      cy.contains('Program Enrollment').should('be.visible');
      
      // Activity heatmap
      cy.get('[data-testid="activity-heatmap"]').should('be.visible');
      cy.contains('Platform Activity').should('be.visible');

      // Time period selector
      cy.get('[data-testid="time-range-selector"]').should('be.visible');
      cy.get('[data-testid="time-range-selector"]').select('30days');
      
      // Charts should update
      cy.get('[data-testid="loading-spinner"]').should('not.exist');
    });

    it('displays recent activity feed', () => {
      cy.contains('Recent Activity').should('be.visible');
      cy.get('[data-testid="activity-feed"]').should('be.visible');
      
      // Check activity items
      cy.get('[data-testid="activity-item"]').should('have.length.greaterThan', 0);
      cy.get('[data-testid="activity-item"]').first().within(() => {
        cy.get('[data-testid="activity-icon"]').should('be.visible');
        cy.get('[data-testid="activity-description"]').should('be.visible');
        cy.get('[data-testid="activity-time"]').should('be.visible');
      });

      // Load more activities
      cy.contains('button', 'Load More').click();
      cy.get('[data-testid="activity-item"]').should('have.length.greaterThan', 5);
    });

    it('shows system health status', () => {
      cy.contains('System Health').should('be.visible');
      
      // API status
      cy.get('[data-testid="health-api"]').within(() => {
        cy.contains('API').should('be.visible');
        cy.get('[data-testid="status-indicator"]').should('have.class', 'status-healthy');
      });

      // Database status
      cy.get('[data-testid="health-database"]').within(() => {
        cy.contains('Database').should('be.visible');
        cy.get('[data-testid="status-indicator"]').should('have.class', 'status-healthy');
      });

      // Storage status
      cy.get('[data-testid="health-storage"]').within(() => {
        cy.contains('Storage').should('be.visible');
        cy.contains('Used').should('be.visible');
        cy.get('[data-testid="storage-bar"]').should('be.visible');
      });
    });
  });

  describe('User Management', () => {
    beforeEach(() => {
      cy.get('nav').contains('Users').click();
      cy.url().should('include', '/admin/users');
    });

    it('lists and filters users', () => {
      // Check user table
      cy.get('[data-testid="users-table"]').should('be.visible');
      cy.get('[data-testid="user-row"]').should('have.length.greaterThan', 0);

      // Search users
      cy.get('input[placeholder="Search users..."]').type('john');
      cy.get('[data-testid="user-row"]').should('have.length.lessThan', 10);
      cy.contains('John Doe').should('be.visible');

      // Filter by role
      cy.get('select[name="role"]').select('trainer');
      cy.get('[data-testid="user-row"]').each(($row) => {
        cy.wrap($row).contains('Trainer').should('be.visible');
      });

      // Filter by status
      cy.get('select[name="status"]').select('active');
      cy.get('[data-testid="user-row"]').each(($row) => {
        cy.wrap($row).find('[data-testid="status-badge"]').should('contain', 'Active');
      });

      // Sort by registration date
      cy.get('th').contains('Registered').click();
      // Verify sort order changed
    });

    it('creates new user', () => {
      cy.contains('button', 'Add User').click();
      cy.contains('Create New User').should('be.visible');

      // Fill user form
      cy.get('input[name="first_name"]').type('Test');
      cy.get('input[name="last_name"]').type('User');
      cy.get('input[name="email"]').type('testuser@example.com');
      cy.get('input[name="phone"]').type('+1234567890');
      cy.get('select[name="role"]').select('student');
      cy.get('select[name="tenant"]').select('Default Tenant');
      
      // Set temporary password
      cy.get('input[name="temporary_password"]').type('TempPass123!');
      cy.get('input[type="checkbox"][name="require_password_change"]').check();

      // Submit form
      cy.contains('button', 'Create User').click();
      cy.contains('User created successfully').should('be.visible');
      
      // Verify user appears in list
      cy.contains('testuser@example.com').should('be.visible');
    });

    it('edits user details and permissions', () => {
      cy.get('[data-testid="user-row"]').first().within(() => {
        cy.get('[data-testid="action-menu"]').click();
      });
      cy.contains('Edit').click();

      // Edit user modal
      cy.contains('Edit User').should('be.visible');
      
      // Update role
      cy.get('select[name="role"]').select('trainer');
      
      // Update permissions
      cy.contains('Permissions').click();
      cy.get('input[type="checkbox"][name="can_create_programs"]').check();
      cy.get('input[type="checkbox"][name="can_view_reports"]').check();
      
      // Save changes
      cy.contains('button', 'Save Changes').click();
      cy.contains('User updated successfully').should('be.visible');
    });

    it('manages user status', () => {
      // Find active user
      cy.get('[data-testid="user-row"]').contains('Active').parents('[data-testid="user-row"]').within(() => {
        cy.get('[data-testid="action-menu"]').click();
      });

      // Suspend user
      cy.contains('Suspend User').click();
      cy.contains('Suspend User?').should('be.visible');
      cy.get('textarea[name="reason"]').type('Policy violation');
      cy.contains('button', 'Suspend').click();
      
      cy.contains('User suspended successfully').should('be.visible');
      cy.get('[data-testid="status-badge"]').should('contain', 'Suspended');

      // Reactivate user
      cy.get('[data-testid="action-menu"]').click();
      cy.contains('Reactivate User').click();
      cy.contains('User reactivated successfully').should('be.visible');
    });

    it('bulk manages users', () => {
      // Select multiple users
      cy.get('input[type="checkbox"][data-testid="select-all"]').check();
      cy.contains('5 users selected').should('be.visible');

      // Open bulk actions
      cy.contains('button', 'Bulk Actions').click();
      
      // Export users
      cy.contains('Export Selected').click();
      cy.contains('Export Users').should('be.visible');
      cy.get('input[type="radio"][value="csv"]').check();
      cy.contains('button', 'Export').click();
      cy.contains('Export started').should('be.visible');

      // Send bulk email
      cy.contains('button', 'Bulk Actions').click();
      cy.contains('Send Email').click();
      cy.get('input[name="subject"]').type('Important Update');
      cy.get('textarea[name="message"]').type('Please check your dashboard for updates.');
      cy.contains('button', 'Send').click();
      cy.contains('Emails queued successfully').should('be.visible');
    });

    it('views user activity logs', () => {
      cy.get('[data-testid="user-row"]').first().click();
      cy.url().should('match', /\/admin\/users\/\d+$/);

      // User detail page
      cy.contains('User Details').should('be.visible');
      cy.contains('Activity Log').click();

      // Activity timeline
      cy.get('[data-testid="activity-timeline"]').should('be.visible');
      cy.get('[data-testid="activity-entry"]').should('have.length.greaterThan', 0);
      
      // Filter activities
      cy.get('select[name="activity_type"]').select('login');
      cy.get('[data-testid="activity-entry"]').each(($entry) => {
        cy.wrap($entry).should('contain', 'Login');
      });

      // View detailed activity
      cy.get('[data-testid="activity-entry"]').first().click();
      cy.contains('Activity Details').should('be.visible');
      cy.contains('IP Address').should('be.visible');
      cy.contains('User Agent').should('be.visible');
    });
  });

  describe('Program Management', () => {
    beforeEach(() => {
      cy.get('nav').contains('Programs').click();
      cy.url().should('include', '/admin/programs');
    });

    it('reviews and approves programs', () => {
      // Navigate to pending programs
      cy.contains('Pending Review').click();
      cy.get('[data-testid="program-card"]').should('have.length.greaterThan', 0);

      // Review program
      cy.get('[data-testid="program-card"]').first().within(() => {
        cy.contains('button', 'Review').click();
      });

      // Program review page
      cy.contains('Program Review').should('be.visible');
      cy.contains('Submitted by').should('be.visible');
      
      // Check content
      cy.contains('Course Content').click();
      cy.get('[data-testid="module-list"]').should('be.visible');
      
      // Check prerequisites
      cy.contains('Prerequisites').click();
      cy.get('[data-testid="prerequisite-list"]').should('be.visible');

      // Add review notes
      cy.get('textarea[name="review_notes"]').type('Content looks good. Approved for launch.');
      
      // Approve program
      cy.contains('button', 'Approve Program').click();
      cy.contains('Program approved successfully').should('be.visible');
    });

    it('manages program settings', () => {
      cy.get('[data-testid="program-card"]').first().within(() => {
        cy.get('[data-testid="action-menu"]').click();
      });
      cy.contains('Settings').click();

      // Program settings modal
      cy.contains('Program Settings').should('be.visible');
      
      // Update visibility
      cy.get('select[name="visibility"]').select('private');
      
      // Update enrollment settings
      cy.get('input[name="max_students"]').clear().type('50');
      cy.get('input[type="checkbox"][name="auto_enroll"]').check();
      
      // Update pricing
      cy.get('input[name="price"]').clear().type('99.99');
      cy.get('select[name="currency"]').select('USD');

      // Save settings
      cy.contains('button', 'Save Settings').click();
      cy.contains('Settings updated successfully').should('be.visible');
    });

    it('views program analytics', () => {
      cy.get('[data-testid="program-card"]').first().click();
      cy.contains('Analytics').click();

      // Analytics dashboard
      cy.contains('Program Analytics').should('be.visible');
      
      // Enrollment stats
      cy.get('[data-testid="enrollment-stats"]').within(() => {
        cy.contains('Total Enrolled').should('be.visible');
        cy.contains('Active Students').should('be.visible');
        cy.contains('Completion Rate').should('be.visible');
      });

      // Progress chart
      cy.get('[data-testid="progress-chart"]').should('be.visible');
      
      // Student performance
      cy.contains('Student Performance').should('be.visible');
      cy.get('[data-testid="performance-table"]').should('be.visible');
      
      // Export analytics
      cy.contains('button', 'Export Report').click();
      cy.get('input[type="radio"][value="pdf"]').check();
      cy.contains('button', 'Generate Report').click();
      cy.contains('Report generation started').should('be.visible');
    });
  });

  describe('System Configuration', () => {
    beforeEach(() => {
      cy.get('nav').contains('Settings').click();
      cy.url().should('include', '/admin/settings');
    });

    it('configures general settings', () => {
      cy.contains('General Settings').should('be.visible');
      
      // Platform settings
      cy.get('input[name="platform_name"]').clear().type('BDC Learning Platform');
      cy.get('textarea[name="platform_description"]').clear().type('Empowering learners worldwide');
      
      // Contact information
      cy.get('input[name="support_email"]').clear().type('support@bdc.edu');
      cy.get('input[name="support_phone"]').clear().type('+1-555-0123');
      
      // Time zone
      cy.get('select[name="default_timezone"]').select('America/New_York');
      
      // Language settings
      cy.get('select[name="default_language"]').select('en');
      cy.get('input[type="checkbox"][name="allow_language_change"]').check();

      // Save settings
      cy.contains('button', 'Save Changes').click();
      cy.contains('Settings saved successfully').should('be.visible');
    });

    it('manages email templates', () => {
      cy.contains('Email Templates').click();
      cy.url().should('include', '/admin/settings/email-templates');

      // Template list
      cy.get('[data-testid="template-list"]').should('be.visible');
      
      // Edit welcome email template
      cy.contains('Welcome Email').click();
      cy.contains('Edit Email Template').should('be.visible');
      
      // Update template
      cy.get('input[name="subject"]').clear().type('Welcome to {{platform_name}}!');
      cy.get('[data-testid="email-editor"]').clear().type('Dear {{user_name}},\n\nWelcome to our learning platform!');
      
      // Preview template
      cy.contains('button', 'Preview').click();
      cy.contains('Email Preview').should('be.visible');
      cy.contains('Welcome to BDC Learning Platform!').should('be.visible');
      
      // Save template
      cy.contains('button', 'Save Template').click();
      cy.contains('Template saved successfully').should('be.visible');

      // Test email
      cy.contains('button', 'Send Test').click();
      cy.get('input[name="test_email"]').type('admin@example.com');
      cy.contains('button', 'Send').click();
      cy.contains('Test email sent').should('be.visible');
    });

    it('configures authentication settings', () => {
      cy.contains('Authentication').click();
      cy.url().should('include', '/admin/settings/authentication');

      // Password policy
      cy.contains('Password Policy').should('be.visible');
      cy.get('input[name="min_password_length"]').clear().type('12');
      cy.get('input[type="checkbox"][name="require_uppercase"]').check();
      cy.get('input[type="checkbox"][name="require_numbers"]').check();
      cy.get('input[type="checkbox"][name="require_special_chars"]').check();
      
      // Session settings
      cy.contains('Session Settings').should('be.visible');
      cy.get('input[name="session_timeout"]').clear().type('30');
      cy.get('input[type="checkbox"][name="remember_me_enabled"]').check();
      
      // Two-factor authentication
      cy.contains('Two-Factor Authentication').should('be.visible');
      cy.get('input[type="checkbox"][name="2fa_enabled"]').check();
      cy.get('select[name="2fa_method"]').select('email');

      // Save settings
      cy.contains('button', 'Save Authentication Settings').click();
      cy.contains('Authentication settings updated').should('be.visible');
    });

    it('manages API keys', () => {
      cy.contains('API Management').click();
      cy.url().should('include', '/admin/settings/api');

      // API key list
      cy.contains('API Keys').should('be.visible');
      cy.get('[data-testid="api-key-list"]').should('be.visible');

      // Create new API key
      cy.contains('button', 'Create API Key').click();
      cy.get('input[name="key_name"]').type('Mobile App Integration');
      cy.get('textarea[name="description"]').type('API key for mobile application');
      
      // Set permissions
      cy.get('input[type="checkbox"][name="read_users"]').check();
      cy.get('input[type="checkbox"][name="read_programs"]').check();
      cy.get('input[type="checkbox"][name="write_enrollments"]').check();
      
      // Set expiration
      cy.get('input[type="radio"][value="expires"]').check();
      cy.get('input[type="date"][name="expiry_date"]').type('2025-12-31');

      // Generate key
      cy.contains('button', 'Generate Key').click();
      cy.contains('API Key Generated').should('be.visible');
      cy.get('[data-testid="api-key-display"]').should('be.visible');
      cy.contains('button', 'Copy Key').click();
      cy.contains('Copied!').should('be.visible');
    });
  });

  describe('Reports and Analytics', () => {
    beforeEach(() => {
      cy.get('nav').contains('Reports').click();
      cy.url().should('include', '/admin/reports');
    });

    it('generates platform usage reports', () => {
      cy.contains('Platform Usage').click();
      
      // Date range selector
      cy.get('[data-testid="date-range-picker"]').click();
      cy.contains('Last 30 days').click();
      
      // Report options
      cy.get('input[type="checkbox"][name="include_user_activity"]').check();
      cy.get('input[type="checkbox"][name="include_course_stats"]').check();
      cy.get('input[type="checkbox"][name="include_revenue"]').check();
      
      // Generate report
      cy.contains('button', 'Generate Report').click();
      cy.get('[data-testid="loading-indicator"]').should('be.visible');
      cy.get('[data-testid="loading-indicator"]').should('not.exist');
      
      // Report viewer
      cy.contains('Platform Usage Report').should('be.visible');
      cy.get('[data-testid="report-summary"]').should('be.visible');
      cy.get('[data-testid="usage-charts"]').should('be.visible');
      
      // Export report
      cy.contains('button', 'Export').click();
      cy.get('select[name="export_format"]').select('excel');
      cy.contains('button', 'Download').click();
    });

    it('views financial reports', () => {
      cy.contains('Financial Reports').click();
      
      // Revenue overview
      cy.contains('Revenue Overview').should('be.visible');
      cy.get('[data-testid="revenue-chart"]').should('be.visible');
      cy.get('[data-testid="revenue-total"]').should('contain', '$');
      
      // Transaction table
      cy.contains('Recent Transactions').should('be.visible');
      cy.get('[data-testid="transaction-table"]').should('be.visible');
      
      // Filter by payment method
      cy.get('select[name="payment_method"]').select('credit_card');
      cy.get('[data-testid="transaction-row"]').each(($row) => {
        cy.wrap($row).should('contain', 'Credit Card');
      });

      // Generate detailed report
      cy.contains('button', 'Detailed Financial Report').click();
      cy.get('input[type="checkbox"][name="include_refunds"]').check();
      cy.get('input[type="checkbox"][name="include_taxes"]').check();
      cy.contains('button', 'Generate').click();
    });

    it('schedules automated reports', () => {
      cy.contains('Scheduled Reports').click();
      
      // Create new scheduled report
      cy.contains('button', 'New Scheduled Report').click();
      
      // Configure report
      cy.get('input[name="report_name"]').type('Weekly Platform Summary');
      cy.get('select[name="report_type"]').select('platform_summary');
      cy.get('select[name="frequency"]').select('weekly');
      cy.get('select[name="day_of_week"]').select('monday');
      cy.get('input[name="time"]').type('09:00');
      
      // Recipients
      cy.get('input[name="recipients"]').type('admin@bdc.edu, manager@bdc.edu');
      
      // Save schedule
      cy.contains('button', 'Create Schedule').click();
      cy.contains('Report scheduled successfully').should('be.visible');
      
      // Verify in list
      cy.contains('Weekly Platform Summary').should('be.visible');
      cy.contains('Every Monday at 9:00 AM').should('be.visible');
    });
  });

  describe('Tenant Management', () => {
    beforeEach(() => {
      cy.get('nav').contains('Tenants').click();
      cy.url().should('include', '/admin/tenants');
    });

    it('creates and configures new tenant', () => {
      cy.contains('button', 'New Tenant').click();
      
      // Tenant details
      cy.get('input[name="tenant_name"]').type('ABC Corporation');
      cy.get('input[name="subdomain"]').type('abc-corp');
      cy.get('textarea[name="description"]').type('Corporate training platform for ABC Corp');
      
      // Admin user
      cy.get('input[name="admin_email"]').type('admin@abc-corp.com');
      cy.get('input[name="admin_first_name"]').type('John');
      cy.get('input[name="admin_last_name"]').type('Smith');
      
      // Subscription plan
      cy.get('select[name="subscription_plan"]').select('enterprise');
      cy.get('input[name="max_users"]').type('500');
      
      // Features
      cy.get('input[type="checkbox"][name="feature_chat"]').check();
      cy.get('input[type="checkbox"][name="feature_video"]').check();
      cy.get('input[type="checkbox"][name="feature_certificates"]').check();
      
      // Create tenant
      cy.contains('button', 'Create Tenant').click();
      cy.contains('Tenant created successfully').should('be.visible');
      
      // Verify tenant appears
      cy.contains('ABC Corporation').should('be.visible');
      cy.contains('abc-corp.bdc.edu').should('be.visible');
    });

    it('manages tenant settings and limits', () => {
      cy.get('[data-testid="tenant-row"]').first().click();
      
      // Tenant details page
      cy.contains('Tenant Details').should('be.visible');
      cy.contains('Settings').click();
      
      // Update limits
      cy.get('input[name="max_users"]').clear().type('1000');
      cy.get('input[name="max_storage_gb"]').clear().type('100');
      cy.get('input[name="max_programs"]').clear().type('50');
      
      // Update features
      cy.get('input[type="checkbox"][name="feature_api_access"]').check();
      cy.get('input[type="checkbox"][name="feature_white_label"]').check();
      
      // Custom branding
      cy.contains('Branding').click();
      cy.get('input[name="primary_color"]').clear().type('#1a73e8');
      cy.get('input[name="logo_url"]').type('https://abc-corp.com/logo.png');
      
      // Save changes
      cy.contains('button', 'Save Changes').click();
      cy.contains('Tenant settings updated').should('be.visible');
    });

    it('monitors tenant usage and billing', () => {
      cy.get('[data-testid="tenant-row"]').first().within(() => {
        cy.contains('Usage & Billing').click();
      });
      
      // Usage overview
      cy.contains('Current Usage').should('be.visible');
      cy.get('[data-testid="usage-meters"]').within(() => {
        cy.contains('Users').should('be.visible');
        cy.contains('Storage').should('be.visible');
        cy.contains('API Calls').should('be.visible');
      });
      
      // Billing history
      cy.contains('Billing History').should('be.visible');
      cy.get('[data-testid="invoice-table"]').should('be.visible');
      
      // Download invoice
      cy.get('[data-testid="invoice-row"]').first().within(() => {
        cy.contains('button', 'Download').click();
      });
      
      // Usage alerts
      cy.contains('Usage Alerts').click();
      cy.get('input[name="alert_threshold_users"]').clear().type('90');
      cy.get('input[name="alert_email"]').type('billing@abc-corp.com');
      cy.contains('button', 'Save Alerts').click();
    });
  });

  describe('Security and Audit', () => {
    beforeEach(() => {
      cy.get('[data-testid="admin-menu"]').click();
      cy.contains('Security').click();
      cy.url().should('include', '/admin/security');
    });

    it('reviews security audit logs', () => {
      cy.contains('Audit Logs').should('be.visible');
      
      // Filter options
      cy.get('select[name="event_type"]').select('authentication');
      cy.get('select[name="severity"]').select('high');
      cy.get('[data-testid="date-range-picker"]').click();
      cy.contains('Last 7 days').click();
      
      // Audit log entries
      cy.get('[data-testid="audit-entry"]').should('have.length.greaterThan', 0);
      cy.get('[data-testid="audit-entry"]').first().within(() => {
        cy.get('[data-testid="severity-badge"]').should('have.class', 'severity-high');
        cy.contains('Failed login attempt').should('be.visible');
        cy.get('[data-testid="ip-address"]').should('be.visible');
      });
      
      // View details
      cy.get('[data-testid="audit-entry"]').first().click();
      cy.contains('Audit Event Details').should('be.visible');
      cy.contains('User Agent').should('be.visible');
      cy.contains('Request Headers').should('be.visible');
    });

    it('manages security settings', () => {
      cy.contains('Security Settings').click();
      
      // IP allowlist
      cy.contains('IP Allowlist').should('be.visible');
      cy.contains('button', 'Add IP Range').click();
      cy.get('input[name="ip_range"]').type('192.168.1.0/24');
      cy.get('input[name="description"]').type('Office network');
      cy.contains('button', 'Add').click();
      
      // Rate limiting
      cy.contains('Rate Limiting').should('be.visible');
      cy.get('input[name="api_rate_limit"]').clear().type('1000');
      cy.get('select[name="rate_limit_window"]').select('hour');
      
      // Security headers
      cy.contains('Security Headers').should('be.visible');
      cy.get('input[type="checkbox"][name="enable_hsts"]').check();
      cy.get('input[type="checkbox"][name="enable_csp"]').check();
      
      // Save security settings
      cy.contains('button', 'Save Security Settings').click();
      cy.contains('Security settings updated').should('be.visible');
    });

    it('performs security scan', () => {
      cy.contains('Security Scan').click();
      
      // Start scan
      cy.contains('button', 'Start Security Scan').click();
      cy.contains('Security scan in progress').should('be.visible');
      
      // Mock scan completion
      cy.intercept('GET', '/api/v1/admin/security/scan/status', {
        statusCode: 200,
        body: { status: 'completed', issues: 3 }
      }).as('scanStatus');
      
      cy.wait('@scanStatus');
      cy.contains('Scan Complete').should('be.visible');
      
      // View results
      cy.contains('3 issues found').should('be.visible');
      cy.get('[data-testid="security-issue"]').should('have.length', 3);
      
      // Fix issue
      cy.get('[data-testid="security-issue"]').first().within(() => {
        cy.contains('Weak password policy').should('be.visible');
        cy.contains('button', 'Fix Now').click();
      });
      
      cy.url().should('include', '/admin/settings/authentication');
    });
  });

  describe('Quick Actions and Shortcuts', () => {
    it('uses command palette for quick navigation', () => {
      // Open command palette
      cy.get('body').type('{ctrl}k');
      cy.get('[data-testid="command-palette"]').should('be.visible');
      
      // Search for user
      cy.get('[data-testid="command-input"]').type('find user john');
      cy.get('[data-testid="command-result"]').first().click();
      cy.url().should('include', '/admin/users');
      cy.contains('john').should('be.visible');
      
      // Quick create program
      cy.get('body').type('{ctrl}k');
      cy.get('[data-testid="command-input"]').type('new program');
      cy.get('[data-testid="command-result"]').contains('Create New Program').click();
      cy.url().should('include', '/programs/new');
    });

    it('uses dashboard widgets effectively', () => {
      // Customize dashboard
      cy.contains('button', 'Customize Dashboard').click();
      
      // Add widget
      cy.contains('Add Widget').click();
      cy.get('[data-testid="widget-catalog"]').should('be.visible');
      cy.get('[data-testid="widget-option"]').contains('Recent Signups').click();
      cy.contains('button', 'Add to Dashboard').click();
      
      // Rearrange widgets
      cy.get('[data-testid="widget-recent-signups"]')
        .trigger('mousedown', { button: 0 })
        .trigger('dragstart');
      cy.get('[data-testid="dashboard-drop-zone"]').first()
        .trigger('dragover')
        .trigger('drop');
      
      // Save layout
      cy.contains('button', 'Save Layout').click();
      cy.contains('Dashboard layout saved').should('be.visible');
    });

    it('exports comprehensive admin reports', () => {
      // Open export dialog
      cy.contains('button', 'Export Data').click();
      cy.contains('Export Admin Data').should('be.visible');
      
      // Select data types
      cy.get('input[type="checkbox"][name="export_users"]').check();
      cy.get('input[type="checkbox"][name="export_programs"]').check();
      cy.get('input[type="checkbox"][name="export_analytics"]').check();
      cy.get('input[type="checkbox"][name="export_audit_logs"]').check();
      
      // Configure export
      cy.get('select[name="format"]').select('json');
      cy.get('input[type="checkbox"][name="include_metadata"]').check();
      
      // Start export
      cy.contains('button', 'Start Export').click();
      cy.contains('Export job started').should('be.visible');
      cy.contains('You will receive an email when the export is ready').should('be.visible');
    });
  });
});

describe('Admin Dashboard - Mobile Responsive', () => {
  beforeEach(() => {
    cy.viewport('iphone-x');
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('admin123');
    cy.get('button[type="submit"]').click();
  });

  it('navigates mobile admin interface', () => {
    // Mobile menu
    cy.get('[data-testid="mobile-menu-toggle"]').click();
    cy.get('[data-testid="mobile-nav"]').should('be.visible');
    
    // Navigate to users
    cy.contains('Users').click();
    cy.url().should('include', '/admin/users');
    
    // Mobile-optimized table
    cy.get('[data-testid="mobile-user-list"]').should('be.visible');
    cy.get('[data-testid="user-card"]').should('have.length.greaterThan', 0);
    
    // Quick actions
    cy.get('[data-testid="user-card"]').first().within(() => {
      cy.get('[data-testid="quick-actions"]').click();
      cy.contains('Edit').should('be.visible');
      cy.contains('Suspend').should('be.visible');
    });
  });
});