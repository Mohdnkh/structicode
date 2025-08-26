# Step 1: Build frontend
FROM node:20 AS frontend
WORKDIR /app/frontend

# نسخ ملفات الحزم والكونفيغ
COPY frontend/package*.json ./
COPY frontend/vite.config.js ./

# تثبيت الحزم
RUN npm install

# ✅ إزالة esbuild وإعادة تركيبه لحل مشكلة binary mismatch
RUN npm uninstall esbuild && npm install esbuild@latest && npm rebuild esbuil

# نسخ باقي ملفات الواجهة
COPY frontend ./ 

# تشغيل build
RUN chmod +x node_modules/.bin/vite && npx vite build

# Step 2: Set up backend
FROM python:3.11-slim AS backend
WORKDIR /app

RUN apt-get update && apt-get install -y gcc

# نسخ ملفات الباكند
COPY backend ./backend

# نسخ ملفات الواجهة المبنية
COPY --from=frontend /app/frontend/dist ./frontend-dist

# تثبيت مكتبات بايثون
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install sqlalchemy

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
