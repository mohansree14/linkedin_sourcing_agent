# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy Steps

### 1. Repository Setup

```bash
# Initialize repository (if needed)
git init

# Add all files
git add .
git commit -m "LinkedIn Sourcing Agent - Ready for deployment"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/linkedin-sourcing-agent.git
git push -u origin main
```

### 2. Deploy to Streamlit Cloud

1. **Visit**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with GitHub
3. **Click** "New app"
4. **Select** your repository
5. **Set main file**: `app_streamlit_cloud.py`
6. **Deploy!**

## Alternative: Direct Deployment Link

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## Files Configured for Deployment

✅ `app_streamlit_cloud.py` - Streamlit Cloud optimized version  
✅ `requirements_streamlit.txt` - Minimal dependencies  
✅ `.streamlit/config.toml` - Streamlit configuration  
✅ `packages.txt` - System packages (if needed)  

## Features in Deployed Version

🎯 **Candidate Search** - Job description-based matching  
📊 **AI Scoring** - Intelligent candidate fit scoring  
💌 **Outreach Generation** - Personalized message creation  
📈 **Analytics** - Search history and insights  
📥 **Export Options** - Excel and JSON downloads  
🎨 **Professional UI** - Modern, responsive design  

## Demo Data

The deployed version uses realistic demo data, making it perfect for:
- Portfolio demonstrations
- Feature showcases  
- Interface testing
- Client presentations

## Environment Variables (Optional)

Add these in Streamlit Cloud settings for enhanced features:

- `OPENAI_API_KEY` - For AI-powered enhancements
- `GEMINI_API_KEY` - Alternative AI provider
- `LINKEDIN_API_KEY` - For real LinkedIn data

## Support

- 📖 [Streamlit Docs](https://docs.streamlit.io)
- 💬 [Community Forum](https://discuss.streamlit.io)
- 🐛 [GitHub Issues](https://github.com/YOUR_USERNAME/linkedin-sourcing-agent/issues)

---

**Ready to deploy?** Your LinkedIn Sourcing Agent will be live in minutes! 🎉
