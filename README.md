<<<<<<< HEAD
# 🎯 LinkedIn Sourcing Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A professional-grade, enterprise-ready LinkedIn candidate sourcing and outreach automation system built for the Synapse AI Hackathon.**

Transform your recruitment workflow with intelligent candidate discovery, automated scoring, personalized outreach generation, and seamless Excel/Google Sheets integration.

---

## 🌟 **Key Features**

### 🔍 **Intelligent Sourcing**
- Multi-source candidate discovery (LinkedIn, GitHub, Stack Overflow)
- Advanced search with location, skills, and experience filters
- Real-time candidate profile enrichment
- Duplicate detection and data deduplication

### 🎯 **Smart Scoring System**
- AI-powered candidate fit scoring (0-100 scale)
- Customizable scoring rubrics for different roles
- Technical skills assessment
- Experience relevance analysis
- Confidence level indicators

### ✉️ **Personalized Outreach**
- GPT-4 powered personalized message generation
- Template-based fallback system
- Role-specific messaging strategies
- Multi-channel outreach support (LinkedIn, Email)

### 📊 **Professional Export Options**
- **Excel Export**: Multi-sheet workbooks with formatted data
- **Google Sheets**: Real-time collaborative spreadsheets
- **JSON/CSV**: Raw data for custom integrations
- Clean company names (no technical clutter)
- Complete LinkedIn URLs for easy access

### 🛠️ **Production Ready**
- Rate limiting and API quota management
- Intelligent caching system
- Comprehensive logging and monitoring
- Error handling and recovery
- Scalable architecture

---

## 🚀 **Quick Start**

### **1. Installation**

```bash
# Clone the repository
git clone <your-repo-url>
cd AL

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### **2. Configuration**

Create your `.env` file:

```bash
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional

# LinkedIn APIs (Optional - will use demo data if not provided)
RAPIDAPI_KEY=your_rapidapi_key_here

# Environment
ENVIRONMENT=development

# Export Configuration
GOOGLE_SHEETS_SERVICE_ACCOUNT=service_account.json  # Optional
```

### **3. Basic Usage**

#### **Command Line Interface**

```bash
# Search for candidates and export to Excel
python -m linkedin_sourcing_agent.cli.main search \
  --query "Python Developer" \
  --location "San Francisco" \
  --limit 10 \
  --format excel

# Export to Google Sheets
python -m linkedin_sourcing_agent.cli.main search \
  --query "Machine Learning Engineer" \
  --location "New York" \
  --limit 15 \
  --format sheets \
  --sheets-name "ML_Engineers_2025"
```

#### **FastAPI Web Server**

```bash
# Start the web server
python api_server.py

# Server runs on http://localhost:8000
# API documentation: http://localhost:8000/docs
```

#### **Python API**

```python
from linkedin_sourcing_agent import LinkedInSourcingAgent

# Initialize the agent
agent = LinkedInSourcingAgent()

# Search for candidates
results = agent.search_candidates(
    query="Senior Frontend Developer",
    location="San Francisco, CA",
    limit=20
)

# Export to Excel
agent.export_manager.export_to_excel(
    results, 
    "frontend_developers.xlsx"
)
```

---

## 📋 **API Endpoints**

### **REST API** (FastAPI Server)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and system info |
| `/health` | GET | System health status |
| `/demo` | GET | Demo data for testing |
| `/source-candidates` | POST | Search and score candidates |

#### **Example API Usage**

```bash
# Search for candidates via API
curl -X POST "http://localhost:8000/source-candidates" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "DevOps Engineer",
    "location": "Seattle",
    "limit": 10,
    "job_description": "Looking for DevOps engineers with Kubernetes experience",
    "export_excel": true
  }'
