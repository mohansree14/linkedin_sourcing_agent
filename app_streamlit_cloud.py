"""
LinkedIn Sourcing Agent - Streamlit Cloud Version
Simplified deployment-ready version for Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import json
import asyncio
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import io
import random

# Page configuration
st.set_page_config(
    page_title="LinkedIn Sourcing Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #0066cc;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .candidate-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f9f9f9;
    }
    .demo-banner {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Demo Mode Classes
class LinkedInSourcingAgent:
    def __init__(self):
        pass
    
    async def search_candidates(self, query, location=None, limit=10):
        # Return demo candidates
        demo_candidates = []
        companies = ['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta', 'Netflix', 'Tesla', 'Uber', 'Airbnb', 'Spotify']
        locations = ['San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX', 'Boston, MA', 'Chicago, IL', 'Los Angeles, CA', 'Denver, CO']
        skills_pool = ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes', 'Machine Learning', 'Data Science', 'SQL', 'MongoDB', 'Redis', 'GraphQL', 'TypeScript', 'Java', 'C++', 'Go', 'Rust']
        
        for i in range(min(limit, 10)):
            demo_candidates.append({
                'name': f'Alex Johnson {i+1}',
                'headline': f'Senior {query.split()[0] if query else "Software"} Engineer',
                'current_company': random.choice(companies),
                'location': location or random.choice(locations),
                'linkedin_url': f'https://linkedin.com/in/demo-user-{i+1}',
                'skills': random.sample(skills_pool, random.randint(5, 10)),
                'experience_years': random.randint(3, 15),
                'education': random.choice(['BS Computer Science - Stanford', 'MS Software Engineering - MIT', 'BS Information Technology - UC Berkeley', 'PhD Computer Science - Carnegie Mellon']),
                'summary': f'Experienced {query.split()[0] if query else "software"} professional with {random.randint(3, 15)} years in the industry.'
            })
        return demo_candidates
    
    async def score_candidate(self, candidate, job_description):
        # Generate realistic fit scores
        base_score = random.uniform(6.5, 9.8)
        
        # Add logic based on candidate data
        if 'Senior' in candidate.get('headline', ''):
            base_score += 0.3
        if candidate.get('experience_years', 0) > 7:
            base_score += 0.2
        if any(skill.lower() in job_description.lower() for skill in candidate.get('skills', [])):
            base_score += 0.5
        
        candidate['fit_score'] = round(min(base_score, 10.0), 1)
        candidate['score_breakdown'] = {
            'skills_match': round(random.uniform(7.0, 9.5), 1),
            'experience_level': round(random.uniform(7.5, 9.8), 1),
            'location_preference': round(random.uniform(8.0, 10.0), 1),
            'culture_fit': round(random.uniform(7.0, 9.2), 1)
        }
        return candidate

class OutreachGenerator:
    def __init__(self, use_ai=True):
        self.use_ai = use_ai
    
    async def generate_message(self, candidate, job_description):
        name = candidate.get('name', 'there')
        company = candidate.get('current_company', 'your current company')
        headline = candidate.get('headline', 'professional background')
        
        templates = [
            f"""Hi {name},

I hope this message finds you well! I came across your profile and was impressed by your experience as a {headline} at {company}.

We're currently seeking talented professionals for an exciting opportunity that aligns well with your background. Based on your expertise and experience, I believe this could be a great fit for your career growth.

Would you be open to a brief conversation to learn more about this opportunity?

Best regards,
Sarah Chen
Senior Technical Recruiter""",
            
            f"""Hello {name},

Your background as a {headline} at {company} caught my attention, and I'd love to connect about a role that might interest you.

We're building an innovative team and looking for someone with your skill set. The position offers excellent growth opportunities and the chance to work on cutting-edge projects.

Are you currently open to exploring new opportunities? I'd be happy to share more details.

Best,
Michael Rodriguez
Talent Acquisition Manager""",
            
            f"""Hi {name},

I hope you're doing well! I noticed your impressive work at {company} and wanted to reach out about a position that seems tailor-made for someone with your background.

This role offers the chance to work with the latest technologies and make a significant impact. Given your experience as a {headline}, I think you'd find it both challenging and rewarding.

Would you be interested in a quick call to discuss this further?

