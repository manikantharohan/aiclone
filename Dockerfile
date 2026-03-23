# Root Dockerfile for Render deployment
# This builds the backend from the backend/ directory

FROM python:3.12-slim

WORKDIR /app

# Copy requirements from backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY backend/config.py .
COPY backend/main.py .
COPY backend/models/ models/
COPY backend/routes/ routes/
COPY backend/services/ services/
COPY backend/utils/ utils/

# Create startup script to handle PORT env var
RUN echo '#!/bin/sh\nuvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh && chmod +x /app/start.sh

# Non-root user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run with startup script
CMD ["/app/start.sh"]
