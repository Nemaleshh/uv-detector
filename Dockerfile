FROM python:3.11-slim

WORKDIR /app

# Fix apt-get issues and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --default-timeout=100 flask==3.0.0 && \
    pip install --no-cache-dir --default-timeout=100 flask-cors==4.0.0 && \
    pip install --no-cache-dir --default-timeout=100 opencv-python-headless==4.8.1.78 && \
    pip install --no-cache-dir --default-timeout=100 numpy==1.24.3 && \
    pip install --no-cache-dir --default-timeout=100 gunicorn==21.2.0 && \
    pip install --no-cache-dir --default-timeout=100 python-dotenv==1.0.0 && \
    pip install --no-cache-dir --default-timeout=100 requests==2.31.0

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=5000
ENV RENDER_FREE_TIER=true
ENV PYTHONUNBUFFERED=1

# Run with gunicorn (1 worker for free tier memory limit)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "--keep-alive", "5", "--max-requests", "500", "app:create_app()"]
