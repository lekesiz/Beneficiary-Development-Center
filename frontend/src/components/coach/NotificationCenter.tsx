import {
  Bell,
  X,
  HelpCircle,
  CheckCircle,
  Clock,
  AlertCircle,
  ExternalLink,
  Trash2,
  Check,
} from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Form';
import { useCoachNotifications } from '@/hooks/useCoachNotifications';
import { formatDistanceToNow } from '@/utils/date';

export default function NotificationCenter() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const { notifications, unreadCount, markAsRead, markAllAsRead, clearNotification, isConnected } =
    useCoachNotifications();

  const handleNotificationClick = (notification: any) => {
    markAsRead(notification.id);
    navigate(`/coach/students/${notification.student_id}`);
    setIsOpen(false);
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'help_request':
        return <HelpCircle className="h-5 w-5 text-orange-500" />;
      case 'milestone_completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-blue-500" />;
    }
  };

  const getPriorityBadge = (priority?: string) => {
    if (!priority) return null;

    const variants = {
      high: 'danger',
      medium: 'warning',
      low: 'default',
    } as const;

    const labels = {
      high: 'High',
      medium: 'Medium',
      low: 'Low',
    };

    return (
      <Badge variant={variants[priority as keyof typeof variants] || 'default'} size="sm">
        {labels[priority as keyof typeof labels] || priority}
      </Badge>
    );
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="h-6 w-6 text-gray-600" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
        {!isConnected && (
          <span className="absolute bottom-0 right-0 h-2 w-2 bg-yellow-400 rounded-full" />
        )}
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
            onKeyDown={(e) => e.key === 'Escape' && setIsOpen(false)}
            role="button"
            tabIndex={0}
            aria-label="Close notifications"
          />

          {/* Dropdown Panel */}
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold flex items-center">
                  <Bell className="mr-2 h-5 w-5" />
                  Notifications
                  {unreadCount > 0 && (
                    <Badge variant="default" size="sm" className="ml-2">
                      {unreadCount} new
                    </Badge>
                  )}
                </h3>
                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <Button variant="ghost" size="sm" onClick={markAllAsRead} className="text-xs">
                      <Check className="h-3 w-3 mr-1" />
                      Mark All as Read
                    </Button>
                  )}
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Notifications List */}
            <div className="max-h-96 overflow-y-auto">
              {notifications.length > 0 ? (
                <div className="divide-y divide-gray-100">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                        !notification.read ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-1">
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <div
                              className="flex-1"
                              onClick={() => handleNotificationClick(notification)}
                            >
                              <p
                                className={`text-sm ${
                                  !notification.read ? 'font-semibold' : 'font-medium'
                                }`}
                              >
                                {notification.student_name}
                              </p>
                              <p className="text-sm text-gray-600 mt-1">
                                {notification.type === 'help_request'
                                  ? `needs help with "${notification.milestone_title}"`
                                  : `completed "${notification.milestone_title}" milestone`}
                              </p>
                              {notification.message && (
                                <p className="text-sm text-gray-500 mt-1 italic">
                                  "{notification.message}"
                                </p>
                              )}
                              <div className="flex items-center mt-2 space-x-3">
                                <span className="text-xs text-gray-500 flex items-center">
                                  <Clock className="h-3 w-3 mr-1" />
                                  {formatDistanceToNow(notification.timestamp)}
                                </span>
                                {notification.priority && getPriorityBadge(notification.priority)}
                                {notification.path_completed && (
                                  <Badge variant="success" size="sm">
                                    Path Completed
                                  </Badge>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center ml-2 space-x-1">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleNotificationClick(notification);
                                }}
                                className="p-1 hover:bg-gray-200 rounded"
                                title="Go to student profile"
                              >
                                <ExternalLink className="h-4 w-4 text-gray-500" />
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  clearNotification(notification.id);
                                }}
                                className="p-1 hover:bg-gray-200 rounded"
                                title="Delete notification"
                              >
                                <Trash2 className="h-4 w-4 text-gray-500" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center">
                  <Bell className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">You have no new notifications</p>
                </div>
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className="p-3 border-t border-gray-200">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    navigate('/coach/notifications');
                    setIsOpen(false);
                  }}
                >
                  View all notifications
                </Button>
              </div>
            )}

            {/* Connection Status */}
            {!isConnected && (
              <div className="px-4 py-2 bg-yellow-50 border-t border-yellow-200">
                <p className="text-xs text-yellow-800 flex items-center">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Connection lost. Attempting to reconnect...
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
