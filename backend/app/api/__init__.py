from app.api.health_routes import router as health_router
from app.api.auth_routes import router as auth_router
from app.api.student_routes import router as student_router
from app.api.roadmap_routes import router as roadmap_router
from app.api.mentor_routes import router as mentor_router
from app.api.search_routes import router as search_router
from app.api.rag_routes import router as rag_router
from app.api.resource_routes import router as resource_router
from app.api.project_routes import router as project_router
from app.api.study_planner_routes import router as study_planner_router
from app.api.career_test_routes import router as career_test_router

ALL_ROUTERS = [
    auth_router,
    health_router,
    student_router,
    roadmap_router,
    mentor_router,
    search_router,
    rag_router,
    resource_router,
    project_router,
    study_planner_router,
    career_test_router,
]

__all__ = ["ALL_ROUTERS"]
