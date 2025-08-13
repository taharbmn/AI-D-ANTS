FROM python:3.13-slim

WORKDIR /app

# Install dependencies including curl, Rust for pydantic-core, and PostgreSQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    pkg-config \
    postgresql-client \
    netcat-traditional \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Rust
ENV PATH="/root/.cargo/bin:${PATH}"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application directory
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/logs && \
    chmod -R 755 /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Expose the port
EXPOSE 8080

# Copy and set permissions for startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# commande to alwase runed comme while 1
# CMD ["sh", "-c", "while :; do sleep 6; done"]

# Run with startup script that handles migrations and server startup
CMD ["bash", "/start.sh"]


