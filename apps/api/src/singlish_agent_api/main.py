from contextlib import asynccontextmanager

from fastapi import FastAPI

from singlish_agent_api.api.routes.health import router as health_router
from singlish_agent_api.infrastructure.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Singlish Agent API", lifespan=lifespan)
    app.include_router(health_router)
    return app


app = create_app()
