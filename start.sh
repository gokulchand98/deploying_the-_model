#!/bin/bash
# Railway startup script

echo "🚀 Starting Job Search Agent..."
echo "Environment: $NODE_ENV"
echo "Port: ${PORT:-8000}"

# Create config directory if it doesn't exist
mkdir -p /app/config

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info