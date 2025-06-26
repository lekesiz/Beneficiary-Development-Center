describe('Beneficiary Management - End to End', () => {
  beforeEach(() => {
    // Login as admin/trainer who can manage beneficiaries
    cy.visit('/login');
    cy.get('input[name="email"]').type('trainer@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('BDC Platform').should('be.visible');
  });

  it('completes full beneficiary lifecycle: create, view, edit, and update status', () => {
    // 1. Navigate to Beneficiaries
    cy.get('nav').contains('Beneficiaries').click();
    cy.url().should('include', '/beneficiaries');
    cy.contains('h1', 'Beneficiaries').should('be.visible');

    // 2. Create New Beneficiary
    cy.contains('button', 'Add Beneficiary').click();
    cy.url().should('include', '/beneficiaries/new');
    
    // Fill Personal Information
    cy.get('input[name="first_name"]').type('John');
    cy.get('input[name="last_name"]').type('Doe');
    cy.get('input[name="email"]').type('john.doe@example.com');
    cy.get('input[name="phone"]').type('+905551234567');
    cy.get('input[name="date_of_birth"]').type('1990-05-15');
    cy.get('select[name="gender"]').select('male');
    cy.get('input[name="national_id"]').type('12345678901');
    
    // Fill Address Information
    cy.get('textarea[name="address"]').type('123 Test Street, Apt 4B');
    cy.get('input[name="city"]').type('Istanbul');
    cy.get('input[name="state"]').type('Istanbul');
    cy.get('input[name="postal_code"]').type('34000');
    cy.get('input[name="country"]').type('Turkey');
    
    // Fill Professional Information
    cy.get('select[name="education_level"]').select('bachelor');
    cy.get('input[name="field_of_study"]').type('Computer Science');
    cy.get('select[name="employment_status"]').select('employed');
    cy.get('input[name="current_job_title"]').type('Junior Developer');
    cy.get('input[name="employer"]').type('Tech Solutions Inc.');
    cy.get('input[name="skills"]').type('JavaScript{enter}React{enter}Node.js{enter}');
    
    // Fill Program Enrollment (if admin)
    cy.get('body').then($body => {
      if ($body.find('select[name="program_id"]').length > 0) {
        cy.get('select[name="program_id"]').select(1); // Select first program
        cy.get('select[name="status"]').select('active');
      }
    });
    
    // Add Emergency Contact
    cy.get('input[name="emergency_contact_name"]').type('Jane Doe');
    cy.get('input[name="emergency_contact_phone"]').type('+905559876543');
    cy.get('input[name="emergency_contact_relationship"]').type('Sister');
    
    // Submit form
    cy.contains('button', 'Create').click();
    
    // Verify success and redirect
    cy.contains('Beneficiary created successfully').should('be.visible');
    cy.url().should('match', /\/beneficiaries\/\d+$/);

    // 3. View Beneficiary Details
    cy.contains('h1', 'John Doe').should('be.visible');
    cy.contains('john.doe@example.com').should('be.visible');
    cy.contains('+905551234567').should('be.visible');
    cy.contains('Active').should('be.visible');
    
    // Check tabs
    cy.contains('button', 'Enrollments').click();
    cy.contains('Active Enrollments').should('be.visible');
    
    cy.contains('button', 'Progress').click();
    cy.contains('Course Progress').should('be.visible');
    
    cy.contains('button', 'Documents').click();
    cy.contains('Uploaded Documents').should('be.visible');
    
    cy.contains('button', 'Notes').click();
    cy.contains('Add Note').should('be.visible');
    
    // 4. Add a Note
    cy.get('textarea[placeholder="Write a note..."]').type('Initial assessment completed. Strong technical background, motivated learner.');
    cy.contains('button', 'Save Note').click();
    cy.contains('Note added successfully').should('be.visible');
    cy.contains('Initial assessment completed').should('be.visible');
    
    // 5. Edit Beneficiary
    cy.contains('button', 'Edit').click();
    cy.url().should('include', '/edit');
    
    // Update some fields
    cy.get('input[name="current_job_title"]').clear().type('Full Stack Developer');
    cy.get('input[name="employer"]').clear().type('Innovation Labs');
    cy.get('input[name="skills"]').type('Python{enter}Docker{enter}');
    
    // Save changes
    cy.contains('button', 'Update').click();
    cy.contains('Beneficiary updated successfully').should('be.visible');
    
    // Verify updates
    cy.contains('Full Stack Developer').should('be.visible');
    cy.contains('Innovation Labs').should('be.visible');
    
    // 6. Upload Document
    cy.contains('button', 'Documents').click();
    cy.contains('button', 'Upload Document').click();
    
    // Upload a file (note: actual file upload in Cypress requires fixture)
    const fileName = 'resume.pdf';
    cy.fixture(fileName, { encoding: null }).then(fileContent => {
      cy.get('input[type="file"]').selectFile({
        contents: fileContent,
        fileName: fileName,
        mimeType: 'application/pdf'
      });
    });
    
    cy.contains('resume.pdf').should('be.visible');
    cy.contains('Document uploaded successfully').should('be.visible');
    
    // 7. Navigate back to Beneficiaries List
    cy.get('nav').contains('Beneficiaries').click();
    
    // Search for the beneficiary
    cy.get('input[placeholder="Search beneficiaries..."]').type('John Doe');
    cy.contains('John Doe').should('be.visible');
    
    // Filter by status
    cy.get('select[aria-label="Filter by status"]').select('active');
    cy.contains('John Doe').should('be.visible');
    
    // 8. Bulk Actions (if available)
    cy.get('input[type="checkbox"][aria-label="Select John Doe"]').check();
    cy.contains('button', '1 selected').should('be.visible');
    
    // Export selected
    cy.contains('button', 'Export Selected').click();
    cy.contains('Export completed').should('be.visible');
  });

  it('validates beneficiary form correctly', () => {
    cy.get('nav').contains('Beneficiaries').click();
    cy.contains('button', 'Add Beneficiary').click();
    
    // Try to submit empty form
    cy.contains('button', 'Create').click();
    
    // Check validation messages
    cy.contains('First name is required').should('be.visible');
    cy.contains('Last name is required').should('be.visible');
    cy.contains('Email is required').should('be.visible');
    cy.contains('Phone is required').should('be.visible');
    
    // Test email validation
    cy.get('input[name="email"]').type('invalid-email');
    cy.contains('button', 'Create').click();
    cy.contains('Invalid email address').should('be.visible');
    
    // Test phone validation
    cy.get('input[name="phone"]').type('123'); // Too short
    cy.contains('button', 'Create').click();
    cy.contains('Invalid phone number').should('be.visible');
    
    // Test national ID validation
    cy.get('input[name="national_id"]').type('123'); // Too short
    cy.contains('button', 'Create').click();
    cy.contains('National ID must be 11 digits').should('be.visible');
  });

  it('manages beneficiary enrollments', () => {
    // Navigate to a beneficiary
    cy.get('nav').contains('Beneficiaries').click();
    cy.get('table tbody tr').first().click();
    
    // Go to Enrollments tab
    cy.contains('button', 'Enrollments').click();
    
    // Enroll in a new program
    cy.contains('button', 'Enroll in Program').click();
    cy.get('select[name="program_id"]').select(1);
    cy.get('textarea[name="enrollment_notes"]').type('Enrolled based on assessment results');
    cy.contains('button', 'Enroll').click();
    
    cy.contains('Enrollment successful').should('be.visible');
    
    // Update enrollment status
    cy.contains('button', 'Update Status').first().click();
    cy.get('select[name="enrollment_status"]').select('completed');
    cy.contains('button', 'Save').click();
    cy.contains('Status updated successfully').should('be.visible');
  });

  it('tracks beneficiary progress', () => {
    cy.get('nav').contains('Beneficiaries').click();
    cy.get('table tbody tr').first().click();
    
    // Go to Progress tab
    cy.contains('button', 'Progress').click();
    
    // View course progress
    cy.contains('Course Progress').should('be.visible');
    
    // Record achievement
    cy.contains('button', 'Record Achievement').click();
    cy.get('input[name="achievement_title"]').type('Completed React Module');
    cy.get('textarea[name="achievement_description"]').type('Successfully completed all React assignments with 95% score');
    cy.get('input[name="achievement_date"]').type('2024-06-20');
    cy.contains('button', 'Save Achievement').click();
    
    cy.contains('Achievement recorded').should('be.visible');
    cy.contains('Completed React Module').should('be.visible');
  });

  it('handles data export and reporting', () => {
    cy.get('nav').contains('Beneficiaries').click();
    
    // Export all beneficiaries
    cy.contains('button', 'Export').click();
    cy.contains('button', 'Export as CSV').click();
    
    // Verify export started
    cy.contains('Export started').should('be.visible');
    
    // Generate report
    cy.contains('button', 'Generate Report').click();
    cy.get('select[name="report_type"]').select('enrollment_summary');
    cy.get('input[name="date_from"]').type('2024-01-01');
    cy.get('input[name="date_to"]').type('2024-12-31');
    cy.contains('button', 'Generate').click();
    
    cy.contains('Report generated successfully').should('be.visible');
  });

  it('shows appropriate empty states', () => {
    // Mock empty response
    cy.intercept('GET', '/api/v1/beneficiaries*', {
      statusCode: 200,
      body: { data: [], total: 0 }
    }).as('emptyBeneficiaries');
    
    cy.get('nav').contains('Beneficiaries').click();
    cy.wait('@emptyBeneficiaries');
    
    cy.contains('No beneficiaries found').should('be.visible');
    cy.contains('Get started by adding your first beneficiary').should('be.visible');
    cy.contains('button', 'Add First Beneficiary').should('be.visible');
  });

  it('handles search and advanced filtering', () => {
    cy.get('nav').contains('Beneficiaries').click();
    
    // Search by name
    cy.get('input[placeholder="Search beneficiaries..."]').type('John');
    cy.wait(500); // Debounce
    
    // Open advanced filters
    cy.contains('button', 'Advanced Filters').click();
    
    // Filter by multiple criteria
    cy.get('select[name="filter_status"]').select('active');
    cy.get('select[name="filter_education"]').select('bachelor');
    cy.get('select[name="filter_employment"]').select('employed');
    cy.get('input[name="filter_age_from"]').type('25');
    cy.get('input[name="filter_age_to"]').type('35');
    
    cy.contains('button', 'Apply Filters').click();
    
    // Verify filters applied
    cy.contains('4 filters applied').should('be.visible');
    
    // Clear filters
    cy.contains('button', 'Clear Filters').click();
    cy.contains('Showing all beneficiaries').should('be.visible');
  });
});

describe('Beneficiary Management - Role-Based Access', () => {
  it('shows limited actions for instructor role', () => {
    // Login as instructor
    cy.visit('/login');
    cy.get('input[name="email"]').type('instructor@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    cy.get('nav').contains('Beneficiaries').click();
    cy.get('table tbody tr').first().click();
    
    // Instructor should see view-only mode
    cy.contains('button', 'Edit').should('not.exist');
    cy.contains('button', 'Delete').should('not.exist');
    
    // But can add notes
    cy.contains('button', 'Notes').click();
    cy.get('textarea[placeholder="Write a note..."]').should('be.visible');
  });

  it('prevents unauthorized access to create form', () => {
    // Login as student
    cy.visit('/login');
    cy.get('input[name="email"]').type('student@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Try to access beneficiaries directly
    cy.visit('/beneficiaries', { failOnStatusCode: false });
    cy.contains('You do not have permission').should('be.visible');
  });
});

describe('Beneficiary Management - Performance', () => {
  it('handles large datasets efficiently', () => {
    // Mock large dataset
    const largeBeneficiaryList = Array.from({ length: 100 }, (_, i) => ({
      id: i + 1,
      first_name: `User${i}`,
      last_name: `Test${i}`,
      email: `user${i}@example.com`,
      status: i % 2 === 0 ? 'active' : 'inactive',
      created_at: new Date().toISOString()
    }));

    cy.intercept('GET', '/api/v1/beneficiaries*', {
      statusCode: 200,
      body: { 
        data: largeBeneficiaryList.slice(0, 10), // First page
        total: 100,
        page: 1,
        per_page: 10
      }
    }).as('largeBeneficiaries');
    
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    cy.get('nav').contains('Beneficiaries').click();
    cy.wait('@largeBeneficiaries');
    
    // Check pagination is shown
    cy.contains('1-10 of 100').should('be.visible');
    cy.get('[aria-label="Go to next page"]').should('be.visible');
    
    // Test pagination
    cy.get('[aria-label="Go to next page"]').click();
    cy.contains('11-20 of 100').should('be.visible');
    
    // Test page size change
    cy.get('select[aria-label="Rows per page"]').select('50');
    cy.contains('1-50 of 100').should('be.visible');
  });
});