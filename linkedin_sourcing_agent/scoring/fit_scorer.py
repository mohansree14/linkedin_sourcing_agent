"""
Candidate Fit Scorer
Professional candidate evaluation and ranking system with comprehensive scoring rubric
"""

import re
import math
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from ..utils.logging_config import get_logger


logger = get_logger(__name__)


@dataclass
class ScoringWeights:
    """Configurable scoring weights for different evaluation criteria"""
    education: float = 0.20
    career_trajectory: float = 0.20
    company_relevance: float = 0.15
    experience_match: float = 0.25
    location_match: float = 0.10
    tenure: float = 0.10


class ScoringCriteria(Enum):
    """Enumeration of scoring criteria"""
    EDUCATION = "education"
    CAREER_TRAJECTORY = "career_trajectory"
    COMPANY_RELEVANCE = "company_relevance"
    EXPERIENCE_MATCH = "experience_match"
    LOCATION_MATCH = "location_match"
    TENURE = "tenure"


class CandidateFitScorer:
    """
    Professional candidate fit scorer implementing comprehensive evaluation rubric
    
    Scoring Criteria:
    - Education (20%): School prestige and relevance
    - Career Trajectory (20%): Growth and progression patterns
    - Company Relevance (15%): Industry and company tier
    - Experience Match (25%): Skills and role alignment
    - Location Match (10%): Geographic compatibility
    - Tenure (10%): Job stability and progression
    
    Features:
    - Multi-source data integration
    - Confidence scoring
    - AI-powered insights
    - Configurable weights
    - Detailed breakdowns
    """
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        """
        Initialize the candidate fit scorer
        
        Args:
            weights: Custom scoring weights, uses defaults if None
        """
        self.weights = weights or ScoringWeights()
        
        # Elite institutions for education scoring
        self.elite_schools = {
            'mit', 'stanford', 'harvard', 'caltech', 'berkeley', 'cmu', 'cornell',
            'princeton', 'yale', 'columbia', 'university of washington', 'georgia tech',
            'carnegie mellon', 'massachusetts institute of technology', 'stanford university',
            'university of california berkeley', 'uc berkeley'
        }
        
        # Strong institutions
        self.strong_schools = {
            'ucla', 'usc', 'ucsd', 'ucsb', 'university of michigan', 'university of illinois',
            'purdue', 'penn state', 'virginia tech', 'texas a&m', 'rice university',
            'duke', 'northwestern', 'johns hopkins', 'university of texas', 'nyu',
            'university of pennsylvania', 'brown', 'dartmouth', 'vanderbilt'
        }
        
        # Top technology companies (Tier 1)
        self.tier1_companies = {
            'google', 'microsoft', 'apple', 'meta', 'facebook', 'amazon', 'netflix',
            'tesla', 'nvidia', 'openai', 'anthropic', 'deepmind', 'spacex', 'uber',
            'airbnb', 'stripe'
        }
        
        # Strong technology companies (Tier 2)
        self.tier2_companies = {
            'twitter', 'linkedin', 'salesforce', 'adobe', 'intel', 'oracle', 'ibm',
            'cisco', 'vmware', 'databricks', 'snowflake', 'palantir', 'twilio',
            'zoom', 'dropbox', 'slack', 'shopify', 'square'
        }
        
        # AI/ML specialized companies
        self.ai_companies = {
            'openai', 'anthropic', 'deepmind', 'hugging face', 'scale ai', 'cohere',
            'stability ai', 'together ai', 'replicate', 'wandb', 'weights & biases',
            'anyscale', 'modal', 'modal labs', 'cerebras', 'graphcore'
        }
        
        # Target locations (configurable for different roles)
        self.target_locations = {
            'mountain view', 'san francisco', 'palo alto', 'menlo park', 'redwood city',
            'cupertino', 'sunnyvale', 'santa clara', 'sf', 'bay area', 'silicon valley',
            'san jose', 'fremont', 'oakland'
        }
        
        # Remote-friendly indicators
        self.remote_indicators = {'remote', 'distributed', 'worldwide', 'anywhere', 'global'}
        
        logger.info("Candidate fit scorer initialized with professional scoring rubric")
    
    def calculate_fit_score(self, candidate: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Calculate comprehensive fit score for a candidate
        
        Args:
            candidate: Candidate data dictionary
            job_description: Job description to match against
            
        Returns:
            Dictionary with fit_score, detailed breakdown, confidence metrics, and insights
        """
        try:
            # Calculate individual criterion scores
            scores = self._calculate_individual_scores(candidate, job_description)
            
            # Apply weights to get weighted scores
            weighted_scores = self._apply_weights(scores)
            
            # Calculate base fit score
            base_score = sum(weighted_scores.values())
            
            # Calculate multi-source enhancement bonus
            multi_source_bonus = self._calculate_multi_source_bonus(candidate)
            
            # Final score with bonus (capped at 10.0)
            final_score = min(base_score + multi_source_bonus, 10.0)
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(candidate, job_description)
            
            # Generate insights and recommendations
            insights = self._generate_insights(candidate, scores, job_description)
            
            return {
                'fit_score': round(final_score, 1),
                'base_score': round(base_score, 1),
                'multi_source_bonus': round(multi_source_bonus, 1),
                'score_breakdown': {
                    criterion.value: round(scores[criterion], 1) 
                    for criterion in ScoringCriteria
                },
                'weighted_scores': {
                    criterion.value: round(weighted_scores[criterion.value], 2)
                    for criterion in ScoringCriteria
                },
                'confidence_score': confidence_metrics['score'],
                'confidence_level': confidence_metrics['level'],
                'data_completeness': confidence_metrics['completeness'],
                'data_sources': candidate.get('data_sources', ['linkedin']),
                'insights': insights,
                'scoring_metadata': {
                    'weights_used': self.weights.__dict__,
                    'scoring_timestamp': self._get_timestamp(),
                    'scorer_version': '2.0'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating fit score for candidate: {str(e)}")
            return self._create_fallback_score(str(e))
    
    def calculate_fit_score_with_multi_source(self, candidate: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Calculate enhanced fit score with multi-source data integration
        
        Args:
            candidate: Candidate data dictionary with multi-source data
            job_description: Job description to match against
            
        Returns:
            Enhanced scoring result with multi-source insights
        """
        try:
            # Get base calculation
            base_result = self.calculate_fit_score(candidate, job_description)
            
            # Enhanced multi-source scoring
            multi_source_scores = self._calculate_detailed_multi_source_bonus(candidate)
            
            # Enhanced confidence with multi-source verification
            enhanced_confidence = self._calculate_enhanced_confidence(candidate, base_result['confidence_score'])
            
            # Generate multi-source insights
            multi_source_insights = self._generate_multi_source_insights(candidate, job_description)
            
            # Calculate enhanced final score
            total_bonus = sum(multi_source_scores.values())
            enhanced_score = min(base_result['base_score'] + total_bonus, 10.0)
            
            # Update result with enhanced data
            enhanced_result = base_result.copy()
            enhanced_result.update({
                'fit_score': round(enhanced_score, 1),
                'multi_source_breakdown': {
                    key: round(value, 2) for key, value in multi_source_scores.items()
                },
                'total_multi_source_bonus': round(total_bonus, 1),
                'confidence_score': enhanced_confidence['score'],
                'confidence_level': enhanced_confidence['level'],
                'multi_source_quality': self._assess_multi_source_quality(candidate),
                'insights': multi_source_insights,
                'verification_status': self._get_verification_status(candidate)
            })
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in multi-source scoring: {str(e)}")
            return self.calculate_fit_score(candidate, job_description)
    
    def _calculate_individual_scores(self, candidate: Dict[str, Any], job_description: str) -> Dict[ScoringCriteria, float]:
        """Calculate individual scores for each criterion"""
        return {
            ScoringCriteria.EDUCATION: self._score_education(candidate),
            ScoringCriteria.CAREER_TRAJECTORY: self._score_career_trajectory(candidate),
            ScoringCriteria.COMPANY_RELEVANCE: self._score_company_relevance(candidate),
            ScoringCriteria.EXPERIENCE_MATCH: self._score_experience_match(candidate, job_description),
            ScoringCriteria.LOCATION_MATCH: self._score_location_match(candidate),
            ScoringCriteria.TENURE: self._score_tenure(candidate)
        }
    
    def _apply_weights(self, scores: Dict[ScoringCriteria, float]) -> Dict[str, float]:
        """Apply scoring weights to individual scores"""
        return {
            ScoringCriteria.EDUCATION.value: scores[ScoringCriteria.EDUCATION] * self.weights.education,
            ScoringCriteria.CAREER_TRAJECTORY.value: scores[ScoringCriteria.CAREER_TRAJECTORY] * self.weights.career_trajectory,
            ScoringCriteria.COMPANY_RELEVANCE.value: scores[ScoringCriteria.COMPANY_RELEVANCE] * self.weights.company_relevance,
            ScoringCriteria.EXPERIENCE_MATCH.value: scores[ScoringCriteria.EXPERIENCE_MATCH] * self.weights.experience_match,
            ScoringCriteria.LOCATION_MATCH.value: scores[ScoringCriteria.LOCATION_MATCH] * self.weights.location_match,
            ScoringCriteria.TENURE.value: scores[ScoringCriteria.TENURE] * self.weights.tenure
        }
    
    def _score_education(self, candidate: Dict[str, Any]) -> float:
        """
        Score education background (0-10 scale)
        
        Elite schools (MIT, Stanford, etc.): 9-10
        Strong schools: 7-8
        Standard universities: 5-6
        Advanced degrees: +0.5-1.0 bonus
        """
        education = candidate.get('education', [])
        
        # Try to extract education from text if not structured
        if not education:
            text = f"{candidate.get('headline', '')} {candidate.get('snippet', '')}"
            education = self._extract_education_from_text(text)
        
        if not education:
            return 4.0  # Neutral score when no education data available
        
        max_score = 0.0
        
        for edu in education:
            school_name = self._normalize_school_name(edu)
            degree = self._extract_degree_type(edu)
            
            # Check for elite institutions
            if any(elite in school_name for elite in self.elite_schools):
                base_score = 9.0
                if 'phd' in degree or 'doctorate' in degree:
                    base_score = 10.0
                elif 'master' in degree or 'ms' in degree or 'meng' in degree:
                    base_score = 9.5
                max_score = max(max_score, base_score)
            
            # Check for strong institutions
            elif any(strong in school_name for strong in self.strong_schools):
                base_score = 7.0
                if 'phd' in degree or 'doctorate' in degree:
                    base_score = 8.5
                elif 'master' in degree or 'ms' in degree:
                    base_score = 7.5
                max_score = max(max_score, base_score)
            
            # Standard universities
            elif any(term in school_name for term in ['university', 'college', 'institute']):
                base_score = 5.0
                if 'phd' in degree or 'doctorate' in degree:
                    base_score = 6.5
                elif 'master' in degree or 'ms' in degree:
                    base_score = 5.5
                max_score = max(max_score, base_score)
        
        return min(max_score, 10.0)
    
    def _score_career_trajectory(self, candidate: Dict[str, Any]) -> float:
        """
        Score career trajectory and progression (0-10 scale)
        
        Clear upward progression: 8-10
        Steady growth: 6-8
        Limited progression: 4-6
        No clear pattern: 3-4
        """
        experience = candidate.get('experience', [])
        headline = candidate.get('headline', '')
        
        # Extract experience from text if not structured
        if not experience:
            text = f"{headline} {candidate.get('snippet', '')}"
            experience = self._extract_experience_indicators(text)
        
        # Analyze progression patterns
        progression_score = self._analyze_career_progression(experience, headline)
        
        # Factor in experience years
        experience_years = candidate.get('experience_years', 0)
        if experience_years >= 8:
            progression_score = min(progression_score + 0.5, 10.0)
        elif experience_years >= 5:
            progression_score = min(progression_score + 0.3, 10.0)
        
        return progression_score
    
    def _score_company_relevance(self, candidate: Dict[str, Any]) -> float:
        """
        Score company relevance and prestige (0-10 scale)
        
        AI/ML specialized companies: 10
        Top tech companies (Tier 1): 9-10
        Strong tech companies (Tier 2): 7-8
        Relevant industry: 6-7
        Any tech experience: 5-6
        """
        # Gather company information from all sources
        companies = self._extract_all_companies(candidate)
        text = f"{candidate.get('headline', '')} {candidate.get('snippet', '')}".lower()
        
        max_score = 4.0  # Base score
        
        # Check for AI/ML specialized companies (highest priority)
        for company in self.ai_companies:
            if self._company_mentioned(company, companies, text):
                max_score = max(max_score, 10.0)
                break
        
        # Check for Tier 1 companies
        for company in self.tier1_companies:
            if self._company_mentioned(company, companies, text):
                max_score = max(max_score, 9.5)
        
        # Check for Tier 2 companies
        for company in self.tier2_companies:
            if self._company_mentioned(company, companies, text):
                max_score = max(max_score, 8.0)
        
        # Check for general tech indicators
        tech_indicators = ['startup', 'fintech', 'saas', 'tech company', 'software company', 
                          'technology', 'engineering', 'developer tools']
        if any(indicator in text for indicator in tech_indicators):
            max_score = max(max_score, 6.5)
        
        return max_score
    
    def _score_experience_match(self, candidate: Dict[str, Any], job_description: str) -> float:
        """
        Score experience match with job requirements (0-10 scale)
        
        Perfect skill alignment: 9-10
        Strong skill overlap: 7-8
        Good relevant skills: 5-6
        Some transferable skills: 3-4
        """
        # Extract key skills from job description
        job_skills = self._extract_job_requirements(job_description)
        
        # Get candidate's skills and experience text
        candidate_text = self._get_candidate_text_for_matching(candidate)
        
        # Calculate skill match scores
        required_match_score = self._calculate_skill_match(candidate_text, job_skills['required'])
        preferred_match_score = self._calculate_skill_match(candidate_text, job_skills['preferred'])
        
        # Combine scores with weighting
        final_score = (required_match_score * 0.7) + (preferred_match_score * 0.3)
        
        # Bonus for highly relevant experience
        if self._has_highly_relevant_experience(candidate_text, job_description):
            final_score = min(final_score + 1.0, 10.0)
        
        return final_score
    
    def _score_location_match(self, candidate: Dict[str, Any]) -> float:
        """
        Score location compatibility (0-10 scale)
        
        Exact target city: 10
        Same metro area: 8-9
        Remote-friendly: 6-7
        Same region: 4-5
        Requires relocation: 2-3
        """
        location = candidate.get('location', '').lower()
        text = candidate.get('snippet', '').lower()
        
        # Extract location from text if not available
        if not location:
            location = self._extract_location_from_text(text)
        
        # Check for exact target location match
        if any(target in location for target in ['mountain view', 'palo alto']):
            return 10.0
        
        # Check for Bay Area
        if any(area in location for area in self.target_locations):
            return 8.5
        
        # Check for remote indicators
        if any(remote in location or remote in text for remote in self.remote_indicators):
            return 7.0
        
        # Check for California
        if 'california' in location or 'ca' in location:
            return 5.0
        
        # Check for West Coast
        if any(state in location for state in ['washington', 'oregon', 'wa', 'or']):
            return 4.0
        
        return 3.0  # Default for other locations
    
    def _score_tenure(self, candidate: Dict[str, Any]) -> float:
        """
        Score job tenure patterns (0-10 scale)
        
        Optimal tenure (2-4 years avg): 9-10
        Good stability (1.5-2 years): 7-8
        Some job hopping (<1.5 years): 4-6
        Excessive job hopping (<1 year): 2-3
        """
        experience = candidate.get('experience', [])
        
        if not experience:
            # Use estimated experience if available
            exp_years = candidate.get('experience_years', 0)
            if exp_years >= 5:
                return 7.0  # Assume reasonable tenure for experienced professionals
            elif exp_years >= 2:
                return 6.0
            else:
                return 5.0
        
        # Calculate tenure patterns
        tenures = self._extract_job_tenures(experience)
        
        if not tenures:
            return 6.0  # Default when no tenure data available
        
        avg_tenure = sum(tenures) / len(tenures)
        
        # Score based on average tenure
        if 2.0 <= avg_tenure <= 4.0:
            return 9.5  # Optimal range
        elif 1.5 <= avg_tenure < 2.0:
            return 8.0  # Good stability
        elif 4.0 < avg_tenure <= 6.0:
            return 8.5  # Long tenure (also good)
        elif 1.0 <= avg_tenure < 1.5:
            return 6.0  # Some job hopping
        elif avg_tenure >= 6.0:
            return 7.0  # Very long tenure (might indicate lack of growth)
        else:
            return 3.0  # Excessive job hopping
    
    def _calculate_multi_source_bonus(self, candidate: Dict[str, Any]) -> float:
        """Calculate basic multi-source bonus"""
        data_sources = candidate.get('data_sources', ['linkedin'])
        bonus = 0.0
        
        if 'github' in data_sources:
            bonus += 0.3
        if 'twitter' in data_sources:
            bonus += 0.1
        if 'website' in data_sources:
            bonus += 0.1
        
        return min(bonus, 0.5)
    
    def _calculate_detailed_multi_source_bonus(self, candidate: Dict[str, Any]) -> Dict[str, float]:
        """Calculate detailed multi-source bonuses"""
        return {
            'github_bonus': self._calculate_github_bonus(candidate),
            'twitter_bonus': self._calculate_twitter_bonus(candidate),
            'website_bonus': self._calculate_website_bonus(candidate),
            'data_completeness_bonus': self._calculate_completeness_bonus(candidate)
        }
    
    def _calculate_github_bonus(self, candidate: Dict[str, Any]) -> float:
        """Calculate GitHub-specific bonus based on profile quality"""
        github_profile = candidate.get('github_profile', {})
        if not github_profile:
            return 0.0
        
        bonus = 0.0
        
        # Repository quality (max 0.3)
        repos = github_profile.get('public_repos', 0)
        stars_total = sum(repo.get('stars', 0) for repo in github_profile.get('notable_repos', []))
        
        if repos >= 50 or stars_total >= 1000:
            bonus += 0.3
        elif repos >= 20 or stars_total >= 500:
            bonus += 0.2
        elif repos >= 10 or stars_total >= 100:
            bonus += 0.15
        elif repos >= 5:
            bonus += 0.1
        
        # Community engagement (max 0.2)
        followers = github_profile.get('followers', 0)
        if followers >= 500:
            bonus += 0.2
        elif followers >= 100:
            bonus += 0.15
        elif followers >= 50:
            bonus += 0.1
        
        return min(bonus, 0.4)
    
    def _calculate_twitter_bonus(self, candidate: Dict[str, Any]) -> float:
        """Calculate Twitter-specific bonus"""
        twitter_profile = candidate.get('twitter_profile', {})
        if not twitter_profile:
            return 0.0
        
        followers = twitter_profile.get('followers', 0)
        bio = twitter_profile.get('bio', '').lower()
        
        bonus = 0.05  # Base bonus
        
        # Follower count bonus
        if followers >= 10000:
            bonus += 0.15
        elif followers >= 5000:
            bonus += 0.1
        elif followers >= 1000:
            bonus += 0.05
        
        # Relevance bonus
        relevant_terms = ['ai', 'ml', 'machine learning', 'engineer', 'developer', 'tech']
        if any(term in bio for term in relevant_terms):
            bonus += 0.05
        
        return min(bonus, 0.2)
    
    def _calculate_website_bonus(self, candidate: Dict[str, Any]) -> float:
        """Calculate personal website bonus"""
        website = candidate.get('personal_website', {})
        if not website:
            return 0.0
        
        bonus = 0.05  # Base bonus
        
        if website.get('has_blog'):
            bonus += 0.1
        if website.get('has_portfolio'):
            bonus += 0.1
        
        # Content relevance
        topics = website.get('content_topics', [])
        if topics:
            relevant_topics = ['machine learning', 'ai', 'programming', 'software', 'tech']
            if any(topic.lower() in ' '.join(topics).lower() for topic in relevant_topics):
                bonus += 0.05
        
        return min(bonus, 0.2)
    
    def _calculate_completeness_bonus(self, candidate: Dict[str, Any]) -> float:
        """Calculate bonus for data completeness"""
        completeness_score = 0
        
        # Core data fields
        if candidate.get('name'): completeness_score += 1
        if candidate.get('headline'): completeness_score += 1
        if candidate.get('location'): completeness_score += 1
        if candidate.get('experience'): completeness_score += 2
        if candidate.get('education'): completeness_score += 2
        if candidate.get('skills'): completeness_score += 1
        
        # Multi-source fields
        if candidate.get('github_profile'): completeness_score += 2
        if candidate.get('twitter_profile'): completeness_score += 1
        if candidate.get('personal_website'): completeness_score += 1
        
        # Calculate bonus (max 0.3)
        max_possible = 12
        completeness_ratio = completeness_score / max_possible
        
        return min(completeness_ratio * 0.3, 0.3)
    
    # Helper methods for data extraction and analysis
    
    def _normalize_school_name(self, edu) -> str:
        """Normalize school name for comparison"""
        if isinstance(edu, dict):
            school = edu.get('school', '').lower()
        else:
            school = str(edu).lower()
        
        # Common normalizations
        school = school.replace('university of ', '').replace('the ', '')
        return school.strip()
    
    def _extract_degree_type(self, edu) -> str:
        """Extract degree type from education entry"""
        if isinstance(edu, dict):
            degree = edu.get('degree', '').lower()
        else:
            degree = str(edu).lower()
        
        return degree
    
    def _extract_education_from_text(self, text: str) -> List[str]:
        """Extract education information from unstructured text"""
        education = []
        text_lower = text.lower()
        
        # Look for university patterns
        patterns = [
            r'(university of [^,.\n]+)',
            r'([^,.\n]*university[^,.\n]*)',
            r'([^,.\n]*institute of technology[^,.\n]*)',
            r'(mit|stanford|harvard|berkeley|cmu)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            education.extend(matches)
        
        return list(set(education))[:3]  # Remove duplicates, limit to 3
    
    def _extract_experience_indicators(self, text: str) -> List[str]:
        """Extract experience indicators from text"""
        indicators = []
        text_lower = text.lower()
        
        # Job title patterns
        job_patterns = [
            r'(senior [^,.\n]*engineer[^,.\n]*)',
            r'(lead [^,.\n]*)',
            r'(principal [^,.\n]*)',
            r'([^,.\n]*scientist[^,.\n]*)',
            r'([^,.\n]*researcher[^,.\n]*)',
            r'([^,.\n]*developer[^,.\n]*)'
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, text_lower)
            indicators.extend(matches)
        
        return indicators
    
    def _analyze_career_progression(self, experience: List, headline: str) -> float:
        """Analyze career progression patterns"""
        if not experience and not headline:
            return 5.0
        
        text = headline.lower() + ' ' + ' '.join([str(exp) for exp in experience]).lower()
        
        # Progression indicators
        senior_indicators = ['senior', 'lead', 'principal', 'staff', 'director', 'vp', 'head of', 'chief']
        mid_indicators = ['engineer', 'scientist', 'researcher', 'developer', 'manager']
        junior_indicators = ['junior', 'associate', 'entry', 'intern', 'assistant']
        
        senior_count = sum(1 for indicator in senior_indicators if indicator in text)
        mid_count = sum(1 for indicator in mid_indicators if indicator in text)
        junior_count = sum(1 for indicator in junior_indicators if indicator in text)
        
        # Score based on progression pattern
        if senior_count >= 2:
            return 9.0  # Multiple senior roles
        elif senior_count >= 1 and mid_count >= 1:
            return 8.5  # Clear progression to senior
        elif senior_count >= 1:
            return 8.0  # Currently senior
        elif mid_count >= 2:
            return 7.0  # Stable at mid-level
        elif mid_count >= 1 and junior_count >= 1:
            return 6.5  # Some progression
        elif mid_count >= 1:
            return 6.0  # Currently mid-level
        else:
            return 5.0  # Limited progression evidence
    
    def _extract_all_companies(self, candidate: Dict[str, Any]) -> List[str]:
        """Extract all company names from candidate data"""
        companies = []
        
        # From structured experience
        experience = candidate.get('experience', [])
        for exp in experience:
            if isinstance(exp, dict):
                company = exp.get('company', '')
                if company:
                    companies.append(company.lower())
        
        return companies
    
    def _company_mentioned(self, company: str, companies: List[str], text: str) -> bool:
        """Check if company is mentioned in candidate data"""
        return (company in text or 
                any(company in comp for comp in companies) or
                any(comp in company for comp in companies if len(comp) > 3))
    
    def _extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Extract required and preferred skills from job description"""
        text_lower = job_description.lower()
        
        # Core ML/AI skills
        required_skills = [
            'machine learning', 'ml', 'deep learning', 'neural networks', 'pytorch', 'tensorflow',
            'python', 'ai', 'artificial intelligence', 'nlp', 'natural language processing',
            'transformers', 'research', 'algorithms', 'statistics'
        ]
        
        # Preferred/bonus skills
        preferred_skills = [
            'code generation', 'llm', 'large language models', 'gpt', 'bert',
            'distributed systems', 'scala', 'rust', 'go', 'java', 'c++',
            'aws', 'gcp', 'kubernetes', 'docker', 'github', 'git'
        ]
        
        return {
            'required': required_skills,
            'preferred': preferred_skills
        }
    
    def _get_candidate_text_for_matching(self, candidate: Dict[str, Any]) -> str:
        """Get all candidate text for skill matching"""
        parts = [
            candidate.get('headline', ''),
            candidate.get('snippet', ''),
            ' '.join([str(exp) for exp in candidate.get('experience', [])]),
            ' '.join([str(edu) for edu in candidate.get('education', [])]),
            ' '.join(candidate.get('skills', []))
        ]
        
        return ' '.join(parts).lower()
    
    def _calculate_skill_match(self, candidate_text: str, skills: List[str]) -> float:
        """Calculate skill match score"""
        matches = sum(1 for skill in skills if skill in candidate_text)
        return min((matches / len(skills)) * 10, 10.0)
    
    def _has_highly_relevant_experience(self, candidate_text: str, job_description: str) -> bool:
        """Check for highly relevant experience indicators"""
        high_value_terms = [
            'machine learning engineer', 'ml engineer', 'ai researcher', 'research scientist',
            'deep learning', 'neural networks', 'llm', 'transformer', 'nlp engineer'
        ]
        
        return any(term in candidate_text for term in high_value_terms)
    
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from text"""
        location_patterns = [
            r'(?:san francisco|sf|mountain view|palo alto|menlo park)',
            r'(?:seattle|new york|nyc|boston|austin|chicago)',
            r'(?:remote|distributed|worldwide)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).lower()
        
        return ''
    
    def _extract_job_tenures(self, experience: List) -> List[float]:
        """Extract job tenure durations"""
        tenures = []
        
        for exp in experience:
            if isinstance(exp, dict):
                duration = exp.get('duration', '')
                years = self._parse_duration_to_years(duration)
                if years > 0:
                    tenures.append(years)
        
        return tenures
    
    def _parse_duration_to_years(self, duration: str) -> float:
        """Parse duration string to years"""
        if not duration:
            return 0.0
        
        duration_lower = duration.lower()
        
        # Look for year patterns
        year_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)', duration_lower)
        if year_match:
            return float(year_match.group(1))
        
        # Look for month patterns
        month_match = re.search(r'(\d+)\s*(?:months?|mos?)', duration_lower)
        if month_match:
            return float(month_match.group(1)) / 12
        
        # Current role estimation
        if 'present' in duration_lower or 'current' in duration_lower:
            return 2.0  # Assume 2 years for current roles
        
        return 1.5  # Default assumption
    
    def _calculate_confidence_metrics(self, candidate: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Calculate comprehensive confidence metrics"""
        base_score = 0.0
        
        # Data completeness factors
        if candidate.get('name'): base_score += 0.1
        if candidate.get('headline'): base_score += 0.1
        if candidate.get('location'): base_score += 0.05
        if candidate.get('experience'): base_score += 0.2
        if candidate.get('education'): base_score += 0.15
        if candidate.get('skills'): base_score += 0.1
        
        # Multi-source verification
        data_sources = candidate.get('data_sources', ['linkedin'])
        source_bonus = min(len(data_sources) * 0.1, 0.3)
        
        final_score = min(base_score + source_bonus, 1.0)
        
        return {
            'score': round(final_score, 2),
            'level': self._get_confidence_level(final_score),
            'completeness': self._assess_data_completeness(candidate)
        }
    
    def _calculate_enhanced_confidence(self, candidate: Dict[str, Any], base_confidence: float) -> Dict[str, Any]:
        """Calculate enhanced confidence with multi-source data"""
        enhanced_score = base_confidence
        
        # Multi-source verification bonuses
        if candidate.get('github_profile'):
            enhanced_score += 0.15
        if candidate.get('twitter_profile'):
            enhanced_score += 0.1
        if candidate.get('personal_website'):
            enhanced_score += 0.1
        
        enhanced_score = min(enhanced_score, 1.0)
        
        return {
            'score': round(enhanced_score, 2),
            'level': self._get_confidence_level(enhanced_score)
        }
    
    def _get_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to readable level"""
        if confidence_score >= 0.8:
            return 'high'
        elif confidence_score >= 0.6:
            return 'medium'
        elif confidence_score >= 0.4:
            return 'low'
        else:
            return 'very_low'
    
    def _assess_data_completeness(self, candidate: Dict[str, Any]) -> str:
        """Assess overall data completeness"""
        fields = ['name', 'headline', 'location', 'experience', 'education', 'skills']
        present_fields = sum(1 for field in fields if candidate.get(field))
        
        ratio = present_fields / len(fields)
        
        if ratio >= 0.8:
            return 'excellent'
        elif ratio >= 0.6:
            return 'good'
        elif ratio >= 0.4:
            return 'moderate'
        else:
            return 'limited'
    
    def _assess_multi_source_quality(self, candidate: Dict[str, Any]) -> str:
        """Assess quality of multi-source data"""
        sources = candidate.get('data_sources', ['linkedin'])
        
        if len(sources) >= 4:
            return 'excellent'
        elif len(sources) >= 3:
            return 'good'
        elif len(sources) >= 2:
            return 'moderate'
        else:
            return 'limited'
    
    def _generate_insights(self, candidate: Dict[str, Any], scores: Dict[ScoringCriteria, float], job_description: str) -> List[str]:
        """Generate professional insights about the candidate"""
        insights = []
        
        # Education insights
        if scores[ScoringCriteria.EDUCATION] >= 8:
            insights.append("Strong educational background from prestigious institution")
        
        # Experience insights
        if scores[ScoringCriteria.EXPERIENCE_MATCH] >= 8:
            insights.append("Excellent technical skill alignment with role requirements")
        
        # Company insights
        if scores[ScoringCriteria.COMPANY_RELEVANCE] >= 9:
            insights.append("Proven track record at top-tier technology companies")
        
        # Career progression insights
        if scores[ScoringCriteria.CAREER_TRAJECTORY] >= 8:
            insights.append("Demonstrates clear career advancement and growth")
        
        # Multi-source insights
        data_sources = candidate.get('data_sources', ['linkedin'])
        if len(data_sources) >= 3:
            insights.append("Profile verified across multiple professional platforms")
        
        return insights
    
    def _generate_multi_source_insights(self, candidate: Dict[str, Any], job_description: str) -> List[str]:
        """Generate insights specifically from multi-source data"""
        insights = []
        
        # GitHub insights
        github_profile = candidate.get('github_profile', {})
        if github_profile:
            repos = github_profile.get('public_repos', 0)
            if repos >= 20:
                insights.append(f"Active open-source contributor with {repos} public repositories")
            
            notable_repos = github_profile.get('notable_repos', [])
            if notable_repos:
                total_stars = sum(repo.get('stars', 0) for repo in notable_repos)
                if total_stars >= 500:
                    insights.append("Created popular open-source projects with significant community adoption")
        
        # Twitter insights
        twitter_profile = candidate.get('twitter_profile', {})
        if twitter_profile:
            followers = twitter_profile.get('followers', 0)
            if followers >= 1000:
                insights.append(f"Established thought leader with {followers:,} social media followers")
        
        # Website insights
        website = candidate.get('personal_website', {})
        if website:
            if website.get('has_blog') and website.get('has_portfolio'):
                insights.append("Maintains comprehensive online presence with blog and portfolio")
        
        return insights
    
    def _get_verification_status(self, candidate: Dict[str, Any]) -> Dict[str, bool]:
        """Get verification status for different data sources"""
        return {
            'linkedin_verified': bool(candidate.get('linkedin_url')),
            'github_verified': bool(candidate.get('github_profile')),
            'twitter_verified': bool(candidate.get('twitter_profile')),
            'website_verified': bool(candidate.get('personal_website'))
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def _create_fallback_score(self, error_message: str) -> Dict[str, Any]:
        """Create fallback score result in case of errors"""
        return {
            'fit_score': 5.0,
            'base_score': 5.0,
            'multi_source_bonus': 0.0,
            'score_breakdown': {criterion.value: 5.0 for criterion in ScoringCriteria},
            'weighted_scores': {criterion.value: 1.0 for criterion in ScoringCriteria},
            'confidence_score': 0.3,
            'confidence_level': 'low',
            'data_completeness': 'limited',
            'data_sources': ['linkedin'],
            'insights': [f"Scoring error occurred: {error_message}"],
            'error': True
        }
