"""
Multi-Source Scorer
Specialized scoring component for evaluating candidates across multiple data sources
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..utils.logging_config import get_logger
from .fit_scorer import CandidateFitScorer


logger = get_logger(__name__)


@dataclass
class MultiSourceWeights:
    """Weights for different multi-source scoring factors"""
    github_contribution: float = 0.35
    social_presence: float = 0.20
    content_creation: float = 0.25
    professional_branding: float = 0.20


class MultiSourceScorer:
    """
    Advanced scorer for evaluating candidates based on multi-source data
    
    Evaluates:
    - GitHub activity and code quality
    - Social media presence and engagement
    - Content creation (blogs, articles, talks)
    - Professional branding consistency
    """
    
    def __init__(self, weights: Optional[MultiSourceWeights] = None):
        """
        Initialize multi-source scorer
        
        Args:
            weights: Custom weights for multi-source factors
        """
        self.weights = weights or MultiSourceWeights()
        self.base_scorer = CandidateFitScorer()
        
        logger.info("Multi-source scorer initialized")
    
    def calculate_enhanced_score(self, candidate: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Calculate enhanced score incorporating multi-source data
        
        Args:
            candidate: Candidate data with multi-source information
            job_description: Job description for context
            
        Returns:
            Enhanced scoring result with multi-source analysis
        """
        try:
            # Get base score from standard scorer
            base_result = self.base_scorer.calculate_fit_score(candidate, job_description)
            
            # Calculate multi-source enhancement scores
            github_score = self._score_github_contribution(candidate)
            social_score = self._score_social_presence(candidate)
            content_score = self._score_content_creation(candidate)
            branding_score = self._score_professional_branding(candidate)
            
            # Apply weights to multi-source scores
            weighted_github = github_score * self.weights.github_contribution
            weighted_social = social_score * self.weights.social_presence
            weighted_content = content_score * self.weights.content_creation
            weighted_branding = branding_score * self.weights.professional_branding
            
            # Calculate total multi-source bonus (max 1.5 points)
            multi_source_bonus = (weighted_github + weighted_social + 
                                weighted_content + weighted_branding) * 1.5
            
            # Enhanced final score
            enhanced_score = min(base_result['fit_score'] + multi_source_bonus, 10.0)
            
            # Generate multi-source insights
            insights = self._generate_multi_source_insights(candidate, {
                'github': github_score,
                'social': social_score,
                'content': content_score,
                'branding': branding_score
            })
            
            # Calculate cross-platform consistency
            consistency_score = self._calculate_platform_consistency(candidate)
            
            # Enhanced result
            enhanced_result = base_result.copy()
            enhanced_result.update({
                'enhanced_fit_score': round(enhanced_score, 1),
                'multi_source_breakdown': {
                    'github_contribution': round(github_score, 1),
                    'social_presence': round(social_score, 1),
                    'content_creation': round(content_score, 1),
                    'professional_branding': round(branding_score, 1)
                },
                'multi_source_bonus': round(multi_source_bonus, 1),
                'platform_consistency': round(consistency_score, 2),
                'multi_source_insights': insights,
                'data_richness': self._assess_data_richness(candidate),
                'verification_level': self._get_verification_level(candidate)
            })
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Multi-source scoring failed: {str(e)}")
            return self.base_scorer.calculate_fit_score(candidate, job_description)
    
    def _score_github_contribution(self, candidate: Dict[str, Any]) -> float:
        """
        Score GitHub contribution and code quality (0-10 scale)
        
        Factors:
        - Repository count and quality
        - Contribution frequency
        - Popular repositories (stars, forks)
        - Language diversity
        - Open source engagement
        """
        github_profile = candidate.get('github_profile', {})
        if not github_profile:
            return 0.0
        
        score = 0.0
        
        # Repository quantity and quality
        repos = github_profile.get('public_repos', 0)
        if repos >= 100:
            score += 3.0
        elif repos >= 50:
            score += 2.5
        elif repos >= 20:
            score += 2.0
        elif repos >= 10:
            score += 1.5
        elif repos >= 5:
            score += 1.0
        
        # Repository popularity (stars and forks)
        notable_repos = github_profile.get('notable_repos', [])
        if notable_repos:
            total_stars = sum(repo.get('stars', 0) for repo in notable_repos)
            max_stars = max(repo.get('stars', 0) for repo in notable_repos)
            
            if max_stars >= 5000:
                score += 3.0
            elif max_stars >= 1000:
                score += 2.5
            elif max_stars >= 500:
                score += 2.0
            elif max_stars >= 100:
                score += 1.5
            elif max_stars >= 50:
                score += 1.0
            
            # Bonus for multiple popular repos
            popular_repos = len([r for r in notable_repos if r.get('stars', 0) >= 100])
            if popular_repos >= 3:
                score += 1.0
            elif popular_repos >= 2:
                score += 0.5
        
        # Language diversity
        languages = github_profile.get('top_languages', [])
        if len(languages) >= 5:
            score += 1.0
        elif len(languages) >= 3:
            score += 0.5
        
        # Community engagement (followers)
        followers = github_profile.get('followers', 0)
        if followers >= 1000:
            score += 2.0
        elif followers >= 500:
            score += 1.5
        elif followers >= 100:
            score += 1.0
        elif followers >= 50:
            score += 0.5
        
        return min(score, 10.0)
    
    def _score_social_presence(self, candidate: Dict[str, Any]) -> float:
        """
        Score social media presence and professional networking (0-10 scale)
        
        Factors:
        - Twitter/LinkedIn followers and engagement
        - Professional network size
        - Industry thought leadership
        - Speaking/conference participation
        """
        score = 0.0
        
        # Twitter presence
        twitter_profile = candidate.get('twitter_profile', {})
        if twitter_profile:
            followers = twitter_profile.get('followers', 0)
            bio = twitter_profile.get('bio', '').lower()
            
            # Follower count scoring
            if followers >= 50000:
                score += 4.0
            elif followers >= 10000:
                score += 3.0
            elif followers >= 5000:
                score += 2.5
            elif followers >= 1000:
                score += 2.0
            elif followers >= 500:
                score += 1.0
            
            # Bio relevance
            relevant_terms = [
                'ai', 'ml', 'machine learning', 'engineer', 'developer', 'tech',
                'researcher', 'scientist', 'cto', 'founder', 'startup'
            ]
            if any(term in bio for term in relevant_terms):
                score += 1.0
            
            # Thought leadership indicators
            leadership_terms = [
                'thought leader', 'speaker', 'author', 'conference', 'keynote',
                'expert', 'consultant', 'advisor'
            ]
            if any(term in bio for term in leadership_terms):
                score += 1.5
        
        # LinkedIn professional network (estimated from data available)
        linkedin_url = candidate.get('linkedin_url', '')
        if linkedin_url:
            # Base score for having LinkedIn
            score += 1.0
            
            # Extract network indicators from headline/snippet
            headline = candidate.get('headline', '').lower()
            snippet = candidate.get('snippet', '').lower()
            
            network_indicators = [
                'connections', 'network', 'community', 'mentor', 'advisor',
                'board member', 'investor', 'angel'
            ]
            
            if any(indicator in headline or indicator in snippet for indicator in network_indicators):
                score += 1.0
        
        return min(score, 10.0)
    
    def _score_content_creation(self, candidate: Dict[str, Any]) -> float:
        """
        Score content creation and knowledge sharing (0-10 scale)
        
        Factors:
        - Personal blog/website
        - Technical articles and publications
        - Conference talks and presentations
        - Open source documentation
        - Educational content
        """
        score = 0.0
        
        # Personal website and blog
        website = candidate.get('personal_website', {})
        if website:
            score += 1.0  # Base score for having a website
            
            if website.get('has_blog'):
                score += 2.0
                
                # Content topic relevance
                topics = website.get('content_topics', [])
                if topics:
                    relevant_topics = [
                        'machine learning', 'ai', 'programming', 'software',
                        'tech', 'data science', 'algorithms', 'engineering'
                    ]
                    topic_text = ' '.join(topics).lower()
                    relevant_count = sum(1 for topic in relevant_topics if topic in topic_text)
                    
                    if relevant_count >= 4:
                        score += 2.0
                    elif relevant_count >= 2:
                        score += 1.0
            
            if website.get('has_portfolio'):
                score += 1.5
        
        # GitHub documentation and educational content
        github_profile = candidate.get('github_profile', {})
        if github_profile:
            notable_repos = github_profile.get('notable_repos', [])
            
            # Look for educational/tutorial repositories
            educational_repos = []
            for repo in notable_repos:
                name = repo.get('name', '').lower()
                description = repo.get('description', '').lower()
                
                educational_keywords = [
                    'tutorial', 'guide', 'examples', 'demo', 'learning',
                    'course', 'workshop', 'book', 'documentation'
                ]
                
                if any(keyword in name or keyword in description for keyword in educational_keywords):
                    educational_repos.append(repo)
            
            if educational_repos:
                score += len(educational_repos) * 0.5  # Up to 2.5 points
                
                # Bonus for popular educational content
                popular_educational = [r for r in educational_repos if r.get('stars', 0) >= 100]
                if popular_educational:
                    score += len(popular_educational) * 0.5
        
        # Social media content creation indicators
        twitter_profile = candidate.get('twitter_profile', {})
        if twitter_profile:
            bio = twitter_profile.get('bio', '').lower()
            content_indicators = [
                'blogger', 'writer', 'author', 'speaker', 'educator',
                'teacher', 'content creator', 'youtuber'
            ]
            
            if any(indicator in bio for indicator in content_indicators):
                score += 1.0
        
        return min(score, 10.0)
    
    def _score_professional_branding(self, candidate: Dict[str, Any]) -> float:
        """
        Score professional branding and online presence consistency (0-10 scale)
        
        Factors:
        - Consistent professional identity across platforms
        - Professional headshot and bio consistency
        - Contact information completeness
        - Professional domain/email
        - Brand recognition and authority
        """
        score = 0.0
        
        # Platform presence completeness
        platforms = []
        if candidate.get('linkedin_url'):
            platforms.append('linkedin')
        if candidate.get('github_profile'):
            platforms.append('github')
        if candidate.get('twitter_profile'):
            platforms.append('twitter')
        if candidate.get('personal_website'):
            platforms.append('website')
        
        # Score based on platform diversity
        platform_count = len(platforms)
        if platform_count >= 4:
            score += 3.0
        elif platform_count >= 3:
            score += 2.0
        elif platform_count >= 2:
            score += 1.0
        
        # Professional website domain
        website = candidate.get('personal_website', {})
        if website:
            url = website.get('url', '').lower()
            
            # Professional domain indicators
            professional_domains = ['.dev', '.ai', '.tech', '.io', '.com']
            if any(domain in url for domain in professional_domains):
                score += 1.0
            
            # Personal domain (name-based)
            name = candidate.get('name', '').lower().replace(' ', '')
            if name and name in url:
                score += 1.5  # Personal branding bonus
        
        # Bio/headline consistency indicators
        linkedin_headline = candidate.get('headline', '').lower()
        twitter_bio = candidate.get('twitter_profile', {}).get('bio', '').lower()
        
        if linkedin_headline and twitter_bio:
            # Simple consistency check (shared keywords)
            linkedin_words = set(linkedin_headline.split())
            twitter_words = set(twitter_bio.split())
            
            # Remove common words
            common_words = {'the', 'and', 'or', 'at', 'in', 'on', 'for', 'with', 'by'}
            linkedin_words -= common_words
            twitter_words -= common_words
            
            if linkedin_words and twitter_words:
                overlap = len(linkedin_words & twitter_words)
                total_unique = len(linkedin_words | twitter_words)
                
                if total_unique > 0:
                    consistency_ratio = overlap / total_unique
                    score += consistency_ratio * 2.0
        
        # Professional authority indicators
        authority_indicators = [
            'founder', 'cto', 'lead', 'principal', 'senior', 'director',
            'head of', 'vp', 'chief', 'expert', 'specialist'
        ]
        
        all_text = f"{linkedin_headline} {twitter_bio}".lower()
        authority_count = sum(1 for indicator in authority_indicators if indicator in all_text)
        
        if authority_count >= 2:
            score += 1.5
        elif authority_count >= 1:
            score += 1.0
        
        # GitHub profile completeness
        github_profile = candidate.get('github_profile', {})
        if github_profile:
            # Professional GitHub setup indicators
            if github_profile.get('followers', 0) >= 50:
                score += 0.5
            
            # Notable repositories indicate active maintenance
            if github_profile.get('notable_repos'):
                score += 0.5
        
        return min(score, 10.0)
    
    def _calculate_platform_consistency(self, candidate: Dict[str, Any]) -> float:
        """Calculate consistency score across platforms"""
        platforms_data = {}
        
        # Extract key information from each platform
        if candidate.get('linkedin_url'):
            platforms_data['linkedin'] = {
                'name': candidate.get('name', ''),
                'title': candidate.get('headline', ''),
                'location': candidate.get('location', '')
            }
        
        if candidate.get('github_profile'):
            github = candidate.get('github_profile', {})
            platforms_data['github'] = {
                'username': github.get('username', ''),
                'bio': github.get('bio', ''),
                'location': github.get('location', '')
            }
        
        if candidate.get('twitter_profile'):
            twitter = candidate.get('twitter_profile', {})
            platforms_data['twitter'] = {
                'username': twitter.get('username', ''),
                'bio': twitter.get('bio', ''),
                'location': twitter.get('location', '')
            }
        
        if len(platforms_data) < 2:
            return 0.5  # Neutral score for single platform
        
        # Calculate consistency metrics
        consistency_scores = []
        
        # Name consistency (if available)
        names = [data.get('name', '') for data in platforms_data.values() if data.get('name')]
        if len(names) >= 2:
            name_consistency = len(set(names)) == 1
            consistency_scores.append(1.0 if name_consistency else 0.3)
        
        # Location consistency
        locations = [data.get('location', '').lower() for data in platforms_data.values() if data.get('location')]
        if len(locations) >= 2:
            # Simple location matching (could be enhanced)
            location_words = [set(loc.split()) for loc in locations]
            if len(location_words) >= 2:
                overlap = len(location_words[0] & location_words[1])
                if overlap > 0:
                    consistency_scores.append(0.8)
                else:
                    consistency_scores.append(0.4)
        
        # Professional role consistency (bio/title overlap)
        bios = []
        for platform, data in platforms_data.items():
            if platform == 'linkedin':
                bios.append(data.get('title', '').lower())
            else:
                bios.append(data.get('bio', '').lower())
        
        bios = [bio for bio in bios if bio]
        if len(bios) >= 2:
            # Calculate keyword overlap
            bio_words = [set(bio.split()) for bio in bios]
            common_words = {'the', 'and', 'or', 'at', 'in', 'on', 'for', 'with', 'by', 'a', 'an'}
            
            # Remove common words and calculate overlap
            meaningful_words = [words - common_words for words in bio_words]
            if len(meaningful_words) >= 2 and all(words for words in meaningful_words):
                overlap = len(meaningful_words[0] & meaningful_words[1])
                total = len(meaningful_words[0] | meaningful_words[1])
                if total > 0:
                    overlap_ratio = overlap / total
                    consistency_scores.append(overlap_ratio)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.5
    
    def _generate_multi_source_insights(self, candidate: Dict[str, Any], scores: Dict[str, float]) -> List[str]:
        """Generate insights from multi-source analysis"""
        insights = []
        
        # GitHub insights
        if scores['github'] >= 8:
            insights.append("Exceptional open-source contributor with high-impact repositories")
        elif scores['github'] >= 6:
            insights.append("Active GitHub contributor with notable open-source projects")
        elif scores['github'] >= 3:
            insights.append("Maintains active GitHub presence with regular contributions")
        
        # Social presence insights
        if scores['social'] >= 7:
            insights.append("Strong professional network and thought leadership presence")
        elif scores['social'] >= 4:
            insights.append("Engaged in professional social media and networking")
        
        # Content creation insights
        if scores['content'] >= 7:
            insights.append("Prolific content creator and knowledge sharer in the tech community")
        elif scores['content'] >= 4:
            insights.append("Actively shares knowledge through blog posts and technical content")
        
        # Professional branding insights
        if scores['branding'] >= 7:
            insights.append("Maintains consistent and professional brand across all platforms")
        elif scores['branding'] >= 4:
            insights.append("Well-established professional online presence")
        
        # Cross-platform insights
        platforms = len([p for p in ['github', 'social', 'content', 'branding'] if scores[p] > 0])
        if platforms >= 3:
            insights.append("Demonstrates comprehensive digital professional presence")
        
        return insights
    
    def _assess_data_richness(self, candidate: Dict[str, Any]) -> str:
        """Assess the richness of multi-source data"""
        richness_score = 0
        
        # LinkedIn data richness
        if candidate.get('experience') and len(candidate['experience']) >= 3:
            richness_score += 2
        if candidate.get('education'):
            richness_score += 1
        if candidate.get('skills') and len(candidate['skills']) >= 5:
            richness_score += 1
        
        # GitHub data richness
        github = candidate.get('github_profile', {})
        if github:
            if github.get('public_repos', 0) >= 10:
                richness_score += 2
            if github.get('notable_repos') and len(github['notable_repos']) >= 3:
                richness_score += 2
            if github.get('top_languages') and len(github['top_languages']) >= 3:
                richness_score += 1
        
        # Social media richness
        twitter = candidate.get('twitter_profile', {})
        if twitter:
            if twitter.get('followers', 0) >= 100:
                richness_score += 1
            if twitter.get('bio'):
                richness_score += 1
        
        # Website richness
        website = candidate.get('personal_website', {})
        if website:
            if website.get('has_blog'):
                richness_score += 2
            if website.get('has_portfolio'):
                richness_score += 1
            if website.get('content_topics'):
                richness_score += 1
        
        # Classify richness
        if richness_score >= 10:
            return 'excellent'
        elif richness_score >= 7:
            return 'good'
        elif richness_score >= 4:
            return 'moderate'
        else:
            return 'limited'
    
    def _get_verification_level(self, candidate: Dict[str, Any]) -> str:
        """Determine verification level based on cross-platform data"""
        verification_points = 0
        
        # Base verification from LinkedIn
        if candidate.get('linkedin_url'):
            verification_points += 1
        
        # GitHub verification
        if candidate.get('github_profile'):
            verification_points += 2
            
            # Higher verification for active GitHub
            github = candidate.get('github_profile', {})
            if github.get('public_repos', 0) >= 5:
                verification_points += 1
        
        # Social media verification
        if candidate.get('twitter_profile'):
            verification_points += 1
            
            # Higher verification for established social presence
            twitter = candidate.get('twitter_profile', {})
            if twitter.get('followers', 0) >= 100:
                verification_points += 1
        
        # Website verification
        if candidate.get('personal_website'):
            verification_points += 2
        
        # Cross-platform name consistency bonus
        if self._has_consistent_identity(candidate):
            verification_points += 1
        
        # Classify verification level
        if verification_points >= 7:
            return 'high'
        elif verification_points >= 5:
            return 'medium'
        elif verification_points >= 3:
            return 'basic'
        else:
            return 'low'
    
    def _has_consistent_identity(self, candidate: Dict[str, Any]) -> bool:
        """Check if candidate has consistent identity across platforms"""
        name = candidate.get('name', '').lower()
        if not name:
            return False
        
        # Check GitHub username consistency
        github = candidate.get('github_profile', {})
        if github:
            username = github.get('username', '').lower()
            name_parts = name.replace(' ', '').replace('.', '')
            if name_parts in username or username in name_parts:
                return True
        
        # Check Twitter username consistency
        twitter = candidate.get('twitter_profile', {})
        if twitter:
            username = twitter.get('username', '').lower()
            name_parts = name.replace(' ', '').replace('.', '')
            if name_parts in username or username in name_parts:
                return True
        
        # Check website domain consistency
        website = candidate.get('personal_website', {})
        if website:
            url = website.get('url', '').lower()
            name_parts = name.replace(' ', '').replace('.', '')
            if name_parts in url:
                return True
        
        return False
