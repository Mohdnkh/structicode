# Step 1: Build frontend
FROM node:18 AS frontend
WORKDIR /app/frontend

# نسخ ملفات الباكج وتثبيت الحزم
COPY frontend/package*.json ./
RUN npm install

# نسخ باقي كود الواجهة
COPY frontend ./

# 🔥 شغّل vite مباشرة من node_modules بدل global
RUN chmod +x ./node_modules/.bin/vite && npm run build
RUN npm run build


# Step 2: Set up backend
FROM python:3.11-slim AS backend
WORKDIR /app

RUN apt-get update && apt-get install -y gcc

# نسخ ملفات الباكند
COPY backend ./backend

# نسخ frontend-dist المبني
COPY --from=frontend /app/frontend/dist ./frontend-dist

# تثبيت الحزم
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
