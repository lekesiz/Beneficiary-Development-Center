import {
  X,
  ChevronRight,
  ChevronLeft,
  Brain,
  Target,
  Calendar,
  Clock,
  BookOpen,
  Award,
  CheckCircle,
  Edit3,
  AlertCircle,
} from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Textarea } from '@/components/ui/Form';
import type { LearningPath } from '@/types/learning-path';

interface LearningPathAcceptanceFlowProps {
  learningPath: LearningPath;
  onAccept: (customizationNotes?: string) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const LearningPathAcceptanceFlow: React.FC<LearningPathAcceptanceFlowProps> = ({
  learningPath,
  onAccept,
  onCancel,
  isLoading = false,
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [customizationNotes, setCustomizationNotes] = useState('');
  const [acceptanceConfirmed, setAcceptanceConfirmed] = useState(false);

  const totalSteps = 3;

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleAccept = () => {
    onAccept(customizationNotes);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Öğrenme Planını İncele ve Kabul Et</h2>
            <p className="text-sm text-gray-600 mt-1">
              Adım {currentStep} / {totalSteps}
            </p>
          </div>
          <button onClick={onCancel} className="p-2 hover:bg-gray-100 rounded-md">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-3 border-b">
          <div className="flex items-center space-x-2">
            {[1, 2, 3].map((step) => (
              <React.Fragment key={step}>
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                    step <= currentStep ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step < currentStep ? <CheckCircle className="h-5 w-5" /> : step}
                </div>
                {step < 3 && (
                  <div
                    className={`flex-1 h-1 ${step < currentStep ? 'bg-blue-600' : 'bg-gray-200'}`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-sm">
            <span className={currentStep >= 1 ? 'text-blue-600 font-medium' : 'text-gray-600'}>
              Plan Özeti
            </span>
            <span className={currentStep >= 2 ? 'text-blue-600 font-medium' : 'text-gray-600'}>
              Detaylı İnceleme
            </span>
            <span className={currentStep >= 3 ? 'text-blue-600 font-medium' : 'text-gray-600'}>
              Kabul ve Özelleştir
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
          {/* Step 1: Overview */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Brain className="h-16 w-16 text-blue-600 mx-auto mb-4" />
                <h3 className="text-2xl font-bold mb-2">
                  Kişiselleştirilmiş Öğrenme Planınız Hazır!
                </h3>
                <p className="text-gray-600">
                  AI, değerlendirme sonuçlarınıza göre size özel bir öğrenme planı oluşturdu.
                </p>
              </div>

              {/* Key Highlights */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="p-4">
                  <div className="flex items-start space-x-3">
                    <Calendar className="h-8 w-8 text-blue-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold">Süre</h4>
                      <p className="text-2xl font-bold text-blue-600">
                        {learningPath.duration_weeks} Hafta
                      </p>
                      <p className="text-sm text-gray-600">
                        Haftada {learningPath.estimated_hours_per_week} saat
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="flex items-start space-x-3">
                    <Target className="h-8 w-8 text-green-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold">Hedefler</h4>
                      <p className="text-2xl font-bold text-green-600">
                        {learningPath.total_milestones}
                      </p>
                      <p className="text-sm text-gray-600">Öğrenme hedefi</p>
                    </div>
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="flex items-start space-x-3">
                    <BookOpen className="h-8 w-8 text-purple-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold">Kaynaklar</h4>
                      <p className="text-2xl font-bold text-purple-600">
                        {learningPath.resources.reduce((acc, cat) => acc + cat.items.length, 0)}+
                      </p>
                      <p className="text-sm text-gray-600">Öğrenme materyali</p>
                    </div>
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="flex items-start space-x-3">
                    <Award className="h-8 w-8 text-orange-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold">Zorluk</h4>
                      <p className="text-2xl font-bold text-orange-600 capitalize">
                        {learningPath.difficulty_adjustment === 'easy'
                          ? 'Kolay'
                          : learningPath.difficulty_adjustment === 'balanced'
                          ? 'Dengeli'
                          : 'Zorlu'}
                      </p>
                      <p className="text-sm text-gray-600">Kişiselleştirilmiş</p>
                    </div>
                  </div>
                </Card>
              </div>

              {/* Main Objective */}
              <Card className="p-6 bg-blue-50 border-blue-200">
                <h4 className="font-semibold text-blue-900 mb-2">Ana Öğrenme Hedefi</h4>
                <p className="text-blue-800">{learningPath.objective}</p>
              </Card>
            </div>
          )}

          {/* Step 2: Detailed Review */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <h3 className="text-xl font-semibold mb-4">Haftalık Plan ve Hedefler</h3>

              {/* Weekly Milestones */}
              <div className="space-y-4">
                {learningPath.milestones.map((milestone, index) => (
                  <Card key={milestone.id} className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="primary">Hafta {milestone.week_number}</Badge>
                          <Badge variant="outline">{milestone.estimated_hours} saat</Badge>
                        </div>
                        <h4 className="font-semibold mb-1">{milestone.title}</h4>
                        <p className="text-sm text-gray-600 mb-3">{milestone.description}</p>

                        {/* Activities */}
                        <div className="mb-3">
                          <h5 className="text-sm font-medium text-gray-700 mb-2">Aktiviteler:</h5>
                          <ul className="space-y-1">
                            {milestone.activities.slice(0, 2).map((activity, aIndex) => (
                              <li key={aIndex} className="text-sm text-gray-600 flex items-start">
                                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 mr-2 flex-shrink-0" />
                                {activity.title}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Assessment Criteria */}
                        {milestone.assessment_criteria.length > 0 && (
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-2">
                              Başarı Kriterleri:
                            </h5>
                            <ul className="space-y-1">
                              {milestone.assessment_criteria.slice(0, 2).map((criteria, cIndex) => (
                                <li key={cIndex} className="text-sm text-gray-600 flex items-start">
                                  <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                                  {criteria}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      <div className="ml-4 text-right">
                        <div className="text-3xl font-bold text-gray-300">{index + 1}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Success Metrics */}
              {learningPath.success_metrics && learningPath.success_metrics.length > 0 && (
                <Card className="p-4 bg-green-50 border-green-200">
                  <h4 className="font-semibold text-green-900 mb-2">Başarı Ölçütleri</h4>
                  <ul className="space-y-1">
                    {learningPath.success_metrics.map((metric, index) => (
                      <li key={index} className="text-sm text-green-800 flex items-start">
                        <Award className="h-4 w-4 mt-0.5 mr-2 flex-shrink-0" />
                        {metric}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}
            </div>
          )}

          {/* Step 3: Accept and Customize */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Planı Kabul Etmek Üzeresiniz</h3>
                <p className="text-gray-600">
                  Planı kabul ettikten sonra öğrenmeye başlayabilirsiniz.
                </p>
              </div>

              {/* Customization Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Özelleştirme Notları (İsteğe Bağlı)
                </label>
                <Textarea
                  value={customizationNotes}
                  onChange={(e) => setCustomizationNotes(e.target.value)}
                  placeholder="Planla ilgili özel istekleriniz veya notlarınız varsa buraya yazabilirsiniz..."
                  rows={4}
                  className="w-full"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Örnek: "Akşamları çalışmayı tercih ederim" veya "Video içeriklere öncelik vermek
                  istiyorum"
                </p>
              </div>

              {/* Important Notes */}
              <Card className="p-4 bg-yellow-50 border-yellow-200">
                <div className="flex items-start space-x-3">
                  <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-yellow-900 mb-1">Önemli Notlar</h4>
                    <ul className="space-y-1 text-sm text-yellow-800">
                      <li>• Plan kabul edildikten sonra öğrenme takibiniz başlayacak</li>
                      <li>• İstediğiniz zaman planı düzenleyebilir ve özelleştirebilirsiniz</li>
                      <li>• Haftalık ilerlemeniz otomatik olarak kaydedilecek</li>
                      <li>• Tamamladığınız hedefler için başarı rozetleri kazanacaksınız</li>
                    </ul>
                  </div>
                </div>
              </Card>

              {/* Acceptance Confirmation */}
              <Card className="p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={acceptanceConfirmed}
                    onChange={(e) => setAcceptanceConfirmed(e.target.checked)}
                    className="mt-1"
                  />
                  <span className="text-sm">
                    Öğrenme planını inceledim ve {learningPath.duration_weeks} haftalık bu programa
                    başlamaya hazırım.
                  </span>
                </label>
              </Card>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t flex items-center justify-between">
          <Button
            variant="outline"
            onClick={currentStep === 1 ? onCancel : handlePrevious}
            disabled={isLoading}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            {currentStep === 1 ? 'İptal' : 'Geri'}
          </Button>

          <div className="flex items-center space-x-2">
            {currentStep < totalSteps ? (
              <Button onClick={handleNext} disabled={isLoading}>
                İleri
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={handleAccept}
                disabled={!acceptanceConfirmed || isLoading}
                className="bg-green-600 hover:bg-green-700"
              >
                {isLoading ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Kabul Ediliyor...
                  </>
                ) : (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Planı Kabul Et ve Başla
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
