/**
 * Course Reorder Page
 */
import { ArrowLeft, Save, RotateCcw } from 'lucide-react';
import * as React from 'react';
import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { DragDropList } from '../../components/ui/DragDropList';
import { Button } from '../../components/ui/Form';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import { useCourses, useReorderCourse } from '../../hooks/useCourses';
import { useProgram } from '../../hooks/usePrograms';
import type { Course } from '../../types/course';
import {
  getCourseStatusInfo,
  getCourseFormatInfo,
  getDifficultyLevelInfo,
} from '../../utils/course';

export const CourseReorder: React.FC = () => {
  const { programId } = useParams<{ programId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const programIdNum = parseInt(programId!);

  const { data: program, isLoading: isLoadingProgram } = useProgram(
    programIdNum,
    false
  );
  const { data: coursesData, isLoading: isLoadingCourses } = useCourses({
    program_id: programIdNum,
    per_page: 100,
  });
  const reorderCourse = useReorderCourse();

  const [courses, setCourses] = useState<Course[]>([]);
  const [hasChanges, setHasChanges] = useState(false);

  // Permission checks
  const canReorder = user?.role && ['admin', 'manager'].includes(user.role);

  // Initialize courses when data is loaded
  React.useEffect(() => {
    if (coursesData?.courses) {
      const sortedCourses = [...coursesData.courses].sort(
        (a, b) => a.order_index - b.order_index
      );
      setCourses(sortedCourses);
    }
  }, [coursesData]);

  // Convert courses to drag-drop items
  const dragDropItems = useMemo(() => {
    return courses.map((course) => {
      const statusInfo = getCourseStatusInfo(course.status);
      const formatInfo = getCourseFormatInfo(course.format);
      const difficultyInfo = getDifficultyLevelInfo(course.difficulty_level);

      return {
        id: course.id,
        data: course,
        content: (
          <div className="flex items-center justify-between w-full">
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <div>
                  <h4 className="font-medium text-gray-900">{course.title}</h4>
                  <p className="text-sm text-gray-500">#{course.code}</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge color={statusInfo.color}>{statusInfo.label}</Badge>
              <div className="flex items-center space-x-1 text-gray-500">
                <span>{formatInfo.icon}</span>
                <span className="text-xs">{formatInfo.label}</span>
              </div>
              <Badge color={difficultyInfo.color} size="sm">
                {difficultyInfo.label}
              </Badge>
              <span className="text-sm text-gray-500">
                {course.duration_hours}sa
              </span>
            </div>
          </div>
        ),
      };
    });
  }, [courses]);

  // Handle reorder
  const handleReorder = (reorderedItems: any[]) => {
    const reorderedCourses = reorderedItems.map((item, index) => ({
      ...item.data,
      order_index: index + 1,
    }));
    setCourses(reorderedCourses);
    setHasChanges(true);
  };

  // Reset to original order
  const handleReset = () => {
    if (coursesData?.courses) {
      const sortedCourses = [...coursesData.courses].sort(
        (a, b) => a.order_index - b.order_index
      );
      setCourses(sortedCourses);
      setHasChanges(false);
    }
  };

  // Save changes
  const handleSave = async () => {
    try {
      const promises = courses.map((course, index) => {
        const newOrderIndex = index + 1;
        if (course.order_index !== newOrderIndex) {
          return reorderCourse.mutateAsync({
            courseId: course.id,
            data: { order_index: newOrderIndex },
          });
        }
        return Promise.resolve();
      });

      await Promise.all(promises);
      setHasChanges(false);
      navigate(`/programs/${programId}`);
    } catch (error) {
      // Error handled by mutations
    }
  };

  if (!canReorder) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          Bu sayfaya erişim yetkiniz bulunmamaktadır.
        </div>
      </Card>
    );
  }

  if (isLoadingProgram || isLoadingCourses) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!program || !coursesData) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          Program bulunamadı veya kurslar yüklenirken hata oluştu.
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/programs/${programId}`)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Programa Dön
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Kurs Sıralama</h1>
            <p className="text-gray-600">
              {program.title} - Kursları sürükleyerek sıralayın
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {hasChanges && (
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Sıfırla
            </Button>
          )}
          <Button
            onClick={handleSave}
            disabled={!hasChanges || reorderCourse.isPending}
          >
            <Save className="h-4 w-4 mr-2" />
            Değişiklikleri Kaydet
          </Button>
        </div>
      </div>

      {/* Info */}
      <Card className="p-4 bg-blue-50 border-blue-200">
        <div className="flex items-center space-x-2 text-blue-700">
          <span className="text-sm">
            💡 Kursları sürükleyerek istediğiniz sıraya getirin.
            Değişikliklerinizi kaydetmeyi unutmayın.
          </span>
        </div>
      </Card>

      {/* Course List */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">
          Kurslar ({courses.length})
        </h3>

        {courses.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            Bu programa henüz kurs eklenmemiş.
          </div>
        ) : (
          <DragDropList
            items={dragDropItems}
            onReorder={handleReorder}
            disabled={reorderCourse.isPending}
          />
        )}
      </Card>

      {/* Changes Warning */}
      {hasChanges && (
        <Card className="p-4 bg-yellow-50 border-yellow-200">
          <div className="flex items-center justify-between">
            <div className="text-yellow-700">
              <span className="font-medium">
                Kaydedilmemiş değişiklikler var!
              </span>
              <span className="ml-2 text-sm">
                Değişikliklerinizi kaydetmeyi unutmayın.
              </span>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={handleReset}>
                Sıfırla
              </Button>
              <Button
                size="sm"
                onClick={handleSave}
                disabled={reorderCourse.isPending}
              >
                Kaydet
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default CourseReorder;
