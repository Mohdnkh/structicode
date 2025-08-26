const { defineConfig } = require('vite')
const react = require('@vitejs/plugin-react')
const path = require('path')

// ✅ هذا السطر غير مطلوب إذا مش مستخدم import.meta.url
module.exports = defineConfig({
  base: './',
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})
