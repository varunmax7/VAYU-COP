import logging
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    aircraft,
    aircraft_types,
    airspace,
    auth,
    bases,
    cop,
    crew,
    fusion,
    kpis,
    missions,
    stores,
    threats,
    weather,
    ws,
)
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, request_id_ctx
from app.services.fusion.engine import fusion_engine
from app.services.ws_manager import start_broadcasters, stop_broadcasters

logger = logging.getLogger("vayu.main")

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger.info(f"starting {settings.app_name} v{settings.version} ({settings.environment})")
    await fusion_engine.start()
    start_broadcasters()
    yield
    await stop_broadcasters()
    await fusion_engine.stop()
    logger.info("shutting down")


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url="/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        req_id = request.headers.get("x-request-id", uuid.uuid4().hex[:12])
        token = request_id_ctx.set(req_id)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["x-request-id"] = req_id
        return response

    @app.get(f"{API_PREFIX}/health")
    async def health() -> dict:
        return {"status": "ok", "version": settings.version}

    for router in (
        auth.router,
        cop.router,
        kpis.router,
        bases.router,
        aircraft_types.router,
        aircraft.router,
        crew.router,
        stores.router,
        missions.router,
        airspace.router,
        threats.router,
        weather.router,
        fusion.router,
    ):
        app.include_router(router, prefix=API_PREFIX)

    app.include_router(ws.router)  # /ws — no /api/v1 prefix, per §12.2

    return app


app = create_app()
