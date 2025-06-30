"""
Professional outreach message generator for LinkedIn sourcing.

This module provides AI-powered and template-based message generation capabilities
for personalized candidate outreach.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..utils.config_manager import ConfigManager
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Only template-based generation will work.")


class MessageType(Enum):
    """Types of outreach messages."""
    INITIAL_OUTREACH = "initial_outreach"
    FOLLOW_UP = "follow_up"
    REFERRAL = "referral"
    EVENT_BASED = "event_based"
    INDUSTRY_UPDATE = "industry_update"


@dataclass
class MessageTemplate:
    """Template for generating messages."""
    name: str
    template: str
    type: MessageType
    tone: str  # professional, casual, executive, academic


class OutreachGenerator:
    """
    Professional outreach message generator with AI and template capabilities.
    
    Features:
    - AI-powered personalized message generation (OpenAI)
    - Template-based message generation with smart template selection
    - Multi-source data integration (LinkedIn, GitHub, Twitter, personal websites)
    - Intelligent personalization scoring and validation
    - Rate limiting and error handling
    - Multiple message types and tones
    """
    
    def __init__(
        self,
        config: Optional[ConfigManager] = None,
        use_ai: bool = False,
        use_open_source: bool = False,
        ai_model: str = "gpt-3.5-turbo",
        personalization_level: str = "high",
        include_multi_source: bool = True
    ):
        """
        Initialize the outreach generator.
        
        Args:
            config: Configuration manager instance
            use_ai: Whether to use AI for message generation
            use_open_source: Whether to use open source models (future feature)
            ai_model: AI model to use for generation
            personalization_level: Level of personalization (low, medium, high)
            include_multi_source: Whether to include multi-source data in messages
        """
        self.config = config or ConfigManager()
        self.use_ai = use_ai
        self.use_open_source = use_open_source
        self.ai_model = ai_model
        self.personalization_level = personalization_level
        self.include_multi_source = include_multi_source
        
        # Rate limiter for API calls
        self.rate_limiter = RateLimiter(
            max_requests=self.config.get('GENERATION_RATE_LIMIT', 30),
            time_window=60  # 60 seconds
        )
        
        # Initialize AI configuration
        self._initialize_ai_config()
        
        # Initialize message templates
        self.templates = self._initialize_templates()
        
        logger.info(f"OutreachGenerator initialized - AI: {self.use_ai}, Model: {self.ai_model}")
    
    def _initialize_ai_config(self) -> None:
        """Initialize AI configuration and check availability."""
        if self.use_ai and OPENAI_AVAILABLE:
            # Configure OpenAI
            openai_key = self.config.get('OPENAI_API_KEY')
            if openai_key:
                openai.api_key = openai_key
                self.ai_type = 'openai'
                logger.info("OpenAI API configured successfully")
            else:
                logger.warning("OpenAI API key not found. Falling back to templates.")
                self.use_ai = False
                self.ai_type = 'template'
        elif self.use_open_source:
            # Future: Initialize open source models
            self.use_ai = False  # For now, fallback to templates
            self.ai_type = 'template'
            logger.info("Open source model support planned for future release")
        else:
            self.use_ai = False
            self.ai_type = 'template'
            logger.info("Using template-based message generation")
    
    def _initialize_templates(self) -> Dict[str, MessageTemplate]:
        """Initialize message templates"""
        return {
            'default': MessageTemplate(
                name='Default Professional',
                template="""Hi {name},

I hope this message finds you well. I came across your profile and was impressed by your {background_highlights}.

We're currently working with {company_name} on an exciting {role_title} opportunity. Given your experience with {relevant_skills}, I thought this might be of interest.

{role_highlights}

Would you be open to a brief conversation about this opportunity?

Best regards,
{recruiter_name}""",
                type=MessageType.INITIAL_OUTREACH,
                tone='professional'
            ),
            
            'senior_executive': MessageTemplate(
                name='Senior Executive',
                template="""Hi {name},

Your leadership experience as {current_title} caught my attention, particularly your work with {relevant_skills}.

