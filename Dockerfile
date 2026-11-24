# Multi-stage Dockerfile for OfferGraph on Google Cloud Run

# Stage 1: Build Frontend SPA
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend Container
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend application source
COPY backend/ ./backend/

# Copy compiled frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Cloud Run injects $PORT (default 8080)
ENV PORT=8080
ENV HOST=0.0.0.0
ENV ENVIRONMENT=production

EXPOSE 8080

# Seed database and start uvicorn
CMD ["sh", "-c", "python -m backend.app.seed && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
