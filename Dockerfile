# Step 1: Build frontend
FROM node:18 AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend ./
RUN npm run build

# Step 2: Setup backend (FastAPI)
FROM python:3.11 AS backend
WORKDIR /app
COPY backend ./backend
COPY --from=frontend /app/frontend/dist ./frontend-dist

# Install backend dependencies
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt

# Expose port and start server
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
