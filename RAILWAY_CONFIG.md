# 🚀 Railway Environment Configuration Guide

Your Job Search Agent is deployed successfully! Now let's configure the environment variables to enable all features.

## 📋 Required Environment Variables

### 1. **OpenAI API Key (Required for cover letters)**
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**How to get it:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

### 2. **Twilio Configuration (Optional - for SMS/Phone notifications)**
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
YOUR_PHONE_NUMBER=+1987654321
```

**How to get Twilio credentials:**
1. Sign up at https://www.twilio.com (free trial available)
2. Go to Console Dashboard
3. Copy Account SID and Auth Token
4. Get a phone number from Twilio Console

## 🔧 How to Add Environment Variables in Railway

### Method 1: Railway Dashboard
1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable name and value

### Method 2: Railway CLI
```bash
# Install Railway CLI if not installed
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Add variables
railway variables set OPENAI_API_KEY=your_key_here
railway variables set TWILIO_ACCOUNT_SID=your_sid_here
railway variables set TWILIO_AUTH_TOKEN=your_token_here
railway variables set TWILIO_PHONE_NUMBER=+1234567890
railway variables set YOUR_PHONE_NUMBER=+1987654321
```

## 🎯 Notification Thresholds (Optional)
```
SMS_THRESHOLD=15          # Send SMS when job score >= 15
CALL_THRESHOLD=30         # Make phone call when job score >= 30
```

## ✅ Testing After Configuration

1. **Update and run the test script:**
   ```bash
   # Edit test_live_api.py with your Railway URL
   python test_live_api.py
   ```

2. **Test job search with notifications:**
   ```bash
   curl -X POST "https://your-app.railway.app/api/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "data engineer",
       "limit": 5,
       "resume_text": "Experienced data engineer with Python and AWS skills",
       "enable_notifications": true
     }'
   ```

3. **Test cover letter generation:**
   ```bash
   curl -X POST "https://your-app.railway.app/api/cover_letter" \
     -H "Content-Type: application/json" \
     -d '{
       "resume_text": "Your resume content here",
       "job": {
         "title": "Senior Data Engineer",
         "company": "Tech Corp",
         "description": "Looking for data engineer with Python experience"
       }
     }'
   ```

## 🔥 What Works Now vs After Configuration

### ✅ **Working Now (No Config Needed):**
- Health checks (`/ping`, `/health`)
- Job searching without notifications
- Application tracking
- Rubrics management
- Basic API endpoints

### 🚀 **After OpenAI Configuration:**
- AI-powered cover letter generation
- Enhanced job descriptions
- Personalized application content

### 📱 **After Twilio Configuration:**
- SMS notifications for job matches
- Phone calls for high-priority matches
- Real-time alerts when good jobs are found

## 🎯 Your Railway Deployment URL

Find your URL in Railway dashboard or it looks like:
```
https://deploying-the-model-production.up.railway.app
```

## 🛠️ Troubleshooting

1. **If variables don't take effect:**
   - Railway redeploys automatically when you add variables
   - Wait 1-2 minutes for redeploy to complete

2. **If OpenAI doesn't work:**
   - Check API key format (should start with `sk-`)
   - Verify you have credits in your OpenAI account

3. **If Twilio doesn't work:**
   - Verify phone number format includes country code (+1 for US)
   - Check Twilio account has sufficient balance

Your job search agent is ready to help you find your next Data Engineering, MLOps, or Cloud role! 🎊