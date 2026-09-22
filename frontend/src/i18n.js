import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import translationEN from './locales/en/translation.json'
import translationAR from './locales/ar/translation.json'

const savedLanguage = typeof window !== 'undefined' ? localStorage.getItem('structicode-language') : null

i18n.use(initReactI18next).init({
  resources: { en: { translation: translationEN }, ar: { translation: translationAR } },
  lng: savedLanguage === 'ar' ? 'ar' : 'en', fallbackLng: 'en', interpolation: { escapeValue: false },
})
export default i18n