"""AI Roadmap Generator for LearnMate AI.

Orchestrates the Skill Gap Analyzer, RAG Service, and Granite Service
into a single personalised learning pipeline. Produces structured
10-week roadmaps with courses, projects, certifications, assessments,
and weekly learning outcomes.

Falls back to deterministic generation when Granite is unavailable.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.models.student import StudentProfile
from app.services.skill_analyzer import (
    SkillAnalysisResult,
    analyze_skill_gap,
)
from app.services.rag_service import rag_service, RAG_AVAILABLE
from app.services import granite_service
from app.services.prompt_templates import (
    build_roadmap_prompt,
    serialize_courses_for_prompt,
    serialize_projects_for_prompt,
    serialize_certifications_for_prompt,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Roadmap Generator
# ---------------------------------------------------------------------------


class RoadmapGenerator:
    """Orchestrates personalised roadmap generation.

    Combines skill gap analysis, RAG-based resource retrieval, and
    Granite AI generation into a single pipeline that produces a
    structured 10-week learning roadmap.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate_roadmap(
        self, profile: StudentProfile
    ) -> Dict[str, Any]:
        """Generate a complete personalised learning roadmap.

        Workflow:

        1. Analyse skill gaps via :class:`SkillGapAnalyzer`.
        2. Retrieve relevant learning resources via RAG.
        3. Build a Granite prompt from profile + analysis + resources.
        4. Generate the AI roadmap via Granite (or deterministic fallback).
        5. Parse the raw output into a structured roadmap dict.

        Args:
            profile: The student's profile with skills, interests,
                     career goal, and proficiency level.

        Returns:
            A structured roadmap dictionary containing weeks,
            certifications, final project, progress, and recommendations.
        """
        logger.info(
            "Generating roadmap for '%s' -> '%s'",
            profile.name,
            profile.career_goal,
        )

        # Step 1: Analyse skill gap
        skill_analysis = analyze_skill_gap(profile)

        # Step 2: Retrieve learning resources via RAG
        resources = await self._retrieve_resources(profile, skill_analysis)

        # Step 3 & 4: Generate roadmap via Granite (with fallback)
        raw_roadmap = await self._generate_with_granite(
            profile, skill_analysis, resources
        )

        # Step 5: Parse into structured roadmap
        roadmap = self._parse_roadmap(
            profile, skill_analysis, raw_roadmap, resources
        )

        logger.info(
            "Roadmap generated: %s (%d weeks, %.1f%% readiness)",
            roadmap["roadmap_id"],
            len(roadmap.get("weeks", [])),
            skill_analysis.coverage_percentage,
        )

        return roadmap

    async def update_roadmap(
        self,
        roadmap: Dict[str, Any],
        completed_topics: List[str],
    ) -> Dict[str, Any]:
        """Update a roadmap based on completed topics.

        Marks completed topics and weeks, recalculates progress,
        removes completed recommendations, and generates new ones
        based on remaining learning needs.

        Args:
            roadmap: The current roadmap dictionary.
            completed_topics: List of newly completed topic names.

        Returns:
            Updated roadmap dictionary with recalculated progress
            and recommendations.
        """
        logger.info(
            "Updating roadmap '%s' with %d completed topics",
            roadmap.get("roadmap_id", "unknown"),
            len(completed_topics),
        )

        completed_lower = {t.lower().strip() for t in completed_topics}

        # Mark completed weeks and calculate progress
        completed_weeks = self._mark_completed_weeks(
            roadmap, completed_lower
        )

        # Calculate new progress
        total_weeks = max(len(roadmap.get("weeks", [])), 1)
        percentage = (
            (completed_weeks / total_weeks * 100.0)
            if total_weeks > 0
            else 0.0
        )

        roadmap["progress"] = {
            "completed_weeks": completed_weeks,
            "total_weeks": total_weeks,
            "percentage": round(percentage, 1),
            "current_week": min(completed_weeks + 1, total_weeks),
        }

        # Refresh recommendations
        roadmap["recommendations"] = self._generate_recommendations(
            roadmap, completed_lower, percentage
        )

        # Calculate remaining study hours
        roadmap["estimated_remaining_hours"] = sum(
            w.get("estimated_hours", 10.0)
            for w in roadmap.get("weeks", [])
            if w.get("completion_status", "pending") != "completed"
        )

        logger.info(
            "Roadmap updated: %d/%d weeks completed (%.1f%%)",
            completed_weeks,
            total_weeks,
            percentage,
        )

        return roadmap

    # ------------------------------------------------------------------
    # RAG resource retrieval
    # ------------------------------------------------------------------

    async def _retrieve_resources(
        self,
        profile: StudentProfile,
        skill_analysis: SkillAnalysisResult,
    ) -> Dict[str, Any]:
        """Retrieve relevant courses, projects, and certifications via RAG.

        Uses the missing skills and career goal to search for the most
        relevant learning resources from the vector database.

        Args:
            profile: The student's profile.
            skill_analysis: Result of the skill gap analysis.

        Returns:
            Dict with ``courses``, ``projects``, and ``certifications``
            lists from RAG search results.
        """
        resources: Dict[str, Any] = {
            "courses": [],
            "projects": [],
            "certifications": [],
        }

        if not RAG_AVAILABLE or rag_service is None:
            logger.info("RAG unavailable – skipping resource retrieval")
            return resources

        try:
            # Search for courses matching missing skills
            if skill_analysis.missing_skills:
                course_results = await rag_service.search_by_skills(
                    skill_analysis.missing_skills, n=10
                )
                resources["courses"] = [
                    r for r in course_results
                    if r.get("metadata", {}).get("resource_type") == "course"
                ]

            # Search for projects matching career goal
            project_skills = skill_analysis.missing_skills[:3]
            project_query = (
                f"Projects for {profile.career_goal} using "
                f"{', '.join(project_skills)}"
                if project_skills
                else f"Projects for {profile.career_goal}"
            )
            project_results = await rag_service.search_courses(
                project_query, n=8
            )
            resources["projects"] = [
                r for r in project_results
                if r.get("metadata", {}).get("resource_type") == "project"
            ]

            # Search for certifications
            cert_query = f"Certifications for {profile.career_goal}"
            cert_results = await rag_service.search_courses(cert_query, n=5)
            resources["certifications"] = [
                r for r in cert_results
                if r.get("metadata", {}).get("resource_type")
                == "certification"
            ]

            # Fallback: use career pathway recommended resources if RAG
            # returned nothing
            if not resources["courses"] and skill_analysis.career_path:
                logger.info(
                    "RAG returned no courses - career pathway data available "
                    "as fallback"
                )

            logger.info(
                "Retrieved %d courses, %d projects, %d certifications",
                len(resources["courses"]),
                len(resources["projects"]),
                len(resources["certifications"]),
            )

        except Exception as exc:
            logger.error("Resource retrieval failed: %s", exc)

        return resources

    # ------------------------------------------------------------------
    # Granite generation with fallback
    # ------------------------------------------------------------------

    async def _generate_with_granite(
        self,
        profile: StudentProfile,
        skill_analysis: SkillAnalysisResult,
        resources: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate roadmap via Granite, falling back to deterministic.

        Builds a prompt from the student profile, skill analysis, and
        retrieved resources, then calls Granite. If the API is
        unavailable or returns malformed output, falls back to a
        deterministic roadmap generator.

        Args:
            profile: The student's profile.
            skill_analysis: Result of the skill gap analysis.
            resources: RAG-retrieved learning resources.

        Returns:
            A dict with a ``"weeks"`` key containing the weekly plan.
        """
        # Serialise resources for Granite context
        courses_str = serialize_courses_for_prompt(
            [self._extract_resource_fields(r) for r in resources.get("courses", [])]
        )
        projects_str = serialize_projects_for_prompt(
            [self._extract_resource_fields(r) for r in resources.get("projects", [])]
        )
        certs_str = serialize_certifications_for_prompt(
            [self._extract_resource_fields(r) for r in resources.get("certifications", [])]
        )

        try:
            raw = await granite_service.generate_roadmap(
                student_name=profile.name,
                career_goal=profile.career_goal,
                current_skills=profile.current_skills,
                interests=profile.interests,
                skill_level=profile.skill_level.value,
                available_courses=courses_str,
                available_projects=projects_str,
                available_certs=certs_str,
            )

            if raw and isinstance(raw, dict) and "weeks" in raw:
                logger.info("Granite roadmap generated successfully")
                return raw

            logger.warning("Granite returned invalid roadmap - using fallback")

        except Exception as exc:
            logger.error("Granite roadmap generation failed: %s", exc)

        # Deterministic fallback
        return self._deterministic_roadmap(profile, skill_analysis, resources)

    @staticmethod
    def _extract_resource_fields(
        rag_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract structured fields from a RAG search result.

        Parses the document string to extract key-value pairs like
        Title, Domain, Level, and Skills.

        Args:
            rag_result: A RAG search result dict with a ``document`` key.

        Returns:
            A dict with extracted fields suitable for serialisation.
        """
        doc = rag_result.get("document", "")
        fields: Dict[str, Any] = {}

        for key in ("Title", "Name"):
            if f"{key}:" in doc:
                start = doc.index(f"{key}:") + len(f"{key}:")
                end = doc.find("|", start)
                if end == -1:
                    end = len(doc)
                fields[key.lower()] = doc[start:end].strip()

        for key in ("Domain", "Level", "Description"):
            if f"{key}:" in doc:
                start = doc.index(f"{key}:") + len(f"{key}:")
                end = doc.find("|", start)
                if end == -1:
                    end = len(doc)
                fields[key.lower()] = doc[start:end].strip()

        for key in ("Skills gained", "Skills covered", "Technologies"):
            if f"{key}:" in doc:
                start = doc.index(f"{key}:") + len(f"{key}:")
                end = doc.find("|", start)
                if end == -1:
                    end = len(doc)
                skills_str = doc[start:end].strip()
                fields[key.lower().replace(" ", "_")] = [
                    s.strip() for s in skills_str.split(",") if s.strip()
                ]

        if not fields.get("title") and not fields.get("name"):
            # Use first 100 chars as title fallback
            fields["title"] = doc[:100].strip() if doc else "Resource"

        return fields

    # ------------------------------------------------------------------
    # Deterministic fallback roadmap
    # ------------------------------------------------------------------

    def _deterministic_roadmap(
        self,
        profile: StudentProfile,
        skill_analysis: SkillAnalysisResult,
        resources: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a deterministic fallback roadmap without Granite.

        Distributes missing skills across 10 weeks following the
        curriculum design rules: prerequisites first, beginner before
        intermediate, intermediate before advanced, certification prep
        near the end, capstone in the last week.

        Args:
            profile: The student's profile.
            skill_analysis: Result of the skill gap analysis.
            resources: RAG-retrieved learning resources.

        Returns:
            A dict with a ``"weeks"`` key containing 10 weekly plans.
        """
        learning_order = skill_analysis.recommended_learning_order
        course_results = resources.get("courses", [])
        project_results = resources.get("projects", [])

        # Week templates with curriculum design rationale
        week_templates: List[Dict[str, Any]] = [
            {
                "goal": "Foundation & Environment Setup",
                "base_topics": [
                    "Development environment configuration",
                    "Review of fundamentals",
                    "Learning roadmap overview",
                ],
                "hours": 10.0,
                "include_project": False,
            },
            {
                "goal": "Prerequisites & Core Concepts",
                "base_topics": [
                    "Prerequisite skill development",
                    "Core concept introduction",
                    "Hands-on exercises",
                ],
                "hours": 12.0,
                "include_project": False,
            },
            {
                "goal": "Building Core Skills",
                "base_topics": [
                    "Key technology deep-dive",
                    "Practical coding exercises",
                    "Concept reinforcement",
                ],
                "hours": 12.0,
                "include_project": False,
            },
            {
                "goal": "Intermediate Concepts",
                "base_topics": [
                    "Intermediate-level topics",
                    "Tooling and workflow optimisation",
                    "Code quality practices",
                ],
                "hours": 13.0,
                "include_project": False,
            },
            {
                "goal": "Applied Learning & Mini-Project",
                "base_topics": [
                    "Real-world application",
                    "Mini-project development",
                    "Code review and feedback",
                ],
                "hours": 14.0,
                "include_project": True,
            },
            {
                "goal": "Advanced Topics",
                "base_topics": [
                    "Advanced concepts and patterns",
                    "Best practices and design patterns",
                    "Performance considerations",
                ],
                "hours": 14.0,
                "include_project": False,
            },
            {
                "goal": "Project-Based Learning",
                "base_topics": [
                    "Hands-on project implementation",
                    "Integration and testing",
                    "Documentation",
                ],
                "hours": 15.0,
                "include_project": True,
            },
            {
                "goal": "Integration & Industry Practices",
                "base_topics": [
                    "Integration patterns",
                    "Testing strategies",
                    "Industry best practices",
                ],
                "hours": 13.0,
                "include_project": False,
            },
            {
                "goal": "Certification Preparation",
                "base_topics": [
                    "Certification topic review",
                    "Practice exams and mock tests",
                    "Weak area reinforcement",
                ],
                "hours": 12.0,
                "include_project": False,
            },
            {
                "goal": "Capstone Project & Final Review",
                "base_topics": [
                    "Capstone project completion",
                    "Portfolio development",
                    "Final review and next steps",
                ],
                "hours": 15.0,
                "include_project": True,
            },
        ]

        # Distribute skills across weeks
        skill_idx = 0
        skills_per_week = (
            max(1, len(learning_order) // 8) if learning_order else 1
        )

        weeks: List[Dict[str, Any]] = []
        for i, template in enumerate(week_templates):
            week_num = i + 1

            # Assign skills to this week
            week_skills: List[str] = []
            for _ in range(skills_per_week):
                if skill_idx < len(learning_order):
                    week_skills.append(learning_order[skill_idx])
                    skill_idx += 1

            # Flush remaining skills into weeks 7-8
            if i in (7, 8) and skill_idx < len(learning_order):
                remaining = learning_order[skill_idx:]
                week_skills.extend(remaining[:3])
                skill_idx += min(3, len(remaining))

            topics = template["base_topics"] + week_skills

            # Assign courses from RAG results
            week_courses: List[str] = []
            if i < len(course_results):
                title = self._extract_title_from_doc(
                    course_results[i].get("document", "")
                )
                if title:
                    week_courses.append(title)

            # Assign projects (weeks 5, 7, 10)
            week_projects: List[str] = []
            if template["include_project"]:
                if i < len(project_results):
                    title = self._extract_title_from_doc(
                        project_results[i].get("document", "")
                    )
                    if title:
                        week_projects.append(title)
                if not week_projects and week_skills:
                    week_projects.append(
                        f"Practice project: {week_skills[0]}"
                    )

            # Assessments
            assessment = (
                f"Quiz on {week_skills[0]}; "
                f"Reflection on {template['goal']}"
                if week_skills
                else f"Week {week_num} self-assessment"
            )

            # Learning outcomes
            learning_outcomes = [
                f"Understand and apply {s}" for s in week_skills[:3]
            ]
            if not learning_outcomes:
                learning_outcomes = [f"Complete {template['goal'].lower()}"]

            weeks.append({
                "week_number": week_num,
                "goal": template["goal"],
                "topics": topics,
                "courses": week_courses,
                "projects": week_projects,
                "hours": template["hours"],
                "assessment": assessment,
                "learning_outcomes": learning_outcomes,
            })

        return {"weeks": weeks}

    @staticmethod
    def _extract_title_from_doc(document: str) -> str:
        """Extract a title from a RAG document string.

        Args:
            document: The raw document string from RAG search.

        Returns:
            The extracted title, or empty string if not found.
        """
        for key in ("Title:", "Name:"):
            if key in document:
                start = document.index(key) + len(key)
                end = document.find("|", start)
                if end == -1:
                    end = len(document)
                return document[start:end].strip()
        return ""

    # ------------------------------------------------------------------
    # Roadmap parsing
    # ------------------------------------------------------------------

    def _parse_roadmap(
        self,
        profile: StudentProfile,
        skill_analysis: SkillAnalysisResult,
        raw_roadmap: Dict[str, Any],
        resources: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Parse raw roadmap data into a structured roadmap dict.

        Normalises the Granite (or fallback) output into a consistent
        structure with all required fields including weeks,
        certifications, final project, progress, and recommendations.

        Args:
            profile: The student's profile.
            skill_analysis: Result of the skill gap analysis.
            raw_roadmap: Raw roadmap dict from Granite or fallback.
            resources: RAG-retrieved learning resources.

        Returns:
            A fully structured roadmap dictionary.
        """
        roadmap_id = f"roadmap-{uuid.uuid4().hex[:12]}"

        # Parse weeks
        weeks = self._parse_weeks(raw_roadmap.get("weeks", []))

        # Pad to exactly 10 weeks if needed
        while len(weeks) < 10:
            next_week_num = len(weeks) + 1
            weeks.append(self._build_empty_week(
                next_week_num, skill_analysis
            ))

        # Parse certifications
        certifications = self._parse_certifications(
            resources, skill_analysis, profile
        )

        # Build final project (capstone)
        final_project = self._build_final_project(
            resources, skill_analysis, profile
        )

        # Build initial recommendations
        recommendations = self._build_initial_recommendations(skill_analysis)

        return {
            "roadmap_id": roadmap_id,
            "student_name": profile.name,
            "career_goal": profile.career_goal,
            "total_duration": "10 weeks",
            "weeks": weeks,
            "certifications": certifications,
            "final_project": final_project,
            "progress": {
                "completed_weeks": 0,
                "total_weeks": 10,
                "percentage": 0.0,
                "current_week": 1,
            },
            "skill_analysis": {
                "coverage_percentage": skill_analysis.coverage_percentage,
                "missing_skills": skill_analysis.missing_skills,
                "matched_skills": skill_analysis.matched_skills,
                "categorized_skills": skill_analysis.categorized_skills,
                "prerequisites": skill_analysis.prerequisites,
            },
            "recommendations": recommendations,
        }

    def _parse_weeks(
        self, raw_weeks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse raw week data into normalised week dicts.

        Handles variations in field names from Granite output
        (e.g. ``goal`` vs ``title``, ``hours`` vs ``estimated_hours``,
        ``assessment`` as string vs list).

        Args:
            raw_weeks: List of raw week dicts from Granite or fallback.

        Returns:
            List of normalised week dicts (max 10).
        """
        weeks: List[Dict[str, Any]] = []

        for week_data in raw_weeks[:10]:
            week_num = week_data.get("week_number", len(weeks) + 1)

            # Normalise assessment field
            assessment_raw = week_data.get(
                "assessment", week_data.get("assessments", [])
            )
            if isinstance(assessment_raw, str):
                assessments = [a.strip() for a in assessment_raw.split(";") if a.strip()]
            elif isinstance(assessment_raw, list):
                assessments = assessment_raw
            else:
                assessments = [f"Week {week_num} self-assessment"]

            # Normalise hours
            hours = week_data.get(
                "hours", week_data.get("estimated_hours", 10.0)
            )
            try:
                hours = float(hours)
            except (TypeError, ValueError):
                hours = 10.0

            week = {
                "week_number": week_num,
                "title": week_data.get(
                    "goal", week_data.get("title", f"Week {week_num}")
                ),
                "topics": week_data.get("topics", []),
                "courses": week_data.get("courses", []),
                "projects": week_data.get("projects", []),
                "assessments": assessments,
                "estimated_hours": hours,
                "learning_outcomes": week_data.get("learning_outcomes", []),
                "completion_status": "pending",
            }
            weeks.append(week)

        return weeks

    @staticmethod
    def _build_empty_week(
        week_num: int, skill_analysis: SkillAnalysisResult
    ) -> Dict[str, Any]:
        """Build a placeholder week dict for padding.

        Args:
            week_num: The week number (1-indexed).
            skill_analysis: The skill analysis for topic assignment.

        Returns:
            A week dict with placeholder content.
        """
        # Assign remaining skills from the analysis
        remaining = skill_analysis.missing_skills[:2] if skill_analysis.missing_skills else []

        return {
            "week_number": week_num,
            "title": f"Week {week_num}: Continued Learning",
            "topics": remaining or ["Review and practice"],
            "courses": [],
            "projects": [],
            "assessments": [f"Week {week_num} self-assessment"],
            "estimated_hours": 10.0,
            "learning_outcomes": [
                f"Practice {s}" for s in remaining[:2]
            ] or [f"Complete week {week_num} activities"],
            "completion_status": "pending",
        }

    def _parse_certifications(
        self,
        resources: Dict[str, Any],
        skill_analysis: SkillAnalysisResult,
        profile: StudentProfile,
    ) -> List[Dict[str, Any]]:
        """Parse certification data from RAG results or career pathway.

        Args:
            resources: RAG-retrieved learning resources.
            skill_analysis: The skill analysis result.
            profile: The student's profile.

        Returns:
            List of certification dicts.
        """
        certifications: List[Dict[str, Any]] = []

        # Try RAG results first
        cert_results = resources.get("certifications", [])
        for cert_data in cert_results[:3]:
            doc = cert_data.get("document", "")
            name = self._extract_title_from_doc(doc) or "Industry Certification"
            certifications.append({
                "id": cert_data.get("id", f"cert-auto-{len(certifications)}"),
                "name": name,
                "provider": "Industry",
                "level": profile.skill_level.value,
                "description": doc[:200] if doc else "",
                "prerequisites": [],
                "exam_link": "",
                "skills_covered": skill_analysis.missing_skills[:5],
            })

        # Fallback to career pathway certifications
        if not certifications and skill_analysis.career_path:
            for cert_id in skill_analysis.career_path.get(
                "certifications", []
            )[:2]:
                certifications.append({
                    "id": cert_id,
                    "name": f"Certification: {profile.career_goal}",
                    "provider": "Industry",
                    "level": profile.skill_level.value,
                    "description": (
                        f"Industry-recognised certification for "
                        f"{profile.career_goal}"
                    ),
                    "prerequisites": [],
                    "exam_link": "",
                    "skills_covered": skill_analysis.missing_skills[:5],
                })

        return certifications

    def _build_final_project(
        self,
        resources: Dict[str, Any],
        skill_analysis: SkillAnalysisResult,
        profile: StudentProfile,
    ) -> Dict[str, Any]:
        """Build the capstone project dict.

        Uses the last RAG project result if available, otherwise
        generates a generic capstone based on the career goal.

        Args:
            resources: RAG-retrieved learning resources.
            skill_analysis: The skill analysis result.
            profile: The student's profile.

        Returns:
            A project dict for the capstone.
        """
        proj_results = resources.get("projects", [])

        if proj_results:
            last_proj = proj_results[-1]
            doc = last_proj.get("document", "")
            title = (
                self._extract_title_from_doc(doc)
                or f"Capstone: {profile.career_goal}"
            )
            return {
                "id": last_proj.get("id", "project-capstone"),
                "title": title,
                "description": (
                    doc[:300] if doc
                    else f"Capstone project demonstrating {profile.career_goal} skills"
                ),
                "domain": profile.career_goal,
                "difficulty": profile.skill_level.value,
                "estimated_time": "2 weeks",
                "required_skills": skill_analysis.missing_skills[:5],
                "learning_outcomes": [
                    f"Apply {s} skills in a real-world project"
                    for s in skill_analysis.missing_skills[:3]
                ],
                "technologies": [],
            }

        return {
            "id": "project-capstone",
            "title": f"Capstone Project: {profile.career_goal}",
            "description": (
                f"Comprehensive project demonstrating mastery of "
                f"{profile.career_goal} skills acquired throughout "
                f"the 10-week programme."
            ),
            "domain": profile.career_goal,
            "difficulty": profile.skill_level.value,
            "estimated_time": "2 weeks",
            "required_skills": skill_analysis.missing_skills[:5],
            "learning_outcomes": [
                "Integrate all learned skills into a cohesive project",
                "Build a portfolio-ready demonstration",
                "Present and document the solution professionally",
            ],
            "technologies": [],
        }

    @staticmethod
    def _build_initial_recommendations(
        skill_analysis: SkillAnalysisResult,
    ) -> List[str]:
        """Build initial learning recommendations.

        Args:
            skill_analysis: The skill analysis result.

        Returns:
            List of recommendation strings.
        """
        recommendations: List[str] = []

        if skill_analysis.prerequisites:
            recommendations.append(
                f"Priority: Learn prerequisite skills first - "
                f"{', '.join(skill_analysis.prerequisites[:3])}"
            )

        if skill_analysis.coverage_percentage < 30:
            recommendations.append(
                "Focus on foundational concepts before advancing to "
                "complex topics"
            )
        elif skill_analysis.coverage_percentage < 60:
            recommendations.append(
                "Good foundation - balance skill gaps with hands-on projects"
            )
        elif skill_analysis.coverage_percentage < 80:
            recommendations.append(
                "Strong base - focus on advanced topics and specialisation"
            )
        else:
            recommendations.append(
                "Near career-ready - concentrate on certification and "
                "portfolio projects"
            )

        if skill_analysis.missing_skills:
            recommendations.append(
                f"Key skills to develop: "
                f"{', '.join(skill_analysis.missing_skills[:5])}"
            )

        return recommendations

    # ------------------------------------------------------------------
    # Week completion marking
    # ------------------------------------------------------------------

    def _mark_completed_weeks(
        self,
        roadmap: Dict[str, Any],
        completed_lower: set[str],
    ) -> int:
        """Mark completed weeks based on finished topics.

        A week is marked as completed when all its topics and projects
        appear in the completed set. Weeks with partial completion are
        marked as in_progress.

        Args:
            roadmap: The roadmap dict to update.
            completed_lower: Set of normalised completed topic names.

        Returns:
            Number of fully completed weeks.
        """
        completed_weeks = 0

        for week in roadmap.get("weeks", []):
            week_items = set()
            for t in week.get("topics", []):
                week_items.add(t.lower().strip())
            for p in week.get("projects", []):
                week_items.add(p.lower().strip())

            # Remove empty strings
            week_items.discard("")

            if not week_items:
                # No items to check - mark as completed if week number
                # is within the completed range
                continue

            overlap = week_items & completed_lower

            if week_items and week_items <= completed_lower:
                week["completion_status"] = "completed"
                completed_weeks += 1
            elif overlap:
                week["completion_status"] = "in_progress"
            else:
                week["completion_status"] = "pending"

        return completed_weeks

    # ------------------------------------------------------------------
    # Dynamic recommendation generation
    # ------------------------------------------------------------------

    def _generate_recommendations(
        self,
        roadmap: Dict[str, Any],
        completed_lower: set[str],
        percentage: float,
    ) -> List[str]:
        """Generate updated recommendations based on current progress.

        Removes completed recommendations and adds new ones based on
        remaining skills and current progress level.

        Args:
            roadmap: The current roadmap dict.
            completed_lower: Set of normalised completed topic names.
            percentage: Current completion percentage.

        Returns:
            Updated list of recommendation strings.
        """
        # Filter out completed recommendations
        existing_recs = roadmap.get("recommendations", [])
        updated_recs: List[str] = []
        for rec in existing_recs:
            is_completed = any(
                ct in rec.lower() for ct in completed_lower
            )
            if not is_completed:
                updated_recs.append(rec)

        # Determine remaining skills
        skill_info = roadmap.get("skill_analysis", {})
        remaining_skills = [
            s for s in skill_info.get("missing_skills", [])
            if not any(
                _skill_name_matches(s, ct) for ct in completed_lower
            )
        ]

        # Add progress-based recommendations
        if remaining_skills:
            updated_recs.append(
                f"Next focus areas: {', '.join(remaining_skills[:3])}"
            )

        if percentage >= 90:
            updated_recs.append(
                "Almost complete! Focus on the capstone project and "
                "certification exam"
            )
        elif percentage >= 70:
            updated_recs.append(
                "Great progress! Start working on portfolio projects "
                "to showcase your skills"
            )
        elif percentage >= 50:
            updated_recs.append(
                "Halfway there! Increase project complexity and "
                "explore advanced topics"
            )
        elif percentage >= 25:
            updated_recs.append(
                "Building momentum - maintain consistent study hours "
                "and practice daily"
            )
        elif percentage > 0:
            updated_recs.append(
                "Good start! Focus on completing foundational topics "
                "before moving forward"
            )

        return updated_recs


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------


async def generate_roadmap(profile: StudentProfile) -> Dict[str, Any]:
    """Generate a personalised roadmap for a student.

    Convenience wrapper that creates a :class:`RoadmapGenerator`
    instance and calls :meth:`generate_roadmap`.

    Args:
        profile: The student's profile.

    Returns:
        A structured roadmap dictionary.
    """
    generator = RoadmapGenerator()
    return await generator.generate_roadmap(profile)


async def update_roadmap(
    roadmap: Dict[str, Any],
    completed_topics: List[str],
) -> Dict[str, Any]:
    """Update a roadmap with completed topics.

    Convenience wrapper that creates a :class:`RoadmapGenerator`
    instance and calls :meth:`update_roadmap`.

    Args:
        roadmap: The current roadmap dictionary.
        completed_topics: List of newly completed topic names.

    Returns:
        Updated roadmap dictionary.
    """
    generator = RoadmapGenerator()
    return await generator.update_roadmap(roadmap, completed_topics)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _skill_name_matches(skill: str, text: str) -> bool:
    """Check if a skill name appears in a text string.

    Args:
        skill: The skill name to match.
        text: The text to search within.

    Returns:
        ``True`` if the skill is found in the text.
    """
    s = skill.lower().strip()
    t = text.lower().strip()
    return s in t or t in s
