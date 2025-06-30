# LinkedIn Sourcing Agent

A professional-grade Python package for automated LinkedIn candidate sourcing, intelligent scoring, and personalized outreach generation.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features

- **Multi-source Candidate Scraping**: LinkedIn, GitHub, Stack Overflow integration
- **AI-powered Scoring**: Intelligent candidate scoring against job requirements  
- **Personalized Outreach**: GPT-4 or open-source model powered message generation
- **Production Ready**: Rate limiting, caching, comprehensive logging, error handling
- **CLI Interface**: Command-line tools for batch processing and automation
- **Extensible Architecture**: Plugin system for custom integrations
- **Free Tier Support**: Open-source model integration (Ollama, Hugging Face)

## 📦 Installation

### Quick Start

```bash
pip install linkedin-sourcing-agent
```

### From Source

```bash
git clone https://github.com/your-org/linkedin-sourcing-agent.git
cd linkedin-sourcing-agent
pip install -e .
```

### Development Setup

```bash
git clone https://github.com/your-org/linkedin-sourcing-agent.git
cd linkedin-sourcing-agent
pip install -e ".[dev]"
pre-commit install
```

## ⚡ Quick Start

### 1. Configuration

Create a `.env` file:

```bash
# Required for advanced features
OPENAI_API_KEY=your_openai_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here

# Optional: Use free open-source models
USE_OPEN_SOURCE_MODEL=true
OPEN_SOURCE_MODEL_TYPE=ollama
OLLAMA_MODEL=llama3.2:3b

# Company information
COMPANY_NAME=Your Company Name
RECRUITER_NAME=Your Name
```

