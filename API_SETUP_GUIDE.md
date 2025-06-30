# 🔑 API Setup Guide - Get Real LinkedIn Data

## Required API Keys for Full Functionality

### 1. **RapidAPI for LinkedIn Data** (Most Important)
- **Service**: RapidAPI LinkedIn Profile Scraper
- **Cost**: Free tier available (100 requests/month)
- **Setup**:
  1. Go to [RapidAPI LinkedIn API](https://rapidapi.com/search/linkedin)
  2. Sign up for RapidAPI account
  3. Subscribe to "LinkedIn Profile Scraper" or "LinkedIn API"
  4. Copy your API key
  5. Add to `.env`: `RAPIDAPI_KEY=your_key_here`

### 2. **OpenAI API** (For AI-Powered Features)
- **Service**: OpenAI GPT for message generation
- **Cost**: Pay-per-use (very affordable)
- **Setup**:
  1. Go to [OpenAI Platform](https://platform.openai.com/)
  2. Create account and add payment method
  3. Generate API key
  4. Add to `.env`: `OPENAI_API_KEY=your_key_here`

### 3. **Alternative Free Options**

#### Google Custom Search (Free 100 queries/day)
```env
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

#### GitHub API (Free 5000 requests/hour)
```env
GITHUB_TOKEN=your_github_token
```

## 🚀 Quick Start with Free APIs

1. **Get RapidAPI LinkedIn API** (15 minutes)
   - Most critical for finding candidates
   - Free tier gives you 100 searches/month
   - Enough for testing and small projects

2. **Optional: Add OpenAI** (5 minutes)
   - Enables AI-powered personalized messages
   - Costs ~$0.01 per message generated
   - Can use templates without this

3. **Test with Demo Data** (immediate)
   - We'll add sample data for testing
   - See results without any API setup

## 💡 Pro Tips

- Start with RapidAPI LinkedIn - it's the most important
- OpenAI is optional but makes messages much better
- Google/GitHub APIs help with data enrichment
- All APIs have free tiers to start with
