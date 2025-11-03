# 🎯 Agent Rubrics System - Customization Guide

## Overview
Your job search agent now uses a flexible **rubrics system** that allows you to completely customize how it behaves. You can set specific criteria for job scoring, cover letter generation, and application decisions.

## 🔧 How to Customize Your Agent

### Method 1: 🌐 Web Interface (Easiest)
1. Open your deployed Streamlit app
2. Scroll to **"Agent Behavior Configuration"**  
3. Use **"Update Agent Instructions"** to give natural language commands
4. Test your changes with **"Test Job Scoring"**

### Method 2: 📝 Direct Instructions
Send natural language instructions to customize behavior:

**Job Prioritization Examples:**
```
• "Prioritize senior and staff level roles over junior positions"
• "Focus on companies with strong engineering culture like Netflix, Spotify, Uber"
• "Prefer remote-first companies, avoid on-site only positions"
• "Only consider jobs mentioning Kubernetes, Docker, and cloud platforms"
• "Avoid companies with less than 50 employees"
```

**Cover Letter Style Examples:**
```  
• "Make cover letters more casual and enthusiastic"
• "Keep cover letters short and to the point"
• "Always mention my startup experience and equity interest"
• "Focus on quantifiable achievements and specific technologies"
• "Use a confident, senior engineer tone"
```

**Application Criteria Examples:**
```
• "Auto-apply only to jobs scoring 30+ points"
• "Never apply to positions mentioning 'junior' or 'entry level'"
• "Require salary range to be mentioned in job description"  
• "Skip companies known for poor work-life balance"
```

## 🎯 Current Default Rubrics

### Job Scoring Weights
**High Priority Keywords (Title):**
- Principal/Staff Data Engineer: 22-25 points
- Senior Data Engineer: 20 points  
- MLOps Engineer: 18 points
- Cloud/Platform Engineer: 14-16 points

**Technical Skills (Description):**
- Apache Spark, Kubernetes: 8 points each
- Kafka, Airflow, Terraform: 7 points each
- AWS/Azure/GCP, Docker: 6 points each
- Python, Scala: 4-5 points each

**Company Preferences:**
- Netflix, Google, Spotify: +5 points
- Meta, Microsoft, Uber: +4 points

**Location Preferences:**
- Remote: +8 points
- Hybrid: +5 points
- Major tech hubs: +3-4 points

### Application Thresholds
- **Minimum Score**: 8 points (to show in results)
- **Auto-Apply Score**: 25+ points (very selective)
- **Required Keywords**: Must mention "data", "engineering", "cloud", or "ml"
- **Blacklist**: Avoids "unpaid", "internship", "entry level"

## 📊 Scoring Examples

**Example 1: "Senior Data Engineer - Netflix"**
- Title match: +20 points
- Company bonus: +5 points  
- Description with Spark, Kafka: +15 points
- Remote: +8 points
- **Total: 48 points** ✅ Auto-apply candidate

**Example 2: "Junior Data Analyst - Small Startup"**
- Blacklisted "junior": Filtered out
- **Result**: Not shown in results

**Example 3: "Cloud Engineer - Microsoft"**  
- Title match: +16 points
- Company bonus: +4 points
- Kubernetes + Docker: +14 points
- **Total: 34 points** ✅ High priority, manual review

## 🚀 Advanced Customization

### API Endpoints
- `GET /api/rubrics` - View current configuration
- `POST /api/rubrics/update` - Update with instructions  
- `POST /api/jobs/score` - Test job scoring

### Direct File Editing
Advanced users can edit `config/rubrics.json` directly:

```json
{
  "job_scoring": {
    "title_keywords": {"senior data engineer": 20},
    "company_preferences": {"netflix": 5},
    "min_score_threshold": 10
  },
  "cover_letter": {
    "tone": "professional",
    "focus_areas": ["technical_skills", "achievements"]
  }
}
```

## 🎯 Rubrics Best Practices

1. **Start Conservative**: Begin with high thresholds, lower as needed
2. **Test Regularly**: Use the scoring tool to validate changes
3. **Be Specific**: "Senior roles at tech companies" vs "good jobs"  
4. **Monitor Results**: Check if changes improve job quality
5. **Iterate**: Refine based on actual job search results

## 💡 Pro Tips

- **Salary Filtering**: Add salary keywords to required/blacklist terms
- **Company Research**: Prioritize companies with good Glassdoor ratings
- **Skills Evolution**: Update technical keywords as you learn new technologies  
- **Market Adaptation**: Adjust scoring based on job market conditions
- **A/B Testing**: Try different cover letter tones and measure response rates

## 🆘 Troubleshooting

**Problem**: No jobs showing up
- **Solution**: Lower `min_score_threshold` or expand keywords

**Problem**: Too many irrelevant jobs  
- **Solution**: Increase scoring weights for important keywords

**Problem**: Cover letters too generic
- **Solution**: Add more specific `custom_instructions`

**Problem**: Missing good opportunities
- **Solution**: Review and expand `title_keywords` and `description_keywords`

---

**🎯 Your agent learns from your instructions and adapts to find exactly the opportunities you want!**