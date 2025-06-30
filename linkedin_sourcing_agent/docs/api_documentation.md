# LinkedIn Sourcing Agent - API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Core Classes](#core-classes)
5. [Usage Examples](#usage-examples)
6. [API Reference](#api-reference)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

## Overview

The LinkedIn Sourcing Agent is a professional-grade Python package for automated candidate sourcing, scoring, and outreach generation. It provides a comprehensive suite of tools for technical recruiters and hiring managers.

### Key Features

- **Multi-source candidate scraping** (LinkedIn, GitHub, Stack Overflow)
- **AI-powered candidate scoring** with customizable criteria
- **Intelligent outreach message generation** (GPT-4 or open-source models)
- **Rate limiting and caching** for production use
- **Comprehensive logging and analytics**
- **CLI interface** for batch processing
- **Extensible architecture** for custom integrations

## Installation

### Requirements

- Python 3.8+
- pip or poetry package manager
- API keys for external services (optional)

### Install from PyPI

```bash
pip install linkedin-sourcing-agent
```

### Install from Source

```bash
git clone https://github.com/your-org/linkedin-sourcing-agent.git
cd linkedin-sourcing-agent
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/your-org/linkedin-sourcing-agent.git
cd linkedin-sourcing-agent
pip install -e ".[dev]"
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=30
BATCH_SIZE=5

# Caching
ENABLE_CACHING=true
CACHE_EXPIRY_HOURS=24

# Open Source Models (Optional)
USE_OPEN_SOURCE_MODEL=false
OPEN_SOURCE_MODEL_TYPE=ollama
OLLAMA_MODEL=llama3.2:3b

# Company Information
COMPANY_NAME=Your Company
RECRUITER_NAME=Your Name
```

### Configuration Templates

Generate configuration templates for different environments:

```python
from linkedin_sourcing_agent.config import create_config_file

# Create development configuration
create_config_file(".env.development", "development")

# Create production configuration  
create_config_file(".env.production", "production")

# Create free tier configuration
create_config_file(".env.free", "free_tier")
```

## Core Classes

### LinkedInSourcingAgent

The main orchestrator class that coordinates all operations.

```python
from linkedin_sourcing_agent import LinkedInSourcingAgent
from linkedin_sourcing_agent.utils.config_manager import ConfigManager

# Initialize with configuration
config_manager = ConfigManager()
config = config_manager.load_config()
agent = LinkedInSourcingAgent(config)
```

### ConfigManager

Handles configuration loading and validation.

```python
from linkedin_sourcing_agent.utils.config_manager import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config(".env")  # Load from specific file
config = config_manager.get_config()         # Get current config
```

### Rate Limiter

Manages API rate limiting to prevent hitting service limits.

```python
from linkedin_sourcing_agent.utils.rate_limiter import RateLimiter

rate_limiter = RateLimiter(max_requests=30, time_window_seconds=60)
await rate_limiter.acquire()  # Wait if necessary before making request
```

## Usage Examples

### Basic Usage

```python
import asyncio
from linkedin_sourcing_agent import LinkedInSourcingAgent
from linkedin_sourcing_agent.utils.config_manager import ConfigManager

async def main():
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Initialize agent
    agent = LinkedInSourcingAgent(config)
    
    # Job description
    job_description = """
    We are hiring a Senior Python Developer with ML experience.
    Requirements: 5+ years Python, TensorFlow/PyTorch, AWS experience.
    Location: San Francisco, CA
    Salary: $150,000 - $220,000 + equity
    """
    
    # Candidate data (typically from LinkedIn search)
    candidate = {
        "name": "John Smith",
        "linkedin_url": "https://linkedin.com/in/johnsmith",
        "headline": "Senior Python Developer | AI/ML Engineer",
        "location": "San Francisco, CA",
        "skills": ["Python", "TensorFlow", "AWS", "Docker"]
    }
    
    # Score candidate
    scored_candidate = await agent.score_candidate(candidate, job_description)
    print(f"Candidate score: {scored_candidate['score']:.1f}/10")
    
    # Generate personalized outreach
    if scored_candidate['score'] >= 7.0:
        outreach = await agent.generate_outreach(candidate, job_description)
        print(f"Outreach message:\n{outreach}")

# Run the example
asyncio.run(main())
```

### Batch Processing

```python
import asyncio
from linkedin_sourcing_agent import LinkedInSourcingAgent
from linkedin_sourcing_agent.utils.misc_utils import batch_process

async def process_candidates_batch(candidates, job_description):
    config_manager = ConfigManager()
    config = config_manager.load_config()
    agent = LinkedInSourcingAgent(config)
    
    async def process_single(candidate):
        try:
            scored = await agent.score_candidate(candidate, job_description)
            if scored['score'] >= 6.0:
                scored['outreach'] = await agent.generate_outreach(candidate, job_description)
            return scored
        except Exception as e:
            print(f"Error processing {candidate.get('name', 'Unknown')}: {e}")
            return None
    
    # Process in batches of 5
    results = await batch_process(candidates, 5, process_single)
    
    # Filter out None results (errors)
    return [r for r in results if r is not None]
```

### CLI Usage

```bash
# Search for candidates
linkedin-agent search --query "python developer" --location "San Francisco" --limit 10

# Process candidates from file
linkedin-agent process --input candidates.json --job-description job.txt --generate-outreach

# Setup open source models
linkedin-agent setup --model ollama

# Validate configuration
linkedin-agent validate --check-apis --check-models
```

## API Reference

### LinkedInSourcingAgent

#### `__init__(config: Dict[str, Any])`

Initialize the agent with configuration.

**Parameters:**
- `config`: Configuration dictionary containing API keys and settings

#### `async score_candidate(candidate: Dict[str, Any], job_description: str) -> Dict[str, Any]`

Score a candidate against a job description.

**Parameters:**
- `candidate`: Candidate profile data
- `job_description`: Job description text

**Returns:**
- Dictionary containing candidate data with added score and score_breakdown

**Example:**
```python
scored = await agent.score_candidate(candidate, job_description)
print(scored['score'])          # Overall score (0-10)
print(scored['score_breakdown']) # Detailed breakdown by category
```

#### `async generate_outreach(candidate: Dict[str, Any], job_description: str) -> str`

Generate personalized outreach message.

**Parameters:**
- `candidate`: Candidate profile data
- `job_description`: Job description text

**Returns:**
- Personalized outreach message string

#### `async search_candidates(query: str, location: str = None, limit: int = 10) -> List[Dict[str, Any]]`

Search for candidates (requires LinkedIn API access).

**Parameters:**
- `query`: Search query string
- `location`: Location filter (optional)
- `limit`: Maximum number of results

**Returns:**
- List of candidate dictionaries

### Scoring Components

#### CandidateFitScorer

Scores candidates based on job requirements.

```python
from linkedin_sourcing_agent.scoring import CandidateFitScorer

scorer = CandidateFitScorer(config)
score_result = await scorer.score_candidate(candidate, job_description)
```

#### MultiSourceScorer

Combines scores from multiple sources.

```python
from linkedin_sourcing_agent.scoring import MultiSourceScorer

multi_scorer = MultiSourceScorer(config)
enhanced_score = await multi_scorer.score_candidate(candidate, job_description)
```

### Outreach Generation

#### OutreachGenerator

Generates personalized outreach messages.

```python
from linkedin_sourcing_agent.generators import OutreachGenerator

generator = OutreachGenerator(config)
message = await generator.generate_message(candidate, job_description)
```

#### OpenSourceModelHandler

Handles open-source model integration for free alternatives.

```python
from linkedin_sourcing_agent.generators import OpenSourceModelHandler

handler = OpenSourceModelHandler(config)
message = await handler.generate_message(candidate, job_description)
```

## Error Handling

### Common Exceptions

#### `ValidationError`
Raised when candidate or job description data is invalid.

```python
from linkedin_sourcing_agent.utils.misc_utils import DataValidator

try:
    validated_candidate = DataValidator.validate_candidate(candidate)
except ValueError as e:
    print(f"Validation error: {e}")
```

#### `RateLimitError`
Raised when API rate limits are exceeded.

```python
from linkedin_sourcing_agent.utils.rate_limiter import RateLimitError

try:
    await agent.score_candidate(candidate, job_description)
except RateLimitError:
    print("Rate limit exceeded, please wait and retry")
```

#### `APIError`
Raised when external API calls fail.

```python
try:
    result = await agent.generate_outreach(candidate, job_description)
except Exception as e:
    if "API" in str(e):
        print(f"API error: {e}")
        # Fallback to template-based generation
```

### Error Recovery

```python
async def robust_processing(candidates, job_description):
    results = []
    
    for candidate in candidates:
        try:
            # Try full processing
            scored = await agent.score_candidate(candidate, job_description)
            
            if scored['score'] >= 6.0:
                try:
                    scored['outreach'] = await agent.generate_outreach(candidate, job_description)
                except Exception as e:
                    # Fallback to template
                    scored['outreach'] = f"Hi {candidate['name']}, I found your profile interesting..."
                    scored['outreach_method'] = 'template_fallback'
            
            results.append(scored)
            
        except Exception as e:
            # Log error and continue
            print(f"Failed to process {candidate.get('name', 'Unknown')}: {e}")
            continue
    
    return results
```

## Best Practices

### 1. Configuration Management

```python
# Use environment-specific configurations
config_manager = ConfigManager()

# Development
config = config_manager.load_config(".env.development")

# Production
config = config_manager.load_config(".env.production")

# Validate configuration
errors = config_manager.validate_config(config)
if errors:
    print(f"Configuration errors: {errors}")
```

### 2. Rate Limiting

```python
# Respect API rate limits
config = {
    'MAX_REQUESTS_PER_MINUTE': 30,  # Conservative limit
    'BATCH_SIZE': 5,                # Process in small batches
    'REQUEST_TIMEOUT': 30,          # Reasonable timeout
}

# Use built-in rate limiting
agent = LinkedInSourcingAgent(config)  # Automatically applies rate limiting
```

### 3. Caching

```python
# Enable caching for better performance
config = {
    'ENABLE_CACHING': True,
    'CACHE_EXPIRY_HOURS': 24,
    'CACHE_DIR': '.cache'
}

# Clear cache when needed
# cache_manager.clear_cache()  # Implementation specific
```

### 4. Error Handling

```python
async def process_with_retry(candidate, job_description, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await agent.score_candidate(candidate, job_description)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 5. Logging

```python
from linkedin_sourcing_agent.utils.logging_config import setup_logging

# Setup appropriate logging level
setup_logging(level="INFO")  # Production
setup_logging(level="DEBUG") # Development

# Use structured logging
import logging
logger = logging.getLogger(__name__)

logger.info("Processing candidate", extra={
    'candidate_name': candidate['name'],
    'job_title': job_title,
    'score': score
})
```

### 6. Monitoring and Analytics

```python
# Track processing metrics
class ProcessingMetrics:
    def __init__(self):
        self.total_processed = 0
        self.successful_scores = 0
        self.successful_outreach = 0
        self.errors = []
    
    def record_success(self, operation_type):
        if operation_type == 'score':
            self.successful_scores += 1
        elif operation_type == 'outreach':
            self.successful_outreach += 1
        self.total_processed += 1
    
    def record_error(self, error, candidate_name):
        self.errors.append({
            'error': str(error),
            'candidate': candidate_name,
            'timestamp': datetime.now().isoformat()
        })

# Usage
metrics = ProcessingMetrics()

try:
    scored = await agent.score_candidate(candidate, job_description)
    metrics.record_success('score')
except Exception as e:
    metrics.record_error(e, candidate['name'])
```

### 7. Production Deployment

```python
# Production configuration
PRODUCTION_CONFIG = {
    'MAX_REQUESTS_PER_MINUTE': 50,
    'BATCH_SIZE': 10,
    'ENABLE_CACHING': True,
    'LOG_LEVEL': 'INFO',
    'CONCURRENT_REQUESTS': 20,
    'RETRY_ATTEMPTS': 3,
    'SECURE_LOGGING': True,
    'ENABLE_ANALYTICS': True,
}

# Health check endpoint
async def health_check():
    try:
        # Test basic functionality
        test_candidate = {"name": "Test", "linkedin_url": "https://linkedin.com/in/test"}
        agent = LinkedInSourcingAgent(PRODUCTION_CONFIG)
        
        # This would be a lightweight test
        status = await agent.health_check()
        return {"status": "healthy", "details": status}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

For more examples and advanced usage patterns, see the [examples directory](../examples/) in the source code.
