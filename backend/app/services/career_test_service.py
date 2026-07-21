"""Career Aptitude Test Service for LearnMate AI.

Contains the question bank, scoring logic, and result calculation.
Deterministic rule-based scoring -- no randomness.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("learnmate.career_test")

# ---------------------------------------------------------------------------
# Supported careers
# ---------------------------------------------------------------------------

CAREERS = [
    {"id": "ai_engineer", "name": "AI Engineer", "description": "Design and build AI systems and models", "skills": ["Python", "Deep Learning", "MLOps", "Cloud"]},
    {"id": "data_scientist", "name": "Data Scientist", "description": "Analyze data to extract insights and build models", "skills": ["Python", "Statistics", "ML", "SQL"]},
    {"id": "ml_engineer", "name": "Machine Learning Engineer", "description": "Build and deploy ML systems at scale", "skills": ["Python", "ML", "Engineering", "Cloud"]},
    {"id": "full_stack_dev", "name": "Full Stack Developer", "description": "Build complete web applications end-to-end", "skills": ["JavaScript", "React", "Node.js", "Databases"]},
    {"id": "frontend_dev", "name": "Frontend Developer", "description": "Create beautiful user interfaces and experiences", "skills": ["HTML", "CSS", "JavaScript", "React"]},
    {"id": "backend_dev", "name": "Backend Developer", "description": "Build server-side logic and APIs", "skills": ["Python", "APIs", "Databases", "Architecture"]},
    {"id": "cybersecurity", "name": "Cybersecurity Analyst", "description": "Protect systems from digital threats", "skills": ["Networking", "Security", "Linux", "Analysis"]},
    {"id": "cloud_engineer", "name": "Cloud Engineer", "description": "Design and manage cloud infrastructure", "skills": ["AWS/Azure/GCP", "DevOps", "Networking", "Security"]},
    {"id": "devops_engineer", "name": "DevOps Engineer", "description": "Automate and optimize software delivery", "skills": ["CI/CD", "Docker", "Kubernetes", "Linux"]},
    {"id": "uiux_designer", "name": "UI/UX Designer", "description": "Design intuitive and beautiful user experiences", "skills": ["Design", "Prototyping", "Research", "Figma"]},
    {"id": "mobile_dev", "name": "Mobile App Developer", "description": "Build mobile applications for iOS and Android", "skills": ["React Native", "Swift", "Kotlin", "UI Design"]},
    {"id": "software_eng", "name": "Software Engineer", "description": "Design, build, and maintain software systems", "skills": ["Programming", "Architecture", "Testing", "Debugging"]},
    {"id": "game_dev", "name": "Game Developer", "description": "Create interactive games and simulations", "skills": ["Unity/Unreal", "C#", "3D Graphics", "Physics"]},
    {"id": "blockchain_dev", "name": "Blockchain Developer", "description": "Build decentralized applications and smart contracts", "skills": ["Solidity", "Web3", "Cryptography", "Smart Contracts"]},
    {"id": "business_analyst", "name": "Business Analyst", "description": "Bridge business needs with technical solutions", "skills": ["Analysis", "SQL", "Communication", "Requirements"]},
    {"id": "product_manager", "name": "Product Manager", "description": "Lead product strategy and delivery", "skills": ["Strategy", "UX", "Data Analysis", "Leadership"]},
    {"id": "data_analyst", "name": "Data Analyst", "description": "Transform data into actionable business insights", "skills": ["SQL", "Excel", "Visualization", "Statistics"]},
]

# ---------------------------------------------------------------------------
# Question bank: 25 questions, 4 options each
# Each answer secretly increments career scores
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "id": 1,
        "text": "Which activity do you enjoy most?",
        "category": "interests",
        "options": [
            {"id": "a", "text": "Building websites and apps", "scores": {"full_stack_dev": 4, "frontend_dev": 3, "software_eng": 2}},
            {"id": "b", "text": "Solving complex programming problems", "scores": {"software_eng": 4, "backend_dev": 3, "ai_engineer": 2}},
            {"id": "c", "text": "Finding patterns in data", "scores": {"data_scientist": 5, "ai_engineer": 3, "data_analyst": 3}},
            {"id": "d", "text": "Designing beautiful interfaces", "scores": {"uiux_designer": 5, "frontend_dev": 4, "mobile_dev": 2}},
        ],
    },
    {
        "id": 2,
        "text": "What type of projects excite you most?",
        "category": "interests",
        "options": [
            {"id": "a", "text": "Training AI models", "scores": {"ai_engineer": 5, "ml_engineer": 4, "data_scientist": 3}},
            {"id": "b", "text": "Building responsive websites", "scores": {"full_stack_dev": 4, "frontend_dev": 5, "mobile_dev": 2}},
            {"id": "c", "text": "Securing network systems", "scores": {"cybersecurity": 5, "cloud_engineer": 3, "devops_engineer": 2}},
            {"id": "d", "text": "Creating mobile apps", "scores": {"mobile_dev": 5, "uiux_designer": 3, "full_stack_dev": 2}},
        ],
    },
    {
        "id": 3,
        "text": "Which skill would you most like to master?",
        "category": "skills",
        "options": [
            {"id": "a", "text": "Machine learning algorithms", "scores": {"ml_engineer": 5, "ai_engineer": 4, "data_scientist": 3}},
            {"id": "b", "text": "Cloud infrastructure", "scores": {"cloud_engineer": 5, "devops_engineer": 4, "backend_dev": 2}},
            {"id": "c", "text": "User experience design", "scores": {"uiux_designer": 5, "frontend_dev": 3, "product_manager": 2}},
            {"id": "d", "text": "Cybersecurity defense", "scores": {"cybersecurity": 5, "cloud_engineer": 2, "devops_engineer": 2}},
        ],
    },
    {
        "id": 4,
        "text": "How do you prefer to work?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Independently on deep technical tasks", "scores": {"ai_engineer": 3, "software_eng": 3, "data_scientist": 2}},
            {"id": "b", "text": "Collaborating with cross-functional teams", "scores": {"product_manager": 4, "business_analyst": 3, "full_stack_dev": 2}},
            {"id": "c", "text": "Leading projects and making decisions", "scores": {"product_manager": 5, "business_analyst": 3, "cloud_engineer": 2}},
            {"id": "d", "text": "Iterating on visual and interactive designs", "scores": {"uiux_designer": 5, "frontend_dev": 3, "mobile_dev": 2}},
        ],
    },
    {
        "id": 5,
        "text": "Which environment appeals to you most?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Fast-paced startup with many hats", "scores": {"full_stack_dev": 3, "software_eng": 3, "product_manager": 2}},
            {"id": "b", "text": "Large enterprise with clear processes", "scores": {"cloud_engineer": 3, "cybersecurity": 3, "business_analyst": 2}},
            {"id": "c", "text": "Research lab pushing boundaries", "scores": {"ai_engineer": 4, "data_scientist": 4, "ml_engineer": 3}},
            {"id": "d", "text": "Creative studio building products", "scores": {"uiux_designer": 4, "frontend_dev": 3, "game_dev": 3}},
        ],
    },
    {
        "id": 6,
        "text": "What is your preferred programming language?",
        "category": "skills",
        "options": [
            {"id": "a", "text": "Python", "scores": {"data_scientist": 3, "ai_engineer": 3, "backend_dev": 2, "ml_engineer": 2}},
            {"id": "b", "text": "JavaScript/TypeScript", "scores": {"full_stack_dev": 3, "frontend_dev": 4, "mobile_dev": 2}},
            {"id": "c", "text": "C/C++/Rust", "scores": {"game_dev": 3, "software_eng": 3, "blockchain_dev": 2}},
            {"id": "d", "text": "SQL and data languages", "scores": {"data_analyst": 4, "data_scientist": 2, "business_analyst": 2}},
        ],
    },
    {
        "id": 7,
        "text": "How do you approach problem-solving?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Systematic analysis and testing", "scores": {"data_analyst": 3, "software_eng": 3, "cybersecurity": 2}},
            {"id": "b", "text": "Creative brainstorming and prototyping", "scores": {"uiux_designer": 4, "game_dev": 3, "frontend_dev": 2}},
            {"id": "c", "text": "Data-driven decision making", "scores": {"data_scientist": 4, "business_analyst": 3, "product_manager": 2}},
            {"id": "d", "text": "Breaking into smaller manageable tasks", "scores": {"devops_engineer": 3, "full_stack_dev": 3, "backend_dev": 2}},
        ],
    },
    {
        "id": 8,
        "text": "Which topic interests you most?",
        "category": "interests",
        "options": [
            {"id": "a", "text": "Artificial intelligence and neural networks", "scores": {"ai_engineer": 5, "ml_engineer": 4, "data_scientist": 2}},
            {"id": "b", "text": "Web development and design", "scores": {"frontend_dev": 4, "full_stack_dev": 4, "uiux_designer": 2}},
            {"id": "c", "text": "Cloud computing and DevOps", "scores": {"cloud_engineer": 5, "devops_engineer": 4, "backend_dev": 2}},
            {"id": "d", "text": "Blockchain and decentralization", "scores": {"blockchain_dev": 5, "software_eng": 2, "backend_dev": 2}},
        ],
    },
    {
        "id": 9,
        "text": "What motivates you most in your career?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Building something millions will use", "scores": {"full_stack_dev": 3, "mobile_dev": 3, "frontend_dev": 2}},
            {"id": "b", "text": "Pushing the boundaries of what's possible", "scores": {"ai_engineer": 4, "ml_engineer": 3, "game_dev": 3}},
            {"id": "c", "text": "Protecting people and organizations", "scores": {"cybersecurity": 5, "cloud_engineer": 2}},
            {"id": "d", "text": "Making data-backed business decisions", "scores": {"business_analyst": 4, "data_analyst": 3, "product_manager": 3}},
        ],
    },
    {
        "id": 10,
        "text": "Which tool would you enjoy learning most?",
        "category": "skills",
        "options": [
            {"id": "a", "text": "TensorFlow or PyTorch", "scores": {"ml_engineer": 5, "ai_engineer": 4, "data_scientist": 2}},
            {"id": "b", "text": "Figma or Adobe XD", "scores": {"uiux_designer": 5, "frontend_dev": 2, "game_dev": 2}},
            {"id": "c", "text": "Docker and Kubernetes", "scores": {"devops_engineer": 5, "cloud_engineer": 4, "backend_dev": 2}},
            {"id": "d", "text": "Wireshark and Nmap", "scores": {"cybersecurity": 5, "cloud_engineer": 2}},
        ],
    },
    {
        "id": 11,
        "text": "How do you handle deadlines?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Plan carefully and execute methodically", "scores": {"business_analyst": 3, "cloud_engineer": 2, "software_eng": 2}},
            {"id": "b", "text": "Work intensely close to the deadline", "scores": {"frontend_dev": 2, "game_dev": 2, "full_stack_dev": 2}},
            {"id": "c", "text": "Break work into sprints", "scores": {"devops_engineer": 3, "product_manager": 3, "full_stack_dev": 2}},
            {"id": "d", "text": "Collaborate and delegate effectively", "scores": {"product_manager": 4, "business_analyst": 3}},
        ],
    },
    {
        "id": 12,
        "text": "What type of data do you enjoy working with?",
        "category": "interests",
        "options": [
            {"id": "a", "text": "Large datasets and statistical models", "scores": {"data_scientist": 5, "data_analyst": 3, "ai_engineer": 2}},
            {"id": "b", "text": "User behavior and analytics", "scores": {"data_analyst": 4, "product_manager": 3, "business_analyst": 3}},
            {"id": "c", "text": "Network traffic and logs", "scores": {"cybersecurity": 4, "devops_engineer": 3, "cloud_engineer": 2}},
            {"id": "d", "text": "I prefer working with visual content", "scores": {"uiux_designer": 4, "game_dev": 3, "frontend_dev": 2}},
        ],
    },
    {
        "id": 13,
        "text": "Which certification would you pursue?",
        "category": "interests",
        "options": [
            {"id": "a", "text": "AWS/Azure Cloud Certification", "scores": {"cloud_engineer": 5, "devops_engineer": 3, "backend_dev": 2}},
            {"id": "b", "text": "Google Data Analytics", "scores": {"data_analyst": 5, "data_scientist": 3, "business_analyst": 2}},
            {"id": "c", "text": "CompTIA Security+", "scores": {"cybersecurity": 5, "cloud_engineer": 2}},
            {"id": "d", "text": "Meta Frontend Developer", "scores": {"frontend_dev": 5, "full_stack_dev": 3, "uiux_designer": 2}},
        ],
    },
    {
        "id": 14,
        "text": "How do you prefer to learn new technologies?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Reading documentation and books", "scores": {"software_eng": 3, "backend_dev": 2, "data_scientist": 2}},
            {"id": "b", "text": "Building projects hands-on", "scores": {"full_stack_dev": 3, "frontend_dev": 2, "game_dev": 2}},
            {"id": "c", "text": "Watching video tutorials", "scores": {"uiux_designer": 2, "mobile_dev": 2, "frontend_dev": 2}},
            {"id": "d", "text": "Taking structured online courses", "scores": {"ai_engineer": 2, "cloud_engineer": 2, "data_analyst": 2}},
        ],
    },
    {
        "id": 15,
        "text": "What is your ideal work-life balance?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Structured 9-5 with clear boundaries", "scores": {"business_analyst": 3, "data_analyst": 2, "cloud_engineer": 2}},
            {"id": "b", "text": "Flexible hours with remote options", "scores": {"full_stack_dev": 3, "frontend_dev": 3, "freelance": 2}},
            {"id": "c", "text": "Passionate about work, hours don't matter", "scores": {"ai_engineer": 2, "game_dev": 3, "startup": 2}},
            {"id": "d", "text": "Prefer contract/project-based work", "scores": {"blockchain_dev": 2, "consultant": 2, "product_manager": 2}},
        ],
    },
    {
        "id": 16,
        "text": "Which industry excites you most?",
        "category": "interests",
        "options": [
            {"id": "a", "text": "Healthcare and biotech", "scores": {"data_scientist": 3, "ai_engineer": 2, "data_analyst": 2}},
            {"id": "b", "text": "Finance and fintech", "scores": {"blockchain_dev": 3, "data_analyst": 3, "business_analyst": 2}},
            {"id": "c", "text": "Gaming and entertainment", "scores": {"game_dev": 5, "uiux_designer": 3, "frontend_dev": 2}},
            {"id": "d", "text": "E-commerce and SaaS", "scores": {"full_stack_dev": 3, "product_manager": 3, "frontend_dev": 2}},
        ],
    },
    {
        "id": 17,
        "text": "How do you handle debugging?",
        "category": "skills",
        "options": [
            {"id": "a", "text": "Methodical step-by-step process", "scores": {"software_eng": 4, "backend_dev": 3, "cybersecurity": 2}},
            {"id": "b", "text": "Using visual tools and browser devtools", "scores": {"frontend_dev": 4, "uiux_designer": 2, "full_stack_dev": 2}},
            {"id": "c", "text": "Analyzing logs and metrics", "scores": {"devops_engineer": 4, "cloud_engineer": 3, "cybersecurity": 2}},
            {"id": "d", "text": "Running experiments and A/B tests", "scores": {"data_scientist": 3, "product_manager": 3, "data_analyst": 2}},
        ],
    },
    {
        "id": 18,
        "text": "Which best describes your communication style?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Technical and precise", "scores": {"software_eng": 3, "backend_dev": 2, "cybersecurity": 2}},
            {"id": "b", "text": "Visual and creative", "scores": {"uiux_designer": 4, "frontend_dev": 3, "game_dev": 2}},
            {"id": "c", "text": "Strategic and persuasive", "scores": {"product_manager": 5, "business_analyst": 3}},
            {"id": "d", "text": "Data-driven and analytical", "scores": {"data_analyst": 4, "data_scientist": 3, "business_analyst": 2}},
        ],
    },
    {
        "id": 19,
        "text": "What scale of system do you enjoy building?",
        "category": "interests",
        "options": [
            {"id": "a", "text": "Microservices and distributed systems", "scores": {"cloud_engineer": 4, "devops_engineer": 3, "backend_dev": 3}},
            {"id": "b", "text": "Single-page applications", "scores": {"frontend_dev": 5, "full_stack_dev": 3}},
            {"id": "c", "text": "ML pipelines and data flows", "scores": {"ml_engineer": 5, "data_scientist": 3, "ai_engineer": 2}},
            {"id": "d", "text": "Mobile-first applications", "scores": {"mobile_dev": 5, "full_stack_dev": 2, "uiux_designer": 2}},
        ],
    },
    {
        "id": 20,
        "text": "How do you approach security?",
        "category:": "personality",
        "options": [
            {"id": "a", "text": "Security-first mindset in everything", "scores": {"cybersecurity": 5, "cloud_engineer": 2, "devops_engineer": 2}},
            {"id": "b", "text": "Follow best practices and standards", "scores": {"software_eng": 3, "backend_dev": 3, "cloud_engineer": 2}},
            {"id": "c", "text": "Focus on user privacy and consent", "scores": {"product_manager": 3, "uiux_designer": 2, "business_analyst": 2}},
            {"id": "d", "text": "Smart contracts and decentralized security", "scores": {"blockchain_dev": 5, "cybersecurity": 2}},
        ],
    },
    {
        "id": 21,
        "text": "What kind of impact do you want to make?",
        "category": "interests",
        "options": [
            {"id": "a", "text": "Automate repetitive tasks", "scores": {"devops_engineer": 4, "ai_engineer": 3, "backend_dev": 2}},
            {"id": "b", "text": "Help people learn and grow", "scores": {"product_manager": 3, "business_analyst": 2}},
            {"id": "c", "text": "Create products people love", "scores": {"uiux_designer": 4, "frontend_dev": 3, "mobile_dev": 3}},
            {"id": "d", "text": "Protect organizations from threats", "scores": {"cybersecurity": 5, "cloud_engineer": 2}},
        ],
    },
    {
        "id": 22,
        "text": "Which framework interests you most?",
        "category": "skills",
        "options": [
            {"id": "a", "text": "React or Vue.js", "scores": {"frontend_dev": 5, "full_stack_dev": 3, "mobile_dev": 2}},
            {"id": "b", "text": "Django or FastAPI", "scores": {"backend_dev": 4, "full_stack_dev": 2, "data_scientist": 2}},
            {"id": "c", "text": "TensorFlow or Hugging Face", "scores": {"ml_engineer": 5, "ai_engineer": 4, "data_scientist": 2}},
            {"id": "d", "text": "Unity or Unreal Engine", "scores": {"game_dev": 5, "uiux_designer": 2}},
        ],
    },
    {
        "id": 23,
        "text": "How do you handle ambiguity?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Research until I find clarity", "scores": {"data_scientist": 3, "business_analyst": 3, "data_analyst": 2}},
            {"id": "b", "text": "Prototype and iterate quickly", "scores": {"full_stack_dev": 3, "uiux_designer": 3, "frontend_dev": 2}},
            {"id": "c", "text": "Define requirements first", "scores": {"product_manager": 4, "business_analyst": 3, "software_eng": 2}},
            {"id": "d", "text": "Break it into known components", "scores": {"software_eng": 3, "devops_engineer": 2, "cloud_engineer": 2}},
        ],
    },
    {
        "id": 24,
        "text": "What is your career after 5 years?",
        "category": "goals",
        "options": [
            {"id": "a", "text": "Tech lead or architect", "scores": {"software_eng": 4, "full_stack_dev": 2, "cloud_engineer": 2}},
            {"id": "b", "text": "AI/ML specialist", "scores": {"ai_engineer": 4, "ml_engineer": 4, "data_scientist": 2}},
            {"id": "c", "text": "Product or engineering manager", "scores": {"product_manager": 5, "business_analyst": 2}},
            {"id": "d", "text": "Independent consultant or founder", "scores": {"blockchain_dev": 2, "game_dev": 2, "full_stack_dev": 2}},
        ],
    },
    {
        "id": 25,
        "text": "Which best describes your creative process?",
        "category": "personality",
        "options": [
            {"id": "a", "text": "Visual and design-oriented", "scores": {"uiux_designer": 5, "frontend_dev": 3, "game_dev": 2}},
            {"id": "b", "text": "Logical and algorithmic", "scores": {"software_eng": 3, "ai_engineer": 3, "data_scientist": 2}},
            {"id": "c", "text": "Systems thinking and architecture", "scores": {"cloud_engineer": 3, "devops_engineer": 3, "backend_dev": 2}},
            {"id": "d", "text": "User empathy and storytelling", "scores": {"product_manager": 4, "uiux_designer": 3, "business_analyst": 2}},
        ],
    },
]


def get_questions() -> List[Dict[str, Any]]:
    """Return all questions without score information (sent to client)."""
    return [
        {
            "id": q["id"],
            "text": q["text"],
            "category": q.get("category", ""),
            "options": [{"id": o["id"], "text": o["text"]} for o in q["options"]],
        }
        for q in QUESTIONS
    ]


def calculate_scores(answers: Dict[str, str]) -> List[Dict[str, Any]]:
    """Calculate career scores from answers. Deterministic.

    Args:
        answers: Mapping of question_id (str) -> answer_id (str).

    Returns:
        List of career score dicts sorted by percentage descending.
    """
    raw_scores: Dict[str, float] = {c["id"]: 0.0 for c in CAREERS}

    for q in QUESTIONS:
        qid = str(q["id"])
        aid = answers.get(qid)
        if not aid:
            continue
        for opt in q["options"]:
            if opt["id"] == aid:
                for career_id, pts in opt.get("scores", {}).items():
                    if career_id in raw_scores:
                        raw_scores[career_id] += pts
                break

    # Normalize to percentages
    max_possible = max(raw_scores.values()) if raw_scores else 1
    if max_possible == 0:
        max_possible = 1

    results = []
    for career in CAREERS:
        raw = raw_scores[career["id"]]
        pct = round((raw / max_possible) * 100, 1)
        results.append({
            "career_id": career["id"],
            "career_name": career["name"],
            "score": raw,
            "percentage": pct,
            "description": career["description"],
            "skills": career["skills"],
        })

    results.sort(key=lambda x: x["percentage"], reverse=True)
    return results


def get_top_careers(answers: Dict[str, str], top_n: int = 3) -> List[Dict[str, Any]]:
    """Get the top N career matches."""
    all_scores = calculate_scores(answers)
    return all_scores[:top_n]


def get_career_recommendations(career_id: str, resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """Filter resources relevant to a career."""
    career = next((c for c in CAREERS if c["id"] == career_id), None)
    if not career:
        return {"courses": [], "projects": [], "certifications": [], "books": []}

    career_skills = set(s.lower() for s in career["skills"])
    career_name_lower = career["name"].lower()

    def matches(item: Dict[str, Any]) -> bool:
        item_text = " ".join([
            str(item.get("title", "")),
            str(item.get("name", "")),
            str(item.get("domain", "")),
            str(item.get("category", "")),
            str(item.get("description", "")),
            " ".join(item.get("skills_gained", [])),
            " ".join(item.get("skills_covered", [])),
            " ".join(item.get("required_skills", [])),
            " ".join(item.get("tags", [])),
        ]).lower()
        if career_name_lower in item_text:
            return True
        return any(s in item_text for s in career_skills)

    return {
        "courses": [c for c in resources.get("courses", []) if matches(c)][:6],
        "projects": [p for p in resources.get("projects", []) if matches(p)][:6],
        "certifications": [c for c in resources.get("certifications", []) if matches(c)][:6],
        "books": [b for b in resources.get("books", []) if matches(b)][:6],
    }
