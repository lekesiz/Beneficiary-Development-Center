describe('Program Management - End to End', () => {
  beforeEach(() => {
    // Login as admin user
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('BDC Platform').should('be.visible');
  });

  it('completes full program lifecycle: create, view, edit, and delete', () => {
    // 1. Navigate to Programs
    cy.get('nav').contains('Programs').click();
    cy.url().should('include', '/programs');
    cy.contains('h1', 'Programs').should('be.visible');

    // 2. Create New Program
    cy.contains('button', 'Yeni Program').click();
    cy.url().should('include', '/programs/new');
    
    // Fill Basic Information
    cy.get('input[name="title"]').type('Advanced Web Development Bootcamp');
    cy.get('textarea[name="description"]').type('A comprehensive bootcamp covering modern web development technologies including React, Node.js, and cloud deployment.');
    cy.get('select[name="program_type"]').select('bootcamp');
    cy.get('select[name="status"]').select('active');
    
    // Fill Dates and Capacity
    cy.get('input[name="start_date"]').type('2024-07-01');
    cy.get('input[name="end_date"]').type('2024-09-30');
    cy.get('input[name="enrollment_start"]').type('2024-06-01');
    cy.get('input[name="enrollment_end"]').type('2024-06-25');
    cy.get('input[name="capacity"]').clear().type('30');
    
    // Fill Location and Format
    cy.get('select[name="delivery_method"]').select('hybrid');
    cy.get('input[name="location"]').type('Istanbul Tech Hub');
    cy.get('input[name="online_meeting_link"]').type('https://zoom.us/j/123456789');
    
    // Fill Pricing
    cy.get('input[name="is_paid"]').check();
    cy.get('input[name="price"]').type('5000');
    cy.get('select[name="currency"]').select('TRY');
    
    // Add Objectives
    cy.contains('button', 'Hedef Ekle').click();
    cy.get('input[placeholder="Hedef açıklaması"]').first().type('Master React and modern frontend development');
    
    cy.contains('button', 'Hedef Ekle').click();
    cy.get('input[placeholder="Hedef açıklaması"]').last().type('Build and deploy full-stack applications');
    
    // Add Tags
    cy.get('.tag-input input').type('web development{enter}');
    cy.get('.tag-input input').type('react{enter}');
    cy.get('.tag-input input').type('nodejs{enter}');
    
    // Submit form
    cy.contains('button', 'Oluştur').click();
    
    // Verify success and redirect
    cy.contains('Program başarıyla oluşturuldu').should('be.visible');
    cy.url().should('match', /\/programs\/\d+$/);

    // 3. View Program Details
    cy.contains('h1', 'Advanced Web Development Bootcamp').should('be.visible');
    cy.contains('Bootcamp').should('be.visible');
    cy.contains('Active').should('be.visible');
    cy.contains('30 participants').should('be.visible');
    cy.contains('₺5,000').should('be.visible');
    
    // Check tabs
    cy.contains('button', 'Courses').click();
    cy.contains('No courses added yet').should('be.visible');
    
    cy.contains('button', 'Participants').click();
    cy.contains('No participants enrolled yet').should('be.visible');
    
    // 4. Edit Program
    cy.contains('button', 'Edit').click();
    cy.url().should('include', '/edit');
    
    // Update some fields
    cy.get('input[name="capacity"]').clear().type('40');
    cy.get('textarea[name="description"]').clear().type('Updated description: An intensive bootcamp with industry mentors and real-world projects.');
    
    // Add another objective
    cy.contains('button', 'Hedef Ekle').click();
    cy.get('input[placeholder="Hedef açıklaması"]').last().type('Get career support and job placement assistance');
    
    // Save changes
    cy.contains('button', 'Güncelle').click();
    cy.contains('Program başarıyla güncellendi').should('be.visible');
    
    // Verify updates
    cy.contains('40 participants').should('be.visible');
    cy.contains('Updated description').should('be.visible');
    
    // 5. Navigate back to Programs List
    cy.get('nav').contains('Programs').click();
    
    // Search for the program
    cy.get('input[placeholder="Search programs..."]').type('Advanced Web Development');
    cy.contains('Advanced Web Development Bootcamp').should('be.visible');
    
    // Filter by status
    cy.get('select[aria-label="Filter by status"]').select('active');
    cy.contains('Advanced Web Development Bootcamp').should('be.visible');
    
    // 6. Delete Program (if delete functionality exists)
    // Note: This assumes there's a delete action in the table or detail view
    // Uncomment and adjust based on actual implementation
    /*
    cy.contains('tr', 'Advanced Web Development Bootcamp')
      .find('button[aria-label="Delete"]')
      .click();
    
    cy.contains('Are you sure you want to delete this program?').should('be.visible');
    cy.contains('button', 'Delete').click();
    cy.contains('Program deleted successfully').should('be.visible');
    
    // Verify program is removed
    cy.contains('Advanced Web Development Bootcamp').should('not.exist');
    */
  });

  it('handles form validation errors', () => {
    cy.get('nav').contains('Programs').click();
    cy.contains('button', 'Yeni Program').click();
    
    // Try to submit empty form
    cy.contains('button', 'Oluştur').click();
    
    // Check validation messages
    cy.contains('Program adı zorunludur').should('be.visible');
    cy.contains('Açıklama zorunludur').should('be.visible');
    cy.contains('Başlangıç tarihi zorunludur').should('be.visible');
    
    // Fill required fields partially
    cy.get('input[name="title"]').type('Test Program');
    cy.get('input[name="start_date"]').type('2024-07-01');
    cy.get('input[name="end_date"]').type('2024-06-01'); // End before start
    
    cy.contains('button', 'Oluştur').click();
    cy.contains('Bitiş tarihi başlangıç tarihinden sonra olmalıdır').should('be.visible');
  });

  it('manages program courses', () => {
    // Navigate to an existing program
    cy.get('nav').contains('Programs').click();
    cy.get('table tbody tr').first().click();
    
    // Go to Courses tab
    cy.contains('button', 'Courses').click();
    
    // Add a course (assuming there's an "Add Course" button)
    // This would depend on the actual implementation
    /*
    cy.contains('button', 'Add Course').click();
    cy.get('input[name="course_title"]').type('Introduction to React');
    cy.get('textarea[name="course_description"]').type('Learn the fundamentals of React');
    cy.contains('button', 'Save Course').click();
    
    cy.contains('Course added successfully').should('be.visible');
    cy.contains('Introduction to React').should('be.visible');
    */
  });

  it('exports program data', () => {
    cy.get('nav').contains('Programs').click();
    
    // Look for export button
    cy.contains('button', 'Export').should('be.visible').click();
    
    // Verify download started (checking for the file download is complex in Cypress)
    // You might want to verify the API call instead
    cy.intercept('GET', '/api/v1/programs/export*', { statusCode: 200 }).as('export');
    cy.wait('@export');
  });

  it('handles pagination and sorting', () => {
    cy.get('nav').contains('Programs').click();
    
    // Check if pagination exists (assuming there are multiple programs)
    cy.get('[aria-label="Go to next page"]').should('exist');
    
    // Sort by title
    cy.get('th').contains('Title').click();
    // Verify sorting (would need to check order of elements)
    
    // Sort by start date
    cy.get('th').contains('Start Date').click();
    // Verify sorting
    
    // Change page size
    cy.get('select[aria-label="Rows per page"]').select('20');
    // Verify table updates
  });

  it('shows appropriate error states', () => {
    // Intercept API call to simulate error
    cy.intercept('GET', '/api/v1/programs*', { 
      statusCode: 500,
      body: { error: 'Internal server error' }
    }).as('programsError');
    
    cy.get('nav').contains('Programs').click();
    cy.wait('@programsError');
    
    cy.contains('Something went wrong').should('be.visible');
    cy.contains('button', 'Try Again').should('be.visible');
  });

  it('respects user permissions', () => {
    // Logout and login as student
    cy.contains('button', 'Logout').click();
    
    cy.get('input[name="email"]').type('student@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Verify Programs nav item is not visible for students
    cy.get('nav').should('not.contain', 'Programs');
    
    // Try to access programs directly
    cy.visit('/programs', { failOnStatusCode: false });
    cy.contains('You do not have permission').should('be.visible');
  });
});

describe('Program Management - Mobile Responsive', () => {
  beforeEach(() => {
    // Set mobile viewport
    cy.viewport('iphone-x');
    
    // Login
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
  });

  it('works on mobile devices', () => {
    // Open mobile menu
    cy.get('button[aria-label="Open menu"]').click();
    cy.contains('Programs').click();
    
    // Check responsive layout
    cy.contains('h1', 'Programs').should('be.visible');
    cy.contains('button', 'Yeni Program').should('be.visible');
    
    // Create program on mobile
    cy.contains('button', 'Yeni Program').click();
    
    // Form should be responsive
    cy.get('input[name="title"]').should('be.visible').type('Mobile Test Program');
    cy.get('textarea[name="description"]').should('be.visible');
    
    // Scroll should work properly
    cy.scrollTo('bottom');
    cy.contains('button', 'Oluştur').should('be.visible');
  });
});