```

---

## 📁 **Output Structure**

All outputs are organized in the `outputs/` directory:

```
outputs/
├── search_results/           # Raw search results
├── processed_candidates/     # Scored and processed data
├── excel_exports/           # Excel workbooks (.xlsx)
├── json_data/              # JSON format exports
└── README.md              # Output documentation
```

### **Excel Export Features**

Each Excel file contains multiple sheets:

- **Candidates**: Main candidate data with clean company names
- **Contact_Info**: Contact details and LinkedIn URLs
- **Experience_Education**: Professional background
- **Skills_Scoring**: Technical skills and fit scores
- **Multi_Source_Data**: GitHub, Twitter, additional profiles
- **Generated_Messages**: Personalized outreach messages
- **Analytics**: Search and scoring analytics
- **Summary**: Executive summary and statistics

---

## 🔧 **Advanced Configuration**

### **Custom Scoring Rubric**

```python
# Create custom scoring configuration
scoring_config = {
    "technical_skills": {
        "weight": 0.4,
        "required_skills": ["Python", "React", "AWS"],
        "bonus_skills": ["Docker", "Kubernetes"]
    },
    "experience": {
        "weight": 0.3,
        "min_years": 3,
        "relevant_industries": ["Tech", "Fintech"]
    },
    "education": {
        "weight": 0.2,
        "preferred_degrees": ["Computer Science", "Engineering"]
    },
    "location": {
        "weight": 0.1,
        "preferred_locations": ["San Francisco", "New York"]
    }
}
```

### **Google Sheets Setup**

1. Create a Google Cloud Service Account
2. Download the JSON credentials file
3. Save as `service_account.json` in project root
4. Share your target Google Sheet with the service account email

See `GOOGLE_SHEETS_SETUP.md` for detailed instructions.

---

## 📊 **Sample Output**

### **Clean Excel Export**

| Name | Company | LinkedIn_URL | Fit_Score | Title |
|------|---------|--------------|-----------|-------|
| Sarah Chen | Google | https://linkedin.com/in/sarah-chen-ml | 92 | Senior ML Engineer |
| Marcus Rodriguez | Meta | https://linkedin.com/in/marcus-rodriguez | 88 | Staff Software Engineer |
| Emma Thompson | Figma | https://linkedin.com/in/emma-thompson-frontend | 85 | Frontend Architect |

### **API Response**

```json
{
  "job_id": "job_1751295835",
  "candidates_found": 15,
  "processing_time_seconds": 2.34,
  "top_candidates": [
    {
      "name": "Sarah Chen",
      "linkedin_url": "https://linkedin.com/in/sarah-chen-ml",
      "headline": "Senior Machine Learning Engineer at Google",
      "location": "Mountain View, CA",
      "fit_score": 92,
      "confidence": "high",
      "key_characteristics": ["Python", "TensorFlow", "MLOps"],
      "outreach_message": "Hi Sarah, I was impressed by your ML work at Google..."
    }
  ],
  "excel_file": "outputs/excel_exports/search_ML_Engineer_20250630_160038.xlsx"
}
```

---

## 🛠️ **Development**

### **Project Structure**

```
linkedin_sourcing_agent/
├── core/                    # Core agent logic
├── scrapers/               # Data collection modules
├── scoring/                # Candidate scoring system
├── generators/             # Outreach message generation
├── utils/                  # Utilities and helpers
├── cli/                    # Command-line interface
├── config/                 # Configuration management
├── examples/               # Usage examples
├── tests/                  # Test suite
└── docs/                   # Documentation
```

### **Running Tests**

```bash
# Run all tests
python -m pytest

# Run specific test files
python -m pytest tests/test_linkedin_agent.py

# Run with coverage
python -m pytest --cov=linkedin_sourcing_agent
```

### **API Testing**

```bash
# Test API endpoints
python test_api.py

# Test Excel export functionality
python test_excel_api.py
```

---

## 📝 **CLI Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Search for candidates | `search --query "Python Dev" --limit 20` |
| `process` | Process existing candidate data | `process --input candidates.json` |
| `export` | Export data to various formats | `export --format excel --input data.json` |
| `setup` | Initial setup and configuration | `setup --create-config` |
| `validate` | Validate configuration and APIs | `validate --check-apis` |

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 **Support & Documentation**

- **📚 Documentation**: Check the `docs/` directory
- **❓ FAQ**: See `TECHNICAL_DOCS.md`
- **🔧 Troubleshooting**: Check `WHERE_ARE_MY_OUTPUTS.md`
- **📊 Google Sheets**: See `GOOGLE_SHEETS_SETUP.md`
- **🎯 Setup Guide**: See `FREE_SETUP_GUIDE.md`

---

## 🏆 **Hackathon Ready**

This project is specifically designed for the **Synapse AI Hackathon** with:

- ✅ **Professional package structure**
- ✅ **Complete API documentation**
- ✅ **Easy demo and testing**
- ✅ **Production-ready features**
- ✅ **Comprehensive export options**
- ✅ **Clean, judgeworthy codebase**

### **Quick Demo**

```bash
# Start the demo in 30 seconds
python api_server.py &
curl http://localhost:8000/demo
```

---

## 📈 **Performance & Scalability**

- **Rate Limiting**: 20 requests/minute for LinkedIn APIs
- **Caching**: Intelligent candidate data caching
- **Batch Processing**: Handle 100+ candidates efficiently  
- **Memory Management**: Optimized for large datasets
- **Error Recovery**: Automatic retry with exponential backoff

---

**Built with ❤️ for the Synapse AI Hackathon**

*Transform your recruitment process with AI-powered candidate sourcing and outreach automation.*
=======
# 🎯 LinkedIn Sourcing Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A professional-grade, enterprise-ready LinkedIn candidate sourcing and outreach automation system built for the Synapse AI Hackathon.**

Transform your recruitment workflow with intelligent candidate discovery, automated scoring, personalized outreach generation, and seamless Excel/Google Sheets integration.

---

## 🌟 **Key Features**

### 🔍 **Intelligent Sourcing**
- Multi-source candidate discovery (LinkedIn, GitHub, Stack Overflow)
- Advanced search with location, skills, and experience filters
- Real-time candidate profile enrichment
- Duplicate detection and data deduplication

### 🎯 **Smart Scoring System**
- AI-powered candidate fit scoring (0-100 scale)
- Customizable scoring rubrics for different roles
- Technical skills assessment
- Experience relevance analysis
- Confidence level indicators

### ✉️ **Personalized Outreach**
- GPT-4 powered personalized message generation
- Template-based fallback system
- Role-specific messaging strategies
- Multi-channel outreach support (LinkedIn, Email)

### 📊 **Professional Export Options**
- **Excel Export**: Multi-sheet workbooks with formatted data
- **Google Sheets**: Real-time collaborative spreadsheets
- **JSON/CSV**: Raw data for custom integrations
- Clean company names (no technical clutter)
- Complete LinkedIn URLs for easy access

### 🛠️ **Production Ready**
- Rate limiting and API quota management
- Intelligent caching system
- Comprehensive logging and monitoring
- Error handling and recovery
- Scalable architecture

---

## 🚀 **Quick Start**

### **1. Installation**

```bash
# Clone the repository
git clone <your-repo-url>
cd AL

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### **2. Configuration**

