import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Lightbulb, Ruler, Globe2 } from 'lucide-react'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom, #f8fafc, #e2e8f0)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '2rem',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* الخلفية المصممة */}
      <motion.div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.1,
          zIndex: 0,
        }}
        initial={{ scale: 1.1 }}
        animate={{ scale: 1 }}
        transition={{ duration: 4 }}
      >
        <img
          src="/background.png"
          alt="Structural background"
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      </motion.div>

      {/* المحتوى الرئيسي */}
      <div style={{ position: 'relative', zIndex: 10, maxWidth: '800px', width: '100%' }}>
        <motion.img
          src="/logo.png"
          alt="Civil Code Logo"
          style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            margin: '0 auto 1rem',
          }}
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
        />

        <motion.h1
          style={{
            fontSize: '2.5rem',
            fontWeight: 800,
            color: '#111827',
            marginBottom: '1rem',
          }}
          initial={{ y: -10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          World Civil Engineering <span style={{ color: '#2563eb' }}>Code Platform</span>
        </motion.h1>

        <motion.p
          style={{
            fontSize: '1.125rem',
            color: '#4b5563',
            marginBottom: '2rem',
            maxWidth: '600px',
            marginLeft: 'auto',
            marginRight: 'auto',
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          Perform smart, fast and code-compliant structural element analysis based on global building standards.
        </motion.p>

        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <button
            onClick={() => navigate('/analyze')}
            style={{
              fontSize: '1rem',
              padding: '0.75rem 1.5rem',
              borderRadius: '12px',
              backgroundColor: '#2563eb',
              color: 'white',
              fontWeight: '600',
              border: 'none',
              boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
              cursor: 'pointer',
            }}
          >
            Start Analysis
          </button>
        </motion.div>
      </div>

      {/* المزايا السريعة */}
      <motion.div
        style={{
          position: 'relative',
          zIndex: 10,
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1.5rem',
          marginTop: '4rem',
          maxWidth: '1000px',
          width: '100%',
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        <FeatureCard icon={<Ruler size={32} />} title="Multi-code Support" desc="Supports ACI, Eurocode, BS, CSA, IS, and more." />
        <FeatureCard icon={<Globe2 size={32} />} title="Country-Specific Design" desc="Includes Middle East codes: Jordan, Egypt, Saudi, UAE, Turkey." />
        <FeatureCard icon={<Lightbulb size={32} />} title="Smart Recommendations" desc="Get suggestions to improve your design safety." />
      </motion.div>
    </div>
  )
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div
      style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '1.5rem',
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <div style={{ marginBottom: '0.75rem', color: '#2563eb' }}>{icon}</div>
      <h3 style={{ fontWeight: 'bold', fontSize: '1.125rem' }}>{title}</h3>
      <p style={{ color: '#4b5563', fontSize: '0.875rem', marginTop: '0.25rem' }}>{desc}</p>
    </div>
  )
}
