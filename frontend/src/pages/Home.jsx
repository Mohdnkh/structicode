import React from "react"
import { useTranslation } from "react-i18next"

export default function Home({ onStart }) {
  const { t } = useTranslation()

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundImage: 'url("/background.png")', // ✅ الصورة من public
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
        src="/logo-structicode.png" // ✅ اللوجو من public
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

      {/* ✅ الوصف */}
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
