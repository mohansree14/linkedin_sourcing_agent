"""
Unit tests package initialization
"""

# Test configuration
import sys
import os

# Add the parent directory to the path so we can import the main package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Test utilities
def mock_config():
    """Create a mock configuration for testing"""
    return {
        'OPENAI_API_KEY': 'test-key-123',
        'RAPIDAPI_KEY': 'test-rapid-key-456',
        'MAX_REQUESTS_PER_MINUTE': 30,
        'BATCH_SIZE': 5,
        'ENABLE_CACHING': True,
        'CACHE_EXPIRY_HOURS': 24,
        'USE_OPEN_SOURCE_MODEL': False,
        'COMPANY_NAME': 'Test Company',
        'RECRUITER_NAME': 'Test Recruiter',
        'LOG_LEVEL': 'INFO'
    }

def mock_candidate():
    """Create a mock candidate for testing"""
    return {
        'name': 'John Doe',
        'linkedin_url': 'https://linkedin.com/in/johndoe',
        'headline': 'Senior Software Engineer',
        'location': 'San Francisco, CA',
        'summary': 'Experienced software engineer with 8 years in Python development',
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS'],
        'experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'Tech Corp',
                'duration': '2020-Present',
                'description': 'Leading backend development team'
            }
        ],
        'education': [
            {
                'school': 'University of California',
                'degree': 'BS Computer Science',
                'year': '2016'
            }
        ]
    }

def mock_job_description():
    """Create a mock job description for testing"""
    return """
    We are looking for a Senior Software Engineer to join our team.
    
    Requirements:
    - 5+ years of software engineering experience
    - Strong Python and JavaScript skills
    - Experience with cloud platforms (AWS, GCP, Azure)
    - Bachelor's degree in Computer Science or related field
    
    Nice to have:
    - Experience with React and Node.js
    - DevOps experience
    - Machine learning background
    
    Location: San Francisco, CA
    Salary: $120,000 - $180,000 + equity
    """
