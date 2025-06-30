"""
LinkedIn Sourcing Agent - Generators Package
Message generation and outreach components
"""

from .outreach_generator import OutreachGenerator, MessageTemplate, MessageType

# Conditionally import OpenSourceModelManager to avoid dependency issues
try:
    from .open_source_models import OpenSourceModelManager
    __all__ = [
        'OutreachGenerator',
        'MessageTemplate',
        'MessageType',
        'OpenSourceModelManager'
    ]
except ImportError:
    # transformers not available, skip OpenSourceModelManager
    __all__ = [
        'OutreachGenerator',
        'MessageTemplate',
        'MessageType'
    ]
