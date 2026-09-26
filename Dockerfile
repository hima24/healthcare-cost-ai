# Single-container deploy: FastAPI backend + static frontend, for Cloud Run
FROM python:3.11-slim

WORKDIR /app

# Install Python deps first (better layer caching)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy app code
COPY backend ./backend
COPY frontend ./frontend

# Cloud Run injects PORT at runtime; default to 8080 for local `docker run`
ENV PORT=8080
EXPOSE 8080

WORKDIR /app/backend
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
