import { Home, ArrowLeft, Mail, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/Button';

interface ErrorPageProps {
  statusCode: 404 | 403 | 500;
  title?: string;
  description?: string;
  showBackButton?: boolean;
  showHomeButton?: boolean;
  showRefreshButton?: boolean;
  showContactButton?: boolean;
}

const errorConfigs = {
  404: {
    title: 'Page Not Found',
    description: "We can't find the page you're looking for. It might have been moved, deleted, or you entered the wrong URL.",
    illustration: '🔍',
    primaryAction: 'Go Home',
    showBackButton: true,
    showHomeButton: true,
    showRefreshButton: false,
    showContactButton: false,
  },
  403: {
    title: 'Access Denied',
    description: "You don't have permission to access this resource. Contact your administrator if you believe this is an error.",
    illustration: '🔒',
    primaryAction: 'Go Back',
    showBackButton: true,
    showHomeButton: true,
    showRefreshButton: false,
    showContactButton: true,
  },
  500: {
    title: 'Server Error',
    description: 'Something went wrong on our end. Please try again later or contact support if the problem persists.',
    illustration: '⚠️',
    primaryAction: 'Try Again',
    showBackButton: true,
    showHomeButton: true,
    showRefreshButton: true,
    showContactButton: true,
  },
};

export default function ErrorPage({
  statusCode,
  title,
  description,
  showBackButton,
  showHomeButton,
  showRefreshButton,
  showContactButton,
}: ErrorPageProps) {
  const navigate = useNavigate();
  const config = errorConfigs[statusCode];

  const handleGoBack = () => {
    navigate(-1);
  };

  const handleGoHome = () => {
    navigate('/dashboard');
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  const handleContact = () => {
    const subject = encodeURIComponent(`Help needed - Error ${statusCode}`);
    const body = encodeURIComponent(
      `I encountered an error while using the BDC application:\n\nError: ${statusCode} - ${title || config.title}\nURL: ${window.location.href}\nTimestamp: ${new Date().toISOString()}\n\nPlease describe what you were trying to do:\n\n`
    );
    window.open(`mailto:support@bdc.com?subject=${subject}&body=${body}`);
  };

  const displayTitle = title || config.title;
  const displayDescription = description || config.description;
  const shouldShowBackButton = showBackButton ?? config.showBackButton;
  const shouldShowHomeButton = showHomeButton ?? config.showHomeButton;
  const shouldShowRefreshButton = showRefreshButton ?? config.showRefreshButton;
  const shouldShowContactButton = showContactButton ?? config.showContactButton;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* Error Illustration */}
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">{config.illustration}</div>
            <div className="text-3xl font-bold text-gray-900 mb-2">{statusCode}</div>
            <h1 className="text-xl font-semibold text-gray-900 mb-3">
              {displayTitle}
            </h1>
            <p className="text-gray-600 text-sm leading-relaxed">
              {displayDescription}
            </p>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            {/* Primary Actions */}
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {shouldShowBackButton && (
                <Button
                  onClick={handleGoBack}
                  variant="outline"
                  className="w-full"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Go Back
                </Button>
              )}
              
              {shouldShowHomeButton && (
                <Button
                  onClick={handleGoHome}
                  variant="primary"
                  className="w-full"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Go Home
                </Button>
              )}
            </div>

            {/* Secondary Actions */}
            {(shouldShowRefreshButton || shouldShowContactButton) && (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {shouldShowRefreshButton && (
                  <Button
                    onClick={handleRefresh}
                    variant="ghost"
                    className="w-full"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Try Again
                  </Button>
                )}
                
                {shouldShowContactButton && (
                  <Button
                    onClick={handleContact}
                    variant="ghost"
                    className="w-full"
                  >
                    <Mail className="h-4 w-4 mr-2" />
                    Contact Support
                  </Button>
                )}
              </div>
            )}
          </div>

          {/* Additional Help */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="text-center">
              <p className="text-xs text-gray-500">
                Error Code: {statusCode} • Time: {new Date().toLocaleTimeString()}
              </p>
              {statusCode === 404 && (
                <p className="text-xs text-gray-500 mt-2">
                  Tip: Check the URL for typos or try searching from the homepage.
                </p>
              )}
              {statusCode === 403 && (
                <p className="text-xs text-gray-500 mt-2">
                  If you need access to this resource, please contact your administrator.
                </p>
              )}
              {statusCode === 500 && (
                <p className="text-xs text-gray-500 mt-2">
                  Our team has been automatically notified about this issue.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}