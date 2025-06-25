// ***********************************************************
// This file is processed and loaded automatically before test files.
// You can change the location of this file or turn off processing
// support files from the 'supportFile' configuration option.
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands')

// cypress-real-events support
import 'cypress-real-events';

// Hide fetch/XHR requests from command log to reduce noise
const app = window.top;
if (!app?.document.head.querySelector('[data-hide-command-log-request]')) {
  const style = app.document.createElement('style');
  style.innerHTML = `.command-name-request, .command-name-xhr { display: none }`;
  style.setAttribute('data-hide-command-log-request', '');
  app.document.head.appendChild(style);
}