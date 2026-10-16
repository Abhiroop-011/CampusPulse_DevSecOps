# ==============================================================================
# CampusPulse Backend Dockerfile
# Python 3.12 Slim with non-root security context (UID 10001)
# ==============================================================================
FROM python:3.12-slim

# Set working directory and unbuffered python environment
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install dependencies and create dedicated non-root application user
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd -g 10001 appuser \
    && useradd -u 10001 -g appuser -s /bin/bash -m appuser \
    && chown -R appuser:appuser /app

# Copy Alembic configuration, migrations, and application code
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser alembic ./alembic
COPY --chown=appuser:appuser app ./app

# Drop root privileges
USER 10001

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run migrations then start uvicorn ASGI server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
