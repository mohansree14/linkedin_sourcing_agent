"""
Core LinkedIn Sourcing Agent

The main orchestrator class that handles the complete pipeline from job description 
to personalized outreach messages with multi-source data enhancement.

This module provides:
- Single job processing pipeline
- Multi-source data integration
- Advanced scoring with confidence metrics  
- Professional outreach generation
- Smart caching and rate limiting

Author: LinkedIn Sourcing Agent Team
Created: June 2025
"""

import os
import json
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..scrapers.linkedin_scraper import LinkedInProfileScraper
from ..scrapers.multi_source_scraper import MultiSourceProfileScraper
from ..scoring.fit_scorer import CandidateFitScorer
from ..generators.outreach_generator import OutreachGenerator
from ..utils.logging_config import get_logger
from ..utils.config_manager import ConfigManager
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.demo_data import demo_generator

logger = get_logger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the sourcing pipeline"""
    max_candidates: int = 25
    top_n: int = 5
    enable_multi_source: bool = True
    enable_caching: bool = True
    cache_expiry_hours: int = 24
    max_requests_per_minute: int = 30


class LinkedInSourcingAgent:
    """
    Main LinkedIn Sourcing Agent that orchestrates the entire pipeline:
    
    1. Search for LinkedIn profiles based on job description
    2. Extract and parse candidate data from multiple sources
    3. Score candidates using comprehensive fit algorithm
    4. Generate personalized outreach messages
    
    Features:
    - Multi-source data aggregation (LinkedIn, GitHub, Twitter, websites)
    - Advanced scoring with confidence metrics
    - Smart caching and rate limiting
    - Professional outreach generation
    - Comprehensive error handling
    """
    
    def __init__(self, config_path: str = ".env"):
        """
        Initialize the LinkedIn Sourcing Agent
        
        Args:
            config_path: Path to configuration file
        """
        logger.info("Initializing LinkedIn Sourcing Agent...")
        
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Initialize pipeline configuration
        self.pipeline_config = PipelineConfig(
            enable_multi_source=self.config.get('ENABLE_MULTI_SOURCE', 'true').lower() == 'true',
            enable_caching=self.config.get('ENABLE_CACHING', 'true').lower() == 'true',
            cache_expiry_hours=int(self.config.get('CACHE_EXPIRY_HOURS', 24)),
            max_requests_per_minute=int(self.config.get('MAX_REQUESTS_PER_MINUTE', 30))
        )
        
        # Initialize core components
        self._initialize_components()
        
        logger.info("LinkedIn Sourcing Agent initialized successfully")
    
    def _initialize_components(self) -> None:
        """Initialize all agent components"""
        try:
            # Scrapers
            self.linkedin_scraper = LinkedInProfileScraper(self.config)
            self.multi_source_scraper = MultiSourceProfileScraper(self.config)
            
            # Scoring
            self.fit_scorer = CandidateFitScorer()
            
            # Message generation
            self.outreach_generator = OutreachGenerator(self.config)
            
            # Utilities
            self.rate_limiter = RateLimiter(
                max_requests=self.pipeline_config.max_requests_per_minute,
                time_window=60
            )
            
            self.cache_manager = CacheManager(
                cache_dir="data",
                ttl_seconds=self.pipeline_config.cache_expiry_hours * 3600
            ) if self.pipeline_config.enable_caching else None
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            raise
    
    async def process_job(
        self, 
        job_description: str,
        job_id: Optional[str] = None,
        config: Optional[PipelineConfig] = None
    ) -> Dict[str, Any]:
        """
        Process a single job description through the complete pipeline
        
        Args:
            job_description: The job description to source candidates for
            job_id: Optional job identifier
            config: Optional pipeline configuration override
            
        Returns:
            Dictionary containing pipeline results
        """
        # Use provided config or default
        pipeline_config = config or self.pipeline_config
        
        if not job_id:
            job_id = f"job_{int(time.time())}"
            
        logger.info(f"Starting pipeline for job: {job_id}")
        start_time = time.time()
        
        try:
            # Step 1: Search for LinkedIn profiles
            candidates = await self._search_candidates(
                job_description, 
                pipeline_config.max_candidates
            )
            
            if not candidates:
                logger.warning(f"No candidates found for job: {job_id}")
                return self._create_empty_result(job_id, "No candidates found")
            
            # Step 2: Enhance with multi-source data
            if pipeline_config.enable_multi_source:
                candidates = await self._enhance_with_multi_source(candidates)
            
            # Step 3: Score candidates
            scored_candidates = await self._score_candidates(candidates, job_description)
            
            # Step 4: Select top candidates
            top_candidates = self._select_top_candidates(
                scored_candidates, 
                pipeline_config.top_n
            )
            
            # Step 5: Generate outreach messages
            await self._generate_outreach_messages(top_candidates, job_description)
            
            # Compile results
            results = self._compile_results(
                job_id=job_id,
                job_description=job_description,
                candidates_found=len(candidates),
                candidates_scored=len(scored_candidates),
                top_candidates=top_candidates,
                processing_time=time.time() - start_time
            )
            
            # Save results
            await self._save_results(job_id, results)
            
            logger.info(f"Pipeline completed successfully for job: {job_id}")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed for job {job_id}: {str(e)}")
            return self._create_error_result(job_id, str(e))
    
    async def _search_candidates(
        self, 
        job_description: str, 
        max_candidates: int
    ) -> List[Dict[str, Any]]:
        """Search for LinkedIn profiles based on job description"""
        
        # Check cache first
        if self.cache_manager:
            cached_candidates = self.cache_manager.get_cached_candidates(job_description)
            if cached_candidates:
                logger.info(f"Found {len(cached_candidates)} cached candidates")
                return cached_candidates[:max_candidates]
        
        # Generate search queries
        search_queries = self._generate_search_queries(job_description)
        logger.info(f"Generated {len(search_queries)} search queries")
        
        all_candidates = []
        
        for query in search_queries[:3]:  # Limit to top 3 queries
            try:
                await self.rate_limiter.wait()
                candidates = await self.linkedin_scraper.search_profiles(
                    query, 
                    max_results=max_candidates//3
                )
                all_candidates.extend(candidates)
                logger.info(f"Query '{query}' returned {len(candidates)} candidates")
                
            except Exception as e:
                logger.error(f"Search query failed: {query} - {str(e)}")
                continue
        
        # Remove duplicates
        unique_candidates = self._remove_duplicate_candidates(all_candidates)
        
        # Cache results
        if self.cache_manager and unique_candidates:
            self.cache_manager.cache_candidates(job_description, unique_candidates)
        
        logger.info(f"Found {len(unique_candidates)} unique candidates")
        return unique_candidates[:max_candidates]
    
    async def _enhance_with_multi_source(
        self, 
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance candidates with multi-source data"""
        logger.info("Enhancing candidates with multi-source data...")
        
        enhanced_candidates = []
        
        for candidate in candidates:
            try:
                await self.rate_limiter.wait()
                multi_source_data = await self.multi_source_scraper.aggregate_candidate_data(candidate)
                candidate.update(multi_source_data)
                enhanced_candidates.append(candidate)
                
            except Exception as e:
                logger.error(f"Failed to enhance candidate {candidate.get('name', 'Unknown')}: {str(e)}")
                enhanced_candidates.append(candidate)  # Add without enhancement
        
        logger.info(f"Enhanced {len(enhanced_candidates)} candidates with multi-source data")
        return enhanced_candidates
    
    async def _score_candidates(
        self, 
        candidates: List[Dict[str, Any]], 
        job_description: str
    ) -> List[Dict[str, Any]]:
        """Score candidates using the fit algorithm"""
        logger.info("Scoring candidates...")
        
        scored_candidates = []
        
        for candidate in candidates:
            try:
                # Extract additional profile data if needed
                if not candidate.get('experience') or not candidate.get('education'):
                    await self.rate_limiter.wait()
                    enhanced_profile = await self.linkedin_scraper.extract_profile_details(
                        candidate['linkedin_url']
                    )
                    candidate.update(enhanced_profile)
                
                # Score the candidate
                if self.pipeline_config.enable_multi_source and candidate.get('github_profile'):
                    score_result = self.fit_scorer.calculate_fit_score_with_multi_source(
                        candidate, job_description
                    )
                else:
                    score_result = self.fit_scorer.calculate_fit_score(
                        candidate, job_description
                    )
                
                candidate.update(score_result)
                scored_candidates.append(candidate)
                
            except Exception as e:
                logger.error(f"Failed to score candidate {candidate.get('name', 'Unknown')}: {str(e)}")
                # Add candidate with default score
                candidate.update({
                    'fit_score': 0.0,
                    'score_breakdown': {},
                    'confidence': 'low'
                })
                scored_candidates.append(candidate)
        
        logger.info(f"Scored {len(scored_candidates)} candidates")
        return scored_candidates
    
    def _select_top_candidates(
        self, 
        scored_candidates: List[Dict[str, Any]], 
        top_n: int
    ) -> List[Dict[str, Any]]:
        """Select top N candidates based on fit score"""
        sorted_candidates = sorted(
            scored_candidates, 
            key=lambda x: x.get('fit_score', 0), 
            reverse=True
        )
        return sorted_candidates[:top_n]
    
    async def _generate_outreach_messages(
        self, 
        candidates: List[Dict[str, Any]], 
        job_description: str
    ) -> None:
        """Generate personalized outreach messages for candidates"""
        logger.info("Generating outreach messages...")
        
        for candidate in candidates:
            try:
                await self.rate_limiter.wait()
                candidate['outreach_message'] = await self.outreach_generator.generate_message(
                    candidate, job_description
                )
            except Exception as e:
                logger.error(f"Failed to generate outreach for {candidate.get('name', 'Unknown')}: {str(e)}")
                candidate['outreach_message'] = "Error generating personalized message"
    
    def _generate_search_queries(self, job_description: str) -> List[str]:
        """Generate LinkedIn search queries from job description"""
        # This would be enhanced with NLP analysis of the job description
        # For now, using the existing logic
        base_queries = [
            'site:linkedin.com/in "machine learning engineer" "AI" "python"',
            'site:linkedin.com/in "ML engineer" "deep learning" "pytorch" "tensorflow"',
            'site:linkedin.com/in "AI engineer" "LLM" "language models"',
            'site:linkedin.com/in "research engineer" "machine learning" "NLP"',
            'site:linkedin.com/in "software engineer" "AI" "research" "ML"'
        ]
        
        return base_queries
    
    def _remove_duplicate_candidates(
        self, 
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate candidates based on LinkedIn URL"""
        seen_urls = set()
        unique_candidates = []
        
        for candidate in candidates:
            url = candidate.get('linkedin_url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def _compile_results(
        self,
        job_id: str,
        job_description: str,
        candidates_found: int,
        candidates_scored: int,
        top_candidates: List[Dict[str, Any]],
        processing_time: float
    ) -> Dict[str, Any]:
        """Compile pipeline results"""
        return {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 2),
            "job_description": job_description,
            "candidates_found": candidates_found,
            "candidates_scored": candidates_scored,
            "top_candidates": top_candidates,
            "pipeline_config": {
                "multi_source_enabled": self.pipeline_config.enable_multi_source,
                "caching_enabled": self.pipeline_config.enable_caching,
                "max_candidates": self.pipeline_config.max_candidates,
                "top_n": self.pipeline_config.top_n
            }
        }
    
    def _create_empty_result(self, job_id: str, message: str) -> Dict[str, Any]:
        """Create empty result for failed searches"""
        return {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "candidates_found": 0,
            "top_candidates": [],
            "message": message
        }
    
    def _create_error_result(self, job_id: str, error: str) -> Dict[str, Any]:
        """Create error result for failed pipelines"""
        return {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "candidates_found": 0,
            "top_candidates": [],
            "error": error
        }
    
    async def _save_results(self, job_id: str, results: Dict[str, Any]) -> None:
        """Save pipeline results to file"""
        try:
            os.makedirs('data', exist_ok=True)
            results_file = f"data/results_{job_id}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
    
    async def search_candidates(
        self, 
        query: str, 
        location: str = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Public method to search for candidates
        
        Args:
            query: Search query for candidates
            location: Geographic location filter
            limit: Maximum number of candidates to return
            
        Returns:
            List of candidate profiles
        """
        logger.info(f"Searching for candidates: query='{query}', location='{location}', limit={limit}")
        
        try:
            # Use the LinkedIn scraper directly for simple searches
            search_query = query
            if location:
                search_query += f" {location}"
            
            # Search using the LinkedIn scraper
            candidates = await self.linkedin_scraper.search_profiles(
                query=search_query,
                max_results=limit
            )
            # Add scoring and insights for demo data
            if candidates and candidates[0].get('is_demo_data'):
                # Use demo data generator to add realistic scoring
                job_desc = demo_generator.generate_job_description()
                candidates = demo_generator.add_fit_scores_and_insights(candidates, job_desc)
            
            logger.info(f"Found {len(candidates)} candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    async def score_candidate(self, candidate: Dict[str, Any], job_description: str = "") -> Dict[str, Any]:
        """
        Score a single candidate against job requirements
        
        Args:
            candidate: Candidate profile data
            job_description: Job requirements for scoring
            
        Returns:
            Candidate with scoring information
        """
        try:
            if job_description:
                # Use the fit scorer (not async)
                if self.pipeline_config.enable_multi_source and candidate.get('github_profile'):
                    score_result = self.fit_scorer.calculate_fit_score_with_multi_source(
                        candidate, job_description
                    )
                else:
                    score_result = self.fit_scorer.calculate_fit_score(
                        candidate, job_description
                    )
                candidate.update(score_result)
                return candidate
            else:
                # Return candidate with default scoring
                candidate['fit_score'] = 5.5  # Better default score
                candidate['scoring_details'] = {'message': 'No job description provided for scoring'}
                return candidate
        except Exception as e:
            logger.error(f"Scoring failed for candidate: {str(e)}")
            candidate['fit_score'] = 3.0  # Better default than 0
            candidate['scoring_details'] = {'error': str(e)}
            return candidate


# Async helper function for backward compatibility
async def run_agent_pipeline(
    job_description: str, 
    max_candidates: int = 25, 
    top_n: int = 5
) -> Dict[str, Any]:
    """
    Helper function to run the agent pipeline
    
    Args:
        job_description: Job description to process
        max_candidates: Maximum candidates to find
        top_n: Number of top candidates to return
        
    Returns:
        Pipeline results dictionary
    """
    agent = LinkedInSourcingAgent()
    config = PipelineConfig(max_candidates=max_candidates, top_n=top_n)
    return await agent.process_job(job_description, config=config)
