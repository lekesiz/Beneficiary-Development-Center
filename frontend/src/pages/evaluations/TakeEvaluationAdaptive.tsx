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
  RotateCcw,
  Brain,
  TrendingUp,
  TrendingDown,
  Activity
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Form';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Modal } from '@/components/ui/Modal';
import { 
  useEvaluation,
  useStartEvaluationAttempt,
  useSubmitEvaluationAttempt,
  useSaveQuestionResponse,
  useEvaluationAttempt
} from '@/hooks/useEvaluations';
import { 
  useAdaptiveNextQuestion, 
  useAdaptiveEvaluationFlow,
  getDifficultyColor,
  getDifficultyLabel 
} from '@/hooks/useAdaptiveEvaluation';
import type { Question, EvaluationAttempt, QuestionResponse } from '@/types/evaluation';

// Question types components (reuse from original TakeEvaluation)
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

// Adaptive Difficulty Indicator
const AdaptiveDifficultyIndicator: React.FC<{
  currentDifficulty: 'easy' | 'medium' | 'hard';
  isAdapting?: boolean;
}> = ({ currentDifficulty, isAdapting }) => {
  return (
    <div className="flex items-center space-x-2">
      <Brain className={`h-5 w-5 ${isAdapting ? 'animate-pulse' : ''} text-purple-600`} />
      <div>
        <span className="text-sm text-gray-600">AI Zorluk Seviyesi:</span>
        <Badge 
          className={`ml-2 ${getDifficultyColor(currentDifficulty)}`}
          variant="outline"
        >
          {getDifficultyLabel(currentDifficulty)}
        </Badge>
      </div>
      {isAdapting && (
        <div className="flex items-center space-x-1">
          <Activity className="h-4 w-4 text-blue-600 animate-pulse" />
          <span className="text-xs text-blue-600">Adapte ediliyor...</span>
        </div>
      )}
    </div>
  );
};

// Performance Indicator
const PerformanceIndicator: React.FC<{
  recentPerformance: number; // 0-1 scale
}> = ({ recentPerformance }) => {
  const getPerformanceIcon = () => {
    if (recentPerformance >= 0.8) return <TrendingUp className="h-5 w-5 text-green-600" />;
    if (recentPerformance <= 0.4) return <TrendingDown className="h-5 w-5 text-red-600" />;
    return <Activity className="h-5 w-5 text-yellow-600" />;
  };

  const getPerformanceText = () => {
    if (recentPerformance >= 0.8) return 'Mükemmel';
    if (recentPerformance <= 0.4) return 'Gelişim Gerekli';
    return 'İyi';
  };

  return (
    <div className="flex items-center space-x-2">
      {getPerformanceIcon()}
      <span className="text-sm font-medium">{getPerformanceText()}</span>
    </div>
  );
};

