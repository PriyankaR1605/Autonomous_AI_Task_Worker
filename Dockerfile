FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HEADLESS_BROWSER=true
ENV PUBLIC_BASE_URL=https://autonomous-ai-task-worker.onrender.com

# Install system dependencies including Nginx and envsubst
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    ca-certificates \
    nginx \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browser and Linux OS dependencies
RUN playwright install --with-deps chromium

# Copy application source code
COPY . .

# Set executable permission for startup script
RUN chmod +x start.sh

# Initialize database and comprehensive enterprise company dataset
RUN python scripts/generate_company_data.py

# Expose ports
EXPOSE 8501 8000

# Start services via unified entrypoint
CMD ["bash", "start.sh"]
