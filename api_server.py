"""
FastAPI Web Service for LinkedIn Sourcing Agent
Hackathon Bonus Requirement

Endpoints:
- POST /source-candidates: Takes job description, returns top 10 candidates with outreach messages
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import our LinkedIn Sourcing Agent
from linkedin_sourcing_agent.core.agent import LinkedInSourcingAgent
from linkedin_sourcing_agent.generators.outreach_generator import OutreachGenerator
from linkedin_sourcing_agent.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="LinkedIn Sourcing Agent API",
    description="AI-powered candidate sourcing and personalized outreach generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class JobRequest(BaseModel):
    job_description: str = Field(..., description="Complete job description text")
    location: Optional[str] = Field(None, description="Geographic location preference")
    max_candidates: int = Field(10, description="Maximum number of candidates to return", ge=1, le=50)
    include_outreach: bool = Field(True, description="Whether to generate outreach messages")
    
class ScoreBreakdown(BaseModel):
    education: float = Field(..., description="Education score (0-10)")
    trajectory: float = Field(..., description="Career trajectory score (0-10)")
    company: float = Field(..., description="Company quality score (0-10)")
    skills: float = Field(..., description="Technical skills score (0-10)")
    location: float = Field(..., description="Location match score (0-10)")
    tenure: float = Field(..., description="Job tenure stability score (0-10)")

class CandidateResponse(BaseModel):
    name: str
    linkedin_url: str
    fit_score: float
    score_breakdown: ScoreBreakdown
    outreach_message: str

class SourcingResponse(BaseModel):
    job_id: str
    candidates_found: int
    top_candidates: List[CandidateResponse]

# Global agent instance
agent = None
outreach_generator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the LinkedIn Sourcing Agent on startup"""
    global agent, outreach_generator
    try:
        logger.info("Initializing LinkedIn Sourcing Agent...")
        agent = LinkedInSourcingAgent()
        outreach_generator = OutreachGenerator(use_ai=True)  # Enable AI for better messages
        logger.info("LinkedIn Sourcing Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        raise e

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LinkedIn Sourcing Agent API",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "source_candidates": "/source-candidates",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "outreach_generator_initialized": outreach_generator is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/source-candidates", response_model=SourcingResponse)
async def source_candidates(request: JobRequest):
    """
    Main endpoint: Source candidates for a job description
    
    This endpoint:
    1. Takes a job description as input
    2. Searches for relevant LinkedIn profiles
    3. Scores candidates using our fit algorithm
    4. Generates personalized outreach messages
    5. Returns top 10 candidates with all details in JSON format
    """
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    start_time = datetime.now()
    job_id = f"job_{int(start_time.timestamp())}"
    
    try:
        logger.info(f"Processing job request: {job_id}")
        
        # Step 1: Search for candidates
        search_query = _extract_search_query(request.job_description)
        candidates = await agent.search_candidates(
            query=search_query,
            location=request.location,
            limit=min(request.max_candidates * 2, 20)  # Get more for better filtering
        )
        
        logger.info(f"Found {len(candidates)} candidates for job {job_id}")
        
        if not candidates:
            return SourcingResponse(
                job_id=job_id,
                candidates_found=0,
                processing_time_seconds=0.0,
                top_candidates=[],
                search_query_used=search_query,
                timestamp=start_time.isoformat()
            )
        
        # Step 2: Score candidates
        scored_candidates = []
        for candidate in candidates:
            try:
                scored_candidate = await agent.score_candidate(candidate, request.job_description)
                scored_candidates.append(scored_candidate)
            except Exception as e:
                logger.warning(f"Failed to score candidate {candidate.get('name', 'Unknown')}: {str(e)}")
                continue
        
        # Step 3: Sort by fit score and take top candidates
        scored_candidates.sort(key=lambda x: x.get('fit_score', 0), reverse=True)
        top_candidates = scored_candidates[:request.max_candidates]
        
        # Step 4: Generate outreach messages if requested
        if request.include_outreach and outreach_generator:
            for candidate in top_candidates:
                try:
                    message_result = await outreach_generator.generate_message(
                        candidate, 
                        request.job_description
                    )
                    candidate['outreach_message'] = message_result.get('message', '')
                    candidate['message_confidence'] = message_result.get('confidence', 'medium')
                except Exception as e:
                    logger.warning(f"Failed to generate outreach for {candidate.get('name', 'Unknown')}: {str(e)}")
                    candidate['outreach_message'] = _generate_fallback_message(candidate, request.job_description)
        
        # Step 5: Format response to match desired structure
        formatted_candidates = []
        for candidate in top_candidates:
            # Create detailed score breakdown
            score_breakdown = ScoreBreakdown(
                education=_calculate_education_score(candidate),
                trajectory=_calculate_trajectory_score(candidate),
                company=_calculate_company_score(candidate),
                skills=_calculate_skills_score(candidate, request.job_description),
                location=_calculate_location_score(candidate, request.location),
                tenure=_calculate_tenure_score(candidate)
            )
            
            formatted_candidates.append(CandidateResponse(
                name=candidate.get('name', 'Unknown'),
                linkedin_url=candidate.get('linkedin_url', candidate.get('profile_url', '')),
                fit_score=round(candidate.get('fit_score', 0.0), 1),
                score_breakdown=score_breakdown,
                outreach_message=candidate.get('outreach_message', f"Hi {candidate.get('name', 'there')}, I noticed your background...")
            ))

        processing_time = (datetime.now() - start_time).total_seconds()
        
        response = SourcingResponse(
            job_id=request.job_description[:20].replace(' ', '-').lower() + f"-{int(start_time.timestamp())}",
            candidates_found=len(candidates),
            top_candidates=formatted_candidates
        )
        
        logger.info(f"Successfully processed job {request.job_description[:20]} in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def _extract_search_query(job_description: str) -> str:
    """Extract search-friendly query from job description"""
    # Simple extraction - in production, use NLP
    keywords = []
    
    # Common job titles
    job_titles = ['engineer', 'developer', 'scientist', 'manager', 'director', 'analyst', 'researcher']
    for title in job_titles:
        if title in job_description.lower():
            keywords.append(title)
    
    # Technology keywords
    tech_keywords = ['python', 'javascript', 'java', 'react', 'node', 'aws', 'docker', 'kubernetes', 
                     'machine learning', 'ai', 'ml', 'deep learning', 'tensorflow', 'pytorch']
    for tech in tech_keywords:
        if tech in job_description.lower():
            keywords.append(tech)
    
    # Industry keywords
    industry_keywords = ['fintech', 'healthcare', 'saas', 'startup', 'enterprise']
    for industry in industry_keywords:
        if industry in job_description.lower():
            keywords.append(industry)
    
    return ' '.join(keywords[:5])  # Top 5 keywords

def _extract_key_characteristics(candidate: Dict[str, Any]) -> List[str]:
    """Extract key characteristics from candidate profile"""
    characteristics = []
    
    # Experience level
    headline = candidate.get('headline', '').lower()
    if 'senior' in headline:
        characteristics.append('Senior-level experience')
    elif 'lead' in headline:
        characteristics.append('Technical leadership')
    elif 'principal' in headline:
        characteristics.append('Principal-level expertise')
    
    # Company background
    current_company = candidate.get('current_company', '').lower()
    if any(company in current_company for company in ['google', 'apple', 'microsoft', 'meta', 'amazon']):
        characteristics.append('Big Tech experience')
    
    # Education
    education = candidate.get('education', [])
    if education:
        for edu in education:
            if isinstance(edu, dict):
                school = edu.get('school', '').lower()
                if any(elite in school for elite in ['mit', 'stanford', 'harvard', 'berkeley']):
                    characteristics.append('Elite university background')
                    break
    
    # Skills
    skills = candidate.get('skills', [])
    if len(skills) >= 10:
        characteristics.append('Diverse technical skill set')
    
    # Multi-source data
    if candidate.get('github_profile'):
        characteristics.append('Active open-source contributor')
    
    return characteristics[:5]  # Top 5 characteristics

def _extract_job_match_reasons(candidate: Dict[str, Any], job_description: str) -> List[str]:
    """Extract reasons why candidate matches the job"""
    reasons = []
    
    # Skill matching
    candidate_text = f"{candidate.get('headline', '')} {' '.join(candidate.get('skills', []))}"
    job_text = job_description.lower()
    
    # Technical skills
    if 'python' in candidate_text.lower() and 'python' in job_text:
        reasons.append('Python programming expertise')
    
    if 'machine learning' in candidate_text.lower() and 'ml' in job_text:
        reasons.append('Machine learning background')
    
    if 'ai' in candidate_text.lower() and 'ai' in job_text:
        reasons.append('AI/ML experience')
    
    # Experience level match
    fit_score = candidate.get('fit_score', 0)
    if fit_score >= 8.0:
        reasons.append('Excellent overall fit score')
    elif fit_score >= 7.0:
        reasons.append('Strong candidate match')
    
    # Location match
    if candidate.get('location_match_score', 0) >= 8:
        reasons.append('Ideal location match')
    
    return reasons[:5]  # Top 5 reasons

def _calculate_education_score(candidate: Dict[str, Any]) -> float:
    """Calculate education score (0-10)"""
    education = candidate.get('education', [])
    if not education:
        return 5.0
    
    score = 5.0
    for edu in education:
        if isinstance(edu, dict):
            school = edu.get('school', '').lower()
            degree = edu.get('degree', '').lower()
            
            # Elite universities
            if any(elite in school for elite in ['mit', 'stanford', 'harvard', 'berkeley', 'carnegie mellon']):
                score += 2.0
            elif any(good in school for good in ['university', 'college']):
                score += 1.0
            
            # Advanced degrees
            if any(advanced in degree for advanced in ['phd', 'ms', 'master', 'mba']):
                score += 1.5
            elif 'bs' in degree or 'bachelor' in degree:
                score += 1.0
    
    return min(score, 10.0)

def _calculate_trajectory_score(candidate: Dict[str, Any]) -> float:
    """Calculate career trajectory score (0-10)"""
    headline = candidate.get('headline', '').lower()
    experience = candidate.get('experience', [])
    
    score = 5.0
    
    # Seniority indicators
    if 'senior' in headline:
        score += 1.5
    elif 'lead' in headline or 'principal' in headline:
        score += 2.0
    elif 'director' in headline or 'vp' in headline:
        score += 2.5
    
    # Career progression
    if len(experience) >= 3:
        score += 1.0
    if len(experience) >= 5:
        score += 1.0
    
    return min(score, 10.0)

def _calculate_company_score(candidate: Dict[str, Any]) -> float:
    """Calculate company quality score (0-10)"""
    headline = candidate.get('headline', '').lower()
    experience = candidate.get('experience', [])
    
    score = 5.0
    
    # Extract company from headline or experience
    companies = []
    if ' at ' in headline:
        companies.append(headline.split(' at ')[1].split('•')[0].strip())
    
    for exp in experience:
        if isinstance(exp, dict):
            companies.append(exp.get('company', '').lower())
    
    # Rate companies
    for company in companies:
        if any(faang in company for faang in ['google', 'apple', 'microsoft', 'meta', 'amazon']):
            score += 2.0
            break
        elif any(unicorn in company for unicorn in ['uber', 'airbnb', 'stripe', 'openai', 'netflix']):
            score += 1.5
            break
        elif any(startup in company for startup in ['startup', 'inc', 'corp']):
            score += 0.5
    
    return min(score, 10.0)

def _calculate_skills_score(candidate: Dict[str, Any], job_description: str) -> float:
    """Calculate technical skills score (0-10)"""
    skills = candidate.get('skills', [])
    headline = candidate.get('headline', '').lower()
    job_desc = job_description.lower()
    
    score = 5.0
    
    # Create combined skills text
    skills_text = ' '.join(skills).lower() + ' ' + headline
    
    # Key technology matches
    tech_matches = 0
    key_techs = ['python', 'javascript', 'java', 'react', 'node', 'aws', 'docker', 'kubernetes', 
                'machine learning', 'ai', 'tensorflow', 'pytorch', 'sql', 'postgresql']
    
    for tech in key_techs:
        if tech in skills_text and tech in job_desc:
            tech_matches += 1
    
    score += min(tech_matches * 0.5, 3.0)
    
    # Overall skill count
    if len(skills) >= 10:
        score += 1.0
    elif len(skills) >= 5:
        score += 0.5
    
    return min(score, 10.0)

def _calculate_location_score(candidate: Dict[str, Any], requested_location: Optional[str]) -> float:
    """Calculate location match score (0-10)"""
    if not requested_location:
        return 8.0  # Neutral if no location specified
    
    candidate_location = candidate.get('location', '').lower()
    requested_location = requested_location.lower()
    
    # Exact match
    if requested_location in candidate_location:
        return 10.0
    
    # Same city (different format)
    location_parts = candidate_location.split(',')
    if location_parts and requested_location in location_parts[0]:
        return 10.0
    
    # Same state/region
    if any(region in candidate_location for region in ['california', 'ca', 'bay area', 'silicon valley']):
        if any(region in requested_location for region in ['california', 'ca', 'san francisco', 'bay area']):
            return 8.0
    
    # Remote-friendly locations
    if 'remote' in candidate_location or 'remote' in requested_location:
        return 7.0
    
    return 4.0  # Different location

def _calculate_tenure_score(candidate: Dict[str, Any]) -> float:
    """Calculate job tenure stability score (0-10)"""
    experience = candidate.get('experience', [])
    
    if not experience:
        return 5.0
    
    score = 5.0
    total_positions = len(experience)
    
    # Calculate average tenure (rough estimation)
    long_tenures = 0
    for exp in experience:
        if isinstance(exp, dict):
            duration = exp.get('duration', '').lower()
            # Look for year indicators
            if 'year' in duration:
                try:
                    years = int(duration.split('year')[0].strip().split()[-1])
                    if years >= 2:
                        long_tenures += 1
                except:
                    pass
    
    # Reward stability
    if total_positions > 0:
        stability_ratio = long_tenures / total_positions
        score += stability_ratio * 3.0
    
    # Penalize job hopping
    if total_positions > 6:
        score -= 1.0
    
    return max(min(score, 10.0), 0.0)

@app.get("/demo")
async def demo_endpoint():
    """Demo endpoint with sample data for testing"""
    sample_job = """
    Software Engineer, ML Research at Windsurf (Codeium)
    
    We're looking for a talented Software Engineer to join our ML Research team at Windsurf, 
    the company behind Codeium. You'll be working on training and optimizing Large Language Models 
    for code generation and AI-powered developer tools.
    
    Requirements:
    - Strong experience with Python, PyTorch, TensorFlow
    - Machine Learning and Deep Learning expertise
    - Experience with LLMs and code generation
    - Located in Mountain View, CA or remote
    
    Compensation: $140-300k + equity
    """
    
    # Process the demo job
    request = JobRequest(
        job_description=sample_job,
        location="Mountain View",
        max_candidates=5,
        include_outreach=True
    )
    
    return await source_candidates(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
