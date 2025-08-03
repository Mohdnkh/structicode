# Step 1: Build frontend
FROM node:18 AS frontend
WORKDIR /app/frontend

# Install frontend dependencies
COPY frontend/package*.json ./
RUN npm install
RUN npm install -g vite

# Copy frontend source code and build it
COPY frontend ./
RUN npm run build

# Step 2: Set up backend
FROM python:3.11-slim AS backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc

# Copy backend files
COPY backend ./backend

# ✅ Ensure font file is copied explicitly
COPY backend/api/utils/DejaVuSans.ttf backend/api/utils/DejaVuSans.ttf

# Copy built frontend
COPY --from=frontend /app/frontend/dist ./frontend-dist

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8000

# Run FastAPI app from backend/api/main.py (where app = FastAPI())
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