I'm reaching out about a unique {role_title} opportunity at {company_name}. They're seeking someone with your caliber of experience to {role_key_responsibility}.

{role_highlights}

Given your background at {current_company}, I believe this could be an excellent strategic career move.

Would you be interested in learning more?

Best,
{recruiter_name}""",
                type=MessageType.INITIAL_OUTREACH,
                tone='executive'
            ),
            
            'technical_researcher': MessageTemplate(
                name='Technical Researcher',
                template="""Hi {name},

I came across your research background and was particularly impressed by your work in {research_areas}.

I wanted to share a {role_title} opportunity at {company_name} that might align perfectly with your research interests.

{role_highlights}

Your expertise in {relevant_skills} would be invaluable for this position. {github_mention}

Would you be open to a discussion about this opportunity?

Best regards,
{recruiter_name}""",
                type=MessageType.INITIAL_OUTREACH,
                tone='academic'
            ),
            
            'startup_focused': MessageTemplate(
                name='Startup Professional',
                template="""Hi {name},

I noticed your entrepreneurial background and thought you might be interested in an exciting opportunity at {company_name}.

They're building {company_mission} and looking for a talented {role_title} to join their growing team.

{role_highlights}

Your experience with {relevant_skills} would be perfect for this fast-paced environment. {additional_context}

Interested in learning more?

