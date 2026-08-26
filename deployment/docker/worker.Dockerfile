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

# Copy requirements and install. workers/celery_app.py registers the ML
# inference task (workers.inference.inference_worker), which imports from
# ml/ at module level — so this image needs ml/requirements.txt too, not
# just workers/requirements.txt.
COPY workers/requirements.txt ./workers-requirements.txt
COPY ml/requirements.txt ./ml-requirements.txt
RUN pip install --no-cache-dir -r workers-requirements.txt -r ml-requirements.txt

# Copy the worker code, plus ml/ (imported by workers.inference.inference_worker)
# and backend/ (celery_app.py imports app.config for the broker/backend URLs).
COPY workers/ .
COPY ml/ /app/ml/
COPY backend/ /app/backend/

# Ensure app runs with PYTHONPATH containing the current directory
ENV PYTHONPATH=/app:/app/backend

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
