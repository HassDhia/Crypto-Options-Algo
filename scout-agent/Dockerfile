# Build stage for common module
FROM python:3.10-slim as builder

# Install system dependencies for snappy
RUN apt-get update && apt-get install -y \
    libsnappy-dev \
    python3-snappy \
    && rm -rf /var/lib/apt/lists/*

# Copy entire project to access common module
WORKDIR /build
COPY . .

# Install dependencies from root requirements.txt
RUN pip install --no-cache-dir -r /build/requirements.txt

# Final stage
FROM python:3.10-slim

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy common module
COPY --from=builder /build/common /app/common

# Copy scout-agent code
COPY ./scout-agent/ /app/

CMD ["python", "-u", "/app/__main__.py"]