Create your `.env` file:

```bash
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional

# LinkedIn APIs (Optional - will use demo data if not provided)
RAPIDAPI_KEY=your_rapidapi_key_here

# Environment
ENVIRONMENT=development

# Export Configuration
GOOGLE_SHEETS_SERVICE_ACCOUNT=service_account.json  # Optional
```

### **3. Basic Usage**

#### **Command Line Interface**

```bash
# Search for candidates and export to Excel
python -m linkedin_sourcing_agent.cli.main search \
  --query "Python Developer" \
  --location "San Francisco" \
  --limit 10 \
  --format excel

# Export to Google Sheets
python -m linkedin_sourcing_agent.cli.main search \
  --query "Machine Learning Engineer" \
  --location "New York" \
  --limit 15 \
  --format sheets \
  --sheets-name "ML_Engineers_2025"
```

#### **FastAPI Web Server**

```bash
# Start the web server
python api_server.py

# Server runs on http://localhost:8000
# API documentation: http://localhost:8000/docs
```

#### **Python API**

```python
from linkedin_sourcing_agent import LinkedInSourcingAgent

# Initialize the agent
agent = LinkedInSourcingAgent()

# Search for candidates
results = agent.search_candidates(
    query="Senior Frontend Developer",
    location="San Francisco, CA",
    limit=20
)

# Export to Excel
agent.export_manager.export_to_excel(
    results, 
    "frontend_developers.xlsx"
)
```

---

## 📋 **API Endpoints**

### **REST API** (FastAPI Server)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and system info |
| `/health` | GET | System health status |
| `/demo` | GET | Demo data for testing |
| `/source-candidates` | POST | Search and score candidates |

#### **Example API Usage**

```bash
# Search for candidates via API
curl -X POST "http://localhost:8000/source-candidates" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "DevOps Engineer",
    "location": "Seattle",
    "limit": 10,
    "job_description": "Looking for DevOps engineers with Kubernetes experience",
    "export_excel": true
  }'
```

---

## 📁 **Output Structure**

All outputs are organized in the `outputs/` directory:

```
outputs/
├── search_results/           # Raw search results
├── processed_candidates/     # Scored and processed data
├── excel_exports/           # Excel workbooks (.xlsx)
├── json_data/              # JSON format exports
└── README.md              # Output documentation
```

### **Excel Export Features**

Each Excel file contains multiple sheets:

- **Candidates**: Main candidate data with clean company names
- **Contact_Info**: Contact details and LinkedIn URLs
- **Experience_Education**: Professional background
- **Skills_Scoring**: Technical skills and fit scores
- **Multi_Source_Data**: GitHub, Twitter, additional profiles
- **Generated_Messages**: Personalized outreach messages
- **Analytics**: Search and scoring analytics
- **Summary**: Executive summary and statistics

---

## 🔧 **Advanced Configuration**

### **Custom Scoring Rubric**

