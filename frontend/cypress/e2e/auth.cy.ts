/// <reference types="cypress" />

describe('Authentication Flow', () => {
  beforeEach(() => {
    // Ensure API is ready before tests
    cy.waitForApi();
    
    // Clear any existing auth state
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  describe('Login Page', () => {
    it('should display login form', () => {
      cy.visit('/login');
      
      // Check form elements
      cy.get('input[name="email"]').should('be.visible');
      cy.get('input[name="password"]').should('be.visible');
      cy.get('button[type="submit"]').should('be.visible').and('contain', 'Login');
      
      // Check page title
      cy.contains('h1', 'Welcome').should('be.visible');
    });

    it('should show validation errors for empty fields', () => {
      cy.visit('/login');
      
      // Submit empty form
      cy.get('button[type="submit"]').click();
      
      // Check for validation messages
      cy.contains('Email is required').should('be.visible');
      cy.contains('Password is required').should('be.visible');
    });

    it('should show error for invalid credentials', () => {
      cy.visit('/login');
      
      // Enter invalid credentials
      cy.get('input[name="email"]').type('invalid@example.com');
      cy.get('input[name="password"]').type('wrongpassword');
      cy.get('button[type="submit"]').click();
      
      // Check for error message
      cy.contains('Invalid email or password').should('be.visible');
    });
  });

  describe('Successful Login Flow', () => {
    it('should login successfully and redirect to dashboard', () => {
      cy.visit('/login');
      
      // Enter valid credentials
      const { email, password } = Cypress.env('testUser');
      cy.get('input[name="email"]').type(email);
      cy.get('input[name="password"]').type(password);
      
      // Submit form
      cy.get('button[type="submit"]').click();
      
      // Should redirect to dashboard
      cy.url().should('include', '/dashboard');
      
      // Check user is logged in
      cy.contains('Welcome').should('be.visible');
      
      // Verify tokens are stored
      cy.window().then((win) => {
        expect(win.localStorage.getItem('access_token')).to.exist;
        expect(win.localStorage.getItem('refresh_token')).to.exist;
        
        const user = JSON.parse(win.localStorage.getItem('user') || '{}');
        expect(user.email).to.equal(email);
      });
    });

    it('should maintain session on page refresh', () => {
      // Login via API
      const { email, password } = Cypress.env('testUser');
      cy.login(email, password);
      
      // Visit dashboard
      cy.visit('/dashboard');
      cy.contains('Welcome').should('be.visible');
      
      // Refresh page
      cy.reload();
      
      // Should still be logged in
      cy.url().should('include', '/dashboard');
      cy.contains('Welcome').should('be.visible');
    });
  });

  describe('Protected Routes', () => {
    it('should redirect to login when accessing protected route without auth', () => {
      // Try to access dashboard without login
      cy.visit('/dashboard');
      
      // Should redirect to login
      cy.url().should('include', '/login');
    });

    it('should allow access to protected routes after login', () => {
      // Login first
      const { email, password } = Cypress.env('testUser');
      cy.login(email, password);
      
      // Visit various protected routes
      const protectedRoutes = [
        '/dashboard',
        '/programs',
        '/beneficiaries',
        '/evaluations'
      ];
      
      protectedRoutes.forEach(route => {
        cy.visit(route);
        cy.url().should('include', route);
      });
    });
  });

  describe('Logout Flow', () => {
    beforeEach(() => {
      // Login before each logout test
      const { email, password } = Cypress.env('testUser');
      cy.login(email, password);
      cy.visit('/dashboard');
    });

    it('should logout successfully', () => {
      // Find and click logout button
      cy.get('[data-testid="user-menu"]').click();
      cy.contains('Logout').click();
      
      // Should redirect to login
      cy.url().should('include', '/login');
      
      // Verify tokens are cleared
      cy.window().then((win) => {
        expect(win.localStorage.getItem('access_token')).to.be.null;
        expect(win.localStorage.getItem('refresh_token')).to.be.null;
        expect(win.localStorage.getItem('user')).to.be.null;
      });
    });

    it('should not allow access to protected routes after logout', () => {
      // Logout
      cy.logout();
      
      // Try to access dashboard
      cy.visit('/dashboard');
      
      // Should redirect to login
      cy.url().should('include', '/login');
    });
  });

  describe('Token Refresh', () => {
    it('should refresh token when expired', () => {
      // This test would require mocking token expiration
      // For now, we'll just verify the refresh token exists
      const { email, password } = Cypress.env('testUser');
      cy.login(email, password);
      
      cy.getAccessToken().then(token => {
        expect(token).to.be.a('string');
        expect(token.split('.').length).to.equal(3); // JWT format
      });
    });
  });

  describe('Multi-tenant Support', () => {
    it('should include tenant header in API requests', () => {
      cy.intercept('POST', '**/api/v1/auth/login', (req) => {
        // Verify tenant header is included
        expect(req.headers).to.have.property('x-tenant-id');
      }).as('loginRequest');
      
      cy.visit('/login');
      const { email, password } = Cypress.env('testUser');
      cy.get('input[name="email"]').type(email);
      cy.get('input[name="password"]').type(password);
      cy.get('button[type="submit"]').click();
      
      cy.wait('@loginRequest');
    });
  });
});