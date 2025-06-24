import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Clock, 
  ChevronLeft, 
  ChevronRight, 
  CheckCircle, 
  AlertCircle, 
  Flag,
  Eye,
  EyeOff,
  Send,
  RotateCcw
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Modal } from '@/components/ui/Modal';
import { 
  useEvaluation,
  useEvaluationQuestions,
  useStartEvaluationAttempt,
  useSubmitEvaluationAttempt,
  useSaveQuestionResponse,
  useEvaluationAttempt
} from '@/hooks/useEvaluations';
import type { Question, EvaluationAttempt, QuestionResponse } from '@/types/evaluation';
import TakeEvaluationAdaptive from './TakeEvaluationAdaptive';

// Question types components
interface QuestionComponentProps {
  question: Question;
  response?: any;
  onResponseChange: (response: any) => void;
  disabled?: boolean;
}

// Multiple Choice Question Component
const MultipleChoiceQuestion: React.FC<QuestionComponentProps> = ({ 
  question, 
  response, 
  onResponseChange, 
  disabled 
}) => {
  const options = question.question_data.options || [];
  
  return (
    <div className="space-y-3">
      {options.map((option: string, index: number) => (
        <label key={index} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
          <input
            type="radio"
            name={`question-${question.id}`}
            value={option}
            checked={response?.selected_option === option}
            onChange={(e) => onResponseChange({ selected_option: e.target.value })}
            disabled={disabled}
            className="text-blue-600"
          />
          <span className="flex-1">{option}</span>
        </label>
      ))}
    </div>
  );
};

// True/False Question Component
const TrueFalseQuestion: React.FC<QuestionComponentProps> = ({ 
  question, 
  response, 
  onResponseChange, 
  disabled 
}) => {
  return (
    <div className="space-y-3">
      <label className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
        <input
          type="radio"
          name={`question-${question.id}`}
          value="true"
          checked={response?.selected_option === true}
          onChange={() => onResponseChange({ selected_option: true })}
          disabled={disabled}
          className="text-blue-600"
        />
        <span className="flex-1">Doğru</span>
      </label>
      <label className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
        <input
          type="radio"
          name={`question-${question.id}`}
          value="false"
          checked={response?.selected_option === false}
          onChange={() => onResponseChange({ selected_option: false })}
          disabled={disabled}
          className="text-blue-600"
        />
        <span className="flex-1">Yanlış</span>
      </label>
    </div>
  );
};

// Short Answer Question Component
const ShortAnswerQuestion: React.FC<QuestionComponentProps> = ({ 
  question, 
  response, 
  onResponseChange, 
  disabled 
}) => {
  return (
    <div>
      <input
        type="text"
        value={response?.text || ''}
        onChange={(e) => onResponseChange({ text: e.target.value })}
        disabled={disabled}
        placeholder="Cevabınızı yazın..."
        className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        maxLength={question.question_data.max_length || 500}
      />
      {question.question_data.max_length && (
        <p className="text-sm text-gray-500 mt-1">
          {(response?.text || '').length} / {question.question_data.max_length} karakter
        </p>
      )}
    </div>
  );
};

// Essay Question Component
const EssayQuestion: React.FC<QuestionComponentProps> = ({ 
  question, 
  response, 
  onResponseChange, 
  disabled 
}) => {
  const maxWords = question.question_data.max_words || 1000;
  const minWords = question.question_data.min_words || 0;
  const wordCount = (response?.text || '').trim().split(/\s+/).length;
  
  return (
    <div>
      <textarea
        value={response?.text || ''}
        onChange={(e) => onResponseChange({ text: e.target.value })}
        disabled={disabled}
        placeholder="Kompozisyon yazın..."
        className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        rows={8}
      />
      <div className="flex justify-between text-sm text-gray-500 mt-1">
        <span>
          Kelime sayısı: {wordCount}
          {minWords > 0 && ` (en az ${minWords})`}
        </span>
        <span>Maksimum: {maxWords} kelime</span>
      </div>
    </div>
  );
};

// Timer Component
const Timer: React.FC<{ 
  timeLeft: number; 
  totalTime: number; 
  onTimeUp: () => void 
}> = ({ timeLeft, totalTime, onTimeUp }) => {
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const percentage = (timeLeft / totalTime) * 100;
  
  useEffect(() => {
    if (timeLeft <= 0) {
      onTimeUp();
    }
  }, [timeLeft, onTimeUp]);
  
  const getTimerColor = () => {
    if (percentage <= 10) return 'text-red-600';
    if (percentage <= 25) return 'text-orange-600';
    return 'text-green-600';
  };
  
  return (
    <div className="flex items-center space-x-2">
      <Clock className={`h-5 w-5 ${getTimerColor()}`} />
      <span className={`font-mono text-lg font-bold ${getTimerColor()}`}>
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </span>
    </div>
  );
};

