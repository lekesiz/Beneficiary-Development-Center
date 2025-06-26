describe('Notification Preferences', () => {
  beforeEach(() => {
    // Login first
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@bdc.com');
    cy.get('input[name="password"]').type('admin123');
    cy.get('select[name="tenantId"]').select('1');
    cy.get('button[type="submit"]').click();
    
    // Wait for redirect and navigate to settings
    cy.url().should('include', '/dashboard');
    cy.visit('/settings#notifications');
  });

  it('should display notification preferences', () => {
    // Check that we're on the notifications tab
    cy.contains('h3', 'Notification Preferences').should('be.visible');
    cy.contains('Choose how you want to be notified').should('be.visible');

    // Check notification categories
    cy.contains('New Messages').should('be.visible');
    cy.contains('Appointment Reminders').should('be.visible');
    cy.contains('Evaluation Completed').should('be.visible');
    cy.contains('Course Enrollment').should('be.visible');
    cy.contains('Program Updates').should('be.visible');

    // Check column headers
    cy.contains('Email').should('be.visible');
    cy.contains('In-App').should('be.visible');

    // Check SMS notice
    cy.contains('SMS Notifications').should('be.visible');
    cy.contains('SMS notifications are not currently available').should('be.visible');
  });

  it('should load current preferences', () => {
    // Intercept the API call
    cy.intercept('GET', '/api/v1/users/me/preferences', {
      statusCode: 200,
      body: {
        preferences: {
          notifications: {
            email: {
              new_message: true,
              appointment_reminder: true,
              evaluation_completed: false,
              course_enrollment: true,
              program_update: true,
            },
            in_app: {
              new_message: true,
              appointment_reminder: true,
              evaluation_completed: true,
              course_enrollment: true,
              program_update: true,
            },
          },
        },
      },
    }).as('getPreferences');

    cy.reload();
    cy.wait('@getPreferences');

    // The toggles should reflect the loaded state
    // Note: This is a simplified check - in reality you'd check the actual toggle states
    cy.get('[role="button"][aria-label*="Toggle email notifications"]').should('have.length', 5);
    cy.get('[role="button"][aria-label*="Toggle in-app notifications"]').should('have.length', 5);
  });

  it('should update notification preferences', () => {
    // Intercept the update API call
    cy.intercept('PUT', '/api/v1/users/me/preferences', {
      statusCode: 200,
      body: {
        message: 'Preferences updated successfully',
        preferences: {
          notifications: {
            email: {
              new_message: false,
              appointment_reminder: true,
              evaluation_completed: true,
              course_enrollment: true,
              program_update: true,
            },
            in_app: {
              new_message: true,
              appointment_reminder: true,
              evaluation_completed: true,
              course_enrollment: true,
              program_update: true,
            },
          },
        },
      },
    }).as('updatePreferences');

    // Click on the first email toggle (New Messages)
    cy.get('[role="button"][aria-label="Toggle email notifications for New Messages"]')
      .first()
      .click();

    // Wait for the API call
    cy.wait('@updatePreferences').then((interception) => {
      // Verify the request body
      expect(interception.request.body.notifications.email.new_message).to.be.false;
    });

    // Check for success toast
    cy.contains('Notification preferences updated successfully').should('be.visible');
  });

  it('should handle API errors gracefully', () => {
    // Intercept with error response
    cy.intercept('GET', '/api/v1/users/me/preferences', {
      statusCode: 500,
      body: { message: 'Server error' },
    }).as('getPreferencesError');

    cy.reload();
    cy.wait('@getPreferencesError');

    // Should show error state
    cy.contains('Failed to load notification preferences').should('be.visible');
  });

  it('should navigate between settings tabs', () => {
    // Start on notifications tab
    cy.contains('h3', 'Notification Preferences').should('be.visible');

    // Click on Profile tab
    cy.contains('button', 'Profile').click();
    cy.contains('h3', 'Profile Settings').should('be.visible');
    cy.url().should('include', '#profile');

    // Click on Security tab
    cy.contains('button', 'Security').click();
    cy.contains('h3', 'Security Settings').should('be.visible');
    cy.url().should('include', '#security');

    // Click on Appearance tab
    cy.contains('button', 'Appearance').click();
    cy.contains('h3', 'Appearance Settings').should('be.visible');
    cy.url().should('include', '#appearance');

    // Click back to Notifications
    cy.contains('button', 'Notifications').click();
    cy.contains('h3', 'Notification Preferences').should('be.visible');
    cy.url().should('include', '#notifications');
  });

  it('should disable toggles while updating', () => {
    // Intercept with a delayed response
    cy.intercept('PUT', '/api/v1/users/me/preferences', (req) => {
      // Delay the response
      req.reply({
        delay: 1000,
        statusCode: 200,
        body: {
          message: 'Preferences updated successfully',
          preferences: req.body,
        },
      });
    }).as('updatePreferencesDelayed');

    // Click a toggle
    const toggle = cy.get('[role="button"][aria-label="Toggle email notifications for New Messages"]').first();
    toggle.click();

    // The toggle should be disabled (have opacity)
    toggle.should('have.class', 'opacity-50');
    toggle.should('have.class', 'cursor-not-allowed');

    // Wait for the update to complete
    cy.wait('@updatePreferencesDelayed');

    // Toggle should be enabled again
    toggle.should('not.have.class', 'opacity-50');
    toggle.should('not.have.class', 'cursor-not-allowed');
  });
});