import {
  ArrowLeft,
  Edit,
  Trash2,
  Mail,
  Phone,
  Calendar,
  MapPin,
  Briefcase,
  GraduationCap,
  Tag,
  User,
  FileText,
  Loader2,
} from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Form';
import { ConfirmDialog } from '@/components/ui/Modal';
import { useAuth } from '@/contexts/AuthContext';
import { useBeneficiary, useDeleteBeneficiary } from '@/hooks/useBeneficiaries';
import { formatDate } from '@/lib/utils';
import {
  BeneficiaryStatus,
  EmploymentStatus,
  EducationLevel,
} from '@/types/beneficiary';

export default function BeneficiaryDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const {
    data: beneficiaryData,
    isLoading,
    error,
  } = useBeneficiary(Number(id));
  const deleteMutation = useDeleteBeneficiary();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error || !beneficiaryData?.data.beneficiary) {
    return (
      <div className="container mx-auto py-6">
        <div className="text-center">
          <h2 className="text-lg font-semibold">Beneficiary not found</h2>
          <p className="text-muted-foreground mt-2">
            The beneficiary you're looking for doesn't exist or you don't have
            permission to view it.
          </p>
          <Button onClick={() => navigate('/beneficiaries')} className="mt-4">
            Back to Beneficiaries
          </Button>
        </div>
      </div>
    );
  }

  const beneficiary = beneficiaryData.data.beneficiary;
  const canEdit = user?.role === 'admin' || user?.role === 'trainer';
  const canDelete = user?.role === 'admin';

  const statusVariants = {
    [BeneficiaryStatus.ACTIVE]: 'success',
    [BeneficiaryStatus.INACTIVE]: 'secondary',
    [BeneficiaryStatus.COMPLETED]: 'default',
    [BeneficiaryStatus.SUSPENDED]: 'danger',
  } as const;

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(Number(id));
      navigate('/beneficiaries');
    } catch (error) {
      // Error is handled by the mutation
    }
    setShowDeleteDialog(false);
  };

  const InfoItem = ({
    icon: Icon,
    label,
    value,
  }: {
    icon: React.ElementType;
    label: string;
    value?: string | null;
  }) => {
    if (!value) return null;

    return (
      <div className="flex items-start gap-3">
        <Icon className="h-5 w-5 text-muted-foreground mt-0.5" />
        <div>
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          <p className="text-sm">{value}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto py-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/beneficiaries')}
            className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Beneficiaries
          </button>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">{beneficiary.full_name}</h1>
              <div className="flex items-center gap-4 mt-2">
                <Badge variant={statusVariants[beneficiary.status]}>
                  {beneficiary.status}
                </Badge>
                {beneficiary.external_id && (
                  <span className="text-sm text-muted-foreground">
                    ID: {beneficiary.external_id}
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {canEdit && (
                <Button
                  onClick={() => navigate(`/beneficiaries/${id}/edit`)}
                  variant="outline"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              )}
              {canDelete && (
                <Button
                  onClick={() => setShowDeleteDialog(true)}
                  variant="destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <InfoItem
                    icon={Mail}
                    label="Email"
                    value={beneficiary.email}
                  />
                  <InfoItem
                    icon={Phone}
                    label="Phone"
                    value={beneficiary.phone}
                  />
                  <InfoItem
                    icon={Phone}
                    label="Mobile"
                    value={beneficiary.mobile_phone}
                  />
                  <InfoItem
                    icon={Calendar}
                    label="Date of Birth"
                    value={
                      beneficiary.date_of_birth
                        ? formatDate(beneficiary.date_of_birth)
                        : null
                    }
                  />
                  <InfoItem
                    icon={User}
                    label="Age"
                    value={beneficiary.age ? `${beneficiary.age} years` : null}
                  />
                  <InfoItem
                    icon={User}
                    label="Gender"
                    value={beneficiary.gender}
                  />
                  <InfoItem
                    icon={MapPin}
                    label="Nationality"
                    value={beneficiary.nationality}
                  />
                  <InfoItem
                    icon={MapPin}
                    label="Birthplace"
                    value={beneficiary.birthplace}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Address */}
            {beneficiary.address && (
              <Card>
                <CardHeader>
                  <CardTitle>Address</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-start gap-3">
                    <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div>
                      {beneficiary.address.street && (
                        <p>{beneficiary.address.street}</p>
                      )}
                      <p>
                        {[
                          beneficiary.address.city,
                          beneficiary.address.state,
                          beneficiary.address.postal_code,
                        ]
                          .filter(Boolean)
                          .join(', ')}
                      </p>
                      {beneficiary.address.country && (
                        <p>{beneficiary.address.country}</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Professional Information */}
            <Card>
              <CardHeader>
                <CardTitle>Professional Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <InfoItem
                    icon={Briefcase}
                    label="Employment Status"
                    value={
                      beneficiary.employment_status
                        ? beneficiary.employment_status
                            .replace(/_/g, ' ')
                            .charAt(0)
                            .toUpperCase() +
                          beneficiary.employment_status
                            .replace(/_/g, ' ')
                            .slice(1)
                        : null
                    }
                  />
                  <InfoItem
                    icon={Briefcase}
                    label="Job Title"
                    value={beneficiary.job_title}
                  />
                  <InfoItem
                    icon={Briefcase}
                    label="Company"
                    value={beneficiary.company}
                  />
                  <InfoItem
                    icon={Briefcase}
                    label="Industry"
                    value={beneficiary.industry}
                  />
                  <InfoItem
                    icon={Briefcase}
                    label="Years of Experience"
                    value={
                      beneficiary.years_of_experience
                        ? `${beneficiary.years_of_experience} years`
                        : null
                    }
                  />
                </div>
              </CardContent>
            </Card>

            {/* Education */}
            <Card>
              <CardHeader>
                <CardTitle>Education</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <InfoItem
                      icon={GraduationCap}
                      label="Education Level"
                      value={
                        beneficiary.education_level
                          ? beneficiary.education_level
                              .replace(/_/g, ' ')
                              .charAt(0)
                              .toUpperCase() +
                            beneficiary.education_level
                              .replace(/_/g, ' ')
                              .slice(1)
                          : null
                      }
                    />
                    <InfoItem
                      icon={GraduationCap}
                      label="Field of Study"
                      value={beneficiary.field_of_study}
                    />
                  </div>

                  {beneficiary.certifications &&
                    beneficiary.certifications.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-muted-foreground mb-2">
                          Certifications
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {beneficiary.certifications.map((cert, index) => (
                            <Badge key={index} variant="outline">
                              {cert}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Management Info */}
            <Card>
              <CardHeader>
                <CardTitle>Management</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {beneficiary.assigned_trainer_name && (
                  <InfoItem
                    icon={User}
                    label="Assigned Trainer"
                    value={beneficiary.assigned_trainer_name}
                  />
                )}

                {beneficiary.tags && beneficiary.tags.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Tag className="h-4 w-4 text-muted-foreground" />
                      <p className="text-sm font-medium text-muted-foreground">
                        Tags
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {beneficiary.tags.map((tag, index) => (
                        <Badge key={index} variant="secondary" size="sm">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t">
                  <p className="text-xs text-muted-foreground">
                    Created: {formatDate(beneficiary.created_at, 'long')}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Updated: {formatDate(beneficiary.updated_at, 'long')}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Skills & Interests */}
            <Card>
              <CardHeader>
                <CardTitle>Skills & Interests</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {beneficiary.skills && beneficiary.skills.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">
                      Skills
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {beneficiary.skills.map((skill, index) => (
                        <Badge key={index} variant="outline" size="sm">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {beneficiary.interests && beneficiary.interests.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">
                      Interests
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {beneficiary.interests.map((interest, index) => (
                        <Badge key={index} variant="outline" size="sm">
                          {interest}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {beneficiary.goals && beneficiary.goals.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">
                      Goals
                    </p>
                    <ul className="list-disc list-inside space-y-1">
                      {beneficiary.goals.map((goal, index) => (
                        <li key={index} className="text-sm">
                          {goal}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Progress Summary */}
            {beneficiary.progress_summary && (
              <Card>
                <CardHeader>
                  <CardTitle>Progress Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center mb-4">
                    <div className="text-3xl font-bold">
                      {Math.round(
                        beneficiary.progress_summary.overall_progress
                      )}
                      %
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Overall Progress
                    </p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Active Enrollments</span>
                      <span className="font-medium">
                        {beneficiary.active_enrollments || 0}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Completed Programs</span>
                      <span className="font-medium">
                        {beneficiary.completed_programs || 0}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Notes */}
            {beneficiary.notes && beneficiary.notes.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {beneficiary.notes.slice(0, 3).map((note) => (
                      <div
                        key={note.id}
                        className="border-l-2 border-primary/20 pl-3"
                      >
                        <p className="text-sm">{note.text}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDate(note.created_at)}
                        </p>
                      </div>
                    ))}
                    {beneficiary.notes.length > 3 && (
                      <p className="text-sm text-muted-foreground">
                        +{beneficiary.notes.length - 3} more notes
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={handleDelete}
        title="Delete Beneficiary"
        message={`Are you sure you want to delete ${beneficiary.full_name}? This action cannot be undone.`}
        confirmText="Delete"
        loading={deleteMutation.isPending}
      />
    </div>
  );
}