```python
# Create custom scoring configuration
scoring_config = {
    "technical_skills": {
        "weight": 0.4,
        "required_skills": ["Python", "React", "AWS"],
        "bonus_skills": ["Docker", "Kubernetes"]
    },
    "experience": {
        "weight": 0.3,
        "min_years": 3,
        "relevant_industries": ["Tech", "Fintech"]
    },
    "education": {
        "weight": 0.2,
        "preferred_degrees": ["Computer Science", "Engineering"]
    },
    "location": {
        "weight": 0.1,
        "preferred_locations": ["San Francisco", "New York"]
    }
}
```

### **Google Sheets Setup**

1. Create a Google Cloud Service Account
2. Download the JSON credentials file
3. Save as `service_account.json` in project root
4. Share your target Google Sheet with the service account email

See `GOOGLE_SHEETS_SETUP.md` for detailed instructions.

---

## 📊 **Sample Output**

### **Clean Excel Export**

| Name | Company | LinkedIn_URL | Fit_Score | Title |
|------|---------|--------------|-----------|-------|
| Sarah Chen | Google | https://linkedin.com/in/sarah-chen-ml | 92 | Senior ML Engineer |
| Marcus Rodriguez | Meta | https://linkedin.com/in/marcus-rodriguez | 88 | Staff Software Engineer |
| Emma Thompson | Figma | https://linkedin.com/in/emma-thompson-frontend | 85 | Frontend Architect |

### **API Response**

```json
{
  "job_id": "job_1751295835",
  "candidates_found": 15,
  "processing_time_seconds": 2.34,
  "top_candidates": [
    {
      "name": "Sarah Chen",
      "linkedin_url": "https://linkedin.com/in/sarah-chen-ml",
      "headline": "Senior Machine Learning Engineer at Google",
      "location": "Mountain View, CA",
      "fit_score": 92,
      "confidence": "high",
      "key_characteristics": ["Python", "TensorFlow", "MLOps"],
      "outreach_message": "Hi Sarah, I was impressed by your ML work at Google..."
    }
  ],
  "excel_file": "outputs/excel_exports/search_ML_Engineer_20250630_160038.xlsx"
}
```

---

## 🛠️ **Development**

### **Project Structure**

```
linkedin_sourcing_agent/
├── core/                    # Core agent logic
├── scrapers/               # Data collection modules
├── scoring/                # Candidate scoring system
├── generators/             # Outreach message generation
├── utils/                  # Utilities and helpers
├── cli/                    # Command-line interface
├── config/                 # Configuration management
├── examples/               # Usage examples
├── tests/                  # Test suite
└── docs/                   # Documentation
```

### **Running Tests**

```bash
# Run all tests
python -m pytest

# Run specific test files
python -m pytest tests/test_linkedin_agent.py

# Run with coverage
python -m pytest --cov=linkedin_sourcing_agent
```

### **API Testing**

```bash
# Test API endpoints
python test_api.py

# Test Excel export functionality
python test_excel_api.py
```

---

## 📝 **CLI Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Search for candidates | `search --query "Python Dev" --limit 20` |
| `process` | Process existing candidate data | `process --input candidates.json` |
| `export` | Export data to various formats | `export --format excel --input data.json` |
| `setup` | Initial setup and configuration | `setup --create-config` |
| `validate` | Validate configuration and APIs | `validate --check-apis` |

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 **Support & Documentation**

- **📚 Documentation**: Check the `docs/` directory
- **❓ FAQ**: See `TECHNICAL_DOCS.md`
- **🔧 Troubleshooting**: Check `WHERE_ARE_MY_OUTPUTS.md`
- **📊 Google Sheets**: See `GOOGLE_SHEETS_SETUP.md`
- **🎯 Setup Guide**: See `FREE_SETUP_GUIDE.md`

---

## 🏆 **Hackathon Ready**

This project is specifically designed for the **Synapse AI Hackathon** with:

- ✅ **Professional package structure**
- ✅ **Complete API documentation**
- ✅ **Easy demo and testing**
- ✅ **Production-ready features**
- ✅ **Comprehensive export options**
- ✅ **Clean, judgeworthy codebase**

### **Quick Demo**

```bash
# Start the demo in 30 seconds
python api_server.py &
curl http://localhost:8000/demo
```

---

## 📈 **Performance & Scalability**

- **Rate Limiting**: 20 requests/minute for LinkedIn APIs
- **Caching**: Intelligent candidate data caching
- **Batch Processing**: Handle 100+ candidates efficiently  
- **Memory Management**: Optimized for large datasets
- **Error Recovery**: Automatic retry with exponential backoff

---

**Built with ❤️ for the Synapse AI Hackathon**

*Transform your recruitment process with AI-powered candidate sourcing and outreach automation.*
>>>>>>> dfc24be5f9fccafa9d211b69a69c115a90911f12
