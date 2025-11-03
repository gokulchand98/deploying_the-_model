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
    
    st.header("� Notification Settings")
    enable_notifications = st.checkbox("Enable SMS/Call Notifications", help="Get notified about high-scoring job matches")
    
    if enable_notifications:
        # Check notification status
        try:
            status_resp = requests.get(f"{BACKEND}/api/notifications/status")
            if status_resp.status_code == 200:
                status = status_resp.json()
                if status["configured"]:
                    st.success("✅ Notifications configured!")
                    st.info(f"📱 SMS threshold: {status['sms_threshold']}+ points")
                    st.info(f"📞 Call threshold: {status['call_threshold']}+ points")
                else:
                    st.warning("⚠️ Configure Twilio credentials in environment variables")
            else:
                st.error("Failed to check notification status")
        except:
            st.error("Backend connection error")
    
    st.header("�🔧 Configuration")
    st.write("Set `BACKEND_URL` env to point to running backend if needed.")
    st.write("Set `OPENAI_API_KEY` env for AI-generated cover letters.")
    if enable_notifications:
        st.write("Set Twilio credentials for notifications:")
        st.code("""
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token  
TWILIO_PHONE_NUMBER=+1234567890
YOUR_PHONE_NUMBER=+1234567890
        """)

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
            search_payload = {
                "query": query, 
                "limit": 15,
                "resume_text": resume_text if enable_notifications else "",
                "enable_notifications": enable_notifications
            }
            resp = requests.post(f"{BACKEND}/api/search", json=search_payload)
            if resp.status_code == 200:
                data = resp.json()
                jobs = data.get("jobs", [])
                st.success(f"Found {len(jobs)} relevant jobs (sorted by relevance)")
                
                for j in jobs:
                    relevance = j.get('relevance_score', 0)
                    resume_match = j.get('resume_match_score', 0)
                    notification_sent = j.get('notification_sent', {})
                    
                    # Enhanced priority badges
                    priority_badge = "🔥 HIGH PRIORITY" if relevance >= 10 else "⭐ RELEVANT" if relevance >= 3 else ""
                    if notification_sent.get('call_made'):
                        priority_badge += " 📞 CALLED"
                    elif notification_sent.get('sms_sent'):
                        priority_badge += " 📱 SMS SENT"
                    
                    score_display = f"Job: {relevance}"
                    if resume_match > 0:
                        score_display += f" | Resume: {resume_match}"
                    
                    with st.expander(f"{priority_badge} {j.get('title')} @ {j.get('company')} ({score_display})"):
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

# Agent Configuration Section
st.header("🤖 Agent Behavior Configuration")

with st.expander("📋 View Current Rubrics"):
    if st.button("Refresh Rubrics"):
        try:
            r = requests.get(f"{BACKEND}/api/rubrics")
            if r.status_code == 200:
                rubrics_data = r.json()
                st.json(rubrics_data)
            else:
                st.error("Failed to fetch rubrics")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")

with st.expander("✏️ Update Agent Instructions"):
    st.write("**Customize how your agent behaves by providing natural language instructions:**")
    
    st.write("**Examples:**")
    st.code("""
• "Prioritize senior roles over junior roles"
• "Avoid companies with less than 100 employees"  
• "Focus on remote-first companies"
• "Prefer jobs mentioning Kubernetes and Docker"
• "Make cover letters more casual and enthusiastic"
• "Only apply to jobs with salary > $150k"
    """)
    
    custom_instructions = st.text_area(
        "Your Instructions", 
        placeholder="e.g., 'Prioritize jobs at startups with strong engineering culture. Focus on roles with equity compensation. Make cover letters highlight my startup experience.'",
        height=150
    )
    
    if st.button("🔄 Update Agent Behavior") and custom_instructions:
        with st.spinner("Updating agent behavior..."):
            try:
                r = requests.post(f"{BACKEND}/api/rubrics/update", 
                                json={"instructions": custom_instructions})
                if r.status_code == 200:
                    st.success("✅ Agent behavior updated!")
                    st.info(r.json().get('message'))
                else:
                    st.error(f"Update failed: {r.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

with st.expander("🧪 Test Job Scoring"):
    st.write("**Test how your agent would score a specific job:**")
    
    test_title = st.text_input("Job Title", placeholder="Senior Data Engineer")
    test_company = st.text_input("Company", placeholder="Netflix")  
    test_location = st.text_input("Location", placeholder="Remote")
    test_description = st.text_area("Job Description", placeholder="Build data pipelines using Spark and Kafka...", height=100)
    
    if st.button("🔍 Score This Job") and test_title:
        test_job = {
            "title": test_title,
            "company": test_company,
            "location": test_location,
            "description": test_description
        }
        
        try:
            r = requests.post(f"{BACKEND}/api/jobs/score", json=test_job)
            if r.status_code == 200:
                score_data = r.json()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📊 Score", score_data['score'])
                with col2:
                    st.metric("✅ Meets Threshold", "Yes" if score_data['meets_threshold'] else "No")
                with col3:
                    st.metric("🤖 Auto-Apply", "Yes" if score_data['should_auto_apply'] else "No")
            else:
                st.error(f"Scoring failed: {r.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")

with st.expander("📱 Test Notifications"):
    st.write("**Test your SMS and phone call setup:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 Test All Notifications"):
            with st.spinner("Testing notifications..."):
                try:
                    r = requests.post(f"{BACKEND}/api/notifications/test")
                    if r.status_code == 200:
                        results = r.json()["test_results"]
                        if results["configured"]:
                            st.success("✅ Twilio configured")
                            if results["sms_test"]:
                                st.success("📱 SMS test sent!")
                            else:
                                st.error("❌ SMS test failed")
                            if results["call_test"]:
                                st.success("📞 Call test initiated!")
                            else:
                                st.error("❌ Call test failed")
                        else:
                            st.warning("⚠️ Notifications not configured")
                    else:
                        st.error("Test failed")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
    
    with col2:
        # Manual notification test
        test_message = st.text_input("Custom Test Message", placeholder="Test message from job agent")
        notification_type = st.selectbox("Notification Type", ["sms", "call"])
        
        if st.button("📤 Send Test") and test_message:
            try:
                r = requests.post(f"{BACKEND}/api/notifications/send", 
                                json={"message": test_message, "type": notification_type})
                if r.status_code == 200 and r.json()["success"]:
                    st.success(f"✅ {notification_type.upper()} sent!")
                else:
                    st.error("❌ Send failed")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
