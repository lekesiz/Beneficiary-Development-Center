import React from 'react';

export const DesignTest: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-slate-900">Design System Test</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Color Test */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Colors Working?</h2>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-blue-600 rounded"></div>
                <span>Primary Blue</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-slate-100 rounded"></div>
                <span>Slate 100</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-green-600 rounded"></div>
                <span>Success Green</span>
              </div>
            </div>
          </div>

          {/* Animation Test */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Animations Working?</h2>
            <div className="space-y-2">
              <div className="bg-blue-100 p-4 rounded animate-fade-in">
                Fade In Animation
              </div>
              <div className="bg-green-100 p-4 rounded animate-slide-up">
                Slide Up Animation
              </div>
            </div>
          </div>
        </div>

        {/* Grid Pattern Test */}
        <div className="relative bg-white rounded-lg shadow-lg p-6 overflow-hidden">
          <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] -z-10" />
          <h2 className="text-2xl font-semibold mb-4">Grid Pattern Working?</h2>
          <p>You should see a subtle grid pattern in the background of this card.</p>
        </div>

        {/* Font Test */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Font Working?</h2>
          <p className="font-sans">This should be Inter font (sans)</p>
          <p className="font-mono mt-2">This should be JetBrains Mono (mono)</p>
        </div>
      </div>
    </div>
  );
};