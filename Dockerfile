# ====== Stage 1: Build frontend ======
FROM node:18 AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ====== Stage 2: Backend ======
FROM python:3.11

WORKDIR /app

# انسخ المتطلبات
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# انسخ كود backend
COPY backend/ ./backend

# انسخ frontend/dist من الستيج الأول
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# شغل FastAPI
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
