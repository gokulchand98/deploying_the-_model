#!/bin/bash
set -e

echo "🚀 Starting Job Search Agent..."

# Ensure proper permissions and directories
mkdir -p /app/config
chmod 755 /app/config

# Export environment variables with defaults
export PORT=${PORT:-8000}
export OPENAI_API_KEY=${OPENAI_API_KEY:-""}

echo "📊 Environment setup:"
echo "  - Port: $PORT"
echo "  - OpenAI configured: $([ -n "$OPENAI_API_KEY" ] && echo "Yes" || echo "No")"
echo "  - Twilio configured: $([ -n "$TWILIO_ACCOUNT_SID" ] && echo "Yes" || echo "No")"

# Start the application
echo "🎯 Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info