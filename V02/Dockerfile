# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for CSV files
RUN mkdir -p /app/data

# Expose ports for Flask (5000) and FastAPI (8000)
EXPOSE 5000 8000

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting FastAPI service..."\n\
uvicorn fastapi_main:app --host 0.0.0.0 --port 8000 &\n\
echo "Starting Flask service..."\n\
python flask_app.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set the default command
CMD ["/app/start.sh"] 