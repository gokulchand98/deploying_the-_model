#!/bin/bash

# Quick API Test Script for Railway Deployed Job Search Agent
# Usage: ./quick_test.sh https://your-app.railway.app

RAILWAY_URL=${1:-"https://your-app-name.up.railway.app"}

echo "🚀 Testing Job Search Agent API at: $RAILWAY_URL"
echo "================================================="

# Test 1: Health Check
echo "1️⃣ Health Check:"
curl -s "$RAILWAY_URL/ping" | head -c 200
echo -e "\n"

# Test 2: Root Endpoint
echo "2️⃣ Root Endpoint:"
curl -s "$RAILWAY_URL/" | jq . 2>/dev/null || curl -s "$RAILWAY_URL/"
echo -e "\n"

# Test 3: Priority Job Search (no auth required)
echo "3️⃣ Priority Job Search:"
curl -s "$RAILWAY_URL/api/search/priority?limit=2" | jq '.jobs | length' 2>/dev/null || echo "Response received"
echo -e "\n"

# Test 4: Application Tracking
echo "4️⃣ Application Tracking:"
curl -s "$RAILWAY_URL/api/applications" | jq '.applications | length' 2>/dev/null || echo "Response received"
echo -e "\n"

# Test 5: Notification Status
echo "5️⃣ Notification Status:"
curl -s "$RAILWAY_URL/api/notifications/status" | jq . 2>/dev/null || curl -s "$RAILWAY_URL/api/notifications/status"
echo -e "\n"

echo "✅ Quick test complete!"
echo "📝 For detailed testing, use: python test_live_api.py"