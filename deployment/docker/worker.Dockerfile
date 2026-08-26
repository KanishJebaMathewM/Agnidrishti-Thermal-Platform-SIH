# 3.14, not the spec's original 3.11: workers/requirements.txt and
# ml/requirements.txt are pinned to versions verified against Python 3.14
# (see the comments in those files) — some of those pins (numpy==2.5.2 in
# particular) have dropped 3.11 support entirely. README.md's stated
# prerequisite is "Python 3.11+", so 3.14 still satisfies it.
FROM python:3.14-slim

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
# just workers/requirements.txt. It also imports app.config (backend/) for
# the broker/backend URLs, which needs pydantic/pydantic-settings from
# backend/requirements.txt (found via a real ModuleNotFoundError at runtime).
COPY workers/requirements.txt ./workers-requirements.txt
COPY ml/requirements.txt ./ml-requirements.txt
COPY backend/requirements.txt ./backend-requirements.txt
RUN pip install --no-cache-dir -r workers-requirements.txt -r ml-requirements.txt -r backend-requirements.txt

# Copy the worker code as a nested `workers` package (celery_app.py's task
# list uses absolute imports like "workers.inference.inference_worker", which
# require a top-level `workers` package on sys.path — a flat `COPY workers/ .`
# put ingestion/, inference/, etc. directly at /app/ with no `workers` package
# at all, so those imports 404'd with ModuleNotFoundError: No module named
# 'workers'). celery_app.py is also copied to /app/celery_app.py so the CMD's
# `-A celery_app` (a bare top-level module name) still resolves.
COPY workers/ /app/workers/
COPY workers/celery_app.py /app/celery_app.py
COPY ml/ /app/ml/
COPY backend/ /app/backend/

# Ensure app runs with PYTHONPATH containing the current directory
ENV PYTHONPATH=/app:/app/backend

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
