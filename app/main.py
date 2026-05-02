from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import init_db
from app.api.routes import routes


logger = get_logger("main")
settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Buyer-driven agentic negotiation platform",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routes.router, prefix="/api/v1", tags=["negotiation"])

    @app.on_event("startup")
    def on_startup() -> None:
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        init_db()
        logger.info("Database initialized")

    @app.get("/health")
    def health_check() -> dict:
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
