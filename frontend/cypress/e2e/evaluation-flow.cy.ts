describe('Evaluation Flow - End to End', () => {
  beforeEach(() => {
    // Login as student
    cy.visit('/login');
    cy.get('input[name="email"]').type('student@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('BDC Platform').should('be.visible');
  });

  it('completes full evaluation flow: browse, start, complete, and review', () => {
    // 1. Navigate to Evaluations
    cy.get('nav').contains('Evaluations').click();
    cy.url().should('include', '/evaluations');
    cy.contains('h1', 'Evaluations').should('be.visible');

    // 2. Browse available evaluations
    cy.contains('Available Evaluations').should('be.visible');
    cy.contains('Completed Evaluations').should('be.visible');
    
    // Check evaluation cards
    cy.get('[data-testid="evaluation-card"]').should('have.length.greaterThan', 0);
    
    // 3. View evaluation details
    cy.get('[data-testid="evaluation-card"]').first().within(() => {
      cy.contains('React Fundamentals Assessment').should('be.visible');
      cy.contains('30 questions').should('be.visible');
      cy.contains('45 minutes').should('be.visible');
      cy.contains('button', 'View Details').click();
    });

    // Check evaluation detail page
    cy.url().should('match', /\/evaluations\/\d+$/);
    cy.contains('h1', 'React Fundamentals Assessment').should('be.visible');
    cy.contains('Evaluation Overview').should('be.visible');
    cy.contains('Multiple Choice').should('be.visible');
    cy.contains('Passing Score: 70%').should('be.visible');

    // 4. Start evaluation
    cy.contains('button', 'Start Evaluation').click();
    
    // Confirm start dialog
    cy.contains('Start Evaluation?').should('be.visible');
    cy.contains('Once you start, you will have 45 minutes to complete all questions.').should('be.visible');
    cy.contains('button', 'Start Now').click();

    // 5. Answer questions
    cy.url().should('include', '/attempt');
    cy.contains('Question 1 of 30').should('be.visible');
    
    // Timer should be visible
    cy.get('[data-testid="timer"]').should('be.visible');
    cy.get('[data-testid="timer"]').should('contain', '44:'); // Should show time remaining

    // Answer first question
    cy.contains('What is React?').should('be.visible');
    cy.get('input[type="radio"][value="A JavaScript library for building user interfaces"]').check();
    cy.contains('button', 'Next').click();

    // Answer more questions (simulate answering 5 questions)
    for (let i = 2; i <= 5; i++) {
      cy.contains(`Question ${i} of 30`).should('be.visible');
      cy.get('input[type="radio"]').first().check();
      
      if (i < 5) {
        cy.contains('button', 'Next').click();
      }
    }

    // Navigate back
    cy.contains('button', 'Previous').click();
    cy.contains('Question 4 of 30').should('be.visible');
    
    // Mark for review
    cy.contains('button', 'Mark for Review').click();
    cy.get('[data-testid="review-indicator"]').should('be.visible');

    // 6. Review screen
    cy.contains('button', 'Review & Submit').click();
    
    cy.contains('Review Your Answers').should('be.visible');
    cy.contains('Questions Answered: 5/30').should('be.visible');
    cy.contains('Marked for Review: 1').should('be.visible');
    
    // Check question navigation grid
    cy.get('[data-testid="question-grid"]').should('be.visible');
    cy.get('[data-testid="question-grid"] button').should('have.length', 30);
    
    // Navigate to unanswered question
    cy.get('[data-testid="question-grid"] button.unanswered').first().click();
    cy.url().should('include', '/attempt');
    
    // Answer the question
    cy.get('input[type="radio"]').first().check();
    cy.contains('button', 'Save & Continue').click();

    // 7. Submit evaluation
    cy.contains('button', 'Review & Submit').click();
    cy.contains('button', 'Submit Evaluation').click();
    
    // Confirm submission
    cy.contains('Submit Evaluation?').should('be.visible');
    cy.contains('You have answered 6 out of 30 questions').should('be.visible');
    cy.contains('button', 'Submit').click();

    // 8. View results
    cy.url().should('include', '/result');
    cy.contains('Evaluation Completed').should('be.visible');
    
    // Check score
    cy.contains('Your Score').should('be.visible');
    cy.get('[data-testid="score-percentage"]').should('be.visible');
    cy.get('[data-testid="score-circle"]').should('be.visible');
    
    // Check pass/fail status
    cy.get('[data-testid="result-status"]').should('contain.text', 'Failed'); // Since we only answered 6/30 questions
    
    // View detailed results
    cy.contains('button', 'View Detailed Results').click();
    
    // Check answer review
    cy.contains('Answer Review').should('be.visible');
    cy.get('[data-testid="answer-review-item"]').should('have.length', 6); // Only answered questions shown
    
    // Check correct/incorrect indicators
    cy.get('[data-testid="answer-review-item"]').first().within(() => {
      cy.get('[data-testid="answer-status"]').should('exist');
      cy.contains('Your Answer').should('be.visible');
    });

    // 9. Navigate back to evaluations
    cy.contains('button', 'Back to Evaluations').click();
    cy.url().should('include', '/evaluations');
    
    // Check that evaluation now appears in completed section
    cy.contains('Completed Evaluations').parent().within(() => {
      cy.contains('React Fundamentals Assessment').should('be.visible');
      cy.contains('Failed').should('be.visible');
    });
  });

  it('handles evaluation time limit', () => {
    // Start a timed evaluation
    cy.get('[data-testid="evaluation-card"]').first().click();
    cy.contains('button', 'Start Evaluation').click();
    cy.contains('button', 'Start Now').click();

    // Mock time passage (this would need backend support)
    cy.intercept('GET', '/api/v1/evaluations/*/attempt/time-remaining', {
      statusCode: 200,
      body: { seconds_remaining: 5 }
    }).as('timeCheck');

    // Wait for time warning
    cy.wait('@timeCheck');
    cy.contains('Time is running out!').should('be.visible');
    cy.contains('You have less than 1 minute remaining').should('be.visible');

    // Auto-submit when time expires
    cy.intercept('POST', '/api/v1/evaluations/*/attempt/auto-submit', {
      statusCode: 200,
      body: { message: 'Evaluation auto-submitted due to time limit' }
    }).as('autoSubmit');

    cy.wait('@autoSubmit');
    cy.url().should('include', '/result');
    cy.contains('Time Expired').should('be.visible');
  });

  it('saves progress and resumes evaluation', () => {
    // Start evaluation
    cy.get('[data-testid="evaluation-card"]').first().click();
    cy.contains('button', 'Start Evaluation').click();
    cy.contains('button', 'Start Now').click();

    // Answer some questions
    cy.get('input[type="radio"]').first().check();
    cy.contains('button', 'Next').click();
    cy.get('input[type="radio"]').first().check();
    
    // Save and exit
    cy.contains('button', 'Save & Exit').click();
    cy.contains('Save Progress?').should('be.visible');
    cy.contains('button', 'Save & Exit').click();

    // Should redirect to evaluations page
    cy.url().should('include', '/evaluations');
    
    // Check in-progress indicator
    cy.get('[data-testid="evaluation-card"]').first().within(() => {
      cy.contains('In Progress').should('be.visible');
      cy.contains('2/30 answered').should('be.visible');
      cy.contains('button', 'Resume').should('be.visible');
    });

    // Resume evaluation
    cy.contains('button', 'Resume').click();
    cy.url().should('include', '/attempt');
    cy.contains('Question 3 of 30').should('be.visible'); // Should continue from where left off
  });

  it('handles different question types', () => {
    // Navigate to evaluation with mixed question types
    cy.contains('Advanced JavaScript Evaluation').click();
    cy.contains('button', 'Start Evaluation').click();
    cy.contains('button', 'Start Now').click();

    // Multiple choice question
    cy.contains('Question Type: Multiple Choice').should('be.visible');
    cy.get('input[type="radio"]').should('have.length.greaterThan', 0);
    cy.get('input[type="radio"]').first().check();
    cy.contains('button', 'Next').click();

    // Multiple select question
    cy.contains('Question Type: Multiple Select').should('be.visible');
    cy.contains('Select all that apply').should('be.visible');
    cy.get('input[type="checkbox"]').should('have.length.greaterThan', 0);
    cy.get('input[type="checkbox"]').first().check();
    cy.get('input[type="checkbox"]').eq(1).check();
    cy.contains('button', 'Next').click();

    // True/False question
    cy.contains('Question Type: True/False').should('be.visible');
    cy.get('input[type="radio"][value="true"]').check();
    cy.contains('button', 'Next').click();

    // Short answer question
    cy.contains('Question Type: Short Answer').should('be.visible');
    cy.get('textarea').type('This is my short answer response');
    cy.contains('button', 'Next').click();

    // Code question
    cy.contains('Question Type: Code').should('be.visible');
    cy.get('[data-testid="code-editor"]').should('be.visible');
    cy.get('[data-testid="code-editor"] textarea').type('function hello() {\n  return "Hello World";\n}');
  });

  it('displays evaluation statistics and analytics', () => {
    // Navigate to completed evaluation
    cy.contains('Completed Evaluations').parent().within(() => {
      cy.get('[data-testid="evaluation-card"]').first().click();
    });

    // View statistics
    cy.contains('button', 'View Statistics').click();
    
    // Check analytics dashboard
    cy.contains('Evaluation Analytics').should('be.visible');
    cy.contains('Score Distribution').should('be.visible');
    cy.contains('Time Spent').should('be.visible');
    cy.contains('Question Performance').should('be.visible');
    
    // Check charts
    cy.get('[data-testid="score-chart"]').should('be.visible');
    cy.get('[data-testid="time-chart"]').should('be.visible');
    
    // Check question-level analytics
    cy.contains('Question Analysis').should('be.visible');
    cy.get('[data-testid="question-analysis-table"]').should('be.visible');
    cy.get('[data-testid="question-analysis-table"] tr').should('have.length.greaterThan', 1);
  });

  it('handles evaluation prerequisites', () => {
    // Try to access advanced evaluation
    cy.contains('Advanced React Patterns').click();
    
    // Should show prerequisites
    cy.contains('Prerequisites Required').should('be.visible');
    cy.contains('You must complete the following evaluations first:').should('be.visible');
    cy.contains('React Fundamentals Assessment').should('be.visible');
    cy.contains('button', 'Start Evaluation').should('be.disabled');
    
    // Navigate to prerequisite
    cy.contains('a', 'React Fundamentals Assessment').click();
    cy.url().should('include', '/evaluations/');
  });

  it('shows evaluation certificates', () => {
    // Navigate to passed evaluation
    cy.contains('Completed Evaluations').parent().within(() => {
      cy.contains('Passed').first().parent().parent().click();
    });

    // View certificate
    cy.contains('Certificate').should('be.visible');
    cy.contains('button', 'View Certificate').click();
    
    // Certificate modal
    cy.contains('Certificate of Completion').should('be.visible');
    cy.contains('This certifies that').should('be.visible');
    cy.contains('Student User').should('be.visible'); // Student name
    cy.contains('has successfully completed').should('be.visible');
    
    // Download certificate
    cy.contains('button', 'Download PDF').click();
    // Note: Actual file download verification is complex in Cypress
    
    // Share certificate
    cy.contains('button', 'Share').click();
    cy.contains('Share Certificate').should('be.visible');
    cy.get('[data-testid="share-link"]').should('be.visible');
    cy.contains('button', 'Copy Link').click();
    cy.contains('Link copied!').should('be.visible');
  });
});

describe('Evaluation Management - Instructor View', () => {
  beforeEach(() => {
    // Login as instructor
    cy.visit('/login');
    cy.get('input[name="email"]').type('instructor@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
  });

  it('creates and manages evaluations', () => {
    cy.get('nav').contains('Evaluations').click();
    
    // Instructor view shows management options
    cy.contains('button', 'Create Evaluation').should('be.visible');
    cy.contains('Manage Evaluations').should('be.visible');
    
    // Create new evaluation
    cy.contains('button', 'Create Evaluation').click();
    cy.url().should('include', '/evaluations/new');
    
    // Fill evaluation details
    cy.get('input[name="title"]').type('Node.js Basics Assessment');
    cy.get('textarea[name="description"]').type('Test your knowledge of Node.js fundamentals');
    cy.get('select[name="evaluation_type"]').select('quiz');
    cy.get('input[name="duration_minutes"]').type('60');
    cy.get('input[name="passing_score"]').type('75');
    
    // Add questions
    cy.contains('button', 'Add Question').click();
    cy.get('textarea[name="question_text"]').type('What is Node.js?');
    cy.get('input[name="option_1"]').type('A JavaScript runtime');
    cy.get('input[name="option_2"]').type('A database');
    cy.get('input[name="correct_answer"]').check('option_1');
    
    // Save evaluation
    cy.contains('button', 'Create Evaluation').click();
    cy.contains('Evaluation created successfully').should('be.visible');
    
    // View student attempts
    cy.contains('button', 'View Attempts').click();
    cy.contains('Student Attempts').should('be.visible');
    cy.get('[data-testid="attempts-table"]').should('be.visible');
  });
});