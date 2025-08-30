import React from "react"
import { useTranslation } from "react-i18next"

// لو الصور بمجلد src/assets لازم نعمل import
// import bgImg from "../assets/background.png"
// import logo from "../assets/logo-structicode.png"

export default function Home({ onStart }) {
  const { t } = useTranslation()

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundImage: 'url("/background.png")', // أو: `url(${bgImg})`
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: "20px"
      }}
    >
      {/* ✅ اللوجو */}
      <img
        src="/logo-structicode.png" // أو: {logo}
        alt="Structicode Logo"
        style={{ width: "160px", marginBottom: "20px" }}
      />

      {/* ✅ العنوان */}
      <h1
        style={{
          fontSize: "2.5rem",
          fontWeight: "bold",
          color: "#1e3a8a",
          marginBottom: "1rem"
        }}
      >
        {t("home.title")}
      </h1>

      {/* ✅ الوصف (معدل ليستخدم subtitle بدل description) */}
      <p style={{ fontSize: "1.2rem", color: "#374151", marginBottom: "2rem" }}>
        {t("home.subtitle")}
      </p>

      {/* ✅ زر البداية */}
      <button
        onClick={onStart}
        style={{
          padding: "12px 24px",
          fontSize: "1rem",
          fontWeight: "600",
          color: "white",
          backgroundColor: "#2563eb",
          borderRadius: "12px",
          border: "none",
          cursor: "pointer"
        }}
      >
        {t("home.start")}
      </button>
    </div>
  )
}
