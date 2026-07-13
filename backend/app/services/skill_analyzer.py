"""Skill Gap Analyzer for LearnMate AI.

Analyses a student's current skills against their desired career path
to identify missing skills, learning priorities, coverage percentage,
and categorised improvement areas.

Loads career pathway data from JSON datasets and performs deterministic
matching without requiring external API calls.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.student import StudentProfile

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path configuration (mirrors rag_service.py convention)
# ---------------------------------------------------------------------------

_BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR: Path = _BACKEND_ROOT / "data"


# ---------------------------------------------------------------------------
# Skill domain categorisation mapping
# ---------------------------------------------------------------------------

SKILL_DOMAIN_MAP: Dict[str, List[str]] = {
    "Programming": [
        "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", "Ruby",
        "PHP", "Swift", "Kotlin", "TypeScript", "R programming",
        "Python syntax", "Scripting",
    ],
    "Web Development": [
        "HTML5", "CSS3", "JavaScript", "React", "Vue.js", "Angular",
        "Responsive design", "DOM manipulation", "JSX", "React Router",
        "REST APIs", "REST API design", "HTTP basics",
    ],
    "Frontend Development": [
        "HTML5", "CSS3", "React", "Vue.js", "Angular",
        "Responsive design", "DOM manipulation", "JSX", "Hooks",
        "State management", "React Router", "Figma", "Wireframing",
        "Prototyping", "User research", "Accessibility",
    ],
    "Backend Development": [
        "Node.js", "FastAPI", "Pydantic", "Django", "Flask",
        "REST APIs", "REST API design", "Async programming",
        "Python syntax", "OpenAPI",
    ],
    "Data Science": [
        "Pandas", "NumPy", "Matplotlib", "Data cleaning", "EDA",
        "Statistics", "Data visualization", "Data preprocessing",
        "Probability", "Hypothesis testing", "Regression",
        "Statistical inference", "Jupyter notebooks", "Seaborn",
        "Data visualization",
    ],
    "Machine Learning": [
        "Scikit-learn", "Machine learning", "Classification",
        "Clustering", "Model evaluation", "MLflow", "Model serving",
        "MLOps", "Model monitoring", "Time series basics",
    ],
    "Artificial Intelligence": [
        "Deep learning", "TensorFlow", "Keras", "PyTorch", "NLP",
        "Transformers", "CNN", "RNN", "Transfer learning", "BERT",
        "Text classification", "Tokenization", "Neural networks",
        "Computer vision basics",
    ],
    "Cloud Computing": [
        "AWS", "Azure", "GCP", "AWS core services", "Cloud architecture",
        "IAM", "S3", "EC2", "Azure services", "Cloud concepts",
        "Serverless concepts", "AWS Lambda", "API Gateway", "DynamoDB",
    ],
    "Cybersecurity": [
        "Security tools", "Penetration testing", "SIEM", "Cryptography",
        "Incident response", "Compliance", "Nmap", "Wireshark",
        "Vulnerability assessment", "OWASP", "Threat detection",
        "Risk management", "Identity management",
    ],
    "Databases": [
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "Database design", "Normalization", "Joins", "NoSQL",
        "Document databases", "Caching", "Aggregation pipeline",
    ],
    "DevOps": [
        "Docker", "Kubernetes", "CI/CD", "Terraform", "Docker Compose",
        "Containers", "Helm", "Monitoring", "Shell scripting",
        "Linux CLI", "File systems", "Process management",
        "Infrastructure as code", "Cloud provisioning", "Modules",
    ],
    "Operating Systems": [
        "Linux", "Linux CLI", "Linux basics", "Linux fundamentals",
        "Command line", "Networking basics",
    ],
    "Networking": [
        "Networking basics", "Network fundamentals", "IP connectivity",
        "IP services", "Networking",
    ],
    "Soft Skills": [
        "Communication", "Team collaboration", "Leadership",
        "Presentation skills", "Time management",
    ],
    "Version Control": [
        "Git", "GitHub", "Version control", "GitLab",
    ],
}

# Reverse lookup: normalised skill name -> domain (first match wins)
_SKILL_TO_DOMAIN: Dict[str, str] = {}
for _domain, _skills in SKILL_DOMAIN_MAP.items():
    for _skill in _skills:
        _key = _skill.lower().strip()
        if _key not in _SKILL_TO_DOMAIN:
            _SKILL_TO_DOMAIN[_key] = _domain


def categorize_skill(skill: str) -> str:
    """Map a skill name to its domain category.

    Args:
        skill: The skill name to categorise.

    Returns:
        The domain category string, or ``"General"`` if uncategorised.
    """
    key = skill.lower().strip()
    if key in _SKILL_TO_DOMAIN:
        return _SKILL_TO_DOMAIN[key]

    # Fuzzy fallback: substring containment
    for mapped_skill, domain in _SKILL_TO_DOMAIN.items():
        if key in mapped_skill or mapped_skill in key:
            return domain

    return "General"


# ---------------------------------------------------------------------------
# Skill Analysis Result Model
# ---------------------------------------------------------------------------


class SkillAnalysisResult(BaseModel):
    """Structured result of a skill gap analysis.

    Attributes:
        missing_skills: Skills required by the career but not yet mastered.
        mastered_skills: Skills the student already possesses.
        matched_skills: Career-required skills the student already has.
        priority_skills: Missing skills ordered by learning priority.
        coverage_percentage: Percentage of required skills already mastered.
        improvement_areas: Ranked areas needing improvement.
        recommended_learning_order: Ordered list of skills to learn next.
        career_path: The matched career pathway data.
        prerequisites: Missing prerequisites to learn first.
        categorized_skills: Skills grouped by domain category.
        total_required_skills: Total number of skills required.
    """

    missing_skills: List[str] = Field(default_factory=list)
    mastered_skills: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    priority_skills: List[str] = Field(default_factory=list)
    coverage_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    improvement_areas: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_learning_order: List[str] = Field(default_factory=list)
    career_path: Dict[str, Any] = Field(default_factory=dict)
    prerequisites: List[str] = Field(default_factory=list)
    categorized_skills: Dict[str, List[str]] = Field(default_factory=dict)
    total_required_skills: int = Field(default=0)


# ---------------------------------------------------------------------------
# Skill Gap Analyzer
# ---------------------------------------------------------------------------


class SkillGapAnalyzer:
    """Analyses skill gaps between a student profile and their career goal.

    Loads career pathway and course prerequisite data from JSON datasets
    and performs deterministic matching, coverage calculation, and
    priority ranking of learning areas.
    """

    def __init__(self) -> None:
        """Initialise the analyzer and cache career pathway data."""
        self._career_pathways: List[Dict[str, Any]] = []
        self._courses: List[Dict[str, Any]] = []
        self._load_datasets()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_datasets(self) -> None:
        """Load career pathways and courses from JSON datasets."""
        self._career_pathways = self._load_json("career_pathways.json")
        self._courses = self._load_json("courses.json")
        logger.info(
            "SkillGapAnalyzer loaded: %d pathways, %d courses",
            len(self._career_pathways),
            len(self._courses),
        )

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load a JSON file from the data directory.

        Args:
            filename: Name of the JSON file.

        Returns:
            Parsed list of dictionaries, or empty list on failure.
        """
        path = _DATA_DIR / filename
        if not path.exists():
            logger.warning("Dataset file not found: %s", path)
            return []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load %s: %s", filename, exc)
            return []

    # ------------------------------------------------------------------
    # Career pathway matching
    # ------------------------------------------------------------------

    def _find_career_pathway(
        self, career_goal: str
    ) -> Optional[Dict[str, Any]]:
        """Find the best matching career pathway for a given goal.

        Uses a multi-strategy matching approach:
        1. Exact name match
        2. Substring containment
        3. Keyword overlap scoring

        Args:
            career_goal: The student's target career role.

        Returns:
            The matching career pathway dict, or ``None``.
        """
        if not self._career_pathways:
            return None

        goal_lower = career_goal.lower().strip()

        # Strategy 1: exact match
        for pathway in self._career_pathways:
            if pathway["name"].lower() == goal_lower:
                return pathway

        # Strategy 2: substring containment
        for pathway in self._career_pathways:
            name_lower = pathway["name"].lower()
            if goal_lower in name_lower or name_lower in goal_lower:
                return pathway

        # Strategy 3: keyword overlap
        goal_words = set(goal_lower.split())
        best_match: Optional[Dict[str, Any]] = None
        best_score = 0

        for pathway in self._career_pathways:
            name_words = set(pathway["name"].lower().split())
            overlap = len(goal_words & name_words)
            if overlap > best_score:
                best_score = overlap
                best_match = pathway

        return best_match if best_score > 0 else None

    # ------------------------------------------------------------------
    # Skill matching helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_skill(skill: str) -> str:
        """Normalise a skill string for comparison."""
        return skill.lower().strip()

    def _skill_matches(
        self, student_skill: str, required_skill: str
    ) -> bool:
        """Determine if a student skill satisfies a required skill.

        Handles exact matches, substring containment, and compound
        requirements like ``"Node.js or Python"``.

        Args:
            student_skill: A skill the student possesses.
            required_skill: A skill required by the career path.

        Returns:
            ``True`` if the student skill satisfies the requirement.
        """
        s = self._normalize_skill(student_skill)
        r = self._normalize_skill(required_skill)

        # Exact match
        if s == r:
            return True

        # One contains the other
        if s in r or r in s:
            return True

        # Handle "or" alternatives (e.g. "TensorFlow or PyTorch")
        if " or " in r:
            alternatives = [a.strip().lower() for a in r.split(" or ")]
            return any(a in s or s in a for a in alternatives)

        return False

    # ------------------------------------------------------------------
    # Skill categorisation
    # ------------------------------------------------------------------

    @staticmethod
    def _categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
        """Group a list of skills by their domain category.

        Args:
            skills: List of skill name strings.

        Returns:
            Dictionary mapping domain names to lists of skill names.
        """
        categorized: Dict[str, List[str]] = {}
        for skill in skills:
            domain = categorize_skill(skill)
            if domain not in categorized:
                categorized[domain] = []
            if skill not in categorized[domain]:
                categorized[domain].append(skill)
        return dict(sorted(categorized.items()))

    # ------------------------------------------------------------------
    # Prerequisite detection
    # ------------------------------------------------------------------

    def _find_missing_prerequisites(
        self,
        missing_skills: List[str],
        student_skills: List[str],
    ) -> List[str]:
        """Identify prerequisite skills the student is missing.

        Examines course prerequisite chains to find foundational skills
        that should be learned before the missing career skills.

        Args:
            missing_skills: Skills the student lacks.
            student_skills: Skills the student already has.

        Returns:
            Ordered list of missing prerequisite skill names.
        """
        prerequisites: List[str] = []

        for missing_skill in missing_skills:
            for course in self._courses:
                skills_gained = [
                    s.lower() for s in course.get("skills_gained", [])
                ]
                teaches_missing = any(
                    missing_skill.lower() in sg
                    or sg in missing_skill.lower()
                    for sg in skills_gained
                )

                if not teaches_missing:
                    continue

                for prereq in course.get("prerequisites", []):
                    prereq_met = any(
                        self._skill_matches(student_skill, prereq)
                        for student_skill in student_skills
                    )
                    if not prereq_met and prereq not in prerequisites:
                        prerequisites.append(prereq)

        return prerequisites

    # ------------------------------------------------------------------
    # Improvement area ranking
    # ------------------------------------------------------------------

    def _rank_improvement_areas(
        self,
        missing_skills: List[str],
        prerequisites: List[str],
    ) -> List[Dict[str, Any]]:
        """Rank improvement areas by learning priority.

        Priority ordering:
        1. Missing prerequisites (highest priority)
        2. Remaining missing skills (by domain grouping)

        Args:
            missing_skills: Skills the student lacks.
            prerequisites: Prerequisite skills that are missing.

        Returns:
            Ordered list of improvement area dicts.
        """
        areas: List[Dict[str, Any]] = []
        prerequisite_set = {pr.lower() for pr in prerequisites}

        for skill in missing_skills:
            is_prereq = any(
                self._skill_matches(skill, pr) for pr in prerequisites
            )
            priority = 1 if is_prereq else 2
            domain = categorize_skill(skill)

            areas.append({
                "skill": skill,
                "domain": domain,
                "is_prerequisite": is_prereq,
                "priority": priority,
            })

        # Sort: prerequisites first, then alphabetically by domain
        areas.sort(key=lambda a: (a["priority"], a["domain"], a["skill"]))
        return areas

    # ------------------------------------------------------------------
    # Learning order determination
    # ------------------------------------------------------------------

    def _determine_learning_order(
        self,
        missing_skills: List[str],
        prerequisites: List[str],
        career_pathway: Dict[str, Any],
    ) -> List[str]:
        """Determine the optimal learning order for missing skills.

        Order:
        1. Missing prerequisites (foundational skills)
        2. Remaining skills in career-pathway order

        Args:
            missing_skills: Skills the student lacks.
            prerequisites: Prerequisite skills that are missing.
            career_pathway: The matched career pathway data.

        Returns:
            Ordered list of skill names to learn.
        """
        prerequisite_skills: List[str] = []
        non_prereq_skills: List[str] = []

        for skill in missing_skills:
            is_prereq = any(
                self._skill_matches(skill, pr) for pr in prerequisites
            )
            if is_prereq:
                prerequisite_skills.append(skill)
            else:
                non_prereq_skills.append(skill)

        # Order non-prerequisite skills by their position in the
        # career pathway's required_skills list (earlier = more foundational)
        required_order = {
            s.lower(): i
            for i, s in enumerate(
                career_pathway.get("required_skills", [])
            )
        }
        non_prereq_skills.sort(
            key=lambda s: required_order.get(s.lower(), 999)
        )

        return prerequisite_skills + non_prereq_skills

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_skill_gap(
        self, profile: StudentProfile
    ) -> SkillAnalysisResult:
        """Analyze the skill gap between a student and their career goal.

        Compares the student's current skills and completed topics against
        the required skills for their target career pathway. Produces a
        comprehensive analysis with coverage percentage, missing skills,
        prerequisites, and prioritised learning recommendations.

        Args:
            profile: The student's profile with current skills, interests,
                     career goal, and skill level.

        Returns:
            A comprehensive :class:`SkillAnalysisResult` with gaps,
            priorities, and recommendations.
        """
        logger.info(
            "Analyzing skill gap for '%s' -> '%s'",
            profile.name,
            profile.career_goal,
        )

        # Find matching career pathway
        career_pathway = self._find_career_pathway(profile.career_goal)

        if career_pathway is None:
            logger.warning(
                "No career pathway found for '%s' - returning empty analysis",
                profile.career_goal,
            )
            return SkillAnalysisResult(
                career_path={
                    "name": profile.career_goal,
                    "description": "",
                },
                coverage_percentage=0.0,
                categorized_skills=self._categorize_skills(
                    profile.current_skills
                ),
            )

        required_skills: List[str] = career_pathway.get(
            "required_skills", []
        )
        total_required = len(required_skills)

        # Build combined student skill set from profile + completed topics
        student_skills: List[str] = [
            s for s in profile.current_skills if s
        ]
        if profile.completed_topics:
            student_skills.extend(
                t for t in profile.completed_topics if t
            )

        # Match current skills against required skills
        matched: List[str] = []
        missing: List[str] = []

        for req_skill in required_skills:
            is_match = any(
                self._skill_matches(student_skill, req_skill)
                for student_skill in student_skills
            )
            if is_match:
                matched.append(req_skill)
            else:
                missing.append(req_skill)

        # Calculate coverage percentage
        coverage = (
            (len(matched) / total_required * 100.0)
            if total_required > 0
            else 0.0
        )

        # Find missing prerequisites
        missing_prereqs = self._find_missing_prerequisites(
            missing, student_skills
        )

        # Rank improvement areas
        improvement_areas = self._rank_improvement_areas(
            missing, missing_prereqs
        )

        # Determine learning order
        learning_order = self._determine_learning_order(
            missing, missing_prereqs, career_pathway
        )

        # Build priority skills list (prerequisites first, then remaining)
        priority_skills = list(missing_prereqs)
        for skill in missing:
            if skill not in priority_skills:
                priority_skills.append(skill)

        # Categorise all skills
        all_skills = list(set(matched + missing))
        categorized = self._categorize_skills(all_skills)

        result = SkillAnalysisResult(
            missing_skills=missing,
            mastered_skills=list(set(student_skills)),
            matched_skills=matched,
            priority_skills=priority_skills,
            coverage_percentage=round(coverage, 1),
            improvement_areas=improvement_areas,
            recommended_learning_order=learning_order,
            career_path=career_pathway,
            prerequisites=missing_prereqs,
            categorized_skills=categorized,
            total_required_skills=total_required,
        )

        logger.info(
            "Skill analysis complete for '%s': %.1f%% coverage, "
            "%d/%d skills matched, %d missing, %d prerequisites",
            profile.name,
            coverage,
            len(matched),
            total_required,
            len(missing),
            len(missing_prereqs),
        )

        return result


# ---------------------------------------------------------------------------
# Module-level singleton and convenience function
# ---------------------------------------------------------------------------

_analyzer = SkillGapAnalyzer()


def analyze_skill_gap(profile: StudentProfile) -> SkillAnalysisResult:
    """Analyze the skill gap for a student profile.

    Convenience wrapper around the module-level
    :class:`SkillGapAnalyzer` instance.

    Args:
        profile: The student's profile.

    Returns:
        A :class:`SkillAnalysisResult` with the full analysis.
    """
    return _analyzer.analyze_skill_gap(profile)
