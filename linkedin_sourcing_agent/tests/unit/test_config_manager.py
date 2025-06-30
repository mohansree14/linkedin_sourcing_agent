"""
Unit tests for ConfigManager
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from linkedin_sourcing_agent.utils.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager"""
    
    def setup_method(self):
        """Setup for each test"""
        self.config_manager = ConfigManager()
    
    def test_init(self):
        """Test ConfigManager initialization"""
        assert self.config_manager is not None
        assert hasattr(self.config_manager, 'config')
    
    def test_load_config_from_dict(self):
        """Test loading configuration from dictionary"""
        test_config = {
            'OPENAI_API_KEY': 'test_key',
            'MAX_REQUESTS_PER_MINUTE': 30,
            'ENABLE_CACHING': True
        }
        
        config = self.config_manager.load_config_from_dict(test_config)
        
        assert config['OPENAI_API_KEY'] == 'test_key'
        assert config['MAX_REQUESTS_PER_MINUTE'] == 30
        assert config['ENABLE_CACHING'] is True
    
    def test_get_config_returns_copy(self):
        """Test that get_config returns a copy of configuration"""
        test_config = {'TEST_KEY': 'test_value'}
        self.config_manager.load_config_from_dict(test_config)
        
        config1 = self.config_manager.get_config()
        config2 = self.config_manager.get_config()
        
        # Should be equal but not the same object
        assert config1 == config2
        assert config1 is not config2
    
    def test_get_with_default(self):
        """Test getting configuration value with default"""
        test_config = {'EXISTING_KEY': 'existing_value'}
        self.config_manager.load_config_from_dict(test_config)
        
        # Test existing key
        assert self.config_manager.get('EXISTING_KEY') == 'existing_value'
        
        # Test non-existing key with default
        assert self.config_manager.get('NON_EXISTING_KEY', 'default') == 'default'
        
        # Test non-existing key without default
        assert self.config_manager.get('NON_EXISTING_KEY') is None
    
    @patch.dict(os.environ, {'TEST_ENV_VAR': 'env_value'})
    def test_load_from_environment(self):
        """Test loading from environment variables"""
        config = self.config_manager._load_from_environment()
        
        assert 'TEST_ENV_VAR' in config
        assert config['TEST_ENV_VAR'] == 'env_value'
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent config file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_file = Path(temp_dir) / "non_existent.env"
            
            # Should not raise exception, should return defaults
            config = self.config_manager.load_config(str(non_existent_file))
            
            # Should contain default values
            assert 'MAX_REQUESTS_PER_MINUTE' in config
            assert config['MAX_REQUESTS_PER_MINUTE'] == 30
    
    def test_load_config_with_env_file(self):
        """Test loading config from .env file"""
        env_content = """
# Test configuration
OPENAI_API_KEY=test_openai_key
MAX_REQUESTS_PER_MINUTE=50
ENABLE_CACHING=true
COMPANY_NAME=Test Company
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = self.config_manager.load_config(f.name)
                
                assert config['OPENAI_API_KEY'] == 'test_openai_key'
                assert config['MAX_REQUESTS_PER_MINUTE'] == 50
                assert config['ENABLE_CACHING'] is True
                assert config['COMPANY_NAME'] == 'Test Company'
                
            finally:
                os.unlink(f.name)
    
    def test_validate_config_success(self):
        """Test successful configuration validation"""
        valid_config = {
            'MAX_REQUESTS_PER_MINUTE': 30,
            'BATCH_SIZE': 5,
            'CACHE_EXPIRY_HOURS': 24
        }
        
        errors = self.config_manager.validate_config(valid_config)
        assert len(errors) == 0
    
    def test_validate_config_errors(self):
        """Test configuration validation with errors"""
        invalid_config = {
            'MAX_REQUESTS_PER_MINUTE': -1,  # Below minimum
            'BATCH_SIZE': 'invalid',        # Wrong type
            'CACHE_EXPIRY_HOURS': 200       # Above maximum
        }
        
        errors = self.config_manager.validate_config(invalid_config)
        assert len(errors) > 0
        assert 'MAX_REQUESTS_PER_MINUTE' in errors
        assert 'BATCH_SIZE' in errors
        assert 'CACHE_EXPIRY_HOURS' in errors
    
    def test_merge_configs(self):
        """Test merging configurations"""
        base_config = {
            'KEY1': 'value1',
            'KEY2': 'value2',
            'KEY3': 'value3'
        }
        
        override_config = {
            'KEY2': 'overridden_value2',
            'KEY4': 'value4'
        }
        
        merged = self.config_manager._merge_configs(base_config, override_config)
        
        assert merged['KEY1'] == 'value1'      # From base
        assert merged['KEY2'] == 'overridden_value2'  # Overridden
        assert merged['KEY3'] == 'value3'      # From base
        assert merged['KEY4'] == 'value4'      # From override
    
    def test_type_conversion(self):
        """Test automatic type conversion"""
        config_with_strings = {
            'MAX_REQUESTS_PER_MINUTE': '50',
            'ENABLE_CACHING': 'true',
            'CACHE_EXPIRY_HOURS': '12',
            'COMPANY_NAME': 'Test Company'
        }
        
        converted = self.config_manager._convert_types(config_with_strings)
        
        assert isinstance(converted['MAX_REQUESTS_PER_MINUTE'], int)
        assert converted['MAX_REQUESTS_PER_MINUTE'] == 50
        
        assert isinstance(converted['ENABLE_CACHING'], bool)
        assert converted['ENABLE_CACHING'] is True
        
        assert isinstance(converted['CACHE_EXPIRY_HOURS'], int)
        assert converted['CACHE_EXPIRY_HOURS'] == 12
        
        assert isinstance(converted['COMPANY_NAME'], str)
        assert converted['COMPANY_NAME'] == 'Test Company'
    
    def test_boolean_conversion(self):
        """Test boolean string conversion"""
        test_cases = {
            'true': True,
            'True': True,
            'TRUE': True,
            '1': True,
            'yes': True,
            'on': True,
            'false': False,
            'False': False,
            'FALSE': False,
            '0': False,
            'no': False,
            'off': False
        }
        
        for string_val, expected_bool in test_cases.items():
            converted = self.config_manager._convert_types({'TEST_BOOL': string_val})
            assert converted['TEST_BOOL'] == expected_bool, f"Failed for {string_val}"
    
    def test_required_keys_validation(self):
        """Test validation of required configuration keys"""
        # Test with missing required keys
        incomplete_config = {
            'MAX_REQUESTS_PER_MINUTE': 30
            # Missing OPENAI_API_KEY and RAPIDAPI_KEY
        }
        
        missing_keys = self.config_manager.get_missing_required_keys(incomplete_config)
        
        # Should identify missing API keys for production use
        expected_missing = ['OPENAI_API_KEY', 'RAPIDAPI_KEY']
        for key in expected_missing:
            assert key in missing_keys or not self.config_manager.is_production_mode()
    
    def test_config_schema_generation(self):
        """Test configuration schema generation"""
        schema = self.config_manager.get_config_schema()
        
        assert 'default_config' in schema
        assert 'validation_rules' in schema
        assert 'required_keys' in schema
        assert 'optional_keys' in schema
        
        # Check that schema contains expected keys
        assert 'MAX_REQUESTS_PER_MINUTE' in schema['default_config']
        assert 'ENABLE_CACHING' in schema['default_config']


if __name__ == '__main__':
    pytest.main([__file__])
