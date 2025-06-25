import { zodResolver } from '@hookform/resolvers/zod';
import {
  ArrowLeft,
  Save,
  Plus,
  Trash2,
  HelpCircle,
  Type,
  CheckSquare,
  FileText,
  Star,
  Hash,
  Eye,
} from 'lucide-react';
import * as React from 'react';
import { useEffect, useState } from 'react';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { z } from 'zod';

import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import {
  FormField,
  Input,
  Textarea,
  Select,
  Button,
} from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { TagInput } from '@/components/ui/TagInput';
import {
  useEvaluation,
  useEvaluationQuestion,
  useCreateEvaluationQuestion,
  useUpdateEvaluationQuestion,
} from '@/hooks/useEvaluations';
import type {
  CreateQuestionRequest,
  UpdateQuestionRequest,
} from '@/types/evaluation';

// Question type specific validation schemas
const multipleChoiceSchema = z.object({
  options: z
    .array(z.string().min(1, 'Seçenek boş olamaz'))
    .min(2, 'En az 2 seçenek gereklidir'),
  correct_answer: z.string().min(1, 'Doğru cevap seçilmelidir'),
});

const trueFalseSchema = z.object({
  correct_answer: z.boolean(),
});

const shortAnswerSchema = z.object({
  correct_answers: z
    .array(z.string().min(1, 'Kabul edilebilir cevap boş olamaz'))
    .min(1, 'En az 1 kabul edilebilir cevap gereklidir'),
  max_length: z.number().min(1).max(1000).optional(),
  case_sensitive: z.boolean().default(false),
});

const essaySchema = z.object({
  min_words: z.number().min(1).max(10000).optional(),
  max_words: z.number().min(1).max(10000).optional(),
  rubric: z.string().optional(),
});

// Main validation schema
const questionSchema = z
  .object({
    question_text: z
      .string()
      .min(1, 'Soru metni gereklidir')
      .max(2000, 'Soru metni en fazla 2000 karakter olabilir'),
    question_type: z.enum([
      'multiple_choice',
      'true_false',
      'short_answer',
      'essay',
    ]),
    points: z
      .number()
      .min(0.1, 'Puan en az 0.1 olmalıdır')
      .max(100, 'Puan en fazla 100 olabilir')
      .default(1),
    difficulty_level: z.enum(['easy', 'medium', 'hard']).default('medium'),
    explanation: z
      .string()
      .max(1000, 'Açıklama en fazla 1000 karakter olabilir')
      .optional(),
    hints: z
      .array(z.string().max(200, 'İpucu en fazla 200 karakter olabilir'))
      .default([]),
    tags: z.array(z.string()).default([]),
    is_required: z.boolean().default(false),
    order: z.number().min(0).optional(),
    question_data: z.union([
      multipleChoiceSchema,
      trueFalseSchema,
      shortAnswerSchema,
      essaySchema,
    ]),
  })
  .refine(
    (data) => {
      // Validate question_data based on question_type
      switch (data.question_type) {
        case 'multiple_choice':
          return multipleChoiceSchema.safeParse(data.question_data).success;
        case 'true_false':
          return trueFalseSchema.safeParse(data.question_data).success;
        case 'short_answer':
          return shortAnswerSchema.safeParse(data.question_data).success;
        case 'essay':
          return essaySchema.safeParse(data.question_data).success;
        default:
          return false;
      }
    },
    {
      message: 'Soru tipi için geçersiz veri',
      path: ['question_data'],
    }
  );

type QuestionFormData = z.infer<typeof questionSchema>;

interface QuestionFormProps {
  mode: 'create' | 'edit';
}