export default function TakeEvaluationAdaptive() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const evaluationId = parseInt(id!);
  
  // State
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<number, any>>({});
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [currentAttempt, setCurrentAttempt] = useState<EvaluationAttempt | null>(null);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [answeredQuestions, setAnsweredQuestions] = useState<Question[]>([]);
  const [recentPerformance, setRecentPerformance] = useState(0.5);
  
  // React Query hooks
  const { data: evaluation, isLoading: evaluationLoading } = useEvaluation(evaluationId);
  const startAttemptMutation = useStartEvaluationAttempt();
  const submitAttemptMutation = useSubmitEvaluationAttempt();
  const saveResponseMutation = useSaveQuestionResponse();
  
  // Adaptive evaluation hooks
  const { getNextQuestion, prefetchNextQuestions, invalidateAdaptiveCache } = useAdaptiveEvaluationFlow();
  
  // Start attempt and get first question
  useEffect(() => {
    if (evaluation?.is_available && !currentAttempt) {
      startAttemptMutation.mutate(evaluationId, {
        onSuccess: async (attempt) => {
          setCurrentAttempt(attempt);
          if (evaluation.time_limit_minutes) {
            setTimeLeft(evaluation.time_limit_minutes * 60);
          }
          
          // Get first question
          await loadNextQuestion(attempt.id, 0);
        }
      });
    }
  }, [evaluation, evaluationId, currentAttempt]);
  
  // Load next adaptive question
  const loadNextQuestion = async (attemptId: number, index: number) => {
    setIsLoadingQuestion(true);
    
    try {
      const result = await getNextQuestion.mutateAsync({
        evaluationId,
        attemptId,
        currentIndex: index
      });
      
      if (result.complete) {
        // No more questions, submit attempt
        handleSubmit();
      } else if (result.question) {
        setCurrentQuestion(result.question);
        setCurrentQuestionIndex(index);
        
        // Prefetch next questions for better performance
        if (currentAttempt) {
          prefetchNextQuestions(evaluationId, attemptId, index);
        }
        
        // Update performance indicator based on adaptive metadata
        updatePerformanceIndicator();
      }
    } catch (error) {
      console.error('Failed to load next question:', error);
    } finally {
      setIsLoadingQuestion(false);
    }
  };
  
  // Update performance indicator
  const updatePerformanceIndicator = () => {
    // Calculate recent performance from last 5 responses
    const recentResponses = Object.entries(responses).slice(-5);
    if (recentResponses.length > 0) {
      // This is a simplified calculation - in real implementation,
      // you would check actual correctness from the backend
      const performance = Math.random(); // Placeholder
      setRecentPerformance(performance);
    }
  };
  
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
      handleSubmit();
    }
  }, [currentAttempt]);
  
  // Handle response change and move to next question
  const handleResponseChange = async (response: any) => {
    if (!currentQuestion || !currentAttempt) return;
    
    // Save response locally
    setResponses(prev => ({
      ...prev,
      [currentQuestion.id]: response
    }));
    
    // Save response to backend
    await saveResponseMutation.mutateAsync({
      evaluationId,
      attemptId: currentAttempt.id,
      data: {
        question_id: currentQuestion.id,
        response_data: response
      }
    });
    
    // Add to answered questions
    setAnsweredQuestions(prev => [...prev, currentQuestion]);
  };
  
  // Handle moving to next question
  const handleNext = async () => {
    if (!currentAttempt || !currentQuestion) return;
    
    // Check if current question is answered
    if (!responses[currentQuestion.id]) {
      // You might want to show a warning here
      return;
    }
    
    // Load next adaptive question
    await loadNextQuestion(currentAttempt.id, currentQuestionIndex + 1);
  };
  
  // Handle going back (if allowed)
  const handlePrevious = () => {
    // In adaptive mode, going back might not be allowed
    // or might require special handling
    console.log('Previous question navigation in adaptive mode');
  };
  
  // Handle submit
  const handleSubmit = () => {
    if (currentAttempt) {
      submitAttemptMutation.mutate({
        evaluationId,
        attemptId: currentAttempt.id
      }, {
        onSuccess: () => {
          navigate(`/evaluations/${evaluationId}/results/${currentAttempt.id}`);
        }
      });
    }
  };
  
  // Render question component based on type
  const renderQuestion = (question: Question) => {
    const commonProps = {
      question,
      response: responses[question.id],
      onResponseChange: handleResponseChange,
      disabled: submitAttemptMutation.isPending || isLoadingQuestion
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
  
  if (evaluationLoading) {
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
  
  const answeredCount = Object.keys(responses).length;
  const progressPercentage = evaluation.total_questions > 0 
    ? (answeredCount / evaluation.total_questions) * 100 
    : 0;
  
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
                  Soru {currentQuestionIndex + 1}
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
              
              <PerformanceIndicator recentPerformance={recentPerformance} />
              
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
      
      <div className="max-w-4xl mx-auto p-6">
        {/* Adaptive Difficulty Indicator */}
        <div className="mb-4">
          <AdaptiveDifficultyIndicator 
            currentDifficulty={currentQuestion?.difficulty_level || 'medium'}
            isAdapting={isLoadingQuestion}
          />
        </div>
        
        {/* Main Content */}
        {isLoadingQuestion ? (
          <Card className="p-12">
            <div className="flex flex-col items-center justify-center space-y-4">
              <Brain className="h-12 w-12 text-purple-600 animate-pulse" />
              <LoadingSpinner size="lg" />
              <p className="text-gray-600">AI sonraki soruyu hazırlıyor...</p>
            </div>
          </Card>
        ) : currentQuestion ? (
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
                  <Badge 
                    className={getDifficultyColor(currentQuestion.difficulty_level)}
                    variant="outline"
                  >
                    {getDifficultyLabel(currentQuestion.difficulty_level)}
                  </Badge>
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
                disabled={true} // Disabled in adaptive mode
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
                disabled={!responses[currentQuestion.id] || isLoadingQuestion}
              >
                Sonraki
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </Card>
        ) : (
          <Card className="p-6">
            <div className="text-center py-8">
              <p className="text-gray-600">Soru yükleniyor...</p>
            </div>
          </Card>
        )}
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
              <div className="font-medium">Cevaplanan</div>
              <div className="text-lg font-bold text-green-600">{answeredCount}</div>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <div className="font-medium">AI Adaptasyon</div>
              <div className="text-lg font-bold text-purple-600">Aktif</div>
            </div>
          </div>
          
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