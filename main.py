#!/usr/bin/env python3
"""
AI-Recruitment-Agent: Multi-Agent System for Automated Recruitment
Built using Google ADK (Agent Development Kit)

This module implements the main entry point for the AI recruitment agent.
"""

import logging
from typing import Dict, Any, Optional
import json
from dataclasses import dataclass
from datetime import datetime

# Simulating ADK imports (would be: from google.adk import Agent, Tool, etc.)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CandidateProfile:
    """Represents a candidate profile."""
    name: str
    email: str
    resume_text: str
    skills: list[str]
    experience_years: float
    
class RecruitmentAgent:
    """Multi-agent orchestrator for recruitment workflows."""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash"):
        """
        Initialize the recruitment agent.
        
        Args:
            api_key: Gemini API key
            model: LLM model to use
        """
        self.api_key = api_key
        self.model = model
        self.session_state = {}
        logger.info(f"Initialized RecruitmentAgent with model: {model}")
    
    def screen_candidate(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Screen a candidate against a job description.
        
        This demonstrates the SCREENING AGENT (Feature: Multi-agent system).
        """
        logger.info(f"Screening candidate resume against job")
        
        # Extract key skills from resume
        resume_skills = self._extract_skills(resume_text)
        
        # Extract required skills from job description
        job_skills = self._extract_job_requirements(job_description)
        
        # Calculate match score
        match_score = self._calculate_match_score(resume_skills, job_skills)
        
        screening_result = {
            "match_score": match_score,
            "resume_skills": resume_skills,
            "required_skills": job_skills,
            "recommendation": "PASS" if match_score >= 70 else "REVIEW" if match_score >= 50 else "REJECT",
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in session memory (Feature: Sessions & Memory)
        self._save_to_memory("screening_result", screening_result)
        
        return screening_result
    
    def match_jobs(self, candidate: CandidateProfile, job_database: list[Dict]) -> Dict[str, Any]:
        """
        Match candidate to suitable jobs.
        
        This demonstrates the MATCHING AGENT (Feature: Sequential agents).
        """
        logger.info(f"Matching jobs for candidate: {candidate.name}")
        
        matches = []
        for job in job_database:
            score = self._calculate_job_fit(candidate, job)
            if score > 50:
                matches.append({
                    "job_id": job["id"],
                    "title": job["title"],
                    "company": job["company"],
                    "match_score": score,
                    "key_matches": self._find_skill_matches(candidate.skills, job["required_skills"])
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        top_matches = matches[:3]  # Return top 3
        
        matching_result = {
            "candidate_id": candidate.name,
            "total_matches_found": len(matches),
            "top_matches": top_matches,
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_to_memory("matching_result", matching_result)
        return matching_result
    
    def generate_interview(self, role_title: str, candidate_skills: list[str]) -> Dict[str, Any]:
        """
        Generate interview questions for a specific role.
        
        This demonstrates the INTERVIEW AGENT (Feature: Tools integration).
        """
        logger.info(f"Generating interview questions for role: {role_title}")
        
        questions = [
            {"id": 1, "category": "Technical", "question": f"Describe your experience with {candidate_skills[0] if candidate_skills else 'software development'}?"},
            {"id": 2, "category": "Technical", "question": "Walk us through a challenging project you've worked on."},
            {"id": 3, "category": "Behavioral", "question": "How do you handle conflicts in a team environment?"},
            {"id": 4, "category": "Behavioral", "question": "Tell us about a time you failed and what you learned."},
            {"id": 5, "category": "Role-Specific", "question": f"Why are you interested in this {role_title} position?"}
        ]
        
        interview_result = {
            "role": role_title,
            "total_questions": len(questions),
            "questions": questions,
            "difficulty_level": "MEDIUM",
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_to_memory("interview_questions", interview_result)
        return interview_result
    
    def full_workflow(self, candidate_data: Dict[str, Any], job_description: str, jobs_db: list[Dict]) -> Dict[str, Any]:
        """
        Execute complete recruitment workflow.
        
        Demonstrates: Sequential agents, Memory management, Observability.
        """
        logger.info(f"Starting full workflow for: {candidate_data['name']}")
        
        # Step 1: Screen candidate
        screening = self.screen_candidate(candidate_data["resume"], job_description)
        
        if screening["recommendation"] == "REJECT":
            logger.warning(f"Candidate {candidate_data['name']} rejected in screening")
            return {"status": "REJECTED", "stage": "screening", "result": screening}
        
        # Step 2: Match jobs (Parallel: could run simultaneously in production)
        candidate = CandidateProfile(
            name=candidate_data["name"],
            email=candidate_data["email"],
            resume_text=candidate_data["resume"],
            skills=candidate_data.get("skills", []),
            experience_years=candidate_data.get("experience_years", 0)
        )
        matching = self.match_jobs(candidate, jobs_db)
        
        # Step 3: Generate interview
        if matching["top_matches"]:
            best_match = matching["top_matches"][0]
            interview = self.generate_interview(best_match["title"], candidate.skills)
        else:
            interview = {"status": "NO_MATCHES"}
        
        # Combine results
        workflow_result = {
            "candidate_name": candidate_data["name"],
            "overall_status": "COMPLETED",
            "screening": screening,
            "matching": matching,
            "interview": interview,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Workflow completed for {candidate_data['name']}")
        return workflow_result
    
    def _extract_skills(self, resume_text: str) -> list[str]:
        """Extract skills from resume (Custom Tool)."""
        # Simulated skill extraction
        skills = []
        keywords = ["Python", "Java", "Machine Learning", "Data Analysis", "Cloud", "SQL", "API", "Docker"]
        for keyword in keywords:
            if keyword.lower() in resume_text.lower():
                skills.append(keyword)
        return skills
    
    def _extract_job_requirements(self, job_description: str) -> list[str]:
        """Extract requirements from job description (Custom Tool)."""
        skills = []
        keywords = ["Python", "Java", "Machine Learning", "Data Analysis", "Cloud", "SQL", "API", "Docker"]
        for keyword in keywords:
            if keyword.lower() in job_description.lower():
                skills.append(keyword)
        return skills
    
    def _calculate_match_score(self, candidate_skills: list[str], required_skills: list[str]) -> float:
        """Calculate resume-to-job match percentage."""
        if not required_skills:
            return 0
        matches = len(set(candidate_skills) & set(required_skills))
        return (matches / len(required_skills)) * 100
    
    def _calculate_job_fit(self, candidate: CandidateProfile, job: Dict) -> float:
        """Calculate candidate-job fit score."""
        skill_match = len(set(candidate.skills) & set(job.get("required_skills", []))) / max(1, len(job.get("required_skills", [])))
        exp_match = min(1.0, candidate.experience_years / max(1, job.get("years_experience_required", 1)))
        return (skill_match * 60 + exp_match * 40)  # Weighted score
    
    def _find_skill_matches(self, candidate_skills: list[str], job_skills: list[str]) -> list[str]:
        """Find overlapping skills."""
        return list(set(candidate_skills) & set(job_skills))
    
    def _save_to_memory(self, key: str, value: Any) -> None:
        """Store data in session memory (InMemorySessionService simulation)."""
        self.session_state[key] = value
        logger.debug(f"Saved to memory: {key}")
    
    def get_session_state(self) -> Dict[str, Any]:
        """Retrieve complete session state (Long-term memory)."""
        return self.session_state

def main():
    """Main entry point."""
    # Sample data
    sample_candidate = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "resume": "Experienced Python developer with 5 years in Machine Learning and Cloud technologies. Proficient in Docker, SQL, and API development. Strong track record building scalable data pipelines.",
        "skills": ["Python", "Machine Learning", "Cloud", "Docker", "SQL", "API"],
        "experience_years": 5
    }
    
    sample_job_description = "Senior Python Developer with Machine Learning expertise. Experience in Cloud platforms required. Strong SQL and API design skills needed."
    
    sample_jobs = [
        {
            "id": "job_001",
            "title": "Senior ML Engineer",
            "company": "TechCorp",
            "required_skills": ["Python", "Machine Learning", "Cloud"],
            "years_experience_required": 3
        },
        {
            "id": "job_002",
            "title": "Data Engineer",
            "company": "DataFlow Inc",
            "required_skills": ["Python", "SQL", "Docker"],
            "years_experience_required": 2
        },
        {
            "id": "job_003",
            "title": "Backend Developer",
            "company": "WebServices Ltd",
            "required_skills": ["Java", "API", "Docker"],
            "years_experience_required": 4
        }
    ]
    
    # Initialize agent
    agent = RecruitmentAgent()
    
    # Run full workflow
    result = agent.full_workflow(sample_candidate, sample_job_description, sample_jobs)
    
    # Print results
    print(json.dumps(result, indent=2))
    
    # Print session memory
    print("\n=== Session Memory ===")
    print(json.dumps(agent.get_session_state(), indent=2, default=str))

if __name__ == "__main__":
    main()