// Question Navigator Component
const QuestionNavigator: React.FC<{
  questions: Question[];
  currentIndex: number;
  responses: Record<number, any>;
  onQuestionSelect: (index: number) => void;
}> = ({ questions, currentIndex, responses, onQuestionSelect }) => {
  return (
    <div className="grid grid-cols-5 gap-2 p-4">
      {questions.map((question, index) => {
        const hasResponse = responses[question.id];
        const isCurrent = index === currentIndex;
        
        return (
          <button
            key={question.id}
            onClick={() => onQuestionSelect(index)}
            className={`
              w-12 h-12 rounded-lg border-2 flex items-center justify-center font-medium transition-colors
              ${isCurrent 
                ? 'border-blue-500 bg-blue-500 text-white' 
                : hasResponse 
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
              }
            `}
          >
            {index + 1}
            {hasResponse && !isCurrent && (
              <CheckCircle className="h-3 w-3 absolute translate-x-2 -translate-y-2" />
            )}
          </button>
        );
      })}
    </div>
  );
};

export default function TakeEvaluation() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const evaluationId = parseInt(id!);
  
  // Check if we should render adaptive version
  const { data: evaluation, isLoading: checkLoading } = useEvaluation(evaluationId);
  
  // If evaluation is adaptive, render adaptive component
  if (!checkLoading && evaluation?.is_adaptive) {
    return <TakeEvaluationAdaptive />;
  }
  
  // State
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<number, any>>({});
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showNavigator, setShowNavigator] = useState(false);
  const [currentAttempt, setCurrentAttempt] = useState<EvaluationAttempt | null>(null);
  
  // React Query hooks
  const { data: evaluation, isLoading: evaluationLoading } = useEvaluation(evaluationId);
  const { data: questions, isLoading: questionsLoading } = useEvaluationQuestions(evaluationId);
  const startAttemptMutation = useStartEvaluationAttempt();
  const submitAttemptMutation = useSubmitEvaluationAttempt();
  const saveResponseMutation = useSaveQuestionResponse();
  
  // Start attempt on component mount
  useEffect(() => {
    if (evaluation?.is_available && !currentAttempt) {
      startAttemptMutation.mutate(evaluationId, {
        onSuccess: (attempt) => {
          setCurrentAttempt(attempt);
          if (evaluation.time_limit_minutes) {
            setTimeLeft(evaluation.time_limit_minutes * 60);
          }
        }
      });
    }
  }, [evaluation, evaluationId, currentAttempt, startAttemptMutation]);
  
  // Timer countdown
  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0) return;
    
    const timer = setInterval(() => {
      setTimeLeft(prev => prev! - 1);
    }, 1000);
    
    return () => clearInterval(timer);
  }, [timeLeft]);
  
  // Handle time up
  const handleTimeUp = useCallback(() => {
    if (currentAttempt) {
      submitAttemptMutation.mutate({
        evaluationId,
        attemptId: currentAttempt.id
      }, {
        onSuccess: () => {
          navigate(`/evaluations/${evaluationId}/results`);
        }
      });
    }
  }, [currentAttempt, evaluationId, navigate, submitAttemptMutation]);
  
  // Handle response change
  const handleResponseChange = (questionId: number, response: any) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: response
    }));
    
    // Auto-save response
    if (currentAttempt) {
      saveResponseMutation.mutate({
        evaluationId,
        attemptId: currentAttempt.id,
        data: {
          question_id: questionId,
          response_data: response
        }
      });
    }
  };
  
  // Handle navigation
  const handlePrevious = () => {
    setCurrentQuestionIndex(prev => Math.max(0, prev - 1));
  };
  
  const handleNext = () => {
    if (questions) {
      setCurrentQuestionIndex(prev => Math.min(questions.length - 1, prev + 1));
    }
  };
  
  // Handle submit
  const handleSubmit = () => {
    if (currentAttempt) {
      submitAttemptMutation.mutate({
        evaluationId,
        attemptId: currentAttempt.id
      }, {
        onSuccess: () => {
          navigate(`/evaluations/${evaluationId}/results`);
        }
      });
    }
  };
  
  // Render question component based on type
  const renderQuestion = (question: Question) => {
    const commonProps = {
      question,
      response: responses[question.id],
      onResponseChange: (response: any) => handleResponseChange(question.id, response),
      disabled: submitAttemptMutation.isPending
    };
    
    switch (question.question_type) {
      case 'multiple_choice':
        return <MultipleChoiceQuestion {...commonProps} />;
      case 'true_false':
        return <TrueFalseQuestion {...commonProps} />;
      case 'short_answer':
        return <ShortAnswerQuestion {...commonProps} />;
      case 'essay':
        return <EssayQuestion {...commonProps} />;
      default:
        return <div>Desteklenmeyen soru tipi</div>;
    }
  };
  
  if (evaluationLoading || questionsLoading) {
    return (
      <div className="p-6 flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  if (!evaluation || !questions) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">Değerlendirme bulunamadı.</p>
          <button
            onClick={() => navigate('/evaluations')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Geri Dön
          </button>
        </div>
      </div>
    );
  }
  
  if (!evaluation.is_available) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <p className="text-yellow-600">Bu değerlendirme şu anda mevcut değil.</p>
          <button
            onClick={() => navigate('/evaluations')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Geri Dön
          </button>
        </div>
      </div>
    );
  }
  
  const currentQuestion = questions[currentQuestionIndex];
  const answeredCount = Object.keys(responses).length;
  const progressPercentage = (answeredCount / questions.length) * 100;
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold">{evaluation.title}</h1>
              <div className="flex items-center space-x-4 mt-1">
                <span className="text-sm text-gray-600">
                  Soru {currentQuestionIndex + 1} / {questions.length}
                </span>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
                <span className="text-sm text-gray-600">
                  {answeredCount} cevaplandı
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {timeLeft !== null && (
                <Timer 
                  timeLeft={timeLeft} 
                  totalTime={evaluation.time_limit_minutes! * 60}
                  onTimeUp={handleTimeUp}
                />
              )}
              
              <button
                onClick={() => setShowNavigator(!showNavigator)}
                className="flex items-center px-3 py-2 border rounded-md hover:bg-gray-50"
              >
                {showNavigator ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                <span className="ml-2 hidden sm:inline">Sorular</span>
              </button>
              
              <button
                onClick={() => setShowSubmitModal(true)}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                <Send className="mr-2 h-4 w-4" />
                Bitir
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="max-w-6xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Question Navigator (Sidebar) */}
          {showNavigator && (
            <div className="lg:col-span-1">
              <Card className="sticky top-24">
                <div className="p-4 border-b">
                  <h3 className="font-semibold">Soru Haritası</h3>
                </div>
                <QuestionNavigator
                  questions={questions}
                  currentIndex={currentQuestionIndex}
                  responses={responses}
                  onQuestionSelect={setCurrentQuestionIndex}
                />
              </Card>
            </div>
          )}
          
          {/* Main Content */}
          <div className={showNavigator ? "lg:col-span-3" : "lg:col-span-4"}>
            <Card className="p-6">
              {/* Question Header */}
              <div className="flex justify-between items-start mb-6">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Badge variant="outline">
                      {currentQuestion.question_type === 'multiple_choice' && 'Çoktan Seçmeli'}
                      {currentQuestion.question_type === 'true_false' && 'Doğru/Yanlış'}
                      {currentQuestion.question_type === 'short_answer' && 'Kısa Cevap'}
                      {currentQuestion.question_type === 'essay' && 'Kompozisyon'}
                    </Badge>
                    <Badge variant="secondary">
                      {currentQuestion.points} Puan
                    </Badge>
                    {currentQuestion.is_required && (
                      <Badge variant="warning">Zorunlu</Badge>
                    )}
                  </div>
                  <h2 className="text-lg font-medium mb-4">
                    {currentQuestion.question_text}
                  </h2>
                </div>
              </div>
              
              {/* Question Content */}
              <div className="mb-8">
                {renderQuestion(currentQuestion)}
              </div>
              
              {/* Question Hints */}
              {currentQuestion.hints && currentQuestion.hints.length > 0 && (
                <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">💡 İpucu:</h4>
                  <ul className="text-blue-700 space-y-1">
                    {currentQuestion.hints.map((hint, index) => (
                      <li key={index} className="text-sm">• {hint}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Navigation Buttons */}
              <div className="flex justify-between items-center pt-6 border-t">
                <Button
                  variant="outline"
                  onClick={handlePrevious}
                  disabled={currentQuestionIndex === 0}
                >
                  <ChevronLeft className="mr-2 h-4 w-4" />
                  Önceki
                </Button>
                
                <div className="flex items-center space-x-2">
                  {responses[currentQuestion.id] && (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  )}
                  <span className="text-sm text-gray-600">
                    {responses[currentQuestion.id] ? 'Cevaplandı' : 'Cevaplanmadı'}
                  </span>
                </div>
                
                <Button
                  onClick={handleNext}
                  disabled={currentQuestionIndex === questions.length - 1}
                >
                  Sonraki
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
      
      {/* Submit Confirmation Modal */}
      <Modal
        isOpen={showSubmitModal}
        onClose={() => setShowSubmitModal(false)}
        title="Değerlendirmeyi Bitir"
      >
        <div className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-yellow-800">Dikkat!</h4>
                <p className="text-yellow-700 text-sm mt-1">
                  Değerlendirmeyi bitirdikten sonra cevaplarınızı değiştiremezsiniz.
                </p>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-gray-50 p-3 rounded">
              <div className="font-medium">Toplam Soru</div>
              <div className="text-lg font-bold">{questions.length}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <div className="font-medium">Cevaplanan</div>
              <div className="text-lg font-bold text-green-600">{answeredCount}</div>
            </div>
          </div>
          
          {answeredCount < questions.length && (
            <p className="text-orange-600 text-sm">
              {questions.length - answeredCount} soru cevaplanmadı. 
              Değerlendirmeyi yine de bitirmek istiyor musunuz?
            </p>
          )}
          
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => setShowSubmitModal(false)}
            >
              Devam Et
            </Button>
            <Button
              onClick={handleSubmit}
              loading={submitAttemptMutation.isPending}
            >
              Bitir ve Gönder
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}