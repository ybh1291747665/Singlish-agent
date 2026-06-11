from fastapi import FastAPI

from singlish_agent_api.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Singlish Agent API")
    app.include_router(health_router)
    return app


app = create_app()
