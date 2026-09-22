import { Link } from 'react-router-dom'
import { ArrowRight, Boxes, LayoutPanelTop } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function Home() {
  const { t } = useTranslation()
  return <section className="home-entry" aria-labelledby="home-title">
    <div className="home-intro">
      <img className="home-logo" src="/logo-structicode.png" alt="Structicode" />
      <p className="eyebrow">Engineering software workspace</p>
      <h1 id="home-title">{t('home.title')}</h1>
      <p>{t('home.subtitle')}</p>
      <div className="action-grid">
        <Link className="entry-action" to="/analyze"><strong><Boxes aria-hidden="true" size={17} /> {t('home.element_action')}</strong><span>{t('home.element_detail')}</span></Link>
        <Link className="entry-action" to="/structure-designer"><strong><LayoutPanelTop aria-hidden="true" size={17} /> {t('home.structure_action')}</strong><span>{t('home.structure_detail')} <ArrowRight aria-hidden="true" size={14} /></span></Link>
      </div>
    </div>
    <aside className="home-boundary"><strong>{t('home.boundary_title')}</strong><p>{t('home.boundary_detail')}</p></aside>
  </section>
}