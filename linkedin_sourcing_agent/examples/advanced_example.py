"""
Advanced example showcasing batch processing and analytics
"""

import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from linkedin_sourcing_agent import LinkedInSourcingAgent
from linkedin_sourcing_agent.utils.config_manager import ConfigManager
from linkedin_sourcing_agent.utils.logging_config import setup_logging
from linkedin_sourcing_agent.utils.misc_utils import batch_process

# Setup logging
setup_logging(level="INFO")


class AdvancedProcessor:
    """Advanced processor with analytics and batch processing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = LinkedInSourcingAgent(config)
        self.results = []
        self.analytics = {
            'total_processed': 0,
            'successful_scores': 0,
            'successful_outreach': 0,
            'processing_time': 0,
            'average_score': 0,
            'score_distribution': {},
            'error_count': 0,
            'errors': []
        }
    
    async def process_batch(self, candidates: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
        """Process a batch of candidates with analytics"""
        
        start_time = time.time()
        
        print(f"Processing batch of {len(candidates)} candidates...")
        
        # Process candidates in smaller batches to respect rate limits
        batch_size = self.config.get('BATCH_SIZE', 5)
        
        async def process_single_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
            """Process a single candidate"""
            
            try:
                # Score candidate
                scored_candidate = await self.agent.score_candidate(candidate, job_description)
                self.analytics['successful_scores'] += 1
                
                # Generate outreach if score is high enough
                min_score = self.config.get('MIN_SCORE_THRESHOLD', 6.0)
                if scored_candidate.get('score', 0) >= min_score:
                    try:
                        outreach = await self.agent.generate_outreach(candidate, job_description)
                        scored_candidate['outreach_message'] = outreach
                        scored_candidate['outreach_generated'] = True
                        self.analytics['successful_outreach'] += 1
                    except Exception as e:
                        scored_candidate['outreach_error'] = str(e)
                        scored_candidate['outreach_generated'] = False
                        self.analytics['errors'].append(f"Outreach generation failed for {candidate.get('name', 'Unknown')}: {e}")
                else:
                    scored_candidate['outreach_generated'] = False
                    scored_candidate['outreach_skip_reason'] = 'Score below threshold'
                
                return scored_candidate
                
            except Exception as e:
                self.analytics['error_count'] += 1
                self.analytics['errors'].append(f"Processing failed for {candidate.get('name', 'Unknown')}: {e}")
                
                # Return candidate with error information
                candidate['processing_error'] = str(e)
                candidate['score'] = 0
                candidate['outreach_generated'] = False
                return candidate
        
        # Process in batches
        results = await batch_process(candidates, batch_size, process_single_candidate)
        
        # Update analytics
        processing_time = time.time() - start_time
        self.analytics['processing_time'] += processing_time
        self.analytics['total_processed'] += len(candidates)
        
        # Calculate score distribution
        scores = [r.get('score', 0) for r in results if 'score' in r]
        if scores:
            self.analytics['average_score'] = sum(scores) / len(scores)
            
            # Score buckets
            for score in scores:
                bucket = f"{int(score)}-{int(score)+1}"
                self.analytics['score_distribution'][bucket] = self.analytics['score_distribution'].get(bucket, 0) + 1
        
        print(f"Batch processed in {processing_time:.2f}s")
        print(f"Success rate: {(len(results) - self.analytics['error_count']) / len(results) * 100:.1f}%")
        
        return results
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        
        report = {
            'summary': {
                'total_candidates_processed': self.analytics['total_processed'],
                'successful_scores': self.analytics['successful_scores'],
                'successful_outreach_generation': self.analytics['successful_outreach'],
                'error_count': self.analytics['error_count'],
                'total_processing_time': f"{self.analytics['processing_time']:.2f}s",
                'average_processing_time_per_candidate': f"{self.analytics['processing_time'] / max(1, self.analytics['total_processed']):.2f}s"
            },
            'scoring_analytics': {
                'average_score': round(self.analytics['average_score'], 2),
                'score_distribution': self.analytics['score_distribution'],
                'high_quality_candidates': len([r for r in self.results if r.get('score', 0) >= 8.0]),
                'moderate_quality_candidates': len([r for r in self.results if 6.0 <= r.get('score', 0) < 8.0]),
                'low_quality_candidates': len([r for r in self.results if r.get('score', 0) < 6.0])
            },
            'outreach_analytics': {
                'outreach_success_rate': f"{(self.analytics['successful_outreach'] / max(1, self.analytics['total_processed'])) * 100:.1f}%",
                'candidates_with_outreach': self.analytics['successful_outreach'],
                'candidates_without_outreach': self.analytics['total_processed'] - self.analytics['successful_outreach']
            },
            'error_analytics': {
                'error_rate': f"{(self.analytics['error_count'] / max(1, self.analytics['total_processed'])) * 100:.1f}%",
                'error_details': self.analytics['errors'][-10:]  # Last 10 errors
            }
        }
        
        return report
    
    def export_results(self, output_dir: Path) -> None:
        """Export results and analytics to files"""
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export results
        results_file = output_dir / "processed_candidates.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Export analytics
        analytics_file = output_dir / "analytics_report.json"
        report = self.generate_analytics_report()
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Export high-quality candidates separately
        high_quality = [r for r in self.results if r.get('score', 0) >= 8.0]
        if high_quality:
            hq_file = output_dir / "high_quality_candidates.json"
            with open(hq_file, 'w', encoding='utf-8') as f:
                json.dump(high_quality, f, indent=2, ensure_ascii=False)
        
        # Export outreach messages
        outreach_candidates = [r for r in self.results if r.get('outreach_generated', False)]
        if outreach_candidates:
            outreach_file = output_dir / "outreach_messages.txt"
            with open(outreach_file, 'w', encoding='utf-8') as f:
                for candidate in outreach_candidates:
                    f.write(f"=== {candidate['name']} (Score: {candidate.get('score', 0):.1f}) ===\n")
                    f.write(f"{candidate.get('outreach_message', 'No message')}\n\n")
        
        print(f"Results exported to: {output_dir}")


async def advanced_example():
    """Advanced example with batch processing and analytics"""
    
    print("=== LinkedIn Sourcing Agent - Advanced Example ===\n")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Create processor
    processor = AdvancedProcessor(config)
    
    # Load candidates from file (or generate sample data)
    candidates_file = Path("sample_candidates.json")
    
    if candidates_file.exists():
        print(f"Loading candidates from {candidates_file}")
        with open(candidates_file, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
    else:
        print("Generating sample candidate data...")
        candidates = generate_sample_candidates()
        
        # Save sample data
        with open(candidates_file, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        print(f"Sample data saved to {candidates_file}")
    
    # Job description
    job_description = """
    Senior Software Engineer - AI/ML Platform
    
    We're looking for a Senior Software Engineer to join our AI/ML Platform team.
    You'll be responsible for building and scaling our machine learning infrastructure
    that powers our AI-driven products.
    
    Requirements:
    - 5+ years of software engineering experience
    - Strong Python programming skills
    - Experience with ML frameworks (TensorFlow, PyTorch, Scikit-learn)
    - Experience with cloud platforms (AWS, GCP, Azure)
    - Experience with containerization (Docker, Kubernetes)
    - Strong understanding of distributed systems
    
    Preferred:
    - Experience with MLOps and model deployment
    - Experience with big data technologies (Spark, Kafka)
    - Open source contributions
    - Advanced degree in Computer Science or related field
    
    Location: San Francisco, CA (Hybrid)
    Compensation: $180,000 - $250,000 + equity + benefits
    """
    
    print(f"Processing {len(candidates)} candidates in batches...")
    print(f"Job: Senior Software Engineer - AI/ML Platform\n")
    
    # Process candidates in batches
    batch_size = 10  # Process 10 candidates at a time
    all_results = []
    
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1} ({len(batch)} candidates)...")
        
        batch_results = await processor.process_batch(batch, job_description)
        all_results.extend(batch_results)
        
        # Brief pause between batches
        await asyncio.sleep(1)
    
    processor.results = all_results
    
    # Generate and display analytics
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE - ANALYTICS REPORT")
    print("=" * 60)
    
    report = processor.generate_analytics_report()
    
    print(f"\n📊 SUMMARY:")
    for key, value in report['summary'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n🎯 SCORING ANALYTICS:")
    for key, value in report['scoring_analytics'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n📧 OUTREACH ANALYTICS:")
    for key, value in report['outreach_analytics'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n⚠️ ERROR ANALYTICS:")
    print(f"  Error Rate: {report['error_analytics']['error_rate']}")
    
    # Export results
    output_dir = Path("advanced_example_results")
    processor.export_results(output_dir)
    
    # Show top candidates
    top_candidates = sorted(all_results, key=lambda x: x.get('score', 0), reverse=True)[:5]
    
    print(f"\n🏆 TOP 5 CANDIDATES:")
    for i, candidate in enumerate(top_candidates, 1):
        print(f"{i}. {candidate['name']} - Score: {candidate.get('score', 0):.1f}/10")
        print(f"   {candidate.get('headline', 'No headline')}")
        print(f"   Outreach: {'✅ Generated' if candidate.get('outreach_generated') else '❌ Not generated'}")
        print()
    
    print("✅ Advanced example completed successfully!")


def generate_sample_candidates() -> List[Dict[str, Any]]:
    """Generate sample candidate data for testing"""
    
    return [
        {
            "name": "Alex Rodriguez",
            "linkedin_url": "https://linkedin.com/in/alex-rodriguez-ml",
            "headline": "Senior ML Engineer at Google | PhD in Computer Science",
            "location": "San Francisco, CA",
            "summary": "Experienced ML engineer with 8 years in production ML systems. Led teams building recommendation engines and NLP models at scale.",
            "experience": [
                {"title": "Senior ML Engineer", "company": "Google", "duration": "2020-Present"},
                {"title": "ML Engineer", "company": "Facebook", "duration": "2018-2020"},
                {"title": "Data Scientist", "company": "Uber", "duration": "2016-2018"}
            ],
            "education": [
                {"school": "Stanford University", "degree": "PhD Computer Science", "year": "2016"},
                {"school": "MIT", "degree": "BS Computer Science", "year": "2012"}
            ],
            "skills": ["Python", "TensorFlow", "PyTorch", "Kubernetes", "AWS", "Spark", "MLOps"]
        },
        {
            "name": "Maria Chen",
            "linkedin_url": "https://linkedin.com/in/maria-chen-ai",
            "headline": "AI Research Scientist | Deep Learning Expert",
            "location": "Palo Alto, CA",
            "summary": "AI researcher with strong publication record and experience in deep learning, computer vision, and NLP.",
            "experience": [
                {"title": "Research Scientist", "company": "OpenAI", "duration": "2021-Present"},
                {"title": "ML Engineer", "company": "Tesla", "duration": "2019-2021"}
            ],
            "education": [
                {"school": "Carnegie Mellon", "degree": "PhD Machine Learning", "year": "2019"},
                {"school": "UC Berkeley", "degree": "MS Computer Science", "year": "2015"}
            ],
            "skills": ["Python", "PyTorch", "Computer Vision", "NLP", "Research", "Publications"]
        },
        {
            "name": "David Kim",
            "linkedin_url": "https://linkedin.com/in/david-kim-backend",
            "headline": "Backend Engineer | Distributed Systems Expert",
            "location": "Seattle, WA",
            "summary": "Backend engineer with expertise in distributed systems and microservices. Limited ML experience but strong foundation.",
            "experience": [
                {"title": "Senior Backend Engineer", "company": "Amazon", "duration": "2019-Present"},
                {"title": "Software Engineer", "company": "Microsoft", "duration": "2017-2019"}
            ],
            "education": [
                {"school": "University of Washington", "degree": "BS Computer Science", "year": "2017"}
            ],
            "skills": ["Python", "Java", "Distributed Systems", "Microservices", "AWS", "Docker"]
        },
        {
            "name": "Sarah Patel",
            "linkedin_url": "https://linkedin.com/in/sarah-patel-data",
            "headline": "Data Scientist | ML Platform Engineer",
            "location": "San Francisco, CA",
            "summary": "Data scientist transitioning to ML engineering with experience in MLOps and model deployment.",
            "experience": [
                {"title": "Data Scientist", "company": "Airbnb", "duration": "2020-Present"},
                {"title": "Data Analyst", "company": "Lyft", "duration": "2018-2020"}
            ],
            "education": [
                {"school": "Stanford University", "degree": "MS Statistics", "year": "2018"},
                {"school": "UC San Diego", "degree": "BS Mathematics", "year": "2016"}
            ],
            "skills": ["Python", "R", "Scikit-learn", "MLOps", "Airflow", "GCP"]
        },
        {
            "name": "James Wilson",
            "linkedin_url": "https://linkedin.com/in/james-wilson-frontend",
            "headline": "Frontend Developer | React & JavaScript Expert",
            "location": "Austin, TX",
            "summary": "Frontend developer with limited backend experience. No ML background but strong technical skills.",
            "experience": [
                {"title": "Senior Frontend Developer", "company": "Indeed", "duration": "2020-Present"},
                {"title": "Frontend Developer", "company": "Dell", "duration": "2018-2020"}
            ],
            "education": [
                {"school": "UT Austin", "degree": "BS Computer Science", "year": "2018"}
            ],
            "skills": ["JavaScript", "React", "TypeScript", "Node.js", "HTML", "CSS"]
        }
    ]


if __name__ == "__main__":
    try:
        asyncio.run(advanced_example())
    except KeyboardInterrupt:
        print("\n❌ Example cancelled by user") 
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        raise
