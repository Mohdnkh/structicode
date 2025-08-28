# =========================
# Backend فقط (مع نسخة frontend-dist جاهزة)
# =========================
FROM python:3.11-slim AS backend
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# نسخ requirements أولاً (للاستفادة من الـ cache)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات الباكند
COPY backend ./backend

# نسخ نسخة الواجهة الجاهزة (prebuilt) 
COPY frontend-dist ./frontend-dist

# فتح البورت
EXPOSE 8000

# تشغيل التطبيق
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
