# 📱 SMS & Phone Call Notifications Setup

## 🎯 What Your Agent Will Do

- **📱 SMS Alerts**: Get text messages for jobs scoring 15+ points
- **📞 Phone Calls**: Get called for jobs scoring 30+ points OR high resume matches
- **🎯 Smart Matching**: Resume analysis to find jobs that specifically match your skills
- **🔔 Real-time Notifications**: Instant alerts as soon as good jobs are found

## 🚀 Quick Setup (5 minutes)

### Step 1: Get Twilio Account (Free)
1. Go to **https://www.twilio.com/try-twilio**
2. Sign up for free account (includes $15 credit)
3. Verify your phone number
4. Get a Twilio phone number (free)

### Step 2: Get Your Credentials
1. In Twilio Console, find:
   - **Account SID** (starts with AC...)
   - **Auth Token** (click to reveal)
   - **Your Twilio Phone Number** (+1...)

### Step 3: Configure Environment Variables

**For Railway Deployment:**
1. Go to Railway dashboard → Your project → Variables
2. Add these environment variables:
   ```
   TWILIO_ACCOUNT_SID=AC1234567890abcdef...
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+15551234567
   YOUR_PHONE_NUMBER=+15559876543
   ```

**For Local Development:**
1. Copy `.env.example` to `.env`
2. Fill in your Twilio credentials

## 🎛️ Notification Settings

### Thresholds (Customizable)
- **SMS_THRESHOLD=15**: Send SMS for jobs scoring 15+ points
- **CALL_THRESHOLD=30**: Make phone calls for jobs scoring 30+ points

### What Triggers Notifications

**SMS Notifications (15+ points):**
- Jobs with relevant titles (Data Engineer, MLOps, etc.)
- Jobs mentioning your tech stack (Spark, Kubernetes, AWS)
- Jobs at preferred companies
- Remote positions

**Phone Call Notifications (30+ points OR high resume match):**
- Senior/Staff/Principal level positions
- Jobs at top-tier companies
- Jobs with 5+ technology matches from your resume
- High-paying roles (if salary mentioned)

## 📱 Example Notifications

**SMS Alert:**
```
🎯 Job Match Alert!

📋 Senior Data Engineer
🏢 Netflix
📍 Remote
⭐ Score: 42/100
🔗 https://jobs.netflix.com/...

Check your agent dashboard!
```

**Phone Call:**
```
"High priority job match found! Senior Data Engineer at Netflix. 
Job score: 42. Resume match: 85. Check your job agent dashboard 
for details."
```

## 🧪 Testing Your Setup

### In Streamlit UI:
1. Go to **"Agent Behavior Configuration"**
2. Expand **"Test Notifications"** 
3. Click **"Test All Notifications"**
4. You should receive test SMS and call

### Via API:
```bash
# Test notifications
curl -X POST "your-app-url/api/notifications/test"

# Check status
curl "your-app-url/api/notifications/status"
```

## 🎯 Smart Features

### Resume Matching
- Agent analyzes your resume for skills/technologies
- Calculates match percentage with job descriptions
- Calls you for jobs that specifically match your experience

### Notification Intelligence
- Won't spam you with low-quality matches
- Higher thresholds for calls vs SMS
- Includes job score and reasoning in messages

### Daily Summaries
- Optional daily SMS with job search stats
- "Jobs Found: 12 | Applications: 3"

## 💰 Costs

**Twilio Pricing (Very Cheap):**
- SMS: ~$0.0075 per message
- Phone calls: ~$0.013 per minute  
- With $15 free credit = ~2000 SMS or ~1150 minutes of calls

**Example Monthly Usage:**
- 50 job matches → 50 SMS = $0.375
- 5 high-priority calls → 5 calls = $0.065
- **Total: ~$0.44/month** 📈

## 🛠️ Customization Options

### Environment Variables
```bash
# Notification thresholds
SMS_THRESHOLD=15        # Lower = more SMS
CALL_THRESHOLD=30       # Lower = more calls

# Phone numbers (E.164 format)
TWILIO_PHONE_NUMBER=+15551234567
YOUR_PHONE_NUMBER=+15559876543
```

### Advanced Rubrics
Use the agent's rubrics system to customize:
- Which companies trigger calls
- Technology keywords that boost scores  
- Experience level preferences
- Location and salary filtering

## 🆘 Troubleshooting

**No notifications received:**
- Check phone numbers are in E.164 format (+1...)
- Verify Twilio credentials in dashboard
- Test with "Test Notifications" button

**SMS works but calls fail:**
- Check if your number is verified in Twilio
- Ensure you have call credits remaining  
- Try with a different phone number

**Getting too many notifications:**
- Increase SMS_THRESHOLD and CALL_THRESHOLD
- Update rubrics to be more selective
- Add companies to blacklist

**Not getting enough notifications:**
- Lower the thresholds
- Expand keyword lists in rubrics
- Check if resume text is provided

## 📞 Support

- **Twilio Issues**: https://help.twilio.com
- **Agent Configuration**: Use the admin UI in Streamlit
- **API Testing**: Check `/api/notifications/status` endpoint

**🎉 You're now set up for intelligent job notifications! Your agent will call and text you about the best opportunities.** 📱✨