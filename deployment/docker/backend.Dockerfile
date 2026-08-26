# 3.14, not the spec's original 3.11 — see worker.Dockerfile: this image
# installs the same ml/workers requirements, pinned to versions that dropped
# 3.11 support (numpy==2.5.2 in particular). README.md's stated prerequisite
# is "Python 3.11+", so 3.14 still satisfies it.
FROM python:3.14-slim

# Same system deps as worker.Dockerfile: backend/app/api/routes/model.py now
# imports workers.inference.inference_worker, which imports ml/ at module
# level (geopandas/shapely/h3 need GDAL/PROJ; xgboost/scikit-learn need none
# of these, but installing alongside the rest is simplest and matches worker).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    libnetcdf-dev \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

# Copy requirements and install. backend/app/api/routes/model.py imports
# workers.inference.inference_worker (ml/ + workers/ requirements needed too).
COPY backend/requirements.txt ./backend-requirements.txt
COPY workers/requirements.txt ./workers-requirements.txt
COPY ml/requirements.txt ./ml-requirements.txt
RUN pip install --no-cache-dir -r backend-requirements.txt -r workers-requirements.txt -r ml-requirements.txt

# Copy the application, plus workers/ and ml/ (imported by
# backend/app/api/routes/model.py via workers.inference.inference_worker).
COPY backend/ .
COPY workers/ /app/workers/
COPY ml/ /app/ml/

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
