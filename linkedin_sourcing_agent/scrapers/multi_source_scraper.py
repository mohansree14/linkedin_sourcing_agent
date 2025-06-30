"""
Multi-Source Profile Scraper
Professional scraper combining LinkedIn, GitHub, Twitter, and personal websites
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


logger = get_logger(__name__)


class MultiSourceProfileScraper:
    """
    Enhanced profile scraper combining multiple data sources:
    - LinkedIn profiles
    - GitHub repositories and activity
    - Twitter profiles  
    - Personal websites and blogs
    
    Features:
    - Cross-platform candidate correlation
    - Intelligent data merging
    - Source-specific rate limiting
    - Quality scoring for data completeness
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize multi-source profile scraper
        
        Args:
            config: Configuration dictionary with API keys and settings
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
        
        # Source-specific rate limiters
        self.linkedin_limiter = RateLimiter(
            max_requests=config.get('LINKEDIN_MAX_REQUESTS', 10),
            time_window=60
        )
        self.github_limiter = RateLimiter(
            max_requests=config.get('GITHUB_MAX_REQUESTS', 30),
            time_window=60
        )
        self.twitter_limiter = RateLimiter(
            max_requests=config.get('TWITTER_MAX_REQUESTS', 20),
            time_window=60
        )
        self.general_limiter = RateLimiter(
            max_requests=config.get('GENERAL_MAX_REQUESTS', 15),
            time_window=60
        )
        
        # API tokens
        self.github_token = config.get('GITHUB_TOKEN')
        self.twitter_bearer_token = config.get('TWITTER_BEARER_TOKEN')
        
        logger.info("Multi-source profile scraper initialized")
    
    async def search_profiles(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for profiles across multiple platforms
        
        Args:
            query: Search query (job description or keywords)
            max_results: Maximum number of profiles to return
            
        Returns:
            List of enhanced candidate dictionaries with multi-source data
        """
        all_candidates = []
        
        try:
            # Primary: Search LinkedIn profiles
            linkedin_candidates = await self._search_linkedin_profiles(query, max_results)
            
            # Enhance each LinkedIn candidate with additional sources
            for candidate in linkedin_candidates:
                enhanced_candidate = await self._enhance_candidate_profile(candidate)
                all_candidates.append(enhanced_candidate)
            
            # Secondary: Direct GitHub search for technical roles
            if self._is_technical_role(query):
                github_candidates = await self._search_github_profiles(query, max_results // 3)
                
                # Add non-duplicate GitHub-only candidates
                for github_candidate in github_candidates:
                    if not self._is_duplicate_candidate(github_candidate, all_candidates):
                        enhanced_candidate = await self._enhance_candidate_profile(github_candidate)
                        all_candidates.append(enhanced_candidate)
            
            # Score and sort by data completeness
            all_candidates = self._score_data_completeness(all_candidates)
            all_candidates.sort(key=lambda x: x.get('data_completeness_score', 0), reverse=True)
            
            logger.info(f"Found {len(all_candidates)} enhanced candidates from multiple sources")
            return all_candidates[:max_results]
            
        except Exception as e:
            logger.error(f"Multi-source profile search failed: {str(e)}")
            return []
    
    async def _search_linkedin_profiles(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search LinkedIn profiles using Google search
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of LinkedIn profile candidates
        """
        candidates = []
        
        # Multiple LinkedIn search strategies
        search_queries = [
            f'site:linkedin.com/in {query}',
            f'site:linkedin.com/in "{query}" engineer',
            f'site:linkedin.com/in "{query}" developer',
            f'site:linkedin.com/in {query} senior'
        ]
        
        for search_query in search_queries[:2]:  # Limit to avoid over-searching
            try:
                await self.linkedin_limiter.acquire()
                results = await self._google_search(search_query, max_results // 2)
                
                for result in results:
                    candidate = await self._extract_linkedin_info(result)
                    if candidate and not self._is_duplicate_candidate(candidate, candidates):
                        candidates.append(candidate)
                
                if len(candidates) >= max_results:
                    break
                    
            except Exception as e:
                logger.warning(f"LinkedIn search failed for query '{search_query}': {str(e)}")
        
        return candidates[:max_results]
    
    async def _search_github_profiles(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search GitHub profiles for technical candidates
        
        Args:
            query: Technical search query
            max_results: Maximum results to return
            
        Returns:
            List of GitHub profile candidates
        """
        candidates = []
        
        try:
            await self.github_limiter.acquire()
            
            # Extract technical keywords
            tech_keywords = self._extract_tech_keywords(query)
            
            # Search GitHub users
            for keyword in tech_keywords[:3]:  # Limit API calls
                try:
                    github_users = await self._github_api_search_users(keyword, max_results // 3)
                    
                    for user in github_users:
                        candidate = await self._extract_github_info(user)
                        if candidate and not self._is_duplicate_candidate(candidate, candidates):
                            candidates.append(candidate)
                    
                except Exception as e:
                    logger.warning(f"GitHub search failed for keyword '{keyword}': {str(e)}")
            
            return candidates[:max_results]
            
        except Exception as e:
            logger.error(f"GitHub profile search failed: {str(e)}")
            return []
    
    async def _enhance_candidate_profile(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance candidate profile with data from multiple sources
        
        Args:
            candidate: Base candidate dictionary
            
        Returns:
            Enhanced candidate with multi-source data
        """
        enhanced_candidate = candidate.copy()
        data_sources = [candidate.get('source', 'unknown')]
        
        try:
            candidate_name = candidate.get('name', '')
            
            # Enhance with GitHub data
            if not candidate.get('github_profile'):
                github_data = await self._find_github_profile(candidate_name, candidate.get('linkedin_url', ''))
                if github_data:
                    enhanced_candidate['github_profile'] = github_data
                    data_sources.append('github')
            
            # Enhance with Twitter data
            if not candidate.get('twitter_profile'):
                twitter_data = await self._find_twitter_profile(candidate_name)
                if twitter_data:
                    enhanced_candidate['twitter_profile'] = twitter_data
                    data_sources.append('twitter')
            
            # Enhance with personal website
            if not candidate.get('personal_website'):
                website_data = await self._find_personal_website(candidate_name)
                if website_data:
                    enhanced_candidate['personal_website'] = website_data
                    data_sources.append('website')
            
            enhanced_candidate['data_sources'] = data_sources
            enhanced_candidate['enhancement_timestamp'] = time.time()
            
            logger.debug(f"Enhanced {candidate_name} with {len(data_sources)} data sources")
            return enhanced_candidate
            
        except Exception as e:
            logger.error(f"Profile enhancement failed: {str(e)}")
            return enhanced_candidate
    
    async def _find_github_profile(self, name: str, linkedin_url: str = '') -> Optional[Dict[str, Any]]:
        """
        Find GitHub profile for a candidate
        
        Args:
            name: Candidate name
            linkedin_url: LinkedIn URL for additional context
            
        Returns:
            GitHub profile data or None
        """
        try:
            await self.github_limiter.acquire()
            
            # Generate possible GitHub usernames
            possible_usernames = self._generate_github_usernames(name)
            
            for username in possible_usernames:
                try:
                    github_data = await self._get_github_user_data(username)
                    if github_data and self._validate_github_match(github_data, name):
                        return github_data
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"GitHub profile search failed for {name}: {str(e)}")
            return None
    
    async def _find_twitter_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find Twitter profile for a candidate
        
        Args:
            name: Candidate name
            
        Returns:
            Twitter profile data or None
        """
        try:
            await self.twitter_limiter.acquire()
            
            # Generate possible Twitter handles
            possible_handles = self._generate_twitter_handles(name)
            
            for handle in possible_handles:
                try:
                    # Use Google search since Twitter API requires significant setup
                    search_query = f'site:twitter.com {handle} "{name}"'
                    results = await self._google_search(search_query, 3)
                    
                    for result in results:
                        if 'twitter.com/' in result.get('url', ''):
                            twitter_data = await self._extract_twitter_info(result)
                            if twitter_data:
                                return twitter_data
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Twitter profile search failed for {name}: {str(e)}")
            return None
    
    async def _find_personal_website(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find personal website for a candidate
        
        Args:
            name: Candidate name
            
        Returns:
            Personal website data or None
        """
        try:
            await self.general_limiter.acquire()
            
            # Search for personal domains
            search_queries = [
                f'"{name}" personal website OR blog OR portfolio',
                f'"{name}" site:github.io',
                f'"{name}" site:*.dev OR site:*.ai OR site:*.tech'
            ]
            
            for query in search_queries:
                try:
                    results = await self._google_search(query, 5)
                    
                    for result in results:
                        url = result.get('url', '')
                        if self._is_personal_website(url, name):
                            website_data = await self._extract_website_info(url, result)
                            if website_data:
                                return website_data
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Website search failed for {name}: {str(e)}")
            return None
    
    async def _google_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform Google search
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={max_results}"
        
        try:
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            for result in soup.find_all('div', class_='g')[:max_results]:
                link_elem = result.find('a')
                if not link_elem:
                    continue
                    
                url = link_elem.get('href', '')
                title_elem = result.find('h3')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                snippet_elem = (result.find('span', class_='st') or 
                              result.find('div', class_='s') or
                              result.find('div', class_='IsZvec'))
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                results.append({
                    'url': url,
                    'title': title,
                    'snippet': snippet
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Google search failed for query '{query}': {str(e)}")
            return []
    
    async def _github_api_search_users(self, keyword: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search GitHub users via API
        
        Args:
            keyword: Search keyword
            max_results: Maximum results
            
        Returns:
            List of GitHub user data
        """
        if not self.github_token:
            return []
        
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            params = {
                'q': f'{keyword} in:bio OR in:name',
                'type': 'Users',
                'per_page': min(max_results, 30)
            }
            
            url = 'https://api.github.com/search/users'
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                logger.warning(f"GitHub API search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"GitHub API search failed: {str(e)}")
            return []
    
    def _extract_tech_keywords(self, query: str) -> List[str]:
        """Extract technical keywords from query"""
        tech_terms = [
            'python', 'javascript', 'java', 'react', 'node', 'golang', 
            'rust', 'kubernetes', 'docker', 'aws', 'machine learning',
            'deep learning', 'ai', 'data science', 'backend', 'frontend',
            'full stack', 'devops', 'cloud', 'microservices'
        ]
        
        query_lower = query.lower()
        found_keywords = [term for term in tech_terms if term in query_lower]
        
        # Add general programming terms if none found
        if not found_keywords:
            found_keywords = ['python', 'javascript', 'engineer']
        
        return found_keywords[:5]  # Limit keywords
    
    def _generate_github_usernames(self, name: str) -> List[str]:
        """Generate possible GitHub usernames from name"""
        if not name:
            return []
        
        name_parts = name.lower().replace('.', '').split()
        if len(name_parts) < 2:
            return [name_parts[0]] if name_parts else []
        
        first, last = name_parts[0], name_parts[-1]
        
        return [
            f"{first}{last}",
            f"{first}_{last}",
            f"{first}-{last}",
            f"{first}.{last}",
            first,
            last,
            f"{first[0]}{last}",
            f"{first}{last[0]}"
        ]
    
    def _generate_twitter_handles(self, name: str) -> List[str]:
        """Generate possible Twitter handles from name"""
        return self._generate_github_usernames(name)  # Similar logic
    
    def _is_technical_role(self, query: str) -> bool:
        """Check if query is for a technical role"""
        tech_terms = [
            'engineer', 'developer', 'programmer', 'architect', 
            'technical', 'software', 'coding', 'programming',
            'backend', 'frontend', 'full stack', 'devops'
        ]
        
        query_lower = query.lower()
        return any(term in query_lower for term in tech_terms)
    
    def _is_duplicate_candidate(self, candidate: Dict[str, Any], candidates: List[Dict[str, Any]]) -> bool:
        """Check if candidate is already in the list"""
        candidate_url = candidate.get('linkedin_url', '')
        candidate_name = candidate.get('name', '').lower()
        
        for existing in candidates:
            existing_url = existing.get('linkedin_url', '')
            existing_name = existing.get('name', '').lower()
            
            # Check URL match
            if candidate_url and existing_url and candidate_url == existing_url:
                return True
            
            # Check name similarity
            if candidate_name and existing_name:
                # Simple name similarity check
                if candidate_name == existing_name:
                    return True
        
        return False
    
    def _score_data_completeness(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score candidates based on data completeness"""
        for candidate in candidates:
            score = 0
            data_sources = candidate.get('data_sources', [])
            
            # Base score from number of sources
            score += len(data_sources) * 25
            
            # Bonus for specific data types
            if candidate.get('github_profile'):
                score += 20
            if candidate.get('twitter_profile'):
                score += 10
            if candidate.get('personal_website'):
                score += 15
            
            # Bonus for rich profile data
            if candidate.get('experience_years', 0) > 0:
                score += 10
            if candidate.get('skills'):
                score += 5
            if candidate.get('location'):
                score += 5
            
            candidate['data_completeness_score'] = min(score, 100)
        
        return candidates
    
    async def _extract_linkedin_info(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract LinkedIn candidate info from search result"""
        # Implementation similar to LinkedInProfileScraper
        # This would extract basic LinkedIn profile info
        return None  # Placeholder
    
    async def _extract_github_info(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract GitHub candidate info"""
        # Implementation for GitHub user data extraction
        return None  # Placeholder
    
    async def _get_github_user_data(self, username: str) -> Optional[Dict[str, Any]]:
        """Get GitHub user data"""
        # Implementation for GitHub API calls
        return None  # Placeholder
    
    def _validate_github_match(self, github_data: Dict[str, Any], name: str) -> bool:
        """Validate if GitHub profile matches candidate"""
        # Implementation for matching validation
        return False  # Placeholder
    
    async def _extract_twitter_info(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract Twitter profile info"""
        # Implementation for Twitter data extraction
        return None  # Placeholder
    
    def _is_personal_website(self, url: str, name: str) -> bool:
        """Check if URL is likely a personal website"""
        # Implementation for website validation
        return False  # Placeholder
    
    async def _extract_website_info(self, url: str, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract personal website info"""
        # Implementation for website data extraction
        return None  # Placeholder
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'session'):
            self.session.close()
