# 🐍 استخدم Python slim
FROM python:3.11-slim

WORKDIR /app

# انسخ requirements من backend
COPY backend/requirements.txt .

# ثبّت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# انسخ كل المشروع
COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
