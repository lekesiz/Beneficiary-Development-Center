import ErrorPage from './ErrorPage';

export default function Unauthorized() {
  return (
    <ErrorPage
      statusCode={403}
      title="Access Denied"
      description="You don't have permission to access this page. Please check with your administrator if you believe you should have access."
    />
  );
}
