# DataDiff Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy project files
COPY . .

EXPOSE 8001

CMD ["datadiff", "serve", "--host", "0.0.0.0", "--port", "8001"]
