import * as React from 'react';

import ErrorPage from './ErrorPage';

export default function ServerError() {
  return (
    <ErrorPage 
      statusCode={500}
      title="Internal Server Error"
      description="We're experiencing technical difficulties. Our team has been notified and is working to resolve the issue."
    />
  );
}