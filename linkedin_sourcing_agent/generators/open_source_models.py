"""
Open Source Model Handler for LinkedIn Sourcing Agent
Provides free alternatives to paid APIs for message generation
"""

import json
import requests
import asyncio
from typing import Dict, Any, Optional, List
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

from ..utils.logging_config import get_logger
from ..utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


class OpenSourceModelHandler:
    """
    Handles various open source models for free text generation
    Supports: Ollama, Hugging Face, Local Transformers
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Open Source Model Handler
        
        Args:
            config: Configuration dictionary containing model settings
        """
        self.config = config
        self.model_type = config.get('OPEN_SOURCE_MODEL_TYPE', 'ollama')
        self.use_open_source = config.get('USE_OPEN_SOURCE_MODEL', 'false').lower() == 'true'
        
        # Initialize model-specific attributes
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.rate_limiter = RateLimiter(
            max_requests=config.get('MAX_REQUESTS_PER_MINUTE', 30),
            time_window_seconds=60
        )
        
        if self.use_open_source:
            self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the selected open source model"""
        
        try:
            if self.model_type == 'ollama':
                self._init_ollama()
            elif self.model_type == 'huggingface':
                self._init_huggingface()
            elif self.model_type == 'local_transformers':
                self._init_local_transformers()
            else:
                logger.warning(f"Unknown model type: {self.model_type}")
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.model_type}: {str(e)}")
            logger.info("Falling back to template-based generation")
    
    def _init_ollama(self) -> None:
        """Initialize Ollama local model"""
        
        self.ollama_url = self.config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = self.config.get('OLLAMA_MODEL', 'llama3.2:3b')
        
        # Test connection
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Ollama connected successfully with model: {self.ollama_model}")
            else:
                raise Exception("Ollama not responding")
        except Exception as e:
            logger.warning(f"Ollama connection failed: {str(e)}")
            logger.info("Install Ollama and run: ollama pull llama3.2:3b")
    
    def _init_huggingface(self) -> None:
        """Initialize Hugging Face model"""
        
        model_name = self.config.get('HUGGINGFACE_MODEL', 'microsoft/DialoGPT-medium')
        
        try:
            # Use free Hugging Face Inference API
            self.hf_token = self.config.get('HUGGINGFACE_API_KEY')
            self.hf_model = model_name
            
            if self.hf_token:
                logger.info(f"Hugging Face API configured with model: {model_name}")
            else:
                logger.info("Hugging Face will use free tier (rate limited)")
                
        except Exception as e:
            logger.error(f"Hugging Face setup failed: {str(e)}")
    
    def _init_local_transformers(self) -> None:
        """Initialize local transformers model"""
        
        model_name = self.config.get('LOCAL_MODEL_NAME', 'distilgpt2')
        
        try:
            # Use a lightweight model for local processing
            self.pipeline = pipeline(
                'text-generation',
                model=model_name,
                tokenizer=model_name,
                device=0 if torch.cuda.is_available() else -1  # Use GPU if available
            )
            
            logger.info(f"Local transformer model loaded: {model_name}")
            
        except Exception as e:
            logger.error(f"Local transformer setup failed: {str(e)}")
            logger.info("Install transformers: pip install transformers torch")
    
    async def generate_message(self, candidate: Dict[str, Any], job_description: str) -> str:
        """
        Generate outreach message using open source models
        
        Args:
            candidate: Candidate data dictionary
            job_description: Job description for context
            
        Returns:
            Generated message string
        """
        
        if not self.use_open_source:
            return self._fallback_template(candidate)
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        try:
            prompt = self._create_prompt(candidate, job_description)
            
            if self.model_type == 'ollama':
                return await self._generate_ollama(prompt)
            elif self.model_type == 'huggingface':
                return await self._generate_huggingface(prompt)
            elif self.model_type == 'local_transformers':
                return await self._generate_local(prompt)
            else:
                return self._fallback_template(candidate)
                
        except Exception as e:
            logger.error(f"Open source generation failed: {str(e)}")
            return self._fallback_template(candidate)
    
    async def _generate_ollama(self, prompt: str) -> str:
        """Generate using Ollama"""
        
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 200,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('response', '').strip()
                return self._clean_message(message)
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {str(e)}")
            raise
    
    async def _generate_huggingface(self, prompt: str) -> str:
        """Generate using Hugging Face API"""
        
        try:
            headers = {}
            if self.hf_token:
                headers['Authorization'] = f'Bearer {self.hf_token}'
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 200,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
            
            api_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
            
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    message = result[0].get('generated_text', '').replace(prompt, '').strip()
                    return self._clean_message(message)
                else:
                    raise Exception("Unexpected response format")
            else:
                raise Exception(f"Hugging Face API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Hugging Face generation failed: {str(e)}")
            raise
    
    async def _generate_local(self, prompt: str) -> str:
        """Generate using local transformers"""
        
        try:
            if not self.pipeline:
                raise Exception("Local pipeline not initialized")
            
            # Generate text
            result = self.pipeline(
                prompt,
                max_length=200,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.pipeline.tokenizer.eos_token_id
            )
            
            if result and len(result) > 0:
                generated_text = result[0]['generated_text']
                message = generated_text.replace(prompt, '').strip()
                return self._clean_message(message)
            else:
                raise Exception("No text generated")
                
        except Exception as e:
            logger.error(f"Local generation failed: {str(e)}")
            raise
    
    def _create_prompt(self, candidate: Dict[str, Any], job_description: str) -> str:
        """Create a prompt for the open source model"""
        
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', '')
        location = candidate.get('location', '')
        
        # Create a concise prompt optimized for smaller models
        prompt = f"""Write a professional LinkedIn recruitment message.