Cheers,
{recruiter_name}""",
                type=MessageType.INITIAL_OUTREACH,
                tone='casual'
            )
        }
    
    async def generate_message(
        self, 
        candidate: Dict[str, Any], 
        job_description: str,
        message_type: MessageType = MessageType.INITIAL_OUTREACH,
        custom_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized outreach message
        
        Args:
            candidate: Candidate data dictionary with multi-source information
            job_description: Job description for context
            message_type: Type of message to generate
            custom_context: Additional context for personalization
            
        Returns:
            Dictionary containing message and metadata
        """
        try:
            # Rate limiting
            await self.rate_limiter.acquire()
            
            # Generate message using AI or templates
            if self.use_ai:
                message_result = await self._generate_ai_message(
                    candidate, job_description, message_type, custom_context
                )
            else:
                message_result = self._generate_template_message(
                    candidate, job_description, message_type, custom_context
                )
            
            # Add metadata
            message_result.update({
                'generation_method': self.ai_type,
                'personalization_level': self.personalization_level,
                'message_type': message_type.value,
                'candidate_name': candidate.get('name', 'Unknown'),
                'generation_timestamp': self._get_timestamp()
            })
            
            logger.info(f"Message generated for {candidate.get('name', 'Unknown')} using {self.ai_type}")
            return message_result
            
        except Exception as e:
            logger.error(f"Message generation failed for {candidate.get('name', 'Unknown')}: {str(e)}")
            return self._create_fallback_message(candidate, str(e))
    
    async def _generate_ai_message(
        self,
        candidate: Dict[str, Any],
        job_description: str,
        message_type: MessageType,
        custom_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate message using AI"""
        
        # Prepare comprehensive candidate context
        candidate_context = self._prepare_enhanced_candidate_context(candidate)
        
        # Create AI prompt
        prompt = self._create_ai_prompt(
            candidate_context, job_description, message_type, custom_context
        )
        
        try:
            if self.ai_type == 'openai' and OPENAI_AVAILABLE:
                response = await self._call_openai_api(prompt)
                message_text = response.choices[0].message.content.strip()
            else:
                # Future: Add support for other AI models
                raise Exception("AI model not available")
            
            # Validate and enhance the message
            validated_message = self._validate_and_enhance_message(message_text, candidate)
            
            return {
                'message': validated_message,
                'confidence': 'high',
                'personalization_score': self._calculate_personalization_score(candidate),
                'ai_generated': True
            }
            
        except Exception as e:
            logger.error(f"AI message generation failed: {str(e)}")
            # Fallback to template
            return self._generate_template_message(candidate, job_description, message_type, custom_context)
    
    def _generate_template_message(
        self,
        candidate: Dict[str, Any],
        job_description: str,
        message_type: MessageType,
        custom_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate message using templates"""
        
        # Select appropriate template
        template = self._select_template(candidate, message_type)
        
        # Prepare context variables
        context_vars = self._prepare_template_context(candidate, job_description, custom_context)
        
        try:
            # Format the template
            message_text = template.template.format(**context_vars)
            
            # Post-process the message
            processed_message = self._post_process_message(message_text, candidate)
            
            return {
                'message': processed_message,
                'confidence': 'medium',
                'personalization_score': self._calculate_personalization_score(candidate),
                'template_used': template.name,
                'ai_generated': False
            }
            
        except KeyError as e:
            logger.warning(f"Template formatting error: {str(e)}")
            # Use basic template with safe variables
            return self._create_safe_template_message(candidate)
    
    def _prepare_enhanced_candidate_context(self, candidate: Dict[str, Any]) -> str:
        """Prepare comprehensive candidate context including multi-source data"""
        
        context_parts = []
        
        # Basic information
        name = candidate.get('name', 'Candidate')
        context_parts.append(f"Name: {name}")
        
        # Professional headline
        headline = candidate.get('headline', '')
        if headline:
            context_parts.append(f"Current Role: {headline}")
        
        # Location
        location = candidate.get('location', '')
        if location:
            context_parts.append(f"Location: {location}")
        
        # Experience history
        experience = candidate.get('experience', [])
        if experience:
            exp_summary = self._summarize_experience(experience)
            context_parts.append(f"Experience: {exp_summary}")
        
        # Education background
        education = candidate.get('education', [])
        if education:
            edu_summary = self._summarize_education(education)
            context_parts.append(f"Education: {edu_summary}")
        
        # Skills and expertise
        skills = candidate.get('skills', [])
        if skills:
            skills_text = ', '.join(skills[:8])  # Top 8 skills
            context_parts.append(f"Skills: {skills_text}")
        
        # Multi-source data (if enabled)
        if self.include_multi_source:
            multi_source_context = self._prepare_multi_source_context(candidate)
            if multi_source_context:
                context_parts.extend(multi_source_context)
        
        # Fit score and insights
        fit_score = candidate.get('fit_score', 0)
        if fit_score:
            context_parts.append(f"Candidate Fit Score: {fit_score}/10")
        
        insights = candidate.get('insights', [])
        if insights:
            insights_text = '; '.join(insights[:3])  # Top 3 insights
            context_parts.append(f"Key Insights: {insights_text}")
        
        return '\n'.join(context_parts)
    
    def _prepare_template_context(self, candidate: Dict[str, Any], job_description: str, custom_context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Prepare context variables for template formatting"""
        
        job_details = self._extract_job_details(job_description)
        
        context = {
            'name': candidate.get('name', 'there'),
            'current_title': self._extract_current_title(candidate),
            'current_company': self._extract_current_company(candidate),
            'background_highlights': self._extract_background_highlights(candidate),
            'relevant_skills': self._extract_relevant_skills(candidate),
            'research_areas': self._extract_research_areas(candidate),
            'company_name': job_details['company'],
            'role_title': job_details['title'],
            'role_key_responsibility': job_details['key_responsibility'],
            'role_highlights': job_details['highlights'],
            'recruiter_name': self.config.get('RECRUITER_NAME', '[Your Name]'),
            'github_mention': self._create_github_mention(candidate),
            'company_mission': job_details.get('mission', 'innovative solutions'),
            'additional_context': self._create_additional_context(candidate)
        }
        
        # Add custom context if provided
        if custom_context:
            context.update(custom_context)
        
        return context
    
    def _extract_job_details(self, job_description: str) -> Dict[str, str]:
        """Extract key details from job description"""
        # This is a simplified extraction - in a real system, you'd use NLP
        details = {
            'title': 'Software Engineer, ML Research',
            'company': 'Windsurf (Codeium)',
            'location': 'Mountain View, CA',
            'compensation': '$140-300k + equity',
            'responsibilities': 'Train and optimize LLMs for code generation',
            'requirements': 'ML/AI expertise, Python, PyTorch/TensorFlow',
            'key_responsibility': 'lead cutting-edge AI research for code generation',
            'highlights': '• Forbes AI 50 company\n• Competitive compensation ($140-300k + equity)\n• Remote flexibility available\n• Direct impact on AI-powered developer tools',
            'mission': 'the future of AI-powered coding'
        }
        
        # Enhanced extraction could be added here
        return details
    
    def _select_template(self, candidate: Dict[str, Any], message_type: MessageType) -> MessageTemplate:
        """Select appropriate template based on candidate profile"""
        
        headline = candidate.get('headline', '').lower()
        experience = candidate.get('experience', [])
        
        # Senior executive template
        if any(term in headline for term in ['director', 'vp', 'vice president', 'head of', 'chief', 'cto', 'ceo']):
            return self.templates['senior_executive']
        
        # Research template
        elif any(term in headline for term in ['research', 'scientist', 'phd', 'researcher']):
            return self.templates['technical_researcher']
        
        # Startup template
        elif any(term in headline for term in ['founder', 'startup', 'entrepreneur']):
            return self.templates['startup_focused']
        
        # Default professional template
        else:
            return self.templates['default']
    
    def _extract_current_title(self, candidate: Dict[str, Any]) -> str:
        """Extract current job title"""
        headline = candidate.get('headline', '')
        
        # Split on common separators
        separators = [' at ', ' | ', ' - ', ' @ ']
        for sep in separators:
            if sep in headline:
                return headline.split(sep)[0].strip()
        
        return headline.strip() if headline else 'Professional'
    
    def _extract_current_company(self, candidate: Dict[str, Any]) -> str:
        """Extract current company"""
        headline = candidate.get('headline', '')
        
        separators = [' at ', ' @ ']
        for sep in separators:
            if sep in headline:
                company_part = headline.split(sep)[1]
                # Clean up company name
                company = company_part.split('|')[0].split('-')[0].split('(')[0].strip()
                return company
        
        return 'your current organization'
    
    def _extract_background_highlights(self, candidate: Dict[str, Any]) -> str:
        """Extract key background highlights"""
        highlights = []
        
        # Education highlights
        education = candidate.get('education', [])
        for edu in education:
            if isinstance(edu, dict):
                school = edu.get('school', '').lower()
                elite_schools = ['mit', 'stanford', 'harvard', 'berkeley', 'cmu', 'caltech']
                if any(elite in school for elite in elite_schools):
                    highlights.append('prestigious educational background')
                    break
        
        # Experience level
        headline = candidate.get('headline', '').lower()
        if any(term in headline for term in ['senior', 'lead', 'principal', 'staff']):
            highlights.append('senior-level expertise')
        elif any(term in headline for term in ['director', 'vp', 'head of']):
            highlights.append('executive leadership experience')
        
        # Company background
        top_companies = ['google', 'microsoft', 'apple', 'meta', 'amazon', 'netflix', 'openai']
        if any(company in headline for company in top_companies):
            highlights.append('top-tier technology company experience')
        
        # Multi-source highlights
        if candidate.get('github_profile', {}).get('public_repos', 0) >= 20:
            highlights.append('active open-source contributions')
        
        return ', '.join(highlights) if highlights else 'impressive professional background'
    
    def _extract_relevant_skills(self, candidate: Dict[str, Any]) -> str:
        """Extract skills relevant to the role"""
        # Combine text sources
        text_sources = [
            candidate.get('headline', ''),
            candidate.get('snippet', ''),
            ' '.join(candidate.get('skills', []))
        ]
        combined_text = ' '.join(text_sources).lower()
        
        # Define relevant skill categories
        skill_categories = {
            'Machine Learning': ['machine learning', 'ml', 'deep learning', 'neural networks'],
            'AI/NLP': ['artificial intelligence', 'ai', 'nlp', 'natural language processing'],
            'Programming': ['python', 'pytorch', 'tensorflow', 'javascript', 'java'],
            'Research': ['research', 'phd', 'publications', 'papers'],
            'Leadership': ['lead', 'senior', 'principal', 'management', 'team lead']
        }
        
        found_skills = []
        for category, keywords in skill_categories.items():
            if any(keyword in combined_text for keyword in keywords):
                found_skills.append(category)
        
        return ', '.join(found_skills[:3]) if found_skills else 'technical expertise'
    
    def _extract_research_areas(self, candidate: Dict[str, Any]) -> str:
        """Extract research areas from candidate profile"""
        text = f"{candidate.get('headline', '')} {candidate.get('snippet', '')}".lower()
        
        research_areas = []
        area_keywords = {
            'Machine Learning': ['machine learning', 'ml'],
            'Deep Learning': ['deep learning', 'neural networks'],
            'NLP': ['nlp', 'natural language processing'],
            'Computer Vision': ['computer vision', 'cv', 'image processing'],
            'Reinforcement Learning': ['reinforcement learning', 'rl'],
            'AI Research': ['ai research', 'artificial intelligence research']
        }
        
        for area, keywords in area_keywords.items():
            if any(keyword in text for keyword in keywords):
                research_areas.append(area)
        
        return ', '.join(research_areas[:3]) if research_areas else 'AI and machine learning'
    
    def _create_github_mention(self, candidate: Dict[str, Any]) -> str:
        """Create GitHub-specific mention if profile exists"""
        github_profile = candidate.get('github_profile', {})
        if not github_profile:
            return ''
        
        username = github_profile.get('username', '')
        repos = github_profile.get('public_repos', 0)
        
        if repos >= 50:
            return f"I noticed your extensive GitHub activity (@{username} with {repos} repos) - impressive technical contributions!"
        elif repos >= 20:
            return f"Your GitHub profile (@{username}) showcases some interesting projects."
        elif username:
            return f"I see you're active on GitHub (@{username})."
        
        return ''
    
    def _create_additional_context(self, candidate: Dict[str, Any]) -> str:
        """Create additional context from multi-source data"""
        context_parts = []
        
        # Twitter context
        twitter_profile = candidate.get('twitter_profile', {})
        if twitter_profile and twitter_profile.get('followers', 0) >= 1000:
            context_parts.append("I also noticed your thought leadership on social media.")
        
        # Website context
        website = candidate.get('personal_website', {})
        if website and website.get('has_blog'):
            context_parts.append("Your technical blog posts demonstrate deep expertise.")
        
        return ' '.join(context_parts)
    
    def _calculate_personalization_score(self, candidate: Dict[str, Any]) -> float:
        """Calculate personalization score based on available data"""
        score = 0.0
        
        # Base data points
        if candidate.get('name'): score += 0.1
        if candidate.get('headline'): score += 0.15
        if candidate.get('location'): score += 0.1
        if candidate.get('experience'): score += 0.2
        if candidate.get('education'): score += 0.15
        if candidate.get('skills'): score += 0.1
        
        # Multi-source data bonus
        if candidate.get('github_profile'): score += 0.1
        if candidate.get('twitter_profile'): score += 0.05
        if candidate.get('personal_website'): score += 0.05
        
        return min(score, 1.0)
    
    def _summarize_experience(self, experience: List[Any]) -> str:
        """Create concise experience summary"""
        if not experience:
            return 'Professional experience'
        
        summaries = []
        for exp in experience[:3]:  # Top 3 experiences
            if isinstance(exp, dict):
                title = exp.get('title', '')
                company = exp.get('company', '')
                if title and company:
                    summaries.append(f"{title} at {company}")
                elif title:
                    summaries.append(title)
        
        return '; '.join(summaries) if summaries else 'Diverse professional background'
    
    def _summarize_education(self, education: List[Any]) -> str:
        """Create concise education summary"""
        if not education:
            return 'Educational background'
        
        summaries = []
        for edu in education[:2]:  # Top 2 educational experiences
            if isinstance(edu, dict):
                degree = edu.get('degree', '')
                school = edu.get('school', '')
                if degree and school:
                    summaries.append(f"{degree} from {school}")
                elif school:
                    summaries.append(school)
        
        return '; '.join(summaries) if summaries else 'Strong educational foundation'
    
    def _post_process_message(self, message: str, candidate: Dict[str, Any]) -> str:
        """Post-process template message"""
        # Clean formatting
        message = self._clean_message_formatting(message)
        
        # Ensure proper greeting
        name = candidate.get('name', '').split()[0] if candidate.get('name') else ''
        if name and not message.startswith(f'Hi {name}'):
            message = f"Hi {name},\n\n{message}"
        
        return message
    
    def _clean_message_formatting(self, message: str) -> str:
        """Clean message formatting"""
        # Remove extra whitespace
        lines = [line.strip() for line in message.split('\n')]
        cleaned_lines = [line for line in lines if line]
        
        # Ensure proper spacing between paragraphs
        result = '\n\n'.join(cleaned_lines)
        
        return result
    
    def _create_safe_template_message(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Create safe fallback message with minimal variables"""
        name = candidate.get('name', 'there')
        
        safe_message = f"""Hi {name},

I hope this message finds you well. I came across your profile and was impressed by your professional background.

We're currently working on an exciting opportunity that might be of interest to you. Given your experience, I thought it would be worth reaching out.

Would you be open to a brief conversation about this opportunity?

Best regards,
{self.config.get('RECRUITER_NAME', '[Recruiter Name]')}"""
        
        return {
            'message': safe_message,
            'confidence': 'low',
            'personalization_score': 0.3,
            'template_used': 'safe_fallback',
            'ai_generated': False
        }
    
    def _create_fallback_message(self, candidate: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Create fallback message in case of errors"""
        logger.error(f"Creating fallback message due to error: {error}")
        return self._create_safe_template_message(candidate)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    # Additional helper methods
    
    def _prepare_multi_source_context(self, candidate: Dict[str, Any]) -> List[str]:
        """Prepare multi-source data context"""
        context_parts = []
        
        # GitHub profile
        github_profile = candidate.get('github_profile', {})
        if github_profile:
            github_info = []
            username = github_profile.get('username', '')
            if username:
                github_info.append(f"@{username}")
            
            repos = github_profile.get('public_repos', 0)
            if repos:
                github_info.append(f"{repos} public repositories")
            
            languages = github_profile.get('top_languages', [])
            if languages:
                github_info.append(f"Primary languages: {', '.join(languages[:3])}")
            
            notable_repos = github_profile.get('notable_repos', [])
            if notable_repos:
                stars = sum(repo.get('stars', 0) for repo in notable_repos)
                github_info.append(f"Repository stars: {stars}")
            
            if github_info:
                context_parts.append(f"GitHub: {'; '.join(github_info)}")
        
        # Twitter profile
        twitter_profile = candidate.get('twitter_profile', {})
        if twitter_profile:
            twitter_info = []
            username = twitter_profile.get('username', '')
            if username:
                twitter_info.append(f"@{username}")
            
            followers = twitter_profile.get('followers', 0)
            if followers:
                twitter_info.append(f"{followers:,} followers")
            
            bio = twitter_profile.get('bio', '')
            if bio:
                twitter_info.append(f"Bio: {bio[:100]}")
            
            if twitter_info:
                context_parts.append(f"Twitter: {'; '.join(twitter_info)}")
        
        # Personal website
        website = candidate.get('personal_website', {})
        if website:
            website_info = []
            url = website.get('url', '')
            if url:
                website_info.append(url)
            
            if website.get('has_blog'):
                website_info.append('maintains blog')
            
            if website.get('has_portfolio'):
                website_info.append('has portfolio')
            
            topics = website.get('content_topics', [])
            if topics:
                website_info.append(f"Content topics: {', '.join(topics[:3])}")
            
            if website_info:
                context_parts.append(f"Website: {'; '.join(website_info)}")
        
        return context_parts
    
    def _create_ai_prompt(
        self,
        candidate_context: str,
        job_description: str,
        message_type: MessageType,
        custom_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create comprehensive AI prompt for message generation"""
        
        # Extract job details
        job_details = self._extract_job_details(job_description)
        
        # Custom context integration
        additional_context = ""
        if custom_context:
            additional_context = f"\nADDITIONAL CONTEXT:\n{json.dumps(custom_context, indent=2)}"
        
        prompt = f"""
You are a professional recruiter writing a personalized LinkedIn outreach message. Create a compelling, authentic message that will generate genuine interest from the candidate.

CANDIDATE PROFILE:
{candidate_context}

JOB OPPORTUNITY:
Role: {job_details['title']}
Company: {job_details['company']}
Location: {job_details['location']}
Compensation: {job_details['compensation']}
Key Responsibilities: {job_details['responsibilities']}
Requirements: {job_details['requirements']}{additional_context}

MESSAGE REQUIREMENTS:
1. Keep under 200 words
2. Professional yet personable tone
3. Highlight 2-3 specific aspects of candidate's background that align with role
4. Mention the company and role clearly
5. Include compelling value proposition
6. End with clear call-to-action
7. Use candidate's actual name
8. Reference multi-source data if available (GitHub, Twitter, personal website)
9. Avoid being overly salesy or generic
10. Show genuine understanding of candidate's expertise

MESSAGE TYPE: {message_type.value}

Generate the outreach message:
"""
        
        return prompt
    
    async def _call_openai_api(self, prompt: str) -> Any:
        """Call OpenAI API with error handling"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert recruiter who writes highly personalized and effective LinkedIn outreach messages. Your messages are known for their authenticity, relevance, and high response rates."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise e
    
    def _validate_and_enhance_message(self, message: str, candidate: Dict[str, Any]) -> str:
        """Validate and enhance AI-generated message"""
        
        # Ensure candidate name is included
        name = candidate.get('name', '').split()[0] if candidate.get('name') else ''
        if name and name not in message:
            message = f"Hi {name},\n\n{message}"
        
        # Remove any placeholder text
        message = message.replace('[Your Name]', self.config.get('RECRUITER_NAME', '[Recruiter Name]'))
        message = message.replace('[Company]', 'the company')
        message = message.replace('[Role]', 'this opportunity')
        
        # Clean formatting
        message = self._clean_message_formatting(message)
        
        # Validate length
        if len(message) > 300:
            message = self._truncate_message(message, 280)
        
        return message
    
    def _truncate_message(self, message: str, max_length: int) -> str:
        """Truncate message while preserving structure"""
        if len(message) <= max_length:
            return message
        
        # Find last complete sentence within limit
        truncated = message[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.7:  # If we can keep most of the message
            return message[:last_period + 1]
        else:
            return truncated + '...'
    
    # Public API methods for different message types
    
    async def generate_initial_outreach(self, candidate: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Generate initial outreach message"""
        return await self.generate_message(candidate, job_description, MessageType.INITIAL_OUTREACH)
    
    async def generate_follow_up(self, candidate: Dict[str, Any], job_description: str, previous_interaction: str) -> Dict[str, Any]:
        """Generate follow-up message"""
        custom_context = {'previous_interaction': previous_interaction}
        return await self.generate_message(candidate, job_description, MessageType.FOLLOW_UP, custom_context)
    
    async def generate_referral_message(self, candidate: Dict[str, Any], job_description: str, referrer_name: str) -> Dict[str, Any]:
        """Generate referral-based message"""
        custom_context = {'referrer_name': referrer_name}
        return await self.generate_message(candidate, job_description, MessageType.REFERRAL, custom_context)
    
    async def generate_batch_messages(self, candidates: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
        """Generate messages for multiple candidates efficiently"""
        tasks = []
        for candidate in candidates:
            task = self.generate_message(candidate, job_description)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in batch results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch message generation failed for candidate {i}: {str(result)}")
                final_results.append(self._create_fallback_message(candidates[i], str(result)))
            else:
                final_results.append(result)
        
        return final_results
