# 🚀 Data Engineering & MLOps Job Search Agent

**Specialized job search agent for Data Engineering, MLOps, and Cloud Engineering roles.**

This end-to-end application automatically finds relevant technical jobs, generates personalized cover letters using AI, and tracks your applications.

## 🎯 Key Features

- **Smart Job Discovery**: Prioritizes DE/MLOps/Cloud roles using keyword scoring
- **AI Cover Letters**: Uses OpenAI GPT-4o-mini to generate tailored technical cover letters
- **Application Tracking**: SQLite database to track all your job applications
- **Web Interface**: Clean Streamlit UI for easy interaction
- **Deployment Ready**: Docker containerization for cloud deployment

Components:
- FastAPI backend (`app/main.py`) exposing endpoints:
  - `POST /api/search` — search jobs (uses Remotive public API)
  - `POST /api/cover_letter` — generate a cover letter (uses OpenAI if configured)
  - `POST /api/apply` — record an application in a local SQLite DB
  - `GET /api/applications` — list recorded applications
- Streamlit UI (`streamlit_app.py`) for quick browser interaction
- Simple SQLite DB (`app/jobs.db`) created automatically on startup
- Dockerfile to build an image and run the backend

Quick start (local, recommended):

1. Create a virtualenv and install dependencies (macOS / zsh):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Set up OpenAI API** (Required for AI cover letters):
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`

3. Start the backend API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

4. In another terminal, start the Streamlit UI:

```bash
export BACKEND_URL=http://127.0.0.1:8000
streamlit run streamlit_app.py
```

5. Use the Streamlit UI to search for jobs, generate draft cover letters, and mark applications.

Docker (optional):

Build the image and run:

```bash
docker build -t job-agent:latest .
docker run -p 8000:8000 --env OPENAI_API_KEY="$OPENAI_API_KEY" job-agent:latest
```

Notes and next steps:
- The job search uses the public Remotive API. You can add additional connectors (LinkedIn, Indeed, company APIs).
- Review `app/agent.py` to tweak the prompt for cover letters.
- Add authentication, rate-limiting, and deployment CI as you move to production.

License: MIT