Candidate: {name}
Background: {headline}
Location: {location}

Job: Software Engineer, ML Research at Windsurf
Company: Forbes AI 50 company building AI developer tools
Salary: $140-300k + equity
Location: Mountain View, CA

Write a brief, professional message (under 150 words):

Hi {name},"""
        
        return prompt
    
    def _clean_message(self, message: str) -> str:
        """Clean and format the generated message"""
        
        if not message:
            return "Hi there,\n\nI hope this message finds you well..."
        
        # Remove any incomplete sentences at the end
        sentences = message.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            message = '.'.join(sentences[:-1]) + '.'
        
        # Ensure proper greeting
        if not message.startswith('Hi '):
            message = f"Hi there,\n\n{message}"
        
        # Add signature
        if not message.endswith('\n\nBest regards,\n[Your Name]'):
            message += '\n\nBest regards,\n[Your Name]'
        
        return message.strip()
    
    def _fallback_template(self, candidate: Dict[str, Any]) -> str:
        """Fallback template when models fail"""
        
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', 'your professional background')
        
        return f"""Hi {name},

I hope this message finds you well. I came across your profile and was impressed by {headline}.

We're currently working with Windsurf (the company behind Codeium) on an exciting opportunity for a Software Engineer, ML Research role. This Forbes AI 50 company is building cutting-edge AI-powered developer tools.

The role involves training LLMs for code generation and offers competitive compensation ($140-300k + equity) in Mountain View.

Given your background, I thought this might be of interest to you. Would you be open to a brief conversation about this opportunity?

Best regards,
[Your Name]"""
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and configuration"""
        
        return {
            'model_type': self.model_type,
            'use_open_source': self.use_open_source,
            'model_initialized': self.model is not None or self.pipeline is not None,
            'rate_limiter_active': self.rate_limiter is not None
        }


def create_model_handler(config: Dict[str, Any]) -> OpenSourceModelHandler:
    """
    Factory function to create the appropriate model handler
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured OpenSourceModelHandler instance
    """
    return OpenSourceModelHandler(config)


# Setup guides for different models
SETUP_GUIDES = {
    'ollama': """
🦙 OLLAMA SETUP (Recommended - Completely Free & Local)

1. Install Ollama:
   - Windows: Download from https://ollama.ai/
   - Or: winget install Ollama.Ollama

2. Install a model:
   ollama pull llama3.2:3b     # 2GB, fast
   ollama pull mistral:7b      # 4GB, better quality
   ollama pull codellama:7b    # 4GB, code-focused

3. Start Ollama:
   ollama serve

4. Update .env:
   USE_OPEN_SOURCE_MODEL=true
   OPEN_SOURCE_MODEL_TYPE=ollama
   OLLAMA_MODEL=llama3.2:3b
""",
    
    'huggingface': """
🤗 HUGGING FACE SETUP (Free API with limits)

1. Create account at https://huggingface.co/
2. Get free API token from Settings > Access Tokens
3. Update .env:
   USE_OPEN_SOURCE_MODEL=true
   OPEN_SOURCE_MODEL_TYPE=huggingface
   HUGGINGFACE_API_KEY=your_token_here
   HUGGINGFACE_MODEL=microsoft/DialoGPT-medium

Note: Free tier has rate limits but no costs
""",
    
    'local_transformers': """
🏠 LOCAL TRANSFORMERS SETUP (Offline)

1. Install transformers:
   pip install transformers torch

2. Update .env:
   USE_OPEN_SOURCE_MODEL=true
   OPEN_SOURCE_MODEL_TYPE=local_transformers
   LOCAL_MODEL_NAME=distilgpt2

Note: First run downloads model (~500MB)
""",
    
    'template_only': """
📝 TEMPLATE ONLY (No AI, No Cost)

Just use built-in templates without any AI:
   USE_OPEN_SOURCE_MODEL=false

This uses smart templates that adapt based on candidate profile.
Still very effective for personalized outreach!
"""
}


def print_setup_guide(model_type: str = 'ollama') -> None:
    """
    Print setup guide for chosen model type
    
    Args:
        model_type: Type of model to show setup guide for
    """
    
    guide = SETUP_GUIDES.get(model_type, SETUP_GUIDES['ollama'])
    print(guide)
