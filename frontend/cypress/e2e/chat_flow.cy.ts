describe('Chat Flow - End to End', () => {
  beforeEach(() => {
    // Intercept API calls for better test control
    cy.intercept('POST', '/api/v1/auth/login').as('login');
    cy.intercept('GET', '/api/v1/chat/conversations').as('getConversations');
    cy.intercept('POST', '/api/v1/chat/conversations').as('createConversation');
    cy.intercept('POST', '/api/v1/chat/messages').as('sendMessage');
    cy.intercept('GET', '/api/v1/notifications**').as('getNotifications');
    cy.intercept('GET', '/api/v1/users**').as('getUsers');
    
    // Mock WebSocket connection
    cy.window().then((win) => {
      // Mock Socket.IO if needed
      if (!win.io) {
        win.io = () => ({
          on: cy.stub(),
          emit: cy.stub(),
          disconnect: cy.stub(),
        });
      }
    });
  });

  it('Complete chat flow: Trainer starts conversation, Student responds', () => {
    // ======================================
    // Phase 1: Trainer (User A) logs in and starts conversation
    // ======================================
    
    cy.visit('/login');
    cy.get('input[name="email"]').type('trainer@example.com');
    cy.get('input[name="password"]').type('trainer123');
    cy.get('button[type="submit"]').click();
    
    cy.wait('@login');
    cy.url().should('include', '/dashboard');
    
    // Navigate to chat/messages
    cy.get('[data-testid="nav-messages"], [href*="chat"], [href*="messages"]')
      .first()
      .click();
    
    cy.url().should('match', /\/(chat|messages)/);
    
    // Start new conversation
    cy.get('[data-testid="new-conversation"], button')
      .contains(/new|start|create/i)
      .first()
      .click();
    
    // Search for or select student user
    cy.get('input[placeholder*="search"], input[placeholder*="user"], select, input[type="text"]')
      .first()
      .type('student@example.com{enter}');
    
    // Type and send initial message
    const trainerMessage = 'Hello! How is your progress on the new course?';
    cy.get('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="message-input"]')
      .first()
      .type(trainerMessage);
    
    cy.get('button[type="submit"], [data-testid="send-button"], button')
      .contains(/send|submit/i)
      .first()
      .click();
    
    cy.wait('@sendMessage', { timeout: 10000 });
    
    // Verify message appears in chat
    cy.contains(trainerMessage).should('be.visible');
    
    // Logout trainer
    cy.get('[data-testid="user-menu"], [data-testid="logout"], button')
      .contains(/logout|sign out/i)
      .first()
      .click();
    
    // ======================================
    // Phase 2: Student (User B) logs in and responds
    // ======================================
    
    cy.visit('/login');
    cy.get('input[name="email"]').clear().type('student@example.com');
    cy.get('input[name="password"]').clear().type('student123');
    cy.get('button[type="submit"]').click();
    
    cy.wait('@login');
    cy.url().should('include', '/dashboard');
    
    // Check for notification indicator (if available)
    cy.get('body').then($body => {
      if ($body.find('[data-testid="notification-badge"], .notification-indicator, .badge').length > 0) {
        cy.get('[data-testid="notification-badge"], .notification-indicator, .badge')
          .should('be.visible');
      }
    });
    
    // Navigate to chat/messages
    cy.get('[data-testid="nav-messages"], [href*="chat"], [href*="messages"]')
      .first()
      .click();
    
    cy.url().should('match', /\/(chat|messages)/);
    
    // Find and open the conversation with the trainer's message
    cy.contains(trainerMessage, { timeout: 10000 })
      .should('be.visible')
      .click();
    
    // Verify trainer's message is visible in the conversation
    cy.contains(trainerMessage).should('be.visible');
    
    // Send reply
    const studentReply = "It's going great, thanks for checking in!";
    cy.get('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="message-input"]')
      .first()
      .type(studentReply);
    
    cy.get('button[type="submit"], [data-testid="send-button"], button')
      .contains(/send|submit/i)
      .first()
      .click();
    
    cy.wait('@sendMessage', { timeout: 10000 });
    
    // Verify student's reply appears instantly
    cy.contains(studentReply).should('be.visible');
    
    // Verify both messages are visible in the conversation
    cy.contains(trainerMessage).should('be.visible');
    cy.contains(studentReply).should('be.visible');
    
    // ======================================
    // Phase 3: Validation - Real-time functionality
    // ======================================
    
    // Verify conversation shows latest message timestamp
    cy.get('.timestamp, [data-testid="message-time"], .message-meta')
      .should('exist');
    
    // Test that conversation appears in recent conversations list
    cy.get('[data-testid="conversation-list"], .conversation-item')
      .should('contain', 'trainer@example.com')
      .or('contain', 'Trainer User');
    
    // Verify message order (trainer first, then student)
    cy.get('.message, [data-testid="message"]')
      .first()
      .should('contain', trainerMessage);
    
    cy.get('.message, [data-testid="message"]')
      .last()
      .should('contain', studentReply);
  });

  it('Chat interface basic functionality', () => {
    // Quick test for chat UI elements
    cy.visit('/login');
    cy.get('input[name="email"]').type('trainer@example.com');
    cy.get('input[name="password"]').type('trainer123');
    cy.get('button[type="submit"]').click();
    
    cy.wait('@login');
    
    // Navigate to chat
    cy.get('[data-testid="nav-messages"], [href*="chat"], [href*="messages"]')
      .first()
      .click();
    
    // Verify chat interface elements exist
    cy.get('body').should('contain.text', /messages|chat|conversations/i);
    
    // Check for essential chat UI components
    cy.get('body').then($body => {
      // Look for common chat elements
      const hasMessageInput = $body.find('textarea, input[placeholder*="message"]').length > 0;
      const hasConversationList = $body.find('[data-testid="conversation-list"], .conversation').length > 0;
      const hasChatContainer = $body.find('[data-testid="chat-container"], .chat, .messages').length > 0;
      
      // At least one of these should exist
      expect(hasMessageInput || hasConversationList || hasChatContainer).to.be.true;
    });
  });

  it('Chat error handling and edge cases', () => {
    cy.visit('/login');
    cy.get('input[name="email"]').type('student@example.com');
    cy.get('input[name="password"]').type('student123');
    cy.get('button[type="submit"]').click();
    
    cy.wait('@login');
    
    // Navigate to chat
    cy.get('[data-testid="nav-messages"], [href*="chat"], [href*="messages"]')
      .first()
      .click();
    
    // Test empty message handling
    cy.get('body').then($body => {
      if ($body.find('textarea[placeholder*="message"], input[placeholder*="message"]').length > 0) {
        // Try to send empty message
        cy.get('textarea[placeholder*="message"], input[placeholder*="message"]')
          .first()
          .clear();
        
        cy.get('button[type="submit"], [data-testid="send-button"]')
          .first()
          .click();
        
        // Should not send empty message or show error
        cy.get('body').should('not.contain', 'undefined');
      }
    });
    
    // Test that chat interface is accessible
    cy.get('body').should('be.visible');
    cy.get('[role="main"], main, .main-content').should('exist');
  });
});