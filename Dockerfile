# Provider-neutral production image. The final stage contains only the ASGI
# runtime, compiled frontend assets, migrations, and required application code.
FROM node:20-bookworm-slim AS frontend-build

WORKDIR /build
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package.json
RUN npm ci --no-audit --no-fund
COPY frontend ./frontend
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    STRUCTICODE_RUNTIME_MODE=production

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
COPY scripts/start_production.py ./scripts/start_production.py
COPY scripts/production_preflight.py ./scripts/production_preflight.py

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "scripts/start_production.py"]
