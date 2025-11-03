#!/bin/bash
# Quick deployment setup script

echo "🚀 Setting up your Job Search Agent for deployment..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git branch -M main
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Environment variables (keep your API key safe!)
.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.pytest_cache/
*.egg-info/

# SQLite database
*.db
app/jobs.db

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
EOF
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "🤖 Initial deployment: DE/MLOps/Cloud Job Search Agent

- FastAPI backend with job search and cover letter generation
- Streamlit UI for easy interaction  
- OpenAI integration for AI cover letters
- Docker deployment ready
- Specialized for Data Engineering, MLOps, Cloud roles"

echo "✅ Repository prepared for deployment!"
echo ""
echo "🌐 Next steps to go live:"
echo "1. Push to GitHub: git remote add origin https://github.com/yourusername/your-repo.git && git push -u origin main"
echo "2. Go to railway.app or render.com" 
echo "3. Connect your GitHub repo"
echo "4. Set OPENAI_API_KEY environment variable"
echo "5. Deploy and your agent will be live! 🚀"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"