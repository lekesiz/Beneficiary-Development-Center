import React from 'react'

const LoadingScreen: React.FC = () => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="relative">
          {/* Spinner */}
          <div className="h-16 w-16 animate-spin rounded-full border-4 border-muted border-t-primary"></div>
          
          {/* Center dot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-3 w-3 rounded-full bg-primary"></div>
          </div>
        </div>
        
        {/* Loading text */}
        <p className="mt-4 text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  )
}

export default LoadingScreen