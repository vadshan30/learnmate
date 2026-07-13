from app.api.health_routes import router as health_router
from app.api.student_routes import router as student_router
from app.api.roadmap_routes import router as roadmap_router
from app.api.chat_routes import router as chat_router
from app.api.search_routes import router as search_router

ALL_ROUTERS = [
    health_router,
    student_router,
    roadmap_router,
    chat_router,
    search_router,
]

__all__ = ["ALL_ROUTERS"]
