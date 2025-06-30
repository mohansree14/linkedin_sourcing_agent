"""
Configuration Manager

Professional configuration management for the LinkedIn Sourcing Agent.
Supports environment variables, configuration files, and validation.

Author: LinkedIn Sourcing Agent Team
Created: June 2025
"""

import os
import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class APIConfig:
    """API configuration settings"""
    openai_api_key: Optional[str] = None
    rapidapi_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    google_gemini_api_key: Optional[str] = None
    github_api_key: Optional[str] = None
    twitter_bearer_token: Optional[str] = None


@dataclass
class SystemConfig:
    """System configuration settings"""
    max_requests_per_minute: int = 30
    batch_size: int = 5
    enable_caching: bool = True
    cache_expiry_hours: int = 24
    enable_multi_source: bool = True
    use_open_source_model: bool = True
    open_source_model_type: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"


@dataclass
class AppConfig:
    """Complete application configuration"""
    api: APIConfig
    system: SystemConfig
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create configuration from dictionary"""
        return cls(
            api=APIConfig(**data.get('api', {})),
            system=SystemConfig(**data.get('system', {}))
        )


class ConfigManager:
    """
    Professional configuration manager with multiple sources support
    
    Supports:
    - Environment variables
    - .env files
    - JSON configuration files
    - Configuration validation
    - Environment-specific overrides
    """
    
    def __init__(self, config_path: str = ".env", environment: str = "development"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
            environment: Environment name (development, staging, production)
        """
        self.config_path = config_path
        self.environment = environment
        self.config_data: Dict[str, Any] = {}
        
        # Load configuration
        self._load_configuration()
        
        logger.info(f"Configuration loaded for environment: {environment}")
    
    def _load_configuration(self) -> None:
        """Load configuration from multiple sources"""
        # Load from .env file if available
        if DOTENV_AVAILABLE and os.path.exists(self.config_path):
            load_dotenv(self.config_path)
            logger.debug(f"Loaded .env file: {self.config_path}")
        
        # Load from JSON config file
        json_config_path = self.config_path.replace('.env', '.json')
        if os.path.exists(json_config_path):
            self._load_json_config(json_config_path)
        
        # Load from environment variables
        self._load_environment_variables()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_json_config(self, config_path: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
                self.config_data.update(json_config)
            logger.debug(f"Loaded JSON config: {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load JSON config {config_path}: {str(e)}")
    
    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables"""
        env_mappings = {
            # API Keys
            'OPENAI_API_KEY': 'OPENAI_API_KEY',
            'RAPIDAPI_KEY': 'RAPIDAPI_KEY',
            'HUGGINGFACE_API_KEY': 'HUGGINGFACE_API_KEY',
            'GOOGLE_GEMINI_API_KEY': 'GOOGLE_GEMINI_API_KEY',
            'GITHUB_API_KEY': 'GITHUB_API_KEY',
            'TWITTER_BEARER_TOKEN': 'TWITTER_BEARER_TOKEN',
            
            # System settings
            'MAX_REQUESTS_PER_MINUTE': 'MAX_REQUESTS_PER_MINUTE',
            'BATCH_SIZE': 'BATCH_SIZE',
            'ENABLE_CACHING': 'ENABLE_CACHING',
            'CACHE_EXPIRY_HOURS': 'CACHE_EXPIRY_HOURS',
            'ENABLE_MULTI_SOURCE': 'ENABLE_MULTI_SOURCE',
            'USE_OPEN_SOURCE_MODEL': 'USE_OPEN_SOURCE_MODEL',
            'OPEN_SOURCE_MODEL_TYPE': 'OPEN_SOURCE_MODEL_TYPE',
            'OLLAMA_BASE_URL': 'OLLAMA_BASE_URL',
            'OLLAMA_MODEL': 'OLLAMA_MODEL',
        }
        
        for config_key, env_key in env_mappings.items():
            value = os.getenv(env_key)
            if value is not None:
                self.config_data[config_key] = value
        
        logger.debug("Loaded environment variables")
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment-specific configuration overrides"""
        environment_configs = {
            'development': {
                'MAX_REQUESTS_PER_MINUTE': '10',  # Lower limits for dev
                'ENABLE_CACHING': 'true',
                'CACHE_EXPIRY_HOURS': '1'  # Shorter cache for dev
            },
            'staging': {
                'MAX_REQUESTS_PER_MINUTE': '20',
                'ENABLE_CACHING': 'true',
                'CACHE_EXPIRY_HOURS': '12'
            },
            'production': {
                'MAX_REQUESTS_PER_MINUTE': '30',
                'ENABLE_CACHING': 'true',
                'CACHE_EXPIRY_HOURS': '24'
            }
        }
        
        if self.environment in environment_configs:
            overrides = environment_configs[self.environment]
            for key, value in overrides.items():
                if key not in self.config_data:  # Don't override explicitly set values
                    self.config_data[key] = value
            
            logger.debug(f"Applied {self.environment} environment overrides")
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings"""
        warnings = []
        
        # Check for API keys (optional but recommended)
        api_keys = ['OPENAI_API_KEY', 'GOOGLE_GEMINI_API_KEY', 'RAPIDAPI_KEY']
        missing_keys = [key for key in api_keys if not self.config_data.get(key)]
        
        if missing_keys:
            warnings.append(f"Missing API keys: {', '.join(missing_keys)} (agent will use fallback modes)")
        
        # Validate numeric settings
        numeric_settings = {
            'MAX_REQUESTS_PER_MINUTE': (1, 100),
            'BATCH_SIZE': (1, 20),
            'CACHE_EXPIRY_HOURS': (1, 168)  # 1 hour to 1 week
        }
        
        for setting, (min_val, max_val) in numeric_settings.items():
            value = self.config_data.get(setting)
            if value:
                try:
                    num_value = int(value)
                    if not (min_val <= num_value <= max_val):
                        warnings.append(f"{setting} value {num_value} outside recommended range {min_val}-{max_val}")
                except ValueError:
                    warnings.append(f"{setting} must be a valid integer")
        
        # Log warnings
        for warning in warnings:
            logger.warning(warning)
        
        if not warnings:
            logger.info("Configuration validation passed")
    
    def get_config(self) -> Dict[str, Any]:
        """Get complete configuration dictionary"""
        return self.config_data.copy()
    
    def get_app_config(self) -> AppConfig:
        """Get structured application configuration"""
        return AppConfig(
            api=APIConfig(
                openai_api_key=self.config_data.get('OPENAI_API_KEY'),
                rapidapi_key=self.config_data.get('RAPIDAPI_KEY'),
                huggingface_api_key=self.config_data.get('HUGGINGFACE_API_KEY'),
                google_gemini_api_key=self.config_data.get('GOOGLE_GEMINI_API_KEY'),
                github_api_key=self.config_data.get('GITHUB_API_KEY'),
                twitter_bearer_token=self.config_data.get('TWITTER_BEARER_TOKEN')
            ),
            system=SystemConfig(
                max_requests_per_minute=int(self.config_data.get('MAX_REQUESTS_PER_MINUTE', 30)),
                batch_size=int(self.config_data.get('BATCH_SIZE', 5)),
                enable_caching=self.config_data.get('ENABLE_CACHING', 'true').lower() == 'true',
                cache_expiry_hours=int(self.config_data.get('CACHE_EXPIRY_HOURS', 24)),
                enable_multi_source=self.config_data.get('ENABLE_MULTI_SOURCE', 'true').lower() == 'true',
                use_open_source_model=self.config_data.get('USE_OPEN_SOURCE_MODEL', 'true').lower() == 'true',
                open_source_model_type=self.config_data.get('OPEN_SOURCE_MODEL_TYPE', 'ollama'),
                ollama_base_url=self.config_data.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
                ollama_model=self.config_data.get('OLLAMA_MODEL', 'llama3.2:3b')
            )
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config_data[key] = value
        logger.debug(f"Configuration updated: {key} = {value}")
    
    def save_config(self, output_path: str) -> None:
        """Save current configuration to JSON file"""
        try:
            config_to_save = self.get_app_config().to_dict()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise
    
    def reload(self) -> None:
        """Reload configuration from sources"""
        self.config_data.clear()
        self._load_configuration()
        logger.info("Configuration reloaded")


def load_config(config_path: str = ".env", environment: str = "development") -> Dict[str, Any]:
    """
    Convenience function to load configuration
    
    Args:
        config_path: Path to configuration file
        environment: Environment name
        
    Returns:
        Configuration dictionary
    """
    config_manager = ConfigManager(config_path, environment)
    return config_manager.get_config()
