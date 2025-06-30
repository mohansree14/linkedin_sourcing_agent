"""
Basic example of using LinkedIn Sourcing Agent
"""

import asyncio
import json
from pathlib import Path

from linkedin_sourcing_agent import LinkedInSourcingAgent
from linkedin_sourcing_agent.utils.config_manager import ConfigManager
from linkedin_sourcing_agent.utils.logging_config import setup_logging

# Setup logging
setup_logging(level="INFO")


async def basic_example():
    """Basic example of searching and scoring candidates"""
    
    print("=== LinkedIn Sourcing Agent - Basic Example ===\n")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Initialize agent
    agent = LinkedInSourcingAgent(config)
    
    # Example job description
    job_description = """
    We are looking for a Senior Python Developer to join our AI team.
    
    Requirements:
    - 5+ years of Python development experience
    - Experience with machine learning frameworks (TensorFlow, PyTorch)
    - Strong background in data structures and algorithms
    - Experience with cloud platforms (AWS, GCP, Azure)
    - Bachelor's degree in Computer Science or related field
    
    Nice to have:
    - Experience with LLMs and NLP
    - DevOps experience with Docker and Kubernetes
    - Open source contributions
    
    Location: San Francisco, CA (Hybrid)
    Salary: $150,000 - $220,000 + equity
    """
    
    print("Job Description:")
    print(job_description)
    print("\n" + "="*50 + "\n")
    
    # Example candidates (in real usage, these would come from LinkedIn search)
    sample_candidates = [
        {
            "name": "John Smith",
            "linkedin_url": "https://linkedin.com/in/johnsmith-dev",
            "headline": "Senior Python Developer | AI/ML Engineer at TechCorp",
            "location": "San Francisco, CA",
            "summary": "Experienced Python developer with 7 years in AI/ML. Built production ML systems using TensorFlow and PyTorch. Strong background in distributed systems and cloud architecture.",
            "experience": [
                {
                    "title": "Senior AI Engineer",
                    "company": "TechCorp",
                    "duration": "2021-Present",
                    "description": "Leading ML model development for recommendation systems"
                },
                {
                    "title": "Python Developer",
                    "company": "DataStart",
                    "duration": "2019-2021",
                    "description": "Built data pipelines and ML models using Python and AWS"
                }
            ],
            "education": [
                {
                    "school": "Stanford University",
                    "degree": "MS Computer Science",
                    "year": "2019"
                }
            ],
            "skills": ["Python", "TensorFlow", "PyTorch", "AWS", "Docker", "Kubernetes"]
        },
        {
            "name": "Sarah Johnson",
            "linkedin_url": "https://linkedin.com/in/sarah-johnson-ml",
            "headline": "Machine Learning Engineer | Open Source Contributor",
            "location": "Seattle, WA",
            "summary": "ML engineer passionate about NLP and LLMs. Active contributor to open source ML projects. Experience building scalable ML infrastructure.",
            "experience": [
                {
                    "title": "ML Engineer",
                    "company": "BigTech",
                    "duration": "2020-Present",
                    "description": "Developing NLP models and LLM fine-tuning pipelines"
                }
            ],
            "education": [
                {
                    "school": "UC Berkeley",
                    "degree": "BS Computer Science",
                    "year": "2020"
                }
            ],
            "skills": ["Python", "PyTorch", "Transformers", "NLP", "LLMs", "GCP"]
        },
        {
            "name": "Mike Chen",
            "linkedin_url": "https://linkedin.com/in/mikechen-fullstack",
            "headline": "Full Stack Developer | React & Node.js Expert",
            "location": "Austin, TX",
            "summary": "Full stack developer with focus on web applications. Some experience with Python for backend development.",
            "experience": [
                {
                    "title": "Full Stack Developer",
                    "company": "WebCorp",
                    "duration": "2021-Present",
                    "description": "Building web applications with React and Node.js"
                }
            ],
            "education": [
                {
                    "school": "UT Austin",
                    "degree": "BS Information Systems",
                    "year": "2021"
                }
            ],
            "skills": ["JavaScript", "React", "Node.js", "Python", "SQL"]
        }
    ]
    
    print(f"Processing {len(sample_candidates)} candidates...\n")
    
    # Process each candidate
    results = []
    
    for i, candidate in enumerate(sample_candidates, 1):
        print(f"Processing candidate {i}: {candidate['name']}")
        
        try:
            # Score candidate
            scored_candidate = await agent.score_candidate(candidate, job_description)
            
            # Generate outreach message
            outreach_message = await agent.generate_outreach(candidate, job_description)
            scored_candidate['outreach_message'] = outreach_message
            
            results.append(scored_candidate)
            
            print(f"  ✓ Score: {scored_candidate.get('score', 0):.1f}/10")
            print(f"  ✓ Outreach message generated")
            
        except Exception as e:
            print(f"  ✗ Error processing candidate: {e}")
        
        print()
    
    # Sort by score
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    print("=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']} - Score: {result.get('score', 0):.1f}/10")
        print(f"   Location: {result.get('location', 'N/A')}")
        print(f"   Headline: {result.get('headline', 'N/A')}")
        
        if 'score_breakdown' in result:
            breakdown = result['score_breakdown']
            print(f"   Breakdown: {' | '.join([f'{k}: {v:.1f}' for k, v in breakdown.items()])}")
        
        if result.get('score', 0) >= 7.0:
            print("   ✅ STRONG MATCH - Recommended for outreach")
        elif result.get('score', 0) >= 5.0:
            print("   ⚡ MODERATE MATCH - Consider for outreach")
        else:
            print("   ❌ WEAK MATCH - May not be suitable")
    
    # Save results to file
    output_file = Path("example_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")
    
    # Show best candidate's outreach message
    if results:
        best_candidate = results[0]
        print(f"\n" + "=" * 50)
        print(f"OUTREACH MESSAGE FOR: {best_candidate['name']}")
        print("=" * 50)
        print(best_candidate.get('outreach_message', 'No message generated'))
    
    print(f"\n✅ Example completed successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(basic_example())
    except KeyboardInterrupt:
        print("\n❌ Example cancelled by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        raise
