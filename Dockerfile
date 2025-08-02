# Step 1: Build frontend
FROM node:18 AS frontend
WORKDIR /app/frontend

# Install frontend dependencies
COPY frontend/package*.json ./
RUN npm install
RUN npm install -g vite

# Copy the rest of the frontend code and build it
COPY frontend ./
RUN npm run build

# Step 2: Set up backend
FROM python:3.11-slim AS backend
WORKDIR /app

# Install system dependencies for Python and uvicorn
RUN apt-get update && apt-get install -y gcc

# Copy backend and frontend build
COPY backend ./backend
COPY --from=frontend /app/frontend/dist ./frontend-dist

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and start FastAPI server
EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
