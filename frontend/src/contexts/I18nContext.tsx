import React, { createContext, useContext, ReactNode } from 'react'
import i18n from 'i18next'
import { initReactI18next, useTranslation } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import HttpBackend from 'i18next-http-backend'

// Initialize i18n
i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'fr',
    debug: false,
    supportedLngs: ['fr', 'en', 'es', 'de', 'it', 'pt', 'ar'],
    
    interpolation: {
      escapeValue: false,
    },

    backend: {
      loadPath: '/locales/{{lng}}/translation.json',
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
  })

interface I18nContextType {
  currentLanguage: string
  changeLanguage: (lang: string) => Promise<void>
  t: (key: string, options?: any) => string
  languages: Array<{ code: string; name: string; flag: string }>
}

const I18nContext = createContext<I18nContextType | undefined>(undefined)

export const useI18n = () => {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider')
  }
  return context
}

interface I18nProviderProps {
  children: ReactNode
}

const languages = [
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  { code: 'pt', name: 'Português', flag: '🇵🇹' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦' },
]

export const I18nProvider: React.FC<I18nProviderProps> = ({ children }) => {
  const { t, i18n: i18nInstance } = useTranslation()

  const changeLanguage = async (lang: string) => {
    await i18nInstance.changeLanguage(lang)
    localStorage.setItem('i18nextLng', lang)
    
    // Set document direction for RTL languages
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'
    document.documentElement.lang = lang
  }

  const value = {
    currentLanguage: i18nInstance.language,
    changeLanguage,
    t,
    languages,
  }

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}