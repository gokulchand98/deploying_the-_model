"""A tiny Streamlit UI to interact with the Job Search Agent backend."""
import streamlit as st
import requests
import os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="DE/MLOps/Cloud Job Agent", layout="wide")
st.title("🚀 Data Engineering & MLOps Job Search Agent")

with st.sidebar:
    st.header("👤 Your Profile")
    resume_text = st.text_area("Paste your resume / technical summary here", height=300, 
                              placeholder="Include your experience with data pipelines, cloud platforms, ML systems, etc.")
    
    st.header("🔧 Configuration")
    st.write("Set `BACKEND_URL` env to point to running backend if needed.")
    st.write("Set `OPENAI_API_KEY` env for AI-generated cover letters.")

# Job search with predefined options
st.header("🔍 Find Your Next Role")
col1, col2 = st.columns([3, 1])

with col1:
    search_option = st.selectbox(
        "Job Type Priority",
        ["All Priority Jobs (DE/MLOps/Cloud)", "Data Engineering", "MLOps & ML Engineering", "Cloud & DevOps Engineering", "Custom Search"]
    )
    
    if search_option == "Custom Search":
        query = st.text_input("Custom search query")
    else:
        query_map = {
            "All Priority Jobs (DE/MLOps/Cloud)": "data engineer OR mlops OR cloud engineer OR devops",
            "Data Engineering": "data engineer OR data engineering OR etl OR data pipeline",
            "MLOps & ML Engineering": "mlops OR ml engineer OR machine learning engineer OR model deployment",
            "Cloud & DevOps Engineering": "cloud engineer OR devops OR aws OR azure OR kubernetes"
        }
        query = query_map.get(search_option, "")
        st.info(f"Searching for: {query}")

with col2:
    st.write("")  # spacing
    st.write("")  # spacing
if st.button("🔍 Search Jobs", type="primary") and query:
    with st.spinner("Searching for DE/MLOps/Cloud opportunities..."):
        try:
            resp = requests.post(f"{BACKEND}/api/search", json={"query": query, "limit": 15})
            if resp.status_code == 200:
                data = resp.json()
                jobs = data.get("jobs", [])
                st.success(f"Found {len(jobs)} relevant jobs (sorted by relevance)")
                
                for j in jobs:
                    relevance = j.get('relevance_score', 0)
                    priority_badge = "🔥 HIGH PRIORITY" if relevance >= 10 else "⭐ RELEVANT" if relevance >= 3 else ""
                    
                    with st.expander(f"{priority_badge} {j.get('title')} @ {j.get('company')} (Score: {relevance})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"📍 **Location:** {j.get('location', 'Not specified')}")
                            if j.get('url'):
                                st.write(f"🔗 [View Job Posting]({j.get('url')})")
                            
                            # Show job description
                            desc = j.get('description', '')
                            if len(desc) > 1000:
                                st.write(desc[:1000] + "...")
                            else:
                                st.write(desc)
                        
                        with col2:
                            if st.button("🤖 Generate Cover Letter", key=f"gen-{j.get('id')}"):
                                if not resume_text:
                                    st.warning("Please paste your resume in the sidebar first!")
                                else:
                                    with st.spinner("Generating personalized cover letter..."):
                                        r = requests.post(f"{BACKEND}/api/cover_letter", 
                                                        json={"job": j, "resume_text": resume_text})
                                        if r.status_code == 200:
                                            st.success("✅ Cover letter generated!")
                                            st.text_area("Your Cover Letter", 
                                                       value=r.json().get('cover_letter'), 
                                                       height=400, key=f"cover-{j.get('id')}")
                                        else:
                                            st.error(f"Error generating cover letter: {r.text}")
                            
                            if st.button("✅ Mark as Applied", key=f"applied-{j.get('id')}"):
                                r = requests.post(f"{BACKEND}/api/apply", 
                                                json={"job": j, "notes": f"Applied via Job Agent - Relevance Score: {relevance}"})
                                if r.status_code == 200:
                                    st.success("Application tracked!")
                                else:
                                    st.error(f"Error: {r.text}")
            else:
                st.error(f"Search failed: {resp.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            st.info("Make sure the backend is running on the configured BACKEND_URL")


st.header("📊 Application Tracker")
if st.button("📋 Show My Applications", type="secondary"):
    try:
        r = requests.get(f"{BACKEND}/api/applications")
        if r.status_code == 200:
            apps = r.json().get('applications', [])
            if apps:
                st.write(f"**Total Applications:** {len(apps)}")
                for a in apps:
                    with st.expander(f"{a.get('job_title')} @ {a.get('company')} - {a.get('applied_at')}"):
                        st.write(f"**Application ID:** {a.get('id')}")
                        st.write(f"**Job ID:** {a.get('job_id', 'N/A')}")
                        st.write(f"**Notes:** {a.get('notes', 'No notes')}")
            else:
                st.info("No applications tracked yet. Start searching and applying!")
        else:
            st.error("Failed to fetch applications")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
