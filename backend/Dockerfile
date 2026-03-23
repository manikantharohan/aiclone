# backend/Dockerfile — production-ready AI chatbot backend
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY config.py .
COPY main.py .
COPY models/ models/
COPY routes/ routes/
COPY services/ services/
COPY utils/ utils/

# Non-root user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run with uvicorn (no --reload in production)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
