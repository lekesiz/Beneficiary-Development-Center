/**
 * Calendar Button Component
 * A dropdown button that allows users to add events to their calendar
 */

import React, { useState, useRef, useEffect } from 'react';
import { Calendar, Download, ChevronDown } from 'lucide-react';
import { Button } from './Form';
import type { CourseSession } from '../../types/course';
import { downloadSessionCalendar, openInCalendar } from '../../utils/calendar';
import { useToast } from '../../hooks/useToast';

interface CalendarButtonProps {
  session: CourseSession;
  courseTitle: string;
  programId: number;
  courseId: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'outline' | 'ghost';
  className?: string;
}

export const CalendarButton: React.FC<CalendarButtonProps> = ({
  session,
  courseTitle,
  programId,
  courseId,
  size = 'sm',
  variant = 'outline',
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { showToast } = useToast();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleDownload = async () => {
    try {
      await downloadSessionCalendar(session, courseTitle, programId, courseId);
      showToast({
        type: 'success',
        message: 'Takvim dosyası indirildi',
      });
      setIsOpen(false);
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Takvim dosyası indirilemedi',
      });
    }
  };

  const handleOpenInCalendar = (type: 'google' | 'outlook' | 'apple') => {
    try {
      openInCalendar(session, courseTitle, type);
      setIsOpen(false);
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Takvim açılamadı',
      });
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant={variant}
        size={size}
        onClick={() => setIsOpen(!isOpen)}
        className={`${className} flex items-center gap-2`}
      >
        <Calendar className="h-4 w-4" />
        <span className="hidden sm:inline">Takvime Ekle</span>
        <ChevronDown className={`h-3 w-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50">
          <div className="py-1" role="menu">
            <button
              onClick={handleDownload}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
              role="menuitem"
            >
              <Download className="h-4 w-4" />
              .ics Dosyası İndir
            </button>
            
            <div className="border-t border-gray-100 my-1" />
            
            <button
              onClick={() => handleOpenInCalendar('google')}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
              role="menuitem"
            >
              <img 
                src="https://www.google.com/favicon.ico" 
                alt="Google Calendar" 
                className="h-4 w-4"
              />
              Google Calendar
            </button>
            
            <button
              onClick={() => handleOpenInCalendar('outlook')}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
              role="menuitem"
            >
              <img 
                src="https://outlook.live.com/favicon.ico" 
                alt="Outlook" 
                className="h-4 w-4"
              />
              Outlook
            </button>
            
            <button
              onClick={() => handleOpenInCalendar('apple')}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
              role="menuitem"
            >
              <Calendar className="h-4 w-4 text-gray-600" />
              Apple Calendar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarButton;