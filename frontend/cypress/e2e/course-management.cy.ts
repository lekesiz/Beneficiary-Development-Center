describe('Course Management - End to End', () => {
  beforeEach(() => {
    // Login as instructor/admin who can manage courses
    cy.visit('/login');
    cy.get('input[name="email"]').type('instructor@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('BDC Platform').should('be.visible');
  });

  it('completes full course lifecycle: create, view, edit, and manage materials', () => {
    // 1. Navigate to Courses
    cy.get('nav').contains('Courses').click();
    cy.url().should('include', '/courses');
    cy.contains('h1', 'Courses').should('be.visible');

    // 2. Create New Course
    cy.contains('button', 'Create Course').click();
    cy.url().should('include', '/courses/new');
    
    // Fill Basic Information
    cy.get('input[name="title"]').type('Introduction to React Development');
    cy.get('textarea[name="description"]').type('Learn the fundamentals of React including components, state management, hooks, and best practices.');
    cy.get('input[name="code"]').type('REACT-101');
    cy.get('select[name="level"]').select('beginner');
    cy.get('input[name="duration_hours"]').type('40');
    cy.get('input[name="credits"]').type('3');
    
    // Set Schedule
    cy.get('input[name="start_date"]').type('2024-07-15');
    cy.get('input[name="end_date"]').type('2024-08-15');
    cy.get('select[name="schedule_type"]').select('weekly');
    cy.get('input[name="schedule_days"]').type('Monday, Wednesday, Friday');
    cy.get('input[name="schedule_time"]').type('19:00-21:00');
    
    // Set Instructor and Prerequisites
    cy.get('select[name="instructor_id"]').select(1); // Select first instructor
    cy.get('input[name="prerequisites"]').type('Basic JavaScript knowledge{enter}HTML & CSS fundamentals{enter}');
    
    // Add Learning Outcomes
    cy.contains('button', 'Add Learning Outcome').click();
    cy.get('input[placeholder="Learning outcome"]').first().type('Understand React component lifecycle');
    
    cy.contains('button', 'Add Learning Outcome').click();
    cy.get('input[placeholder="Learning outcome"]').last().type('Build interactive web applications with React');
    
    // Add Tags
    cy.get('.tag-input input').type('react{enter}');
    cy.get('.tag-input input').type('frontend{enter}');
    cy.get('.tag-input input').type('javascript{enter}');
    
    // Submit form
    cy.contains('button', 'Create Course').click();
    
    // Verify success and redirect
    cy.contains('Course created successfully').should('be.visible');
    cy.url().should('match', /\/courses\/\d+$/);

    // 3. View Course Details
    cy.contains('h1', 'Introduction to React Development').should('be.visible');
    cy.contains('REACT-101').should('be.visible');
    cy.contains('Beginner').should('be.visible');
    cy.contains('40 hours').should('be.visible');
    cy.contains('3 credits').should('be.visible');
    
    // Check tabs
    cy.contains('button', 'Materials').click();
    cy.contains('No materials uploaded yet').should('be.visible');
    
    cy.contains('button', 'Assignments').click();
    cy.contains('No assignments created yet').should('be.visible');
    
    cy.contains('button', 'Students').click();
    cy.contains('No students enrolled yet').should('be.visible');
    
    // 4. Upload Course Materials
    cy.contains('button', 'Materials').click();
    cy.contains('button', 'Upload Material').click();
    
    // Fill material details
    cy.get('input[name="material_title"]').type('Lecture 1: React Basics');
    cy.get('textarea[name="material_description"]').type('Introduction slides and code examples');
    cy.get('select[name="material_type"]').select('presentation');
    
    // Upload file
    const fileName = 'lecture1.pdf';
    cy.fixture(fileName, { encoding: null }).then(fileContent => {
      cy.get('input[type="file"]').selectFile({
        contents: fileContent,
        fileName: fileName,
        mimeType: 'application/pdf'
      });
    });
    
    cy.contains('button', 'Upload').click();
    cy.contains('Material uploaded successfully').should('be.visible');
    cy.contains('Lecture 1: React Basics').should('be.visible');
    
    // 5. Create Assignment
    cy.contains('button', 'Assignments').click();
    cy.contains('button', 'Create Assignment').click();
    
    cy.get('input[name="assignment_title"]').type('Build a Todo App');
    cy.get('textarea[name="assignment_description"]').type('Create a simple todo application using React hooks');
    cy.get('input[name="due_date"]').type('2024-07-25');
    cy.get('input[name="max_points"]').type('100');
    
    cy.contains('button', 'Create Assignment').click();
    cy.contains('Assignment created successfully').should('be.visible');
    cy.contains('Build a Todo App').should('be.visible');
    
    // 6. Edit Course
    cy.contains('button', 'Edit').click();
    cy.url().should('include', '/edit');
    
    // Update some fields
    cy.get('input[name="duration_hours"]').clear().type('45');
    cy.get('textarea[name="description"]').clear().type('Updated: Comprehensive React course covering modern React patterns and best practices.');
    
    // Add another learning outcome
    cy.contains('button', 'Add Learning Outcome').click();
    cy.get('input[placeholder="Learning outcome"]').last().type('Master React Router and state management');
    
    // Save changes
    cy.contains('button', 'Update Course').click();
    cy.contains('Course updated successfully').should('be.visible');
    
    // Verify updates
    cy.contains('45 hours').should('be.visible');
    cy.contains('Updated: Comprehensive React course').should('be.visible');
    
    // 7. Manage Course Settings
    cy.contains('button', 'Settings').click();
    
    // Update enrollment settings
    cy.get('input[name="max_students"]').type('30');
    cy.get('input[name="enrollment_deadline"]').type('2024-07-10');
    cy.get('input[name="allow_late_enrollment"]').check();
    
    cy.contains('button', 'Save Settings').click();
    cy.contains('Settings updated successfully').should('be.visible');
    
    // 8. Navigate back to Courses List
    cy.get('nav').contains('Courses').click();
    
    // Search for the course
    cy.get('input[placeholder="Search courses..."]').type('React Development');
    cy.contains('Introduction to React Development').should('be.visible');
    
    // Filter by level
    cy.get('select[aria-label="Filter by level"]').select('beginner');
    cy.contains('Introduction to React Development').should('be.visible');
  });

  it('manages course enrollments and student progress', () => {
    // Navigate to an existing course
    cy.get('nav').contains('Courses').click();
    cy.get('table tbody tr').first().click();
    
    // Go to Students tab
    cy.contains('button', 'Students').click();
    
    // Enroll a student manually
    cy.contains('button', 'Enroll Student').click();
    cy.get('select[name="student_id"]').select(1); // Select first student
    cy.get('textarea[name="enrollment_notes"]').type('Manual enrollment by instructor');
    cy.contains('button', 'Enroll').click();
    
    cy.contains('Student enrolled successfully').should('be.visible');
    
    // View student progress
    cy.contains('tr', 'Student Name').within(() => {
      cy.contains('button', 'View Progress').click();
    });
    
    // Record attendance
    cy.contains('button', 'Record Attendance').click();
    cy.get('input[name="attendance_date"]').type('2024-07-15');
    cy.get('select[name="attendance_status"]').select('present');
    cy.contains('button', 'Save').click();
    
    cy.contains('Attendance recorded').should('be.visible');
    
    // Grade assignment
    cy.contains('button', 'Assignments').click();
    cy.contains('tr', 'Build a Todo App').within(() => {
      cy.contains('button', 'Grade').click();
    });
    
    cy.get('input[name="score"]').type('85');
    cy.get('textarea[name="feedback"]').type('Good work! Consider adding error handling.');
    cy.contains('button', 'Submit Grade').click();
    
    cy.contains('Grade submitted successfully').should('be.visible');
  });

  it('handles course scheduling and calendar integration', () => {
    cy.get('nav').contains('Courses').click();
    cy.contains('button', 'Create Course').click();
    
    // Fill basic info
    cy.get('input[name="title"]').type('Advanced JavaScript');
    cy.get('textarea[name="description"]').type('Deep dive into JavaScript');
    cy.get('input[name="code"]').type('JS-201');
    
    // Test recurring schedule
    cy.get('select[name="schedule_type"]').select('recurring');
    cy.get('input[name="recurrence_pattern"]').check('weekly');
    cy.get('input[name="recurrence_days"][value="monday"]').check();
    cy.get('input[name="recurrence_days"][value="wednesday"]').check();
    cy.get('input[name="start_time"]').type('18:00');
    cy.get('input[name="end_time"]').type('20:00');
    
    // Set recurrence end
    cy.get('input[name="recurrence_end"]').type('2024-12-31');
    
    // Generate sessions
    cy.contains('button', 'Generate Sessions').click();
    cy.contains('Sessions generated successfully').should('be.visible');
    
    // View calendar
    cy.contains('button', 'View Calendar').click();
    cy.contains('Course Calendar').should('be.visible');
    
    // Verify sessions are shown
    cy.get('.calendar-event').should('have.length.greaterThan', 0);
  });

  it('exports course data and generates reports', () => {
    cy.get('nav').contains('Courses').click();
    cy.get('table tbody tr').first().click();
    
    // Export course roster
    cy.contains('button', 'Students').click();
    cy.contains('button', 'Export Roster').click();
    cy.contains('button', 'Export as CSV').click();
    
    cy.contains('Roster exported successfully').should('be.visible');
    
    // Generate progress report
    cy.contains('button', 'Reports').click();
    cy.contains('button', 'Generate Progress Report').click();
    
    cy.get('select[name="report_format"]').select('pdf');
    cy.get('input[name="include_attendance"]').check();
    cy.get('input[name="include_grades"]').check();
    cy.contains('button', 'Generate').click();
    
    cy.contains('Report generated successfully').should('be.visible');
    
    // Generate certificate of completion
    cy.contains('button', 'Generate Certificates').click();
    cy.get('input[name="min_attendance"]').type('80');
    cy.get('input[name="min_grade"]').type('70');
    cy.contains('button', 'Generate for Eligible Students').click();
    
    cy.contains('Certificates generated').should('be.visible');
  });

  it('handles course duplication and templates', () => {
    cy.get('nav').contains('Courses').click();
    cy.get('table tbody tr').first().within(() => {
      cy.get('[aria-label="More actions"]').click();
    });
    
    // Duplicate course
    cy.contains('button', 'Duplicate').click();
    cy.contains('Duplicate Course').should('be.visible');
    
    // Modify duplicated course
    cy.get('input[name="title"]').clear().type('Introduction to React Development - Summer 2024');
    cy.get('input[name="code"]').clear().type('REACT-101-S24');
    cy.get('input[name="start_date"]').clear().type('2024-08-01');
    cy.get('input[name="end_date"]').clear().type('2024-09-01');
    
    cy.contains('button', 'Create Duplicate').click();
    cy.contains('Course duplicated successfully').should('be.visible');
    
    // Save as template
    cy.contains('button', 'Save as Template').click();
    cy.get('input[name="template_name"]').type('React Course Template');
    cy.get('textarea[name="template_description"]').type('Standard template for React courses');
    cy.contains('button', 'Save Template').click();
    
    cy.contains('Template saved successfully').should('be.visible');
  });

  it('validates course form and handles errors', () => {
    cy.get('nav').contains('Courses').click();
    cy.contains('button', 'Create Course').click();
    
    // Try to submit empty form
    cy.contains('button', 'Create Course').click();
    
    // Check validation messages
    cy.contains('Title is required').should('be.visible');
    cy.contains('Description is required').should('be.visible');
    cy.contains('Course code is required').should('be.visible');
    
    // Test date validation
    cy.get('input[name="title"]').type('Test Course');
    cy.get('input[name="start_date"]').type('2024-08-01');
    cy.get('input[name="end_date"]').type('2024-07-01'); // End before start
    
    cy.contains('button', 'Create Course').click();
    cy.contains('End date must be after start date').should('be.visible');
    
    // Test duplicate course code
    cy.get('input[name="code"]').type('EXISTING-CODE');
    cy.intercept('POST', '/api/v1/courses', {
      statusCode: 400,
      body: { error: 'Course code already exists' }
    }).as('duplicateCode');
    
    cy.contains('button', 'Create Course').click();
    cy.wait('@duplicateCode');
    cy.contains('Course code already exists').should('be.visible');
  });

  it('handles permissions for different roles', () => {
    // Logout and login as student
    cy.contains('button', 'Logout').click();
    
    cy.get('input[name="email"]').type('student@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Students should see limited course view
    cy.get('nav').contains('Courses').should('not.exist');
    
    // Access course directly (if enrolled)
    cy.visit('/courses/1');
    
    // Should not see edit/delete buttons
    cy.contains('button', 'Edit').should('not.exist');
    cy.contains('button', 'Delete').should('not.exist');
    
    // But can see materials and assignments
    cy.contains('button', 'Materials').should('be.visible');
    cy.contains('button', 'Assignments').should('be.visible');
  });
});

describe('Course Management - Mobile Responsive', () => {
  beforeEach(() => {
    cy.viewport('iphone-x');
    
    cy.visit('/login');
    cy.get('input[name="email"]').type('instructor@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
  });

  it('works on mobile devices', () => {
    // Open mobile menu
    cy.get('button[aria-label="Open menu"]').click();
    cy.contains('Courses').click();
    
    // Check responsive table
    cy.contains('h1', 'Courses').should('be.visible');
    
    // Cards should be shown instead of table on mobile
    cy.get('.course-card').should('be.visible');
    
    // Navigate to course detail
    cy.get('.course-card').first().click();
    
    // Tabs should be scrollable
    cy.get('[role="tablist"]').should('have.css', 'overflow-x', 'auto');
    
    // Create course on mobile
    cy.get('[aria-label="Back"]').click();
    cy.contains('button', 'Create Course').click();
    
    // Form should be mobile-friendly
    cy.get('form').should('be.visible');
    cy.get('input[name="title"]').should('be.visible');
  });
});