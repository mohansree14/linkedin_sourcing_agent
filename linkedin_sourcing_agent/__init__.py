"""
Professional LinkedIn Sourcing Agent
=====================================

A comprehensive Python package for automated LinkedIn candidate sourcing,
intelligent scoring, and personalized outreach generation.

Features:
- Multi-source candidate scraping (LinkedIn, GitHub, Stack Overflow)
- AI-powered candidate scoring with customizable criteria
- Intelligent outreach message generation (GPT-4 or open-source models)
- Professional rate limiting, caching, and error handling
- CLI interface for batch processing
- Extensible architecture for custom integrations

Author: Your Name
License: MIT
Version: 1.0.0
"""

from .core.agent import LinkedInSourcingAgent
from .utils.config_manager import ConfigManager
from .utils.logging_config import setup_logging, get_logger
from .utils.rate_limiter import RateLimiter
from .utils.misc_utils import DataValidator, batch_process

# Import major components for easy access
from .scrapers.linkedin_scraper import LinkedInProfileScraper
from .scrapers.multi_source_scraper import MultiSourceProfileScraper
from .scoring.fit_scorer import CandidateFitScorer
from .scoring.multi_source_scorer import MultiSourceScorer
from .generators.outreach_generator import OutreachGenerator

# Conditionally import OpenSourceModelHandler to avoid dependency issues
try:
    from .generators.open_source_models import OpenSourceModelHandler
except ImportError:
    # transformers not available, skip OpenSourceModelHandler
    OpenSourceModelHandler = None

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"
__description__ = "Professional LinkedIn candidate sourcing and outreach automation"
__url__ = "https://github.com/your-org/linkedin-sourcing-agent"

# Core exports
__all__ = [
    # Main orchestrator
    "LinkedInSourcingAgent",
    
    # Configuration and utilities
    "ConfigManager", 
    "setup_logging",
    "get_logger",
    "RateLimiter",
    "DataValidator",
    "batch_process",
    
    # Scrapers
    "LinkedInProfileScraper",
    "MultiSourceProfileScraper",
    
    # Scoring
    "CandidateFitScorer",
    "MultiSourceScorer",
    
    # Generators
    "OutreachGenerator",
    "OpenSourceModelHandler",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    "__url__"
]

# Package-level configuration
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Version compatibility check
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("LinkedIn Sourcing Agent requires Python 3.8 or higher")

# Optional dependency warnings
try:
    import openai
except ImportError:
    logging.getLogger(__name__).warning(
        "OpenAI package not found. GPT-powered outreach generation will not be available. "
        "Install with: pip install openai"
    )

try:
    import transformers
except ImportError:
    logging.getLogger(__name__).debug(
        "Transformers package not found. Local model support will be limited. "
        "Install with: pip install transformers torch"
    )
