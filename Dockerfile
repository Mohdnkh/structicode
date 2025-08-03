FROM node:18 AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend ./
RUN npm run build

FROM python:3.11-slim AS backend
WORKDIR /app

RUN apt-get update && apt-get install -y gcc

COPY backend ./backend
COPY backend/api/utils/DejaVuSans.ttf ./backend/api/utils/DejaVuSans.ttf  
COPY --from=frontend /app/frontend/dist ./frontend-dist

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
