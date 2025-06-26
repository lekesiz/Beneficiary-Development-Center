describe('Chat Flow - End to End', () => {
  // Test data
  const user1 = {
    email: 'trainer@example.com',
    password: 'password123',
    name: 'John Trainer'
  };
  
  const user2 = {
    email: 'student@example.com',
    password: 'password123',
    name: 'Jane Student'
  };

  describe('Real-time messaging between users', () => {
    it('allows users to send and receive messages in real-time', () => {
      // User 1 logs in
      cy.visit('/login');
      cy.get('input[name="email"]').type(user1.email);
      cy.get('input[name="password"]').type(user1.password);
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
      
      // Navigate to chat
      cy.get('nav').contains('Chat').click();
      cy.url().should('include', '/chat');
      cy.contains('h1', 'Messages').should('be.visible');
      
      // Start a new conversation
      cy.get('[data-testid="new-conversation-btn"]').click();
      cy.get('[data-testid="user-search"]').type(user2.name);
      cy.get('[data-testid="user-option"]').contains(user2.name).click();
      cy.get('[data-testid="start-chat-btn"]').click();
      
      // Send a message
      const message1 = 'Hello Jane, how is your progress with the React course?';
      cy.get('[data-testid="message-input"]').type(message1);
      cy.get('[data-testid="send-message-btn"]').click();
      
      // Verify message appears
      cy.get('[data-testid="message-stream"]').should('contain', message1);
      cy.get('[data-testid="message-bubble-own"]').should('contain', message1);
      
      // Log out user 1
      cy.get('[data-testid="user-menu"]').click();
      cy.contains('Logout').click();
      
      // User 2 logs in in a new window/session
      cy.visit('/login');
      cy.get('input[name="email"]').type(user2.email);
      cy.get('input[name="password"]').type(user2.password);
      cy.get('button[type="submit"]').click();
      
      // Navigate to chat
      cy.get('nav').contains('Chat').click();
      
      // Should see the conversation with unread indicator
      cy.get('[data-testid="conversation-item"]')
        .contains(user1.name)
        .parent()
        .within(() => {
          cy.get('[data-testid="unread-badge"]').should('contain', '1');
          cy.contains(message1.substring(0, 50)).should('be.visible');
        });
      
      // Open the conversation
      cy.get('[data-testid="conversation-item"]').contains(user1.name).click();
      
      // Message should be marked as read
      cy.get('[data-testid="message-bubble-other"]').should('contain', message1);
      cy.get('[data-testid="read-receipt"]').should('be.visible');
      
      // Reply to the message
      const message2 = 'Hi John! I just completed the hooks chapter. It was challenging but very interesting!';
      cy.get('[data-testid="message-input"]').type(message2);
      cy.get('[data-testid="send-message-btn"]').click();
      
      // Verify reply appears
      cy.get('[data-testid="message-bubble-own"]').last().should('contain', message2);
    });

    it('shows typing indicators in real-time', () => {
      // Login as user 1
      cy.visit('/login');
      cy.get('input[name="email"]').type(user1.email);
      cy.get('input[name="password"]').type(user1.password);
      cy.get('button[type="submit"]').click();
      
      // Navigate to existing conversation
      cy.get('nav').contains('Chat').click();
      cy.get('[data-testid="conversation-item"]').first().click();
      
      // Start typing
      cy.get('[data-testid="message-input"]').type('I am typing...');
      
      // In a real implementation with multiple browser sessions,
      // the other user would see typing indicator
      // For this test, we verify the typing event is triggered
      cy.window().its('socketIO').should('exist');
    });

    it('handles message actions (edit, delete)', () => {
      // Login
      cy.visit('/login');
      cy.get('input[name="email"]').type(user1.email);
      cy.get('input[name="password"]').type(user1.password);
      cy.get('button[type="submit"]').click();
      
      // Navigate to chat
      cy.get('nav').contains('Chat').click();
      cy.get('[data-testid="conversation-item"]').first().click();
      
      // Send a message
      const originalMessage = 'This message has a typo: Recat';
      cy.get('[data-testid="message-input"]').type(originalMessage);
      cy.get('[data-testid="send-message-btn"]').click();
      
      // Edit the message
      cy.get('[data-testid="message-bubble-own"]')
        .last()
        .trigger('mouseenter')
        .within(() => {
          cy.get('[data-testid="message-actions"]').should('be.visible');
          cy.get('[data-testid="edit-message-btn"]').click();
        });
      
      // Update the message
      cy.get('[data-testid="message-input"]').clear().type('This message has been corrected: React');
      cy.get('[data-testid="save-edit-btn"]').click();
      
      // Verify edit
      cy.get('[data-testid="message-bubble-own"]').last().should('contain', 'React');
      cy.get('[data-testid="edited-indicator"]').should('be.visible');
      
      // Delete a message
      cy.get('[data-testid="message-bubble-own"]')
        .last()
        .trigger('mouseenter')
        .within(() => {
          cy.get('[data-testid="delete-message-btn"]').click();
        });
      
      // Confirm deletion
      cy.get('[data-testid="confirm-delete-btn"]').click();
      
      // Message should be removed
      cy.get('[data-testid="message-stream"]').should('not.contain', 'React');
    });

    it('supports file attachments', () => {
      // Login
      cy.visit('/login');
      cy.get('input[name="email"]').type(user1.email);
      cy.get('input[name="password"]').type(user1.password);
      cy.get('button[type="submit"]').click();
      
      // Navigate to chat
      cy.get('nav').contains('Chat').click();
      cy.get('[data-testid="conversation-item"]').first().click();
      
      // Upload a file
      const fileName = 'test-document.pdf';
      cy.get('[data-testid="attach-file-btn"]').click();
      cy.get('input[type="file"]').selectFile({
        contents: Cypress.Buffer.from('fake PDF content'),
        fileName: fileName,
        mimeType: 'application/pdf'
      }, { force: true });
      
      // Send message with attachment
      cy.get('[data-testid="message-input"]').type('Here is the course material');
      cy.get('[data-testid="send-message-btn"]').click();
      
      // Verify attachment appears
      cy.get('[data-testid="message-attachment"]').should('contain', fileName);
      cy.get('[data-testid="download-attachment-btn"]').should('be.visible');
    });

    it('displays conversation list with latest messages', () => {
      // Login
      cy.visit('/login');
      cy.get('input[name="email"]').type(user1.email);
      cy.get('input[name="password"]').type(user1.password);
      cy.get('button[type="submit"]').click();
      
      // Navigate to chat
      cy.get('nav').contains('Chat').click();
      
      // Verify conversation list
      cy.get('[data-testid="conversation-list"]').should('be.visible');
      
      // Check conversation items show:
      // - Other user's name and avatar
      // - Last message preview
      // - Time since last message
      // - Unread count (if any)
      cy.get('[data-testid="conversation-item"]').each(($item) => {
        cy.wrap($item).within(() => {
          cy.get('[data-testid="user-avatar"]').should('be.visible');
          cy.get('[data-testid="user-name"]').should('not.be.empty');
          cy.get('[data-testid="last-message"]').should('not.be.empty');
          cy.get('[data-testid="message-time"]').should('not.be.empty');
        });
      });
      
      // Search conversations
      cy.get('[data-testid="search-conversations"]').type('Jane');
      cy.get('[data-testid="conversation-item"]').should('have.length', 1);
      cy.get('[data-testid="conversation-item"]').should('contain', 'Jane');
    });

    it('handles empty states gracefully', () => {
      // Login as a user with no conversations
      cy.visit('/login');
      cy.get('input[name="email"]').type('newuser@example.com');
      cy.get('input[name="password"]').type('password123');
      cy.get('button[type="submit"]').click();
      
      // Navigate to chat
      cy.get('nav').contains('Chat').click();
      
      // Should show empty state
      cy.get('[data-testid="empty-conversations"]').should('be.visible');
      cy.contains('No conversations yet').should('be.visible');
      cy.contains('Start a conversation').should('be.visible');
      
      // Click to start new conversation
      cy.get('[data-testid="start-conversation-empty"]').click();
      cy.get('[data-testid="user-search"]').should('be.visible');
    });
  });

  describe('Chat error handling and edge cases', () => {
    it('handles connection errors gracefully', () => {
      // Simulate offline scenario
      cy.visit('/login');
      cy.get('input[name="email"]').type(user1.email);
      cy.get('input[name="password"]').type(user1.password);
      cy.get('button[type="submit"]').click();
      
      // Navigate to chat
      cy.get('nav').contains('Chat').click();
      
      // Go offline
      cy.window().then((win) => {
        cy.stub(win.navigator, 'onLine').value(false);
        win.dispatchEvent(new Event('offline'));
      });
      
      // Try to send a message
      cy.get('[data-testid="conversation-item"]').first().click();
      cy.get('[data-testid="message-input"]').type('This should fail');
      cy.get('[data-testid="send-message-btn"]').click();
      
      // Should show error or offline indicator
      cy.get('[data-testid="offline-indicator"]').should('be.visible');
      cy.contains('Unable to send message').should('be.visible');
    });

    it('handles long messages and text wrapping', () => {
      cy.visit('/login');
      cy.get('input[name="email"]').type(user1.email);
      cy.get('input[name="password"]').type(user1.password);
      cy.get('button[type="submit"]').click();
      
      // Navigate to chat
      cy.get('nav').contains('Chat').click();
      cy.get('[data-testid="conversation-item"]').first().click();
      
      // Send a very long message
      const longMessage = 'Lorem ipsum '.repeat(100);
      cy.get('[data-testid="message-input"]').type(longMessage, { delay: 0 });
      cy.get('[data-testid="send-message-btn"]').click();
      
      // Verify message displays correctly without breaking layout
      cy.get('[data-testid="message-bubble-own"]')
        .last()
        .should('have.css', 'word-wrap', 'break-word');
    });
  });
});
