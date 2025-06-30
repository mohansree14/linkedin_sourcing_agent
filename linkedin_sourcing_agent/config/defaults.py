"""
Configuration templates and defaults for LinkedIn Sourcing Agent
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


# Default configuration values
DEFAULT_CONFIG = {
    # API Configuration
    'OPENAI_API_KEY': '',
    'RAPIDAPI_KEY': '',
    'HUGGINGFACE_API_KEY': '',
    
    # Rate Limiting
    'MAX_REQUESTS_PER_MINUTE': 30,
    'BATCH_SIZE': 5,
    'REQUEST_TIMEOUT': 30,
    
    # Caching
    'ENABLE_CACHING': True,
    'CACHE_EXPIRY_HOURS': 24,
    'CACHE_DIR': '.cache',
    
    # Scoring
    'SCORING_WEIGHTS': {
        'experience': 0.3,
        'skills': 0.25,
        'education': 0.2,
        'location': 0.15,
        'cultural_fit': 0.1
    },
    'MIN_SCORE_THRESHOLD': 6.0,
    
    # Open Source Models
    'USE_OPEN_SOURCE_MODEL': False,
    'OPEN_SOURCE_MODEL_TYPE': 'ollama',
    'OLLAMA_BASE_URL': 'http://localhost:11434',
    'OLLAMA_MODEL': 'llama3.2:3b',
    'HUGGINGFACE_MODEL': 'microsoft/DialoGPT-medium',
    'LOCAL_MODEL_NAME': 'distilgpt2',
    
    # Outreach Generation
    'OUTREACH_TONE': 'professional',
    'OUTREACH_LENGTH': 'medium',
    'INCLUDE_SALARY_RANGE': True,
    'PERSONALIZATION_LEVEL': 'high',
    
    # Logging
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': 'linkedin_agent.log',
    'LOG_ROTATION': True,
    'LOG_MAX_SIZE': '10MB',
    'LOG_BACKUP_COUNT': 5,
    
    # Database (if using)
    'DATABASE_URL': '',
    'DATABASE_POOL_SIZE': 10,
    
    # Company Information
    'COMPANY_NAME': 'Your Company',
    'COMPANY_DESCRIPTION': 'Innovative tech company',
    'RECRUITER_NAME': 'Your Name',
    'RECRUITER_TITLE': 'Technical Recruiter',
    
    # Job Posting Defaults
    'DEFAULT_JOB_TITLE': 'Software Engineer',
    'DEFAULT_LOCATION': 'San Francisco, CA',
    'DEFAULT_SALARY_RANGE': '$120,000 - $200,000',
    'DEFAULT_BENEFITS': 'Health, Dental, Vision, 401k, Equity',
    
    # Advanced Features
    'ENABLE_MULTI_SOURCE': True,
    'ENABLE_BACKGROUND_PROCESSING': True,
    'ENABLE_ANALYTICS': True,
    'ENABLE_WEBHOOKS': False,
    'WEBHOOK_URL': '',
    
    # Performance Tuning
    'CONCURRENT_REQUESTS': 10,
    'RETRY_ATTEMPTS': 3,
    'RETRY_DELAY': 1.0,
    'EXPONENTIAL_BACKOFF': True,
    
    # Security
    'ENABLE_API_KEY_ROTATION': False,
    'API_KEY_ROTATION_DAYS': 30,
    'ENCRYPT_CACHE': False,
    'SECURE_LOGGING': True,
}


# Environment variable mappings
ENV_MAPPINGS = {
    'OPENAI_API_KEY': 'OPENAI_API_KEY',
    'RAPIDAPI_KEY': 'RAPIDAPI_KEY',
    'HUGGINGFACE_API_KEY': 'HUGGINGFACE_API_KEY',
    'MAX_REQUESTS_PER_MINUTE': 'MAX_REQUESTS_PER_MINUTE',
    'BATCH_SIZE': 'BATCH_SIZE',
    'ENABLE_CACHING': 'ENABLE_CACHING',
    'CACHE_EXPIRY_HOURS': 'CACHE_EXPIRY_HOURS',
    'USE_OPEN_SOURCE_MODEL': 'USE_OPEN_SOURCE_MODEL',
    'OPEN_SOURCE_MODEL_TYPE': 'OPEN_SOURCE_MODEL_TYPE',
    'OLLAMA_BASE_URL': 'OLLAMA_BASE_URL',
    'OLLAMA_MODEL': 'OLLAMA_MODEL',
    'LOG_LEVEL': 'LOG_LEVEL',
    'COMPANY_NAME': 'COMPANY_NAME',
    'RECRUITER_NAME': 'RECRUITER_NAME',
}


# Configuration validation rules
VALIDATION_RULES = {
    'MAX_REQUESTS_PER_MINUTE': {'type': int, 'min': 1, 'max': 100},
    'BATCH_SIZE': {'type': int, 'min': 1, 'max': 20},
    'CACHE_EXPIRY_HOURS': {'type': int, 'min': 1, 'max': 168},  # 1 week max
    'MIN_SCORE_THRESHOLD': {'type': float, 'min': 0.0, 'max': 10.0},
    'CONCURRENT_REQUESTS': {'type': int, 'min': 1, 'max': 50},
    'RETRY_ATTEMPTS': {'type': int, 'min': 0, 'max': 10},
    'RETRY_DELAY': {'type': float, 'min': 0.1, 'max': 60.0},
}


# Configuration templates for different use cases
CONFIG_TEMPLATES = {
    'development': {
        'LOG_LEVEL': 'DEBUG',
        'ENABLE_CACHING': True,
        'MAX_REQUESTS_PER_MINUTE': 10,
        'BATCH_SIZE': 2,
        'RETRY_ATTEMPTS': 1,
        'CONCURRENT_REQUESTS': 3,
    },
    
    'production': {
        'LOG_LEVEL': 'INFO',
        'ENABLE_CACHING': True,
        'MAX_REQUESTS_PER_MINUTE': 50,
        'BATCH_SIZE': 10,
        'RETRY_ATTEMPTS': 3,
        'CONCURRENT_REQUESTS': 20,
        'ENABLE_ANALYTICS': True,
        'SECURE_LOGGING': True,
    },
    
    'free_tier': {
        'LOG_LEVEL': 'WARNING',
        'MAX_REQUESTS_PER_MINUTE': 5,
        'BATCH_SIZE': 1,
        'ENABLE_CACHING': True,
        'CACHE_EXPIRY_HOURS': 48,
        'USE_OPEN_SOURCE_MODEL': True,
        'OPEN_SOURCE_MODEL_TYPE': 'ollama',
    },
    
    'enterprise': {
        'LOG_LEVEL': 'INFO',
        'MAX_REQUESTS_PER_MINUTE': 100,
        'BATCH_SIZE': 20,
        'CONCURRENT_REQUESTS': 50,
        'ENABLE_MULTI_SOURCE': True,
        'ENABLE_BACKGROUND_PROCESSING': True,
        'ENABLE_ANALYTICS': True,
        'ENABLE_WEBHOOKS': True,
        'DATABASE_POOL_SIZE': 50,
        'ENABLE_API_KEY_ROTATION': True,
        'ENCRYPT_CACHE': True,
    }
}


def generate_env_template(template_type: str = 'development') -> str:
    """
    Generate .env file template
    
    Args:
        template_type: Type of template to generate
        
    Returns:
        .env file content as string
    """
    
    template_config = CONFIG_TEMPLATES.get(template_type, CONFIG_TEMPLATES['development'])
    
    lines = [
        f"# LinkedIn Sourcing Agent Configuration ({template_type})",
        f"# Generated configuration template",
        "",
        "# =============================================================================",
        "# API KEYS (Required)",
        "# =============================================================================",
        "",
        "# OpenAI API Key for GPT-based outreach generation",
        "OPENAI_API_KEY=your_openai_api_key_here",
        "",
        "# RapidAPI Key for LinkedIn data access",
        "RAPIDAPI_KEY=your_rapidapi_key_here",
        "",
        "# Hugging Face API Key (optional, for open source models)",
        "HUGGINGFACE_API_KEY=your_huggingface_token_here",
        "",
        "# =============================================================================",
        "# RATE LIMITING & PERFORMANCE",
        "# =============================================================================",
        "",
    ]
    
    # Add configuration values
    config = {**DEFAULT_CONFIG, **template_config}
    
    sections = {
        'rate_limiting': ['MAX_REQUESTS_PER_MINUTE', 'BATCH_SIZE', 'REQUEST_TIMEOUT', 'CONCURRENT_REQUESTS'],
        'caching': ['ENABLE_CACHING', 'CACHE_EXPIRY_HOURS', 'CACHE_DIR'],
        'scoring': ['MIN_SCORE_THRESHOLD'],
        'open_source': ['USE_OPEN_SOURCE_MODEL', 'OPEN_SOURCE_MODEL_TYPE', 'OLLAMA_BASE_URL', 'OLLAMA_MODEL'],
        'outreach': ['OUTREACH_TONE', 'OUTREACH_LENGTH', 'INCLUDE_SALARY_RANGE', 'PERSONALIZATION_LEVEL'],
        'logging': ['LOG_LEVEL', 'LOG_FILE', 'LOG_ROTATION'],
        'company': ['COMPANY_NAME', 'COMPANY_DESCRIPTION', 'RECRUITER_NAME', 'RECRUITER_TITLE'],
    }
    
    for section_name, keys in sections.items():
        lines.append(f"# {section_name.replace('_', ' ').title()}")
        for key in keys:
            if key in config:
                value = config[key]
                if isinstance(value, bool):
                    value = str(value).lower()
                lines.append(f"{key}={value}")
        lines.append("")
    
    return "\n".join(lines)


def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate configuration values
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of validation errors (empty if valid)
    """
    
    errors = {}
    
    for key, rules in VALIDATION_RULES.items():
        if key not in config:
            continue
            
        value = config[key]
        
        # Type validation
        if 'type' in rules:
            expected_type = rules['type']
            if not isinstance(value, expected_type):
                try:
                    # Try to convert
                    if expected_type == int:
                        value = int(value)
                    elif expected_type == float:
                        value = float(value)
                    elif expected_type == bool:
                        value = str(value).lower() in ('true', '1', 'yes', 'on')
                    config[key] = value
                except (ValueError, TypeError):
                    errors[key] = f"Expected {expected_type.__name__}, got {type(value).__name__}"
                    continue
        
        # Range validation
        if 'min' in rules and value < rules['min']:
            errors[key] = f"Value {value} is below minimum {rules['min']}"
        if 'max' in rules and value > rules['max']:
            errors[key] = f"Value {value} is above maximum {rules['max']}"
    
    return errors


def get_config_schema() -> Dict[str, Any]:
    """
    Get configuration schema for documentation
    
    Returns:
        Configuration schema dictionary
    """
    
    return {
        'default_config': DEFAULT_CONFIG,
        'env_mappings': ENV_MAPPINGS,
        'validation_rules': VALIDATION_RULES,
        'templates': list(CONFIG_TEMPLATES.keys()),
        'required_keys': ['OPENAI_API_KEY', 'RAPIDAPI_KEY'],
        'optional_keys': [k for k in DEFAULT_CONFIG.keys() if k not in ['OPENAI_API_KEY', 'RAPIDAPI_KEY']]
    }


def create_config_file(file_path: str, template_type: str = 'development') -> None:
    """
    Create configuration file
    
    Args:
        file_path: Path to create config file
        template_type: Type of template to use
    """
    
    content = generate_env_template(template_type)
    
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == '__main__':
    # Generate example configuration files
    for template_type in CONFIG_TEMPLATES.keys():
        filename = f"config_{template_type}.env"
        create_config_file(filename, template_type)
        print(f"Created {filename}")
