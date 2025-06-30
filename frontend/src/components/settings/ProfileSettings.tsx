import React, { useState } from 'react';
import { Camera, Mail, Phone, MapPin, Building, Calendar, Globe, Loader2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/Select';
import { Avatar } from '@/components/ui/Avatar';
import { useToast } from '@/hooks/useToast';
import { api } from '@/services/api';

// Form validation schema
const profileSchema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  country: z.string().optional(),
  postalCode: z.string().optional(),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
  language: z.string().optional(),
  timezone: z.string().optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

const timezones = [
  { value: 'UTC', label: 'UTC (GMT+0:00)' },
  { value: 'America/New_York', label: 'Eastern Time (GMT-5:00)' },
  { value: 'America/Chicago', label: 'Central Time (GMT-6:00)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (GMT-8:00)' },
  { value: 'Europe/London', label: 'London (GMT+0:00)' },
  { value: 'Europe/Paris', label: 'Paris (GMT+1:00)' },
  { value: 'Europe/Istanbul', label: 'Istanbul (GMT+3:00)' },
  { value: 'Asia/Dubai', label: 'Dubai (GMT+4:00)' },
  { value: 'Asia/Kolkata', label: 'India (GMT+5:30)' },
  { value: 'Asia/Shanghai', label: 'China (GMT+8:00)' },
  { value: 'Asia/Tokyo', label: 'Tokyo (GMT+9:00)' },
  { value: 'Australia/Sydney', label: 'Sydney (GMT+10:00)' },
];

const languages = [
  { value: 'en', label: 'English' },
  { value: 'tr', label: 'Türkçe' },
  { value: 'es', label: 'Español' },
  { value: 'fr', label: 'Français' },
  { value: 'de', label: 'Deutsch' },
  { value: 'ar', label: 'العربية' },
  { value: 'zh', label: '中文' },
  { value: 'ja', label: '日本語' },
];

export const ProfileSettings: React.FC = () => {
  const { user, updateUser } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset,
    setValue,
    watch,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      firstName: user?.first_name || '',
      lastName: user?.last_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      address: user?.address || '',
      city: user?.city || '',
      country: user?.country || '',
      postalCode: user?.postal_code || '',
      bio: user?.bio || '',
      language: user?.language || 'en',
      timezone: user?.timezone || 'UTC',
    },
  });

  const watchedValues = watch();

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Image size must be less than 5MB');
        return;
      }

      setAvatarFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const onSubmit = async (data: ProfileFormData) => {
    setIsLoading(true);
    try {
      // First update profile data
      const profileData = {
        first_name: data.firstName,
        last_name: data.lastName,
        email: data.email,
        phone: data.phone,
        address: data.address,
        city: data.city,
        country: data.country,
        postal_code: data.postalCode,
        bio: data.bio,
        language: data.language,
        timezone: data.timezone,
      };

      const response = await api.put('/users/profile', profileData);

      // Upload avatar if changed
      if (avatarFile) {
        const formData = new FormData();
        formData.append('avatar', avatarFile);
        
        await api.post('/users/avatar', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      // Update local user data
      updateUser(response.data);
      reset(data);
      
      toast.success('Profile updated successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    reset();
    setAvatarFile(null);
    setAvatarPreview(null);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Avatar Section */}
      <Card>
        <CardHeader>
          <CardTitle>Profile Picture</CardTitle>
          <CardDescription>
            Update your profile picture. Recommended size is 400x400px.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-6">
            <div className="relative">
              <Avatar
                src={avatarPreview || user?.avatar_url || undefined}
                alt={`${user?.first_name} ${user?.last_name}`}
                size="xl"
                className="w-24 h-24"
              />
              <label
                htmlFor="avatar-upload"
                className="absolute bottom-0 right-0 p-1.5 bg-primary text-primary-foreground rounded-full cursor-pointer hover:bg-primary/90 transition-colors"
              >
                <Camera className="w-4 h-4" />
                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleAvatarChange}
                  disabled={isLoading}
                />
              </label>
            </div>
            <div className="flex-1">
              <p className="text-sm text-muted-foreground">
                JPG, PNG or GIF. Max size 5MB.
              </p>
              {avatarFile && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={() => {
                    setAvatarFile(null);
                    setAvatarPreview(null);
                  }}
                >
                  Remove
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>
            Update your personal details and contact information.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="firstName">First Name</Label>
              <Input
                id="firstName"
                {...register('firstName')}
                placeholder="John"
                disabled={isLoading}
              />
              {errors.firstName && (
                <p className="text-sm text-destructive">{errors.firstName.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="lastName">Last Name</Label>
              <Input
                id="lastName"
                {...register('lastName')}
                placeholder="Doe"
                disabled={isLoading}
              />
              {errors.lastName && (
                <p className="text-sm text-destructive">{errors.lastName.message}</p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">
              <Mail className="w-4 h-4 inline mr-1" />
              Email Address
            </Label>
            <Input
              id="email"
              type="email"
              {...register('email')}
              placeholder="john.doe@example.com"
              disabled={isLoading}
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">
              <Phone className="w-4 h-4 inline mr-1" />
              Phone Number
            </Label>
            <Input
              id="phone"
              type="tel"
              {...register('phone')}
              placeholder="+1 (555) 123-4567"
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="bio">Bio</Label>
            <textarea
              id="bio"
              {...register('bio')}
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Tell us a little about yourself..."
              rows={4}
              disabled={isLoading}
            />
            {errors.bio && (
              <p className="text-sm text-destructive">{errors.bio.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Location Information */}
      <Card>
        <CardHeader>
          <CardTitle>Location</CardTitle>
          <CardDescription>
            Your location information helps us provide better localized content.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="address">
              <MapPin className="w-4 h-4 inline mr-1" />
              Address
            </Label>
            <Input
              id="address"
              {...register('address')}
              placeholder="123 Main Street"
              disabled={isLoading}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="city">
                <Building className="w-4 h-4 inline mr-1" />
                City
              </Label>
              <Input
                id="city"
                {...register('city')}
                placeholder="New York"
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="country">Country</Label>
              <Input
                id="country"
                {...register('country')}
                placeholder="United States"
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="postalCode">Postal Code</Label>
              <Input
                id="postalCode"
                {...register('postalCode')}
                placeholder="10001"
                disabled={isLoading}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
          <CardDescription>
            Set your language and timezone preferences.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="language">
                <Globe className="w-4 h-4 inline mr-1" />
                Language
              </Label>
              <Select
                value={watchedValues.language}
                onChange={(e) => setValue('language', e.target.value)}
                options={languages}
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="timezone">
                <Calendar className="w-4 h-4 inline mr-1" />
                Timezone
              </Label>
              <Select
                value={watchedValues.timezone}
                onChange={(e) => setValue('timezone', e.target.value)}
                options={timezones}
                disabled={isLoading}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Information (Read-only) */}
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
          <CardDescription>
            Your account details and membership information.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">User ID</p>
              <p className="text-sm">{user?.id}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Role</p>
              <p className="text-sm capitalize">{user?.roles?.[0]?.name || 'User'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Member Since</p>
              <p className="text-sm">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
              <p className="text-sm">
                {user?.updated_at ? new Date(user.updated_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Form Actions */}
      <div className="flex justify-end space-x-4">
        <Button
          type="button"
          variant="outline"
          onClick={handleCancel}
          disabled={isLoading || !isDirty}
        >
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading || !isDirty}>
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            'Save Changes'
          )}
        </Button>
      </div>
    </form>
  );
};