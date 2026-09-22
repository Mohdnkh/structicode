import { NavLink } from 'react-router-dom'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Activity, Languages, Layers3 } from 'lucide-react'

export default function AppShell({ children }) {
  const { i18n } = useTranslation()
  const language = i18n.language?.startsWith('ar') ? 'ar' : 'en'
  const navigation = language === 'ar'
    ? [{ to: '/', label: 'الرئيسية', icon: Layers3 }, { to: '/analyze', label: 'تحليل العناصر', icon: Activity }, { to: '/structure-designer', label: 'مساحة عمل المنشأ', icon: Layers3 }]
    : [{ to: '/', label: 'Home', icon: Layers3 }, { to: '/analyze', label: 'Element Analysis', icon: Activity }, { to: '/structure-designer', label: 'Structure Workspace', icon: Layers3 }]

  useEffect(() => {
    document.documentElement.lang = language
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr'
    localStorage.setItem('structicode-language', language)
  }, [language])

  const switchLanguage = () => i18n.changeLanguage(language === 'ar' ? 'en' : 'ar')

  return <div className="app-shell">
    <a className="skip-link" href="#workspace-main">Skip to workspace</a>
    <header className="app-header">
      <NavLink to="/" className="brand" aria-label="Structicode home">
        <span className="brand-mark">S</span>
        <span><strong>Structicode</strong><small>Engineering workspace</small></span>
      </NavLink>
      <nav className="workspace-nav" aria-label="Primary navigation">
        {navigation.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to}
          className={({ isActive }) => `nav-link ${isActive ? 'is-active' : ''}`}>
          <Icon aria-hidden="true" size={16} /> <span>{label}</span>
        </NavLink>)}
      </nav>
      <button className="language-control" type="button" onClick={switchLanguage}
        aria-label={`Switch to ${language === 'ar' ? 'English' : 'Arabic'}`}>
        <Languages aria-hidden="true" size={16} /> {language === 'ar' ? 'English' : 'العربية'}
      </button>
    </header>
    <main id="workspace-main" className="workspace-main">{children}</main>
  </div>
}
