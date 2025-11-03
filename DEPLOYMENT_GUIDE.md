# 🚀 Deploy Your Job Search Agent Live

## 🏃‍♂️ Quick Deploy Options (Choose One)

### Option 1: 🚄 Railway (Recommended - Easiest)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial job search agent"
   git push origin main
   ```

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Set environment variables:
     - `OPENAI_API_KEY` = `your_api_key_here`
   - Railway auto-detects Dockerfile and deploys!

3. **Your agent will be live at**: `https://your-app-name.up.railway.app`

---

### Option 2: 🎨 Render.com

1. **Push to GitHub** (same as above)

2. **Deploy Backend**:
   - Go to [render.com](https://render.com)
   - New → Web Service → Connect GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables: `OPENAI_API_KEY=your_key`

3. **Deploy Frontend**:
   - New → Web Service (same repo)
   - Build Command: `pip install streamlit requests`  
   - Start Command: `streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT`
   - Environment Variables: `BACKEND_URL=https://your-backend-url.onrender.com`

---

### Option 3: ☁️ Streamlit Community Cloud (Frontend Only)

**For UI deployment:**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub and select your repository
3. Main file path: `streamlit_app.py`
4. Add secrets in settings:
   ```
   OPENAI_API_KEY = "your_api_key_here"
   BACKEND_URL = "your_backend_url_here"
   ```

**Note**: You'll need to deploy the backend separately (Railway/Render)

---

### Option 4: 🐳 Digital Ocean/AWS/GCP (Docker)

```bash
# Build and push to your container registry
docker build -t your-username/job-agent .
docker push your-username/job-agent

# Deploy on any cloud platform that supports Docker
# Set environment variable: OPENAI_API_KEY=your_key
```

---

## 🔧 Local Development/Testing

```bash
# Terminal 1 - Start Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Start Frontend  
BACKEND_URL=http://localhost:8000 streamlit run streamlit_app.py
```

**Access your agent**: 
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8501

---

## 🌍 Production Checklist

- [ ] **Environment Variables Set**:
  - `OPENAI_API_KEY` = Your OpenAI API key
  - `BACKEND_URL` = Your backend service URL (for frontend)

- [ ] **Domain & SSL** (Optional):
  - Most platforms provide free HTTPS domains
  - Can add custom domain later

- [ ] **Monitoring** (Optional):
  - Railway/Render provide basic monitoring
  - Add error tracking (Sentry) if needed

---

## 💡 Recommended Deployment Flow

1. **Start with Railway** (easiest, free tier)
2. **Test your live agent** with real job searches
3. **Monitor usage** and costs
4. **Scale up** to paid tiers or other platforms as needed

**Your agent will be fully live and accessible from anywhere in the world!** 🌐

## 🆘 Need Help?

- **Railway Issues**: Check their [docs](https://docs.railway.app)
- **Render Issues**: Check their [docs](https://render.com/docs)  
- **OpenAI API**: Monitor usage at [platform.openai.com](https://platform.openai.com)

**Next Steps**: Pick a deployment option above and make your agent live! 🚀