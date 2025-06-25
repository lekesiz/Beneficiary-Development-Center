/// <reference types="cypress" />

// Custom commands for BDC E2E tests

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to login via API
       * @example cy.login('admin@bdc.local', 'admin123')
       */
      login(email: string, password: string): Chainable<void>;
      
      /**
       * Custom command to logout
       * @example cy.logout()
       */
      logout(): Chainable<void>;
      
      /**
       * Custom command to get access token from localStorage
       * @example cy.getAccessToken()
       */
      getAccessToken(): Chainable<string>;
      
      /**
       * Custom command to wait for API response
       * @example cy.waitForApi()
       */
      waitForApi(): Chainable<void>;
    }
  }
}

// Login command
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.request('POST', `${Cypress.env('apiUrl')}/api/v1/auth/login`, {
    email,
    password
  }).then((response) => {
    expect(response.status).to.eq(200);
    expect(response.body).to.have.property('access_token');
    expect(response.body).to.have.property('refresh_token');
    
    // Store tokens
    window.localStorage.setItem('access_token', response.body.access_token);
    window.localStorage.setItem('refresh_token', response.body.refresh_token);
    window.localStorage.setItem('user', JSON.stringify(response.body.user));
  });
});

// Logout command
Cypress.Commands.add('logout', () => {
  window.localStorage.removeItem('access_token');
  window.localStorage.removeItem('refresh_token');
  window.localStorage.removeItem('user');
  cy.visit('/login');
});

// Get access token
Cypress.Commands.add('getAccessToken', () => {
  return cy.window().then((win) => {
    const token = win.localStorage.getItem('access_token');
    expect(token).to.exist;
    return token;
  });
});

// Wait for API to be ready
Cypress.Commands.add('waitForApi', () => {
  cy.request({
    url: `${Cypress.env('apiUrl')}/health`,
    retryOnStatusCodeFailure: true,
    retryOnNetworkFailure: true,
    timeout: 30000
  }).its('status').should('eq', 200);
});

// Prevent TypeScript errors
export {};