# LinkedIn Sourcing Agent - Streamlit Cloud Deployment

## 🚀 Quick Deploy to Streamlit Cloud

This LinkedIn Sourcing Agent can be deployed to Streamlit Cloud for public access.

### Prerequisites

1. **GitHub Repository**: Push this code to a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

### Deployment Steps

#### 1. Prepare Your Repository

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial LinkedIn Sourcing Agent deployment"

# Add your GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/linkedin-sourcing-agent.git

# Push to GitHub
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/linkedin-sourcing-agent`
5. Set the main file path: `streamlit_app.py`
6. Click "Deploy!"

### Environment Variables (Optional)

For production deployment, you can set these environment variables in Streamlit Cloud:

- `OPENAI_API_KEY`: Your OpenAI API key for AI-powered features
- `GOOGLE_GEMINI_API_KEY`: Your Google Gemini API key
- `LINKEDIN_API_KEY`: LinkedIn API credentials (optional)

### App Features

✅ **Works without API keys** - Demo mode with realistic sample data  
✅ **Professional UI** - Modern, responsive design  
✅ **Candidate Search** - Job description-based candidate matching  
✅ **AI Scoring** - Intelligent candidate fit scoring  
✅ **Outreach Generation** - Personalized message creation  
✅ **Export Options** - Excel, JSON, and CSV downloads  
✅ **Analytics Dashboard** - Search history and insights  

### Configuration Files

The following files are configured for deployment:

- `.streamlit/config.toml` - Streamlit configuration
- `requirements.txt` - Python dependencies
- `streamlit_app.py` - Main application file
- `packages.txt` - System packages (if needed)

### Demo Mode

The app automatically falls back to demo mode if the LinkedIn Sourcing Agent package imports fail, ensuring it works even in restricted environments.

### Troubleshooting

If you encounter issues during deployment:

1. **Import Errors**: The app has robust fallback mechanisms and will run in demo mode
2. **Memory Issues**: Streamlit Cloud has memory limits; the app is optimized for efficiency
3. **Dependency Issues**: All dependencies are listed in `requirements.txt`

### Local Testing

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

### Support

For issues or questions about deployment, check:

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Community Forum](https://discuss.streamlit.io)
- This project's GitHub repository

---

**Ready to deploy?** Follow the steps above to get your LinkedIn Sourcing Agent live on Streamlit Cloud! 🎯
