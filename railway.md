# Railway.app deployment configuration
# Just connect your GitHub repo to Railway and it will deploy automatically

# Environment Variables to set in Railway Dashboard:
# OPENAI_API_KEY=your_openai_key_here
# PORT=8000

# Railway will automatically detect the Dockerfile and deploy the backend
# For the frontend, create a separate Railway service with:
# Build Command: pip install streamlit requests
# Start Command: streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT