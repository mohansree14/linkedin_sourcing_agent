"""
LinkedIn Profile Scraper
Professional web scraping component for LinkedIn profiles with rate limiting and error handling
"""

import asyncio
import json
import re
import time
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from retrying import retry

from ..utils.logging_config import get_logger
from ..utils.rate_limiter import RateLimiter
from ..utils.demo_data import demo_generator


logger = get_logger(__name__)


class LinkedInProfileScraper:
    """
    Professional LinkedIn profile scraper with multiple data sources:
    1. Google search for LinkedIn profile URLs
    2. RapidAPI integration for structured data
    3. Fallback web scraping with rate limiting
    
    Features:
    - Intelligent rate limiting
    - Multiple data quality levels
    - Graceful error handling
    - Comprehensive data extraction
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LinkedIn profile scraper
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        self.config = config
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=config.get('SCRAPER_MAX_REQUESTS', 20),
            time_window=config.get('SCRAPER_TIME_WINDOW', 60)
        )
        
        # RapidAPI configuration
        self.rapidapi_key = config.get('RAPIDAPI_KEY')
        self.rapidapi_available = bool(self.rapidapi_key)
        
        logger.info(f"LinkedIn scraper initialized (RapidAPI: {'Enabled' if self.rapidapi_available else 'Disabled'})")
    
    async def search_profiles(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for LinkedIn profiles using multiple methods
        
        Args:
            query: Search query (should include relevant keywords)
            max_results: Maximum number of profiles to return
            
        Returns:
            List of candidate dictionaries with profile information
        """
        candidates = []
        
        try:
            # Method 1: Try real API methods first
            if self.rapidapi_available:
                # Use RapidAPI for LinkedIn data
                await self.rate_limiter.wait()
                rapidapi_results = await self._rapidapi_search(query, max_results)
                candidates.extend(rapidapi_results)
            
            # Method 2: Google search for LinkedIn URLs (if API not available)
            if not candidates:
                await self.rate_limiter.wait()
                google_results = await self._google_search_linkedin(query, max_results)
                
                for result in google_results:
                    candidate = await self._extract_basic_info_from_search(result)
                    if candidate:
                        candidates.append(candidate)
            
            # Method 3: Fallback to demo data (for testing/demo purposes)
            if not candidates:
                logger.info("No API keys available - using demo data for testing")
                demo_candidates = demo_generator.generate_candidates(query, location="", limit=max_results)
                candidates.extend(demo_candidates)
                
                # Add a demo indicator
                for candidate in candidates:
                    candidate['is_demo_data'] = True
                    candidate['demo_notice'] = "This is demo data. Add API keys for real LinkedIn data."
            
            # Deduplicate and clean results
            candidates = self._deduplicate_candidates(candidates)
            
            logger.info(f"Found {len(candidates)} candidates for query: '{query}' (Demo: {candidates[0].get('is_demo_data', False) if candidates else False})")
            return candidates[:max_results]
            
        except Exception as e:
            logger.error(f"Profile search failed: {str(e)}")
            
            # Final fallback - return demo data even on error
            logger.info("Falling back to demo data due to error")
            demo_candidates = demo_generator.generate_candidates(query, location="", limit=max_results)
            for candidate in demo_candidates:
                candidate['is_demo_data'] = True
                candidate['demo_notice'] = "Demo data (API error occurred)"
            return demo_candidates
    
    async def extract_profile_details(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Extract detailed information from a LinkedIn profile
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Dictionary with comprehensive profile information
        """
        profile_data = {
            'experience': [],
            'education': [],
            'skills': [],
            'summary': '',
            'location': '',
            'connections': 0,
            'data_completeness': 'basic',
            'extraction_timestamp': time.time()
        }
        
        try:
            await self.rate_limiter.wait()
            
            # Try RapidAPI first for high-quality data
            if self.rapidapi_available:
                rapidapi_data = await self._rapidapi_profile_details(linkedin_url)
                if rapidapi_data:
                    profile_data.update(rapidapi_data)
                    profile_data['data_completeness'] = 'high'
                    logger.info(f"High-quality data extracted via RapidAPI for {linkedin_url}")
                    return profile_data
            
            # Fallback to web scraping
            basic_data = await self._extract_basic_profile_data(linkedin_url)
            profile_data.update(basic_data)
            profile_data['data_completeness'] = 'medium' if basic_data else 'basic'
            
            logger.info(f"Profile data extracted for {linkedin_url} (completeness: {profile_data['data_completeness']})")
            return profile_data
            
        except Exception as e:
            logger.error(f"Profile extraction failed for {linkedin_url}: {str(e)}")
            return profile_data
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    async def _google_search_linkedin(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Perform Google search for LinkedIn profiles
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results with URLs and metadata
        """
        # Construct LinkedIn-specific search query
        linkedin_query = f'{query} site:linkedin.com/in'
        search_url = f"https://www.google.com/search?q={quote_plus(linkedin_query)}&num={min(max_results * 2, 20)}"
        
        try:
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Parse Google search results
            for result in soup.find_all('div', class_='g')[:max_results]:
                link_elem = result.find('a')
                if not link_elem:
                    continue
                    
                url = link_elem.get('href', '')
                if 'linkedin.com/in/' not in url:
                    continue
                
                # Extract title and snippet
                title_elem = result.find('h3')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Try multiple selectors for snippet
                snippet_elem = (result.find('span', class_='st') or 
                              result.find('div', class_='s') or
                              result.find('div', class_='IsZvec'))
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                results.append({
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'search_rank': len(results) + 1
                })
            
            logger.debug(f"Google search returned {len(results)} LinkedIn profiles")
            return results
            
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            return []
    
    async def _extract_basic_info_from_search(self, search_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract basic candidate information from search result
        
        Args:
            search_result: Dictionary containing URL, title, and snippet
            
        Returns:
            Candidate dictionary or None if extraction fails
        """
        try:
            url = search_result['url']
            title = search_result['title']
            snippet = search_result['snippet']
            
            # Clean and validate LinkedIn URL
            linkedin_url = self._clean_linkedin_url(url)
            if not linkedin_url:
                return None
            
            # Parse name from title (format: "Name - Current Position - Company")
            name_parts = title.split(' - ')
            name = name_parts[0].strip() if name_parts else 'Unknown'
            
            # Extract current position/headline
            headline = ''
            if len(name_parts) > 1:
                headline = ' - '.join(name_parts[1:])
                # Remove common LinkedIn suffixes
                headline = re.sub(r'\s*\|\s*LinkedIn$', '', headline)
            elif snippet:
                headline = snippet[:100] + '...' if len(snippet) > 100 else snippet
            
            # Extract location and experience
            location = self._extract_location_from_text(snippet)
            experience_years = self._estimate_experience_years(snippet + ' ' + headline)
            
            candidate = {
                'name': name,
                'linkedin_url': linkedin_url,
                'headline': headline.strip(),
                'location': location,
                'experience_years': experience_years,
                'snippet': snippet,
                'search_rank': search_result.get('search_rank', 0),
                'source': 'google_search',
                'data_quality': 'basic',
                'extraction_timestamp': time.time()
            }
            
            return candidate
            
        except Exception as e:
            logger.error(f"Failed to extract info from search result: {str(e)}")
            return None
    
    async def _rapidapi_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using RapidAPI LinkedIn service
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of candidate dictionaries
        """
        if not self.rapidapi_available:
            return []
        
        try:
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": self.config.get('RAPIDAPI_HOST', 'linkedin-data-api.p.rapidapi.com')
            }
            
            params = {
                "keywords": query.replace('site:linkedin.com/in', '').strip(),
                "location": self.config.get('DEFAULT_LOCATION', 'United States'),
                "count": max_results
            }
            
            # Placeholder for actual RapidAPI implementation
            # This would be replaced with the actual API endpoint
            logger.info(f"RapidAPI search would be performed for: {query}")
            
            # For now, return empty list since we don't have actual credentials configured
            return []
            
        except Exception as e:
            logger.error(f"RapidAPI search failed: {str(e)}")
            return []
    
    async def _rapidapi_profile_details(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed profile data using RapidAPI
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Detailed profile data or None
        """
        if not self.rapidapi_available:
            return None
        
        try:
            # Placeholder for RapidAPI profile extraction
            logger.info(f"RapidAPI profile extraction would be performed for: {linkedin_url}")
            return None
            
        except Exception as e:
            logger.error(f"RapidAPI profile extraction failed: {str(e)}")
            return None
    
    async def _extract_basic_profile_data(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Extract basic profile data using web scraping fallback
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Dictionary with extracted profile data
        """
        profile_data = {
            'experience': [],
            'education': [],
            'skills': [],
            'summary': '',
            'location': '',
            'connections': 0
        }
        
        try:
            # Note: LinkedIn actively blocks scraping
            # This is a simplified approach for demonstration
            response = self.session.get(linkedin_url, timeout=15)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract from meta tags (limited info available without login)
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                if ' | ' in title:
                    parts = title.split(' | ')
                    if len(parts) >= 2:
                        profile_data['summary'] = parts[0]
                        if 'LinkedIn' not in parts[1]:
                            profile_data['location'] = parts[1]
            
            # Try to extract any visible content
            body_text = soup.get_text() if soup.body else ''
            
            # Simple pattern matching for experience
            years_match = re.search(r'(\d+)\s*(?:\+)?\s*years?', body_text.lower())
            if years_match:
                profile_data['experience_years'] = int(years_match.group(1))
            
            return profile_data
            
        except Exception as e:
            logger.warning(f"Basic profile extraction failed for {linkedin_url}: {str(e)}")
            return profile_data
    
    def _clean_linkedin_url(self, url: str) -> Optional[str]:
        """
        Clean and validate LinkedIn URL
        
        Args:
            url: Raw URL from search results
            
        Returns:
            Clean LinkedIn URL or None if invalid
        """
        if not url or 'linkedin.com/in/' not in url:
            return None
        
        # Remove Google redirect and tracking parameters
        if url.startswith('/url?q='):
            try:
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                url = parsed.get('q', [url])[0]
            except:
                pass
        
        # Extract clean LinkedIn profile URL
        match = re.search(r'linkedin\.com/in/([^/?&#]+)', url)
        if match:
            username = match.group(1)
            return f"https://www.linkedin.com/in/{username}"
        
        return None
    
    def _extract_location_from_text(self, text: str) -> str:
        """
        Extract location information from text using pattern matching
        
        Args:
            text: Text to search for location
            
        Returns:
            Extracted location or empty string
        """
        if not text:
            return ''
        
        # Major tech hubs and cities
        location_patterns = [
            r'(?:San Francisco|SF|San Francisco Bay Area)',
            r'(?:Mountain View|Palo Alto|Menlo Park|Cupertino)',
            r'(?:New York|NYC|Brooklyn|Manhattan)',
            r'(?:Seattle|Redmond|Bellevue)',
            r'(?:Austin|Dallas|Houston)',
            r'(?:Boston|Cambridge)',
            r'(?:Los Angeles|LA|Santa Monica)',
            r'(?:Chicago|Remote|Worldwide)',
            r'(?:London|Berlin|Toronto|Vancouver)'
        ]
        
        text_lower = text.lower()
        
        for pattern in location_patterns:
            match = re.search(pattern.lower(), text_lower)
            if match:
                return match.group(0).title()
        
        # Generic city, state pattern
        city_state_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})', text)
        if city_state_match:
            return f"{city_state_match.group(1)}, {city_state_match.group(2)}"
        
        return ''
    
    def _estimate_experience_years(self, text: str) -> int:
        """
        Estimate years of experience from text content
        
        Args:
            text: Text to analyze for experience indicators
            
        Returns:
            Estimated years of experience
        """
        if not text:
            return 0
        
        text_lower = text.lower()
        
        # Look for explicit year mentions
        year_patterns = [
            r'(\d+)\s*(?:\+)?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\s*(?:\+)?\s*yrs?\s*(?:experience|exp)',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        
        # Estimate based on seniority keywords
        seniority_mapping = {
            ('senior', 'lead', 'principal', 'staff', 'architect'): 7,
            ('manager', 'director', 'head'): 8,
            ('vp', 'vice president', 'cto', 'ceo'): 10,
            ('mid', 'intermediate'): 4,
            ('junior', 'entry', 'associate', 'new grad', 'intern'): 1
        }
        
        for keywords, years in seniority_mapping.items():
            if any(keyword in text_lower for keyword in keywords):
                return years
        
        return 3  # Default mid-level estimate
    
    def _deduplicate_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate candidates based on LinkedIn URL or name
        
        Args:
            candidates: List of candidate dictionaries
            
        Returns:
            Deduplicated list of candidates
        """
        seen_identifiers = set()
        unique_candidates = []
        
        for candidate in candidates:
            # Use LinkedIn URL as primary identifier, fallback to name for demo data
            url = candidate.get('linkedin_url', candidate.get('profile_url', ''))
            name = candidate.get('name', '')
            
            # Create unique identifier
            identifier = url if url else name
            
            if identifier and identifier not in seen_identifiers:
                seen_identifiers.add(identifier)
                unique_candidates.append(candidate)
            elif not identifier and candidate:  # Keep candidates without identifiers (shouldn't happen but safety net)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'session'):
            self.session.close()
