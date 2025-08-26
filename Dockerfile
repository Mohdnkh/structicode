# Step 1: Build frontend
FROM node:18 AS frontend
WORKDIR /app/frontend

# نسخ package.json و vite.config.js وكل ما يلزم
COPY frontend/package*.json ./
COPY frontend/vite.config.js ./

# تثبيت الحزم
RUN npm install

# نسخ باقي ملفات الواجهة (بما فيها src و public)
COPY frontend ./ 

# منح صلاحية تنفيذ لـ vite وتشغيل build
RUN chmod +x ./node_modules/.bin/vite && npm run build

# Step 2: Set up backend
FROM python:3.11-slim AS backend
WORKDIR /app

# أدوات ضرورية للـ pip
RUN apt-get update && apt-get install -y gcc

# نسخ ملفات الباكند
COPY backend ./backend

# نسخ ملفات الواجهة المبنية
COPY --from=frontend /app/frontend/dist ./frontend-dist

# تثبيت مكتبات البايثون
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# فتح البورت
EXPOSE 8000

# 🚀 تشغيل التطبيق FastAPI من main.py داخل backend/api
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