### 2. Basic Usage

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
    Senior Python Developer - AI/ML Focus
    Requirements: 5+ years Python, TensorFlow/PyTorch, AWS
    Location: San Francisco, CA | Salary: $150K-220K + equity
    """
    
    # Candidate data (from LinkedIn search)
    candidate = {
        "name": "John Smith",
        "linkedin_url": "https://linkedin.com/in/johnsmith-dev",
        "headline": "Senior Python Developer | AI/ML Engineer",
        "location": "San Francisco, CA",
        "skills": ["Python", "TensorFlow", "AWS", "Docker", "Kubernetes"]
    }
    
    # Score candidate (0-10 scale)
    scored_candidate = await agent.score_candidate(candidate, job_description)
    print(f"Candidate Score: {scored_candidate['score']:.1f}/10")
    
    # Generate personalized outreach
    if scored_candidate['score'] >= 7.0:
        outreach = await agent.generate_outreach(candidate, job_description)
        print(f"Outreach Message:\n{outreach}")

asyncio.run(main())
```

### 3. CLI Usage

```bash
# Search and score candidates
linkedin-agent search --query "python developer ML" --location "San Francisco" --limit 20

# Process candidates from file
linkedin-agent process --input candidates.json --job-description job.txt --output results.json

# Setup free open-source models
linkedin-agent setup --model ollama

# Batch process with outreach generation
linkedin-agent process --input candidates.json --generate-outreach --output results_with_outreach.json
```

## 🏗️ Architecture

```
linkedin_sourcing_agent/
├── core/                    # Main orchestration
│   └── agent.py            # LinkedInSourcingAgent class
├── scrapers/               # Data collection
│   ├── linkedin_scraper.py
│   └── multi_source_scraper.py
├── scoring/                # Candidate evaluation
│   ├── fit_scorer.py
│   └── multi_source_scorer.py
├── generators/             # Outreach generation
│   ├── outreach_generator.py
│   └── open_source_models.py
├── utils/                  # Shared utilities
│   ├── config_manager.py
│   ├── rate_limiter.py
│   ├── logging_config.py
│   └── misc_utils.py
├── cli/                    # Command line interface
├── config/                 # Configuration templates
├── examples/               # Usage examples
└── docs/                   # Documentation
```

## 🎯 Use Cases

### Technical Recruiting
- Automated candidate discovery and scoring
- Personalized outreach at scale
- Candidate pipeline management

### Sales & Business Development
- Lead qualification and scoring
- Personalized prospect outreach
- Account research automation

### Market Research
- Talent landscape analysis
- Competitor intelligence
- Industry trend analysis

## 🔧 Configuration Options

### API Keys (Optional)
```bash
OPENAI_API_KEY=sk-...           # For GPT-4 powered outreach
RAPIDAPI_KEY=...                # For LinkedIn data access
HUGGINGFACE_API_KEY=...         # For Hugging Face models
```

### Free Open-Source Models
```bash
USE_OPEN_SOURCE_MODEL=true
OPEN_SOURCE_MODEL_TYPE=ollama   # ollama, huggingface, local_transformers
OLLAMA_MODEL=llama3.2:3b        # Fast, lightweight model
```

### Performance Tuning
```bash
MAX_REQUESTS_PER_MINUTE=30      # Rate limiting
BATCH_SIZE=5                    # Batch processing size
ENABLE_CACHING=true             # Result caching
CACHE_EXPIRY_HOURS=24           # Cache duration
```

### Scoring Weights
```bash
SCORING_WEIGHTS='{
  "experience": 0.3,
  "skills": 0.25,
  "education": 0.2,
  "location": 0.15,
  "cultural_fit": 0.1
}'
```

## 📊 Scoring System

The agent uses a comprehensive 10-point scoring system:

| Score Range | Classification | Action |
|-------------|----------------|---------|
| 8.0 - 10.0  | Excellent Match | Priority outreach |
| 6.0 - 7.9   | Good Match | Standard outreach |
| 4.0 - 5.9   | Moderate Match | Consider for pipeline |
| 0.0 - 3.9   | Poor Match | Skip |

### Scoring Factors
- **Experience Relevance** (30%): Years and type of relevant experience
- **Skills Match** (25%): Technical and soft skills alignment
- **Education** (20%): Degree relevance and institution quality
- **Location** (15%): Geographic preferences and remote work
- **Cultural Fit** (10%): Company values and culture alignment

## 🔄 Open Source Model Setup

### Ollama (Recommended - Free & Local)

```bash
# Install Ollama
winget install Ollama.Ollama  # Windows
brew install ollama           # macOS

# Download model
ollama pull llama3.2:3b      # 2GB, fast
ollama pull mistral:7b       # 4GB, better quality

# Start service
ollama serve

# Configure
echo "USE_OPEN_SOURCE_MODEL=true" >> .env
echo "OPEN_SOURCE_MODEL_TYPE=ollama" >> .env
echo "OLLAMA_MODEL=llama3.2:3b" >> .env
```

### Hugging Face (Free API)

```bash
# Get free API token from https://huggingface.co/settings/tokens
echo "USE_OPEN_SOURCE_MODEL=true" >> .env
echo "OPEN_SOURCE_MODEL_TYPE=huggingface" >> .env
echo "HUGGINGFACE_API_KEY=your_token_here" >> .env
```

### Local Transformers (Offline)

```bash
pip install transformers torch

echo "USE_OPEN_SOURCE_MODEL=true" >> .env
echo "OPEN_SOURCE_MODEL_TYPE=local_transformers" >> .env
echo "LOCAL_MODEL_NAME=distilgpt2" >> .env
```

## 📈 Advanced Features

### Batch Processing with Analytics

```python
from linkedin_sourcing_agent.examples import AdvancedProcessor

processor = AdvancedProcessor(config)
results = await processor.process_batch(candidates, job_description)

# Get analytics
analytics = processor.generate_analytics_report()
print(f"Success rate: {analytics['summary']['success_rate']}")
print(f"Average score: {analytics['scoring_analytics']['average_score']}")
```

### Custom Scoring Weights

```python
custom_config = {
    **config,
    'SCORING_WEIGHTS': {
        'experience': 0.4,      # Prioritize experience
        'skills': 0.3,          # Technical skills important
        'education': 0.1,       # Less emphasis on education
        'location': 0.1,        # Remote-friendly
        'cultural_fit': 0.1
    }
}

agent = LinkedInSourcingAgent(custom_config)
```

### Multi-Source Scoring

```python
from linkedin_sourcing_agent.scoring import MultiSourceScorer

# Combine LinkedIn + GitHub + Stack Overflow data
multi_scorer = MultiSourceScorer(config)
enhanced_score = await multi_scorer.score_candidate(candidate, job_description)
```

## 🚢 Production Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "linkedin_sourcing_agent.cli"]
```

### Environment Variables

```bash
# Production settings
LOG_LEVEL=INFO
MAX_REQUESTS_PER_MINUTE=50
CONCURRENT_REQUESTS=20
ENABLE_ANALYTICS=true
ENABLE_CACHING=true
SECURE_LOGGING=true
```

### Health Checks

```python
from linkedin_sourcing_agent import LinkedInSourcingAgent

async def health_check():
    try:
        agent = LinkedInSourcingAgent(config)
        status = await agent.health_check()
        return {"status": "healthy", "details": status}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## 🔍 Troubleshooting

### Common Issues

**API Rate Limits**
```bash
# Reduce request rate
MAX_REQUESTS_PER_MINUTE=10
BATCH_SIZE=2
```

**Model Loading Errors**
```bash
# Check Ollama status
ollama list
ollama serve

# Alternative: Use template-only mode
USE_OPEN_SOURCE_MODEL=false
```

**Configuration Errors**
```bash
# Validate configuration
linkedin-agent validate --check-apis --check-models
```

### Debug Mode

```python
from linkedin_sourcing_agent.utils.logging_config import setup_logging

# Enable debug logging
setup_logging(level="DEBUG")

# Check configuration
config_manager = ConfigManager()
config = config_manager.load_config()
print(config_manager.validate_config(config))
```

## 📚 Documentation

- [API Documentation](docs/api_documentation.md)
- [Configuration Guide](docs/configuration.md)
- [Examples](examples/)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/your-org/linkedin-sourcing-agent.git
cd linkedin-sourcing-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
black .
flake8 .
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Hugging Face for open-source model ecosystem
- Ollama for local model serving
- The open-source community for inspiration and contributions

## 📞 Support

- 📧 Email: support@your-company.com
- 💬 Discord: [Join our community](https://discord.gg/your-invite)
- 📚 Documentation: [docs.your-site.com](https://docs.your-site.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/linkedin-sourcing-agent/issues)

---

**Made with ❤️ for the recruiting community**
