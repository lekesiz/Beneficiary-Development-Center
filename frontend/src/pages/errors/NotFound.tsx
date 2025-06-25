import * as React from 'react';

import ErrorPage from './ErrorPage';

export default function NotFound() {
  return <ErrorPage statusCode={404} />;
}