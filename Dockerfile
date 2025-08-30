# 🐍 استخدم Python slim
FROM python:3.11-slim

# اضبط مجلد العمل
WORKDIR /app

# انسخ requirements وثبتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# انسخ بقية المشروع
COPY . .

# افتح البورت
EXPOSE 8000

# ✅ شغل uvicorn على backend.api.main
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