const QuestionForm: React.FC<QuestionFormProps> = ({ mode }) => {
  const navigate = useNavigate();
  const { evaluationId, questionId } = useParams<{
    evaluationId: string;
    questionId?: string;
  }>();
  const [showPreview, setShowPreview] = useState(false);

  const evalId = parseInt(evaluationId!);
  const qId = questionId ? parseInt(questionId) : undefined;

  // React Query hooks
  const { data: evaluation, isLoading: evaluationLoading } =
    useEvaluation(evalId);
  const { data: question, isLoading: questionLoading } = useEvaluationQuestion(
    evalId,
    qId!,
    { enabled: mode === 'edit' && !!qId }
  );
  const createMutation = useCreateEvaluationQuestion();
  const updateMutation = useUpdateEvaluationQuestion();

  // Form setup
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue,
  } = useForm<QuestionFormData>({
    resolver: zodResolver(questionSchema),
    defaultValues: {
      question_text: '',
      question_type: 'multiple_choice',
      points: 1,
      difficulty_level: 'medium',
      explanation: '',
      hints: [],
      tags: [],
      is_required: false,
      question_data: {
        options: ['', ''],
        correct_answer: '',
      },
    },
  });

  // Watch question type for dynamic form changes
  const watchedQuestionType = watch('question_type');
  const watchedQuestionData = watch('question_data');

  // Field arrays for dynamic inputs
  const {
    fields: optionFields,
    append: addOption,
    remove: removeOption,
  } = useFieldArray({
    control,
    name: 'question_data.options' as any,
  });

  const {
    fields: hintFields,
    append: addHint,
    remove: removeHint,
  } = useFieldArray({
    control,
    name: 'hints',
  });

  const {
    fields: answerFields,
    append: addAnswer,
    remove: removeAnswer,
  } = useFieldArray({
    control,
    name: 'question_data.correct_answers' as any,
  });

  // Reset form when question data is loaded
  useEffect(() => {
    if (mode === 'edit' && question) {
      reset({
        question_text: question.question_text,
        question_type: question.question_type,
        points: question.points,
        difficulty_level: question.difficulty_level,
        explanation: question.explanation || '',
        hints: question.hints || [],
        tags: question.tags || [],
        is_required: question.is_required,
        order: question.order,
        question_data: question.question_data,
      });
    }
  }, [mode, question, reset]);

  // Update question_data structure when question type changes
  useEffect(() => {
    const currentType = watchedQuestionType;
    const currentData = watchedQuestionData;

    // Don't reset if data already matches the expected structure
    if (currentType === 'multiple_choice' && currentData?.options) return;
    if (
      currentType === 'true_false' &&
      typeof currentData?.correct_answer === 'boolean'
    )
      return;
    if (currentType === 'short_answer' && currentData?.correct_answers) return;
    if (currentType === 'essay' && typeof currentData === 'object') return;

    switch (currentType) {
      case 'multiple_choice':
        setValue('question_data', {
          options: ['', ''],
          correct_answer: '',
        });
        break;
      case 'true_false':
        setValue('question_data', {
          correct_answer: true,
        });
        break;
      case 'short_answer':
        setValue('question_data', {
          correct_answers: [''],
          max_length: 100,
          case_sensitive: false,
        });
        break;
      case 'essay':
        setValue('question_data', {
          min_words: 50,
          max_words: 500,
          rubric: '',
        });
        break;
    }
  }, [watchedQuestionType, setValue]);

  // Handle form submission
  const onSubmit = async (data: QuestionFormData) => {
    try {
      if (mode === 'create') {
        await createMutation.mutateAsync({
          evaluationId: evalId,
          data: data as CreateQuestionRequest,
        });
        navigate(`/evaluations/${evalId}`);
      } else if (mode === 'edit' && qId) {
        await updateMutation.mutateAsync({
          evaluationId: evalId,
          questionId: qId,
          data: data as UpdateQuestionRequest,
        });
        navigate(`/evaluations/${evalId}`);
      }
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  // Render question type specific fields
  const renderQuestionTypeFields = () => {
    switch (watchedQuestionType) {
      case 'multiple_choice':
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="font-medium">Seçenekler</h4>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => addOption('')}
              >
                <Plus className="mr-1 h-4 w-4" />
                Seçenek Ekle
              </Button>
            </div>

            <div className="space-y-3">
              {optionFields.map((field, index) => (
                <div key={field.id} className="flex items-center space-x-2">
                  <span className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-xs font-medium">
                    {String.fromCharCode(65 + index)}
                  </span>
                  <Controller
                    name={`question_data.options.${index}` as any}
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        placeholder={`${index + 1}. seçenek`}
                        className="flex-1"
                      />
                    )}
                  />
                  {optionFields.length > 2 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeOption(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>

            <Controller
              name="question_data.correct_answer"
              control={control}
              render={({ field }) => (
                <FormField
                  label="Doğru Cevap"
                  error={errors.question_data?.correct_answer?.message}
                  required
                >
                  <Select
                    {...field}
                    error={!!errors.question_data?.correct_answer}
                  >
                    <option value="">Doğru cevabı seçin</option>
                    {(watchedQuestionData as any)?.options?.map(
                      (option: string, index: number) => (
                        <option key={index} value={option}>
                          {String.fromCharCode(65 + index)} -{' '}
                          {option || `${index + 1}. seçenek`}
                        </option>
                      )
                    )}
                  </Select>
                </FormField>
              )}
            />
          </div>
        );

      case 'true_false':
        return (
          <Controller
            name="question_data.correct_answer"
            control={control}
            render={({ field }) => (
              <FormField
                label="Doğru Cevap"
                error={errors.question_data?.correct_answer?.message}
                required
              >
                <div className="flex space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      checked={field.value === true}
                      onChange={() => field.onChange(true)}
                      className="text-blue-600"
                    />
                    <span>Doğru</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      checked={field.value === false}
                      onChange={() => field.onChange(false)}
                      className="text-blue-600"
                    />
                    <span>Yanlış</span>
                  </label>
                </div>
              </FormField>
            )}
          />
        );

      case 'short_answer':
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="font-medium">Kabul Edilebilir Cevaplar</h4>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => addAnswer('')}
              >
                <Plus className="mr-1 h-4 w-4" />
                Cevap Ekle
              </Button>
            </div>

            <div className="space-y-3">
              {answerFields.map((field, index) => (
                <div key={field.id} className="flex items-center space-x-2">
                  <Controller
                    name={`question_data.correct_answers.${index}` as any}
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        placeholder={`${index + 1}. kabul edilebilir cevap`}
                        className="flex-1"
                      />
                    )}
                  />
                  {answerFields.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeAnswer(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Controller
                name="question_data.max_length"
                control={control}
                render={({ field }) => (
                  <FormField
                    label="Maksimum Karakter"
                    error={errors.question_data?.max_length?.message}
                  >
                    <Input
                      {...field}
                      type="number"
                      min="1"
                      max="1000"
                      onChange={(e) =>
                        field.onChange(
                          e.target.value ? parseInt(e.target.value) : undefined
                        )
                      }
                    />
                  </FormField>
                )}
              />

              <Controller
                name="question_data.case_sensitive"
                control={control}
                render={({ field }) => (
                  <FormField label="Seçenekler">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={field.value}
                        onChange={field.onChange}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm">Büyük/küçük harf duyarlı</span>
                    </label>
                  </FormField>
                )}
              />
            </div>
          </div>
        );

      case 'essay':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Controller
                name="question_data.min_words"
                control={control}
                render={({ field }) => (
                  <FormField
                    label="Minimum Kelime Sayısı"
                    error={errors.question_data?.min_words?.message}
                  >
                    <Input
                      {...field}
                      type="number"
                      min="1"
                      max="10000"
                      onChange={(e) =>
                        field.onChange(
                          e.target.value ? parseInt(e.target.value) : undefined
                        )
                      }
                    />
                  </FormField>
                )}
              />

              <Controller
                name="question_data.max_words"
                control={control}
                render={({ field }) => (
                  <FormField
                    label="Maksimum Kelime Sayısı"
                    error={errors.question_data?.max_words?.message}
                  >
                    <Input
                      {...field}
                      type="number"
                      min="1"
                      max="10000"
                      onChange={(e) =>
                        field.onChange(
                          e.target.value ? parseInt(e.target.value) : undefined
                        )
                      }
                    />
                  </FormField>
                )}
              />
            </div>

            <Controller
              name="question_data.rubric"
              control={control}
              render={({ field }) => (
                <FormField
                  label="Değerlendirme Rubriği"
                  error={errors.question_data?.rubric?.message}
                >
                  <Textarea
                    {...field}
                    placeholder="Bu sorunun nasıl değerlendirileceğine dair yönergeler..."
                    rows={4}
                  />
                </FormField>
              )}
            />
          </div>
        );

      default:
        return null;
    }
  };

  if ((mode === 'edit' && questionLoading) || evaluationLoading) {
    return (
      <div className="p-6 flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <p className="text-red-600">Değerlendirme bulunamadı.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate(`/evaluations/${evalId}`)}
            className="p-2 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">
              {mode === 'create' ? 'Yeni Soru Ekle' : 'Soruyu Düzenle'}
            </h1>
            <p className="text-gray-600">{evaluation.title}</p>
          </div>
        </div>

        <Button variant="outline" onClick={() => setShowPreview(!showPreview)}>
          <Eye className="mr-2 h-4 w-4" />
          {showPreview ? 'Düzenlemeyi Göster' : 'Önizleme'}
        </Button>
      </div>

      {showPreview ? (
        /* Preview Mode */
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
              <Badge variant="outline">
                {watchedQuestionType === 'multiple_choice' && 'Çoktan Seçmeli'}
                {watchedQuestionType === 'true_false' && 'Doğru/Yanlış'}
                {watchedQuestionType === 'short_answer' && 'Kısa Cevap'}
                {watchedQuestionType === 'essay' && 'Kompozisyon'}
              </Badge>
              <Badge variant="secondary">{watch('points')} Puan</Badge>
              <Badge
                variant={
                  watch('difficulty_level') === 'easy'
                    ? 'success'
                    : watch('difficulty_level') === 'medium'
                    ? 'warning'
                    : 'danger'
                }
              >
                {watch('difficulty_level') === 'easy' && 'Kolay'}
                {watch('difficulty_level') === 'medium' && 'Orta'}
                {watch('difficulty_level') === 'hard' && 'Zor'}
              </Badge>
            </div>

            <h3 className="text-lg font-medium">
              {watch('question_text') || 'Soru metni...'}
            </h3>

            {/* Question preview based on type */}
            {watchedQuestionType === 'multiple_choice' && (
              <div className="space-y-2">
                {(watchedQuestionData as any)?.options?.map(
                  (option: string, index: number) => (
                    <div
                      key={index}
                      className="flex items-center space-x-2 p-2 border rounded"
                    >
                      <span className="w-6 h-6 border rounded-full flex items-center justify-center text-xs">
                        {String.fromCharCode(65 + index)}
                      </span>
                      <span>{option || `${index + 1}. seçenek`}</span>
                    </div>
                  )
                )}
              </div>
            )}

            {watch('explanation') && (
              <div className="p-3 bg-blue-50 rounded">
                <h4 className="font-medium text-blue-800 mb-1">Açıklama:</h4>
                <p className="text-blue-700 text-sm">{watch('explanation')}</p>
              </div>
            )}

            {watch('hints').length > 0 && (
              <div className="p-3 bg-yellow-50 rounded">
                <h4 className="font-medium text-yellow-800 mb-1">İpuçları:</h4>
                <ul className="text-yellow-700 text-sm space-y-1">
                  {watch('hints').map((hint, index) => (
                    <li key={index}>• {hint}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card>
      ) : (
        /* Edit Mode */
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Information */}
          <Card className="p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Type className="h-5 w-5 text-blue-600" />
              <h2 className="text-lg font-semibold">Soru Bilgileri</h2>
            </div>

            <div className="space-y-4">
              <Controller
                name="question_text"
                control={control}
                render={({ field }) => (
                  <FormField
                    label="Soru Metni"
                    error={errors.question_text?.message}
                    required
                  >
                    <Textarea
                      {...field}
                      placeholder="Sorunuzu buraya yazın..."
                      rows={4}
                      error={!!errors.question_text}
                    />
                  </FormField>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Controller
                  name="question_type"
                  control={control}
                  render={({ field }) => (
                    <FormField
                      label="Soru Tipi"
                      error={errors.question_type?.message}
                      required
                    >
                      <Select {...field} error={!!errors.question_type}>
                        <option value="multiple_choice">Çoktan Seçmeli</option>
                        <option value="true_false">Doğru/Yanlış</option>
                        <option value="short_answer">Kısa Cevap</option>
                        <option value="essay">Kompozisyon</option>
                      </Select>
                    </FormField>
                  )}
                />

                <Controller
                  name="points"
                  control={control}
                  render={({ field }) => (
                    <FormField
                      label="Puan"
                      error={errors.points?.message}
                      required
                    >
                      <Input
                        {...field}
                        type="number"
                        min="0.1"
                        max="100"
                        step="0.1"
                        onChange={(e) =>
                          field.onChange(parseFloat(e.target.value))
                        }
                        error={!!errors.points}
                      />
                    </FormField>
                  )}
                />

                <Controller
                  name="difficulty_level"
                  control={control}
                  render={({ field }) => (
                    <FormField
                      label="Zorluk Seviyesi"
                      error={errors.difficulty_level?.message}
                      required
                    >
                      <Select {...field} error={!!errors.difficulty_level}>
                        <option value="easy">Kolay</option>
                        <option value="medium">Orta</option>
                        <option value="hard">Zor</option>
                      </Select>
                    </FormField>
                  )}
                />
              </div>

              <Controller
                name="is_required"
                control={control}
                render={({ field }) => (
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={field.onChange}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm font-medium">
                      Bu soru zorunludur
                    </span>
                  </label>
                )}
              />
            </div>
          </Card>

          {/* Question Type Specific Fields */}
          <Card className="p-6">
            <div className="flex items-center space-x-2 mb-4">
              <CheckSquare className="h-5 w-5 text-green-600" />
              <h2 className="text-lg font-semibold">Soru İçeriği</h2>
            </div>

            {renderQuestionTypeFields()}
          </Card>

          {/* Additional Information */}
          <Card className="p-6">
            <div className="flex items-center space-x-2 mb-4">
              <FileText className="h-5 w-5 text-purple-600" />
              <h2 className="text-lg font-semibold">Ek Bilgiler</h2>
            </div>

            <div className="space-y-4">
              <Controller
                name="explanation"
                control={control}
                render={({ field }) => (
                  <FormField
                    label="Açıklama"
                    error={errors.explanation?.message}
                  >
                    <Textarea
                      {...field}
                      placeholder="Sorunun doğru cevabının açıklaması..."
                      rows={3}
                      error={!!errors.explanation}
                    />
                  </FormField>
                )}
              />

              {/* Hints */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-medium">İpuçları</label>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => addHint('')}
                  >
                    <Plus className="mr-1 h-4 w-4" />
                    İpucu Ekle
                  </Button>
                </div>

                <div className="space-y-2">
                  {hintFields.map((field, index) => (
                    <div key={field.id} className="flex items-center space-x-2">
                      <HelpCircle className="h-4 w-4 text-gray-400" />
                      <Controller
                        name={`hints.${index}`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            {...field}
                            placeholder={`${index + 1}. ipucu`}
                            className="flex-1"
                          />
                        )}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeHint(index)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tags */}
              <Controller
                name="tags"
                control={control}
                render={({ field }) => (
                  <FormField label="Etiketler" error={errors.tags?.message}>
                    <TagInput
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="Etiket eklemek için yazın ve Enter'a basın"
                    />
                  </FormField>
                )}
              />
            </div>
          </Card>

          {/* Form Actions */}
          <div className="flex justify-end space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate(`/evaluations/${evalId}`)}
              disabled={isSubmitting}
            >
              İptal
            </Button>

            <Button
              type="submit"
              loading={isSubmitting}
              disabled={isSubmitting}
            >
              <Save className="mr-2 h-4 w-4" />
              {mode === 'create' ? 'Soruyu Ekle' : 'Güncelle'}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
};

// Create and Edit page components
export const CreateQuestionPage = () => <QuestionForm mode="create" />;
export const EditQuestionPage = () => <QuestionForm mode="edit" />;

export default QuestionForm;
