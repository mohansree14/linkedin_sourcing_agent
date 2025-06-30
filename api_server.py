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
    
class CandidateResponse(BaseModel):
    name: str
    linkedin_url: str
    headline: str
    location: str
    fit_score: float
    score_breakdown: Dict[str, float]
    confidence: str
    key_characteristics: List[str]
    job_match_reasons: List[str]
    outreach_message: Optional[str] = None
    
class SourcingResponse(BaseModel):
    job_id: str
    candidates_found: int
    processing_time_seconds: float
    top_candidates: List[CandidateResponse]
    search_query_used: str
    timestamp: str

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
                    candidate['outreach_message'] = "Custom outreach message generation failed"
        
        # Step 5: Format response
        formatted_candidates = []
        for candidate in top_candidates:
            formatted_candidates.append(CandidateResponse(
                name=candidate.get('name', 'Unknown'),
                linkedin_url=candidate.get('linkedin_url', ''),
                headline=candidate.get('headline', ''),
                location=candidate.get('location', ''),
                fit_score=candidate.get('fit_score', 0.0),
                score_breakdown=candidate.get('score_breakdown', {}),
                confidence=candidate.get('confidence', 'medium'),
                key_characteristics=_extract_key_characteristics(candidate),
                job_match_reasons=_extract_job_match_reasons(candidate, request.job_description),
                outreach_message=candidate.get('outreach_message') if request.include_outreach else None
            ))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        response = SourcingResponse(
            job_id=job_id,
            candidates_found=len(candidates),
            processing_time_seconds=round(processing_time, 2),
            top_candidates=formatted_candidates,
            search_query_used=search_query,
            timestamp=start_time.isoformat()
        )
        
        logger.info(f"Successfully processed job {job_id} in {processing_time:.2f}s")
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
