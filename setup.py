"""
Setup configuration for LinkedIn Sourcing Agent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
try:
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    # Fallback requirements if file doesn't exist
    requirements = [
        "aiohttp>=3.8.0",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "pydantic>=1.10.0",
        "asyncio-throttle>=1.0.0",
        "rich>=12.0.0",
        "click>=8.0.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0"
    ]

# Development requirements
dev_requirements = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.20.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
    "pre-commit>=2.20.0",
    "isort>=5.10.0",
    "bandit>=1.7.0",
    "safety>=2.0.0"
]

# Optional requirements for different features
extras_require = {
    'dev': dev_requirements,
    'transformers': [
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "accelerate>=0.20.0"
    ],
    'full': [
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "accelerate>=0.20.0",
        "psycopg2-binary>=2.9.0",  # PostgreSQL support
        "redis>=4.3.0",            # Redis caching
        "celery>=5.2.0",           # Background tasks
        "prometheus-client>=0.14.0" # Metrics
    ]
}

setup(
    name="linkedin-sourcing-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Professional LinkedIn candidate sourcing, scoring, and outreach automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/linkedin-sourcing-agent",
    project_urls={
        "Bug Tracker": "https://github.com/your-org/linkedin-sourcing-agent/issues",
        "Documentation": "https://docs.your-site.com",
        "Source Code": "https://github.com/your-org/linkedin-sourcing-agent",
        "Changelog": "https://github.com/your-org/linkedin-sourcing-agent/blob/main/CHANGELOG.md"
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Human Resources",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Natural Language :: English",
        "Typing :: Typed"
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "linkedin-agent=linkedin_sourcing_agent.cli:main",
            "linkedin-sourcing-agent=linkedin_sourcing_agent.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "linkedin_sourcing_agent": [
            "config/*.py",
            "examples/*.py",
            "docs/*.md",
            "*.md",
            "*.txt"
        ]
    },
    zip_safe=False,
    keywords=[
        "linkedin", "recruitment", "sourcing", "ai", "automation", 
        "candidates", "outreach", "scoring", "hr", "hiring", 
        "machine-learning", "nlp", "gpt", "chatgpt"
    ],
    platforms=["any"],
    license="MIT",
    maintainer="Your Name",
    maintainer_email="your.email@example.com"
)
