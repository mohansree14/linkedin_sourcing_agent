"""
Demo data generator for testing LinkedIn Sourcing Agent without API keys.

This module provides realistic sample candidate data for testing and demonstration
purposes when API keys are not available.
"""

import json
import random
from typing import Dict, List, Any
from datetime import datetime, timedelta

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class DemoDataGenerator:
    """Generate realistic demo candidate data for testing"""
    
    def __init__(self):
        self.sample_candidates = self._create_sample_candidates()
        self.sample_companies = [
            "Google", "Microsoft", "Apple", "Meta", "Amazon", "Netflix", "OpenAI",
            "Uber", "Airbnb", "Stripe", "Databricks", "Snowflake", "Figma",
            "Notion", "Linear", "Vercel", "Supabase", "PlanetScale"
        ]
        self.sample_skills = [
            "Python", "JavaScript", "React", "Node.js", "TypeScript", "Go",
            "Rust", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow",
            "AWS", "GCP", "Docker", "Kubernetes", "PostgreSQL", "Redis",
            "GraphQL", "REST APIs", "Microservices", "System Design"
        ]
    
    def generate_candidates(self, query: str, location: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generate demo candidates based on search parameters
        
        Args:
            query: Search query (e.g., "Python developer")
            location: Location filter
            limit: Number of candidates to generate
            
        Returns:
            List of candidate dictionaries
        """
        logger.info(f"Generating {limit} demo candidates for query: '{query}'")
        
        # Filter candidates based on query
        relevant_candidates = self._filter_candidates_by_query(query)
        
        # Randomly select candidates
        selected = random.sample(relevant_candidates, min(limit, len(relevant_candidates)))
        
        # Add location if specified
        if location:
            for candidate in selected:
                candidate['location'] = self._get_location_variation(location)
        
        # Add search metadata
        for i, candidate in enumerate(selected):
            candidate.update({
                'search_rank': i + 1,
                'search_query': query,
                'search_timestamp': datetime.now().isoformat(),
                'data_source': 'demo_generator',
                'confidence_score': random.uniform(0.7, 0.95),
                # Ensure linkedin_url is set from profile_url
                'linkedin_url': candidate.get('profile_url', candidate.get('linkedin_url', ''))
            })
        
        logger.info(f"Generated {len(selected)} demo candidates")
        return selected
    
    def _create_sample_candidates(self) -> List[Dict[str, Any]]:
        """Create comprehensive sample candidate profiles"""
        return [
            {
                'name': 'Sarah Chen',
                'headline': 'Senior Machine Learning Engineer at Google',
                'location': 'Mountain View, CA',
                'snippet': 'ML engineer with 8+ years building production ML systems. Led teams developing recommendation engines and NLP models.',
                'profile_url': 'https://linkedin.com/in/sarah-chen-ml',
                'image_url': 'https://example.com/avatar1.jpg',
                'experience': [
                    {
                        'title': 'Senior ML Engineer',
                        'company': 'Google',
                        'duration': '2021 - Present',
                        'description': 'Lead ML infrastructure team, built recommendation systems serving 1B+ users'
                    },
                    {
                        'title': 'ML Engineer',
                        'company': 'Uber',
                        'duration': '2019 - 2021',
                        'description': 'Developed fraud detection models, improved accuracy by 25%'
                    }
                ],
                'education': [
                    {
                        'degree': 'MS Computer Science',
                        'school': 'Stanford University',
                        'year': '2019'
                    }
                ],
                'skills': ['Python', 'PyTorch', 'TensorFlow', 'MLOps', 'Kubernetes', 'GCP'],
                'github_profile': {
                    'username': 'sarah-chen-ml',
                    'public_repos': 45,
                    'followers': 1200,
                    'top_languages': ['Python', 'Jupyter Notebook', 'Go'],
                    'notable_repos': [
                        {'name': 'ml-pipeline-tools', 'stars': 890, 'description': 'Production ML pipeline utilities'},
                        {'name': 'pytorch-examples', 'stars': 234, 'description': 'PyTorch learning examples'}
                    ]
                },
                'twitter_profile': {
                    'username': 'sarahchen_ml',
                    'followers': 5600,
                    'bio': 'ML Engineer @Google • Building AI systems that matter • Thoughts on ML in production'
                }
            },
            {
                'name': 'Marcus Rodriguez',
                'headline': 'Staff Software Engineer at Meta • Ex-Netflix',
                'location': 'San Francisco, CA',
                'snippet': 'Full-stack engineer specializing in scalable systems. Built infrastructure serving 500M+ users.',
                'profile_url': 'https://linkedin.com/in/marcus-rodriguez',
                'image_url': 'https://example.com/avatar2.jpg',
                'experience': [
                    {
                        'title': 'Staff Software Engineer',
                        'company': 'Meta',
                        'duration': '2022 - Present',
                        'description': 'Lead Instagram backend infrastructure, reduced latency by 40%'
                    },
                    {
                        'title': 'Senior Software Engineer',
                        'company': 'Netflix',
                        'duration': '2020 - 2022',
                        'description': 'Built video streaming infrastructure, handled 200M concurrent users'
                    }
                ],
                'education': [
                    {
                        'degree': 'BS Computer Engineering',
                        'school': 'UC Berkeley',
                        'year': '2018'
                    }
                ],
                'skills': ['Python', 'Go', 'React', 'PostgreSQL', 'Kubernetes', 'AWS'],
                'github_profile': {
                    'username': 'marcus-dev',
                    'public_repos': 67,
                    'followers': 890,
                    'top_languages': ['Go', 'Python', 'JavaScript'],
                    'notable_repos': [
                        {'name': 'distributed-cache', 'stars': 1200, 'description': 'High-performance distributed caching system'},
                        {'name': 'microservices-toolkit', 'stars': 445, 'description': 'Toolkit for building microservices'}
                    ]
                }
            },
            {
                'name': 'Dr. Priya Patel',
                'headline': 'AI Research Scientist at OpenAI • PhD Stanford',
                'location': 'Palo Alto, CA',
                'snippet': 'AI researcher focused on large language models and multimodal AI. Published 15+ papers in top venues.',
                'profile_url': 'https://linkedin.com/in/priya-patel-ai',
                'image_url': 'https://example.com/avatar3.jpg',
                'experience': [
                    {
                        'title': 'Research Scientist',
                        'company': 'OpenAI',
                        'duration': '2023 - Present',
                        'description': 'Research on large language models, multimodal AI, and AI safety'
                    },
                    {
                        'title': 'Research Intern',
                        'company': 'DeepMind',
                        'duration': '2022 - 2023',
                        'description': 'Worked on reinforcement learning and AI alignment'
                    }
                ],
                'education': [
                    {
                        'degree': 'PhD Computer Science (AI)',
                        'school': 'Stanford University',
                        'year': '2023'
                    }
                ],
                'skills': ['Python', 'PyTorch', 'Transformers', 'Research', 'NLP', 'Computer Vision'],
                'publications': [
                    'Scaling Laws for Large Language Models (NeurIPS 2023)',
                    'Multimodal Learning with Attention Mechanisms (ICML 2023)',
                    'AI Safety in Production Systems (ICLR 2022)'
                ],
                'github_profile': {
                    'username': 'priya-ai-research',
                    'public_repos': 23,
                    'followers': 3400,
                    'top_languages': ['Python', 'Jupyter Notebook'],
                    'notable_repos': [
                        {'name': 'llm-research-tools', 'stars': 2100, 'description': 'Tools for LLM research and evaluation'},
                        {'name': 'multimodal-ai', 'stars': 890, 'description': 'Multimodal AI experiments and demos'}
                    ]
                }
            },
            {
                'name': 'Alex Kim',
                'headline': 'Engineering Manager at Stripe • Building Payment Infrastructure',
                'location': 'Seattle, WA',
                'snippet': 'Engineering leader with 10+ years experience. Currently managing 15+ engineers building global payment systems.',
                'profile_url': 'https://linkedin.com/in/alex-kim-stripe',
                'image_url': 'https://example.com/avatar4.jpg',
                'experience': [
                    {
                        'title': 'Engineering Manager',
                        'company': 'Stripe',
                        'duration': '2021 - Present',
                        'description': 'Manage payments infrastructure team, lead 15+ engineers'
                    },
                    {
                        'title': 'Senior Software Engineer',
                        'company': 'Airbnb',
                        'duration': '2018 - 2021',
                        'description': 'Built booking and payments systems handling $50B+ annually'
                    }
                ],
                'education': [
                    {
                        'degree': 'MS Software Engineering',
                        'school': 'Carnegie Mellon University',
                        'year': '2018'
                    }
                ],
                'skills': ['Python', 'Java', 'Leadership', 'System Design', 'PostgreSQL', 'Kafka'],
                'github_profile': {
                    'username': 'alex-kim-eng',
                    'public_repos': 34,
                    'followers': 567,
                    'top_languages': ['Java', 'Python', 'Go']
                }
            },
            {
                'name': 'Emma Thompson',
                'headline': 'Frontend Architect at Figma • React & TypeScript Expert',
                'location': 'New York, NY',
                'snippet': 'Frontend expert building design tools used by millions. Passionate about developer experience and performance.',
                'profile_url': 'https://linkedin.com/in/emma-thompson-frontend',
                'image_url': 'https://example.com/avatar5.jpg',
                'experience': [
                    {
                        'title': 'Frontend Architect',
                        'company': 'Figma',
                        'duration': '2022 - Present',
                        'description': 'Lead frontend architecture for design collaboration tools'
                    },
                    {
                        'title': 'Senior Frontend Engineer',
                        'company': 'Notion',
                        'duration': '2020 - 2022',
                        'description': 'Built collaborative editing features and real-time sync'
                    }
                ],
                'education': [
                    {
                        'degree': 'BS Computer Science',
                        'school': 'MIT',
                        'year': '2019'
                    }
                ],
                'skills': ['React', 'TypeScript', 'JavaScript', 'CSS', 'GraphQL', 'Node.js'],
                'github_profile': {
                    'username': 'emma-frontend',
                    'public_repos': 78,
                    'followers': 2100,
                    'top_languages': ['TypeScript', 'JavaScript', 'CSS'],
                    'notable_repos': [
                        {'name': 'react-performance-tools', 'stars': 1800, 'description': 'Performance optimization tools for React'},
                        {'name': 'design-system-components', 'stars': 950, 'description': 'Production-ready design system components'}
                    ]
                },
                'personal_website': {
                    'url': 'https://emmathompson.dev',
                    'has_blog': True,
                    'has_portfolio': True,
                    'content_topics': ['Frontend Architecture', 'React Performance', 'Design Systems'],
                    'recent_posts': [
                        'Building Scalable Design Systems',
                        'React Performance: Beyond React.memo',
                        'The Future of Frontend Architecture'
                    ]
                }
            },
            {
                'name': 'David Park',
                'headline': 'DevOps Engineer at Netflix • Kubernetes & Cloud Expert',
                'location': 'Los Angeles, CA',
                'snippet': 'DevOps engineer managing infrastructure for 200M+ Netflix users. Expert in Kubernetes, AWS, and site reliability.',
                'profile_url': 'https://linkedin.com/in/david-park-devops',
                'image_url': 'https://example.com/avatar6.jpg',
                'experience': [
                    {
                        'title': 'Senior DevOps Engineer',
                        'company': 'Netflix',
                        'duration': '2021 - Present',
                        'description': 'Manage global streaming infrastructure, 99.99% uptime'
                    },
                    {
                        'title': 'Cloud Engineer',
                        'company': 'Spotify',
                        'duration': '2019 - 2021',
                        'description': 'Built music streaming infrastructure on AWS'
                    }
                ],
                'education': [
                    {
                        'degree': 'BS Information Systems',
                        'school': 'UCLA',
                        'year': '2019'
                    }
                ],
                'skills': ['Kubernetes', 'AWS', 'Docker', 'Terraform', 'Python', 'Go'],
                'certifications': [
                    'AWS Solutions Architect Professional',
                    'Certified Kubernetes Administrator (CKA)',
                    'HashiCorp Terraform Associate'
                ]
            }
        ]
    
    def _filter_candidates_by_query(self, query: str) -> List[Dict[str, Any]]:
        """Filter candidates based on search query"""
        query_lower = query.lower()
        relevant_candidates = []
        
        for candidate in self.sample_candidates:
            # Check if query matches headline, skills, or experience
            text_to_search = f"{candidate['headline']} {candidate['snippet']} {' '.join(candidate['skills'])}".lower()
            
            # Score relevance
            relevance_score = 0
            query_terms = query_lower.split()
            
            for term in query_terms:
                if term in text_to_search:
                    relevance_score += 1
            
            # Add candidate if relevant
            if relevance_score > 0:
                candidate['relevance_score'] = relevance_score / len(query_terms)
                relevant_candidates.append(candidate.copy())
        
        # Sort by relevance
        relevant_candidates.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return relevant_candidates
    
    def _get_location_variation(self, base_location: str) -> str:
        """Get location variation for more realistic results"""
        if 'san francisco' in base_location.lower():
            variations = ['San Francisco, CA', 'SF Bay Area', 'Palo Alto, CA', 'Mountain View, CA']
        elif 'new york' in base_location.lower():
            variations = ['New York, NY', 'NYC', 'Brooklyn, NY', 'Manhattan, NY']
        elif 'seattle' in base_location.lower():
            variations = ['Seattle, WA', 'Bellevue, WA', 'Redmond, WA']
        else:
            return base_location
        
        return random.choice(variations)
    
    def generate_job_description(self) -> str:
        """Generate sample job description for testing"""
        return """
        Software Engineer, ML Research - Windsurf (Codeium)
        
        Location: Mountain View, CA (Hybrid/Remote options available)
        Compensation: $140,000 - $300,000 + Equity + Benefits
        
        About Windsurf:
        Windsurf by Codeium is revolutionizing how developers write code with AI. We're a Forbes AI 50 company building the future of AI-powered development tools. Our mission is to make coding more efficient, creative, and accessible to everyone.
        
        Role Overview:
        We're seeking a talented Software Engineer to join our ML Research team. You'll work on cutting-edge AI models that understand and generate code, helping millions of developers worldwide be more productive.
        
        Key Responsibilities:
        • Train and optimize large language models for code generation and understanding
        • Develop novel ML architectures for programming language understanding
        • Build infrastructure for training and deploying ML models at scale
        • Collaborate with product teams to integrate research into user-facing features
        • Conduct experiments and analyze model performance metrics
        
        Required Qualifications:
        • 3+ years of experience in machine learning or AI research
        • Strong programming skills in Python, PyTorch, or TensorFlow
        • Experience with transformer architectures and large language models
        • Background in NLP, code analysis, or program synthesis
        • MS/PhD in Computer Science, Machine Learning, or related field
        
        Preferred Qualifications:
        • Experience with code generation models (Codex, CodeT5, etc.)
        • Publications in top ML/AI venues (NeurIPS, ICML, ICLR, etc.)
        • Open source contributions to ML frameworks or tools
        • Experience with distributed training and MLOps
        
        What We Offer:
        • Competitive compensation package ($140-300k + equity)
        • Work with world-class AI researchers and engineers
        • Access to cutting-edge compute resources and datasets
        • Flexible work arrangements (hybrid/remote)
        • Comprehensive health, dental, and vision insurance
        • $5,000 annual learning and development budget
        • Equity participation in a fast-growing AI company
        
        Join us in building the future of AI-powered software development!
        """
    
    def add_fit_scores_and_insights(self, candidates: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
        """Add realistic fit scores and insights to candidates"""
        
        for candidate in candidates:
            # Calculate fit score based on skills and experience
            fit_score = self._calculate_demo_fit_score(candidate, job_description)
            
            # Generate insights
            insights = self._generate_demo_insights(candidate, fit_score)
            
            # Add to candidate
            candidate.update({
                'fit_score': fit_score,
                'insights': insights,
                'scoring_timestamp': datetime.now().isoformat(),
                'scoring_method': 'demo_algorithm'
            })
        
        return candidates
    
    def _calculate_demo_fit_score(self, candidate: Dict[str, Any], job_description: str) -> float:
        """Calculate realistic fit score for demo purposes"""
        score = 0.0
        
        # Skills matching
        candidate_skills = [skill.lower() for skill in candidate.get('skills', [])]
        job_skills = ['python', 'machine learning', 'pytorch', 'tensorflow', 'ai', 'nlp']
        
        skill_matches = sum(1 for skill in job_skills if any(skill in cs for cs in candidate_skills))
        score += (skill_matches / len(job_skills)) * 4.0  # Max 4 points for skills
        
        # Experience level
        headline = candidate.get('headline', '').lower()
        if 'senior' in headline or 'staff' in headline:
            score += 2.0
        elif 'lead' in headline or 'principal' in headline:
            score += 2.5
        elif 'manager' in headline:
            score += 1.5
        else:
            score += 1.0
        
        # Company prestige
        top_companies = ['google', 'microsoft', 'openai', 'meta', 'netflix', 'stripe']
        if any(company in headline for company in top_companies):
            score += 1.5
        
        # Education
        education = candidate.get('education', [])
        for edu in education:
            school = edu.get('school', '').lower()
            if any(elite in school for elite in ['stanford', 'mit', 'harvard', 'berkeley', 'cmu']):
                score += 1.0
                break
        
        # Research background (for ML roles)
        if 'research' in headline or candidate.get('publications', []):
            score += 1.5
        
        # Normalize to 0-10 scale
        return min(10.0, max(1.0, score))
    
    def _generate_demo_insights(self, candidate: Dict[str, Any], fit_score: float) -> List[str]:
        """Generate realistic insights for demo purposes"""
        insights = []
        
        if fit_score >= 8.0:
            insights.append("🎯 Exceptional match - Top-tier experience and skills alignment")
        elif fit_score >= 7.0:
            insights.append("⭐ Strong candidate - High skill relevance and experience level")
        elif fit_score >= 6.0:
            insights.append("✅ Good fit - Solid background with relevant experience")
        else:
            insights.append("💭 Potential candidate - Some relevant skills, may need development")
        
        # Add specific insights based on profile
        headline = candidate.get('headline', '').lower()
        skills = candidate.get('skills', [])
        
        if 'machine learning' in headline or 'ml' in headline:
            insights.append("🤖 Direct ML experience - Perfect for ML research role")
        
        if any('pytorch' in str(skill).lower() or 'tensorflow' in str(skill).lower() for skill in skills):
            insights.append("🔧 Strong ML framework experience (PyTorch/TensorFlow)")
        
        if candidate.get('publications', []):
            insights.append("📚 Research publications - Strong academic/research background")
        
        if candidate.get('github_profile', {}).get('public_repos', 0) >= 30:
            insights.append("💻 Active open-source contributor - Strong technical engagement")
        
        # Company insights
        top_companies = ['google', 'microsoft', 'openai', 'meta', 'netflix']
        if any(company in headline for company in top_companies):
            insights.append("🏢 Top-tier company experience - Proven ability to work at scale")
        
        return insights[:4]  # Limit to top 4 insights


# Global instance for easy access
demo_generator = DemoDataGenerator()
