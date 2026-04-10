# Use Python 3.12 slim line for smaller image footprint and performance
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Upgrade pip and install dependencies
# We copy only requirements first to cache dependency layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy internal application codebase
COPY app/ ./app/

# Port exposure purely for container documentation
EXPOSE 8000

# Invoke standard production process
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
