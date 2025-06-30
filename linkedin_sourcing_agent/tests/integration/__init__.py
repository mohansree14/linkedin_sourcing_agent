"""
Integration tests package initialization
"""

# Test configuration for integration tests
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Integration test utilities
def requires_api_keys(func):
    """Decorator to skip tests that require API keys"""
    import pytest
    
    def wrapper(*args, **kwargs):
        import os
        if not os.getenv('OPENAI_API_KEY') or not os.getenv('RAPIDAPI_KEY'):
            pytest.skip("API keys required for integration tests")
        return func(*args, **kwargs)
    
    return wrapper

def slow_test(func):
    """Decorator to mark tests as slow"""
    import pytest
    return pytest.mark.slow(func)

def integration_test_config():
    """Configuration for integration tests"""
    import os
    
    return {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'RAPIDAPI_KEY': os.getenv('RAPIDAPI_KEY', ''),
        'MAX_REQUESTS_PER_MINUTE': 5,  # Lower for integration tests
        'BATCH_SIZE': 2,
        'ENABLE_CACHING': True,
        'CACHE_EXPIRY_HOURS': 1,  # Shorter for tests
        'USE_OPEN_SOURCE_MODEL': False,
        'LOG_LEVEL': 'DEBUG',
        'REQUEST_TIMEOUT': 30
    }