Looking forward to hearing from you,
Jennifer Kim
Lead Recruiter"""
        ]
        
        message = random.choice(templates)
        
        return {
            'message': message,
            'confidence': random.choice(['High', 'Very High']),
            'personalization_score': round(random.uniform(8.5, 9.8), 1),
            'template_used': f'Professional Template {random.randint(1, 3)}',
            'estimated_response_rate': f"{random.randint(25, 45)}%"
        }

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'candidates' not in st.session_state:
    st.session_state.candidates = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False

# Auto-initialize agent
if not st.session_state.agent_initialized:
    try:
        st.session_state.agent = LinkedInSourcingAgent()
        st.session_state.agent_initialized = True
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")

# Header
st.markdown('<h1 class="main-header">🎯 LinkedIn Sourcing Agent</h1>', unsafe_allow_html=True)
st.markdown("**Professional candidate sourcing and outreach automation powered by AI**")

# Demo banner
st.markdown("""
<div class="demo-banner">
    <h3>🚀 Demo Mode</h3>
    <p>This is a demonstration version with realistic sample data. Perfect for testing the interface and features!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔧 Configuration")
    
    # Search Configuration
    st.subheader("Search Settings")
    max_candidates = st.slider("Max Candidates", 5, 20, 10)
    include_outreach = st.checkbox("Generate Outreach Messages", True)
    
    st.subheader("🎯 Features")
    st.write("• AI-powered candidate scoring")
    st.write("• Personalized outreach generation")  
    st.write("• Export to Excel/JSON")
    st.write("• Analytics dashboard")
    
    st.info("💡 **Demo Mode**: Using realistic sample data for demonstration purposes.")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search", "📊 Results", "💌 Outreach", "📈 Analytics"])

with tab1:
    st.header("🔍 Candidate Search")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        job_description = st.text_area(
            "Job Description",
            placeholder="Enter the complete job description here...",
            height=200,
            help="Provide detailed job requirements for better candidate matching"
        )
        
        search_query = st.text_input(
            "Search Keywords",
            placeholder="e.g., Python Developer, Machine Learning Engineer",
            help="Key skills and job titles to search for"
        )
    
    with col2:
        location = st.text_input(
            "Location",
            placeholder="e.g., San Francisco, Remote",
            help="Geographic preference for candidates"
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Any", "Entry Level", "Mid Level", "Senior", "Lead/Principal", "Executive"]
        )
        
        industry = st.selectbox(
            "Industry",
            ["Any", "Technology", "Healthcare", "Finance", "Startup", "Enterprise"]
        )
    
    # Search button
    if st.button("🔍 Search Candidates", type="primary"):
        if not job_description and not search_query:
            st.warning("Please provide either a job description or search keywords.")
        else:
            try:
                with st.spinner("Searching for candidates... This may take a few moments."):
                    # Simulate async call
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    query = search_query if search_query else job_description[:100]
                    candidates = loop.run_until_complete(
                        st.session_state.agent.search_candidates(
                            query=query,
                            location=location,
                            limit=max_candidates
                        )
                    )
                    
                    # Score candidates
                    scored_candidates = []
                    for candidate in candidates:
                        scored_candidate = loop.run_until_complete(
                            st.session_state.agent.score_candidate(candidate, job_description)
                        )
                        scored_candidates.append(scored_candidate)
                    
                    # Sort by fit score
                    scored_candidates.sort(key=lambda x: x.get('fit_score', 0), reverse=True)
                    
                    st.session_state.candidates = scored_candidates
                    st.session_state.search_history.append({
                        'timestamp': datetime.now(),
                        'query': query,
                        'location': location,
                        'results': len(scored_candidates)
                    })
                    
                    loop.close()
                
                st.success(f"Found {len(st.session_state.candidates)} candidates!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Search failed: {str(e)}")

