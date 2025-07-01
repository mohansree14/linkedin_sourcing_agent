# Deploying LinkedIn Sourcing Agent with Real Model

## Overview
The LinkedIn Sourcing Agent can be deployed in two modes:
1. **Demo Mode**: Uses mock data for testing and demonstration
2. **Real Model Mode**: Uses the actual LinkedIn Sourcing Agent package

## Current Configuration

The app is now configured to **automatically try the real model first** and fall back to demo mode if imports fail.

```python
DEMO_MODE = False  # Set to True to force demo mode, False to try real model first
```

## For Streamlit Cloud Deployment with Real Model

### 1. Repository Setup
The repository should include:
- ✅ `streamlit_app.py` (main application)
- ✅ `requirements.txt` (all dependencies)
- ✅ `linkedin_sourcing_agent/` (the actual package)
- ✅ `setup.py` (package installation)

### 2. Requirements.txt
Updated to include all necessary dependencies:
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
python-dotenv>=1.0.0
retrying>=1.3.3
tenacity>=8.1.0
openai>=1.3.0
google-generativeai>=0.3.0
aiohttp>=3.8.0
pydantic>=1.10.0
asyncio-throttle>=1.0.0
rich>=12.0.0
click>=8.0.0
numpy>=1.21.0
```

### 3. Installation on Streamlit Cloud
Streamlit Cloud will automatically:
1. Install dependencies from `requirements.txt`
2. The app will try to import the LinkedIn Sourcing Agent package
3. If successful, use the real model
4. If failed, automatically fall back to demo mode with realistic sample data

### 4. API Keys (Optional)
For full functionality, you can add these in Streamlit Cloud secrets:
- `OPENAI_API_KEY`: For AI-powered outreach generation
- `GOOGLE_GEMINI_API_KEY`: Alternative AI provider
- `LINKEDIN_API_KEY`: For LinkedIn API access (if available)

### 5. Local Development
To test locally with the real model:

```bash
# Install the package in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## Features Available with Real Model

When the real model is successfully loaded, you get:
- ✅ Actual LinkedIn profile scraping (with proper API keys)
- ✅ AI-powered candidate scoring
- ✅ Personalized outreach message generation
- ✅ Multi-source data integration
- ✅ Advanced analytics and insights
- ✅ Professional export capabilities

## Fallback to Demo Mode

If the real model can't be loaded (missing dependencies, import errors, etc.), the app automatically falls back to demo mode with:
- ✅ Realistic sample candidate data
- ✅ Simulated scoring algorithms
- ✅ Mock outreach message generation
- ✅ Full UI functionality for testing

## Current Status

✅ **App configured for real model deployment**
✅ **Automatic fallback to demo mode**
✅ **All dependencies included in requirements.txt**
✅ **Package structure ready for deployment**

The app will now attempt to use the real LinkedIn Sourcing Agent model when deployed to Streamlit Cloud, providing full functionality for candidate sourcing and outreach generation.
