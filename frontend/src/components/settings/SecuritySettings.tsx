import React, { useState } from 'react';
import { Shield, Key, Smartphone, History, AlertTriangle, Check, X, Loader2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/Badge';
import { useToast } from '@/hooks/useToast';
import { api } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

// Password validation schema
const passwordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type PasswordFormData = z.infer<typeof passwordSchema>;

interface LoginSession {
  id: string;
  device: string;
  browser: string;
  ip_address: string;
  location: string;
  last_active: string;
  is_current: boolean;
}

export const SecuritySettings: React.FC = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isPasswordLoading, setIsPasswordLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(user?.two_factor_enabled || false);
  const [sessions, setSessions] = useState<LoginSession[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  });

  // Load active sessions
  React.useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const response = await api.get('/auth/sessions');
      setSessions(response.data || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const handlePasswordChange = async (data: PasswordFormData) => {
    setIsPasswordLoading(true);
    try {
      await api.post('/auth/change-password', {
        current_password: data.currentPassword,
        new_password: data.newPassword,
      });
      
      toast.success('Password changed successfully');
      reset();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to change password');
    } finally {
      setIsPasswordLoading(false);
    }
  };

  const handleTwoFactorToggle = async (enabled: boolean) => {
    try {
      if (enabled) {
        // Initiate 2FA setup
        const response = await api.post('/auth/2fa/enable');
        // In a real app, show QR code for authenticator app
        toast.success('Two-factor authentication enabled');
      } else {
        await api.post('/auth/2fa/disable');
        toast.success('Two-factor authentication disabled');
      }
      setTwoFactorEnabled(enabled);
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to update 2FA settings');
      setTwoFactorEnabled(!enabled); // Revert the toggle
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await api.delete(`/auth/sessions/${sessionId}`);
      setSessions(sessions.filter(s => s.id !== sessionId));
      toast.success('Session revoked successfully');
    } catch (error) {
      toast.error('Failed to revoke session');
    }
  };

  const getDeviceIcon = (device: string) => {
    if (device.toLowerCase().includes('mobile')) {
      return <Smartphone className="w-4 h-4" />;
    }
    return <Shield className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      {/* Change Password */}
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>
            Update your password regularly to keep your account secure.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(handlePasswordChange)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="currentPassword">Current Password</Label>
              <div className="relative">
                <Input
                  id="currentPassword"
                  type={showPassword ? 'text' : 'password'}
                  {...register('currentPassword')}
                  disabled={isPasswordLoading}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-1 top-1 h-7 w-7 p-0"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <X className="h-4 w-4" /> : <Key className="h-4 w-4" />}
                </Button>
              </div>
              {errors.currentPassword && (
                <p className="text-sm text-destructive">{errors.currentPassword.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="newPassword">New Password</Label>
              <Input
                id="newPassword"
                type={showPassword ? 'text' : 'password'}
                {...register('newPassword')}
                disabled={isPasswordLoading}
              />
              {errors.newPassword && (
                <p className="text-sm text-destructive">{errors.newPassword.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                {...register('confirmPassword')}
                disabled={isPasswordLoading}
              />
              {errors.confirmPassword && (
                <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
              )}
            </div>

            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters.
              </AlertDescription>
            </Alert>

            <Button type="submit" disabled={isPasswordLoading}>
              {isPasswordLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Changing Password...
                </>
              ) : (
                'Change Password'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Two-Factor Authentication */}
      <Card>
        <CardHeader>
          <CardTitle>Two-Factor Authentication</CardTitle>
          <CardDescription>
            Add an extra layer of security to your account with 2FA.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-muted-foreground" />
                <span className="font-medium">
                  Two-factor authentication is {twoFactorEnabled ? 'enabled' : 'disabled'}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                {twoFactorEnabled 
                  ? 'Your account is protected with two-factor authentication.'
                  : 'Enable two-factor authentication for enhanced security.'}
              </p>
            </div>
            <Switch
              checked={twoFactorEnabled}
              onCheckedChange={handleTwoFactorToggle}
            />
          </div>
        </CardContent>
      </Card>

      {/* Active Sessions */}
      <Card>
        <CardHeader>
          <CardTitle>Active Sessions</CardTitle>
          <CardDescription>
            Manage your active login sessions across different devices.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingSessions ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : sessions.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No active sessions found.
            </p>
          ) : (
            <div className="space-y-4">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-start space-x-3">
                    <div className="p-2 bg-muted rounded-lg">
                      {getDeviceIcon(session.device)}
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <p className="font-medium">{session.device}</p>
                        {session.is_current && (
                          <Badge variant="success" className="text-xs">
                            Current
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {session.browser} • {session.ip_address}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {session.location} • Last active: {new Date(session.last_active).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  {!session.is_current && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRevokeSession(session.id)}
                    >
                      Revoke
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Security Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Security Activity</CardTitle>
          <CardDescription>
            Recent security-related activities on your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <History className="w-4 h-4 text-muted-foreground" />
              <span>Password changed</span>
              <span className="text-muted-foreground">2 days ago</span>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-blue-500 rounded-full" />
              <History className="w-4 h-4 text-muted-foreground" />
              <span>New login from Chrome on Windows</span>
              <span className="text-muted-foreground">5 days ago</span>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <History className="w-4 h-4 text-muted-foreground" />
              <span>Two-factor authentication enabled</span>
              <span className="text-muted-foreground">1 week ago</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Security Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Security Tips</CardTitle>
          <CardDescription>
            Follow these best practices to keep your account secure.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start space-x-2">
              <Check className="w-5 h-5 text-green-600 mt-0.5" />
              <p className="text-sm">Use a strong, unique password for your BDC account</p>
            </div>
            <div className="flex items-start space-x-2">
              <Check className="w-5 h-5 text-green-600 mt-0.5" />
              <p className="text-sm">Enable two-factor authentication for extra security</p>
            </div>
            <div className="flex items-start space-x-2">
              <Check className="w-5 h-5 text-green-600 mt-0.5" />
              <p className="text-sm">Regularly review your active sessions and revoke suspicious ones</p>
            </div>
            <div className="flex items-start space-x-2">
              <Check className="w-5 h-5 text-green-600 mt-0.5" />
              <p className="text-sm">Keep your email address up to date for security notifications</p>
            </div>
            <div className="flex items-start space-x-2">
              <Check className="w-5 h-5 text-green-600 mt-0.5" />
              <p className="text-sm">Be cautious of phishing emails asking for your credentials</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};