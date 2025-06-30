"""
Additional utility functions for LinkedIn Sourcing Agent
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable, Union


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text string
    """
    
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove common LinkedIn-specific text
    text = text.replace("LinkedIn", "").replace("| LinkedIn", "")
    
    return text.strip()


def extract_name_from_linkedin_url(url: str) -> str:
    """
    Extract name from LinkedIn URL
    
    Args:
        url: LinkedIn profile URL
        
    Returns:
        Extracted name or empty string
    """
    
    if not url or 'linkedin.com/in/' not in url:
        return ""
    
    try:
        # Extract username from URL
        username = url.split('linkedin.com/in/')[-1].split('/')[0].split('?')[0]
        
        # Convert username to readable name (basic heuristic)
        name_parts = username.replace('-', ' ').replace('_', ' ').split()
        return ' '.join(word.capitalize() for word in name_parts if word.isalpha())
        
    except Exception:
        return ""


def validate_linkedin_url(url: str) -> bool:
    """
    Validate LinkedIn profile URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid LinkedIn URL, False otherwise
    """
    
    if not url:
        return False
    
    return 'linkedin.com/in/' in url and len(url.split('/')[-1]) > 3


def format_score_breakdown(breakdown: Dict[str, float]) -> str:
    """
    Format score breakdown for display
    
    Args:
        breakdown: Dictionary of category scores
        
    Returns:
        Formatted score breakdown string
    """
    
    formatted = []
    for category, score in breakdown.items():
        category_name = category.replace('_', ' ').title()
        formatted.append(f"{category_name}: {score}/10")
    
    return " | ".join(formatted)


def mask_api_key(api_key: str) -> str:
    """
    Mask API key for secure logging
    
    Args:
        api_key: API key to mask
        
    Returns:
        Masked API key string
    """
    
    if not api_key or len(api_key) < 8:
        return "None"
    
    return api_key[:4] + "..." + api_key[-4:]


async def batch_process(
    items: List[Any], 
    batch_size: int, 
    process_func: Callable,
    *args,
    **kwargs
) -> List[Any]:
    """
    Process items in batches asynchronously
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        process_func: Async function to process each item
        *args: Additional arguments for process_func
        **kwargs: Additional keyword arguments for process_func
        
    Returns:
        List of results from processing
    """
    
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[process_func(item, *args, **kwargs) for item in batch],
            return_exceptions=True
        )
        results.extend(batch_results)
    
    return results


class DataValidator:
    """Validates and cleans candidate data"""
    
    @staticmethod
    def validate_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean candidate data
        
        Args:
            candidate: Candidate data dictionary
            
        Returns:
            Validated and cleaned candidate data
            
        Raises:
            ValueError: If required data is missing or invalid
        """
        
        # Required fields
        if not candidate.get('name'):
            candidate['name'] = extract_name_from_linkedin_url(candidate.get('linkedin_url', ''))
        
        if not candidate.get('linkedin_url'):
            raise ValueError("LinkedIn URL is required")
        
        if not validate_linkedin_url(candidate['linkedin_url']):
            raise ValueError("Invalid LinkedIn URL")
        
        # Clean text fields
        for field in ['headline', 'snippet', 'location', 'summary']:
            if field in candidate:
                candidate[field] = clean_text(candidate[field])
        
        # Ensure numeric fields
        candidate['experience_years'] = candidate.get('experience_years', 0)
        candidate['connections'] = candidate.get('connections', 0)
        
        # Ensure list fields
        for field in ['experience', 'education', 'skills']:
            if field not in candidate:
                candidate[field] = []
        
        return candidate
    
    @staticmethod
    def calculate_data_completeness(candidate: Dict[str, Any]) -> float:
        """
        Calculate data completeness score (0-1)
        
        Args:
            candidate: Candidate data dictionary
            
        Returns:
            Completeness score between 0 and 1
        """
        
        required_fields = ['name', 'linkedin_url', 'headline']
        optional_fields = ['education', 'experience', 'skills', 'location', 'summary']
        
        required_score = sum(1 for field in required_fields if candidate.get(field))
        optional_score = sum(1 for field in optional_fields if candidate.get(field))
        
        total_possible = len(required_fields) * 2 + len(optional_fields)  # Required fields count double
        total_actual = required_score * 2 + optional_score
        
        return total_actual / total_possible
    
    @staticmethod
    def validate_job_description(job_description: str) -> str:
        """
        Validate and clean job description
        
        Args:
            job_description: Job description text
            
        Returns:
            Cleaned job description
            
        Raises:
            ValueError: If job description is invalid
        """
        
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        # Clean and normalize
        cleaned = clean_text(job_description)
        
        if len(cleaned) < 50:
            raise ValueError("Job description too short (minimum 50 characters)")
        
        return cleaned


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem usage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number format
    
    Args:
        phone: Phone number string
        
    Returns:
        Normalized phone number
    """
    
    if not phone:
        return ""
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format based on length
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't normalize


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    
    if not text:
        return []
    
    import re
    
    # Split into words and filter
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
    }
    
    # Filter words
    keywords = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate basic similarity between two texts
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    
    if not text1 or not text2:
        return 0.0
    
    # Extract keywords from both texts
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    
    return intersection / union if union > 0 else 0.0


def generate_candidate_id(candidate: Dict[str, Any]) -> str:
    """
    Generate unique candidate ID from profile data
    
    Args:
        candidate: Candidate profile data
        
    Returns:
        Unique candidate ID
    """
    
    import hashlib
    
    # Use LinkedIn URL as primary identifier
    linkedin_url = candidate.get('linkedin_url', '')
    if linkedin_url:
        return hashlib.md5(linkedin_url.encode()).hexdigest()[:8]
    
    # Fallback to name + location
    name = candidate.get('name', '')
    location = candidate.get('location', '')
    fallback_string = f"{name}_{location}"
    
    return hashlib.md5(fallback_string.encode()).hexdigest()[:8]
