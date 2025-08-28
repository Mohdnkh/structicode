# Step 1: Build frontend
FROM node:20 AS frontend
WORKDIR /app/frontend

# نسخ ملفات الحزم والكونفيغ
COPY frontend/package*.json ./
COPY frontend/vite.config.js ./

# تثبيت الحزم
RUN npm install

# ✅ إصلاح esbuild
RUN npm uninstall esbuild && npm install esbuild@latest && npm rebuild esbuild

# نسخ باقي ملفات الواجهة
COPY frontend ./ 

# تشغيل build
RUN npm run build

# Step 2: Set up backend
FROM python:3.11-slim AS backend
WORKDIR /app

RUN apt-get update && apt-get install -y gcc

# نسخ requirements أولاً (للاستفادة من الـ cache)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات الباكند
COPY backend ./backend

# نسخ ملفات الواجهة المبنية
COPY --from=frontend /app/frontend/dist ./frontend-dist

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
