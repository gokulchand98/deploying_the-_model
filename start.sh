#!/bin/bash
set -e

echo "🚀 Starting Job Search Agent..."

# Ensure proper permissions and directories (Docker vs local)
if [ -w "/app" ]; then
    # Running in Docker container
    mkdir -p /app/config
    chmod 755 /app/config
    echo "✅ Docker environment detected"
else
    # Running locally
    mkdir -p ./config
    echo "✅ Local environment detected"
fi

# Railway injects PORT - must use exactly as provided
if [ -z "$PORT" ]; then
    echo "⚠️ PORT environment variable not set, using default 8000"
    export PORT=8000
else
    echo "✅ Using Railway PORT: $PORT"
fi

echo "📊 Environment setup:"
echo "  - Port: $PORT"
echo "  - Host: 0.0.0.0 (required for Railway)"
echo "  - OpenAI configured: $([ -n "$OPENAI_API_KEY" ] && echo "Yes" || echo "No")"
echo "  - Twilio configured: $([ -n "$TWILIO_ACCOUNT_SID" ] && echo "Yes" || echo "No")"

# Ensure we're starting FastAPI, not Streamlit
echo "🎯 Starting FastAPI uvicorn server for Railway deployment..."
echo "Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT"

# Unset any Streamlit environment variables that might interfere
unset STREAMLIT_SERVER_PORT
unset STREAMLIT_SERVER_ADDRESS

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info \
    --access-log \
    --loop asyncio