with tab2:
    st.header("📊 Search Results")
    
    if st.session_state.candidates:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        avg_score = sum(c.get('fit_score', 0) for c in st.session_state.candidates) / len(st.session_state.candidates)
        high_score_count = sum(1 for c in st.session_state.candidates if c.get('fit_score', 0) >= 8.0)
        
        with col1:
            st.metric("Total Candidates", len(st.session_state.candidates))
        with col2:
            st.metric("Average Fit Score", f"{avg_score:.1f}")
        with col3:
            st.metric("High Score (8.0+)", high_score_count)
        with col4:
            st.metric("Top Candidate Score", f"{max(c.get('fit_score', 0) for c in st.session_state.candidates):.1f}")
        
        # Score distribution chart
        scores = [c.get('fit_score', 0) for c in st.session_state.candidates]
        fig = px.histogram(
            x=scores,
            nbins=10,
            title="Candidate Score Distribution",
            labels={'x': 'Fit Score', 'y': 'Number of Candidates'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Candidate list
        st.subheader("Candidate Details")
        
        for i, candidate in enumerate(st.session_state.candidates):
            with st.expander(f"#{i+1} {candidate.get('name', 'Unknown')} - Score: {candidate.get('fit_score', 0):.1f}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Company:** {candidate.get('current_company', 'N/A')}")
                    st.write(f"**Title:** {candidate.get('headline', 'N/A')}")
                    st.write(f"**Location:** {candidate.get('location', 'N/A')}")
                    st.write(f"**Experience:** {candidate.get('experience_years', 'N/A')} years")
                    st.write(f"**Education:** {candidate.get('education', 'N/A')}")
                    
                    # Skills
                    if candidate.get('skills'):
                        st.write("**Skills:**")
                        skills_str = ", ".join(candidate['skills'][:10])
                        st.write(skills_str)
                
                with col2:
                    # Score visualization
                    score = candidate.get('fit_score', 0)
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Fit Score"},
                        gauge = {
                            'axis': {'range': [None, 10]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 6], 'color': "lightgray"},
                                {'range': [6, 8], 'color': "yellow"},
                                {'range': [8, 10], 'color': "green"}
                            ]
                        }
                    ))
                    fig.update_layout(height=200)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Export options
        st.subheader("📥 Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel export
            df = pd.DataFrame(st.session_state.candidates)
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Candidates')
            excel_buffer.seek(0)
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer,
                file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            # JSON export
            json_str = json.dumps(st.session_state.candidates, indent=2, default=str)
            st.download_button(
                label="📄 Download JSON",
                data=json_str,
                file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    else:
        st.info("No candidates found. Please run a search first.")

with tab3:
    st.header("💌 Outreach Messages")
    
    if st.session_state.candidates:
        st.subheader("Generate Personalized Messages")
        
        selected_candidate = st.selectbox(
            "Select Candidate",
            options=range(len(st.session_state.candidates)),
            format_func=lambda x: f"{st.session_state.candidates[x].get('name', 'Unknown')} - {st.session_state.candidates[x].get('current_company', 'N/A')}"
        )
        
        message_type = st.selectbox(
            "Message Type",
            ["Professional Introduction", "Job Opportunity", "Networking", "Custom"]
        )
        
        custom_notes = st.text_area(
            "Additional Notes",
            placeholder="Any specific points to mention in the outreach...",
            help="These will be incorporated into the personalized message"
        )
        
        if st.button("✨ Generate Outreach Message"):
            try:
                candidate = st.session_state.candidates[selected_candidate]
                
                with st.spinner("Generating personalized outreach message..."):
                    outreach_generator = OutreachGenerator(use_ai=True)
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    job_desc = f"We're looking for talented professionals like you. {custom_notes}"
                    message_result = loop.run_until_complete(
                        outreach_generator.generate_message(candidate, job_desc)
                    )
                    
                    loop.close()
                
                st.success("Message generated successfully!")
                
                # Display the message
                st.subheader("Generated Message")
                message = message_result.get('message', 'Message generation failed')
                st.text_area("Outreach Message", message, height=300)
                
                # Message analytics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Confidence Level", message_result.get('confidence', 'Medium'))
                with col2:
                    st.metric("Personalization Score", f"{message_result.get('personalization_score', 0):.1f}/10")
                with col3:
                    st.metric("Est. Response Rate", message_result.get('estimated_response_rate', 'N/A'))
                
            except Exception as e:
                st.error(f"Failed to generate message: {str(e)}")
    
    else:
        st.info("No candidates available. Please run a search first.")

with tab4:
    st.header("📈 Analytics & Insights")
    
    if st.session_state.search_history:
        # Search history
        st.subheader("Search History")
        
        history_df = pd.DataFrame(st.session_state.search_history)
        st.dataframe(history_df, use_container_width=True)
        
        # Search trends
        if len(st.session_state.search_history) > 1:
            fig = px.line(
                history_df,
                x='timestamp',
                y='results',
                title="Search Results Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.candidates:
        # Candidate insights
        st.subheader("Candidate Insights")
        
        # Company distribution
        companies = [c.get('current_company', 'Unknown') for c in st.session_state.candidates]
        company_counts = pd.Series(companies).value_counts().head(8)
        
        fig = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation='h',
            title="Top Companies"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Experience distribution
        experience_years = [c.get('experience_years', 0) for c in st.session_state.candidates]
        fig = px.histogram(
            x=experience_years,
            title="Experience Distribution",
            labels={'x': 'Years of Experience', 'y': 'Number of Candidates'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics
    st.subheader("System Performance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Searches", len(st.session_state.search_history))
    with col2:
        total_candidates = sum(h['results'] for h in st.session_state.search_history) if st.session_state.search_history else 0
        st.metric("Total Candidates Found", total_candidates)
    with col3:
        if st.session_state.search_history:
            avg_results = total_candidates / len(st.session_state.search_history)
            st.metric("Avg Results per Search", f"{avg_results:.1f}")

# Footer
st.markdown("---")
st.markdown("**🎯 LinkedIn Sourcing Agent** | Professional Recruitment Platform | Powered by AI")

# Reset button in sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 Reset Session"):
        st.session_state.clear()
        st.rerun()
