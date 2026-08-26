FROM python:3.11-slim

# Install system dependencies for geospatial packages and database connections
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    libnetcdf-dev \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL compilation/headers
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

# Copy requirements and install
COPY workers/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the worker code
COPY workers/ .
COPY backend/ /app/backend/

# Ensure app runs with PYTHONPATH containing the current directory
ENV PYTHONPATH=/app:/app/backend

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
