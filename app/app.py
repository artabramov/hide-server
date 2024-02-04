from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.context import get_ctx
from app.routers import hello_routers
from app.routers import user_routers
from app.config import get_cfg
from app.logger import log
from app.session import get_session
from uuid import uuid4
import os
import time
from app.session import Base, async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create SQLAlchemy tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


cfg = get_cfg()
app = FastAPI(lifespan=lifespan)
app.include_router(hello_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(user_routers.router, prefix=cfg.APP_PREFIX)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    ctx = get_ctx()
    ctx.request_start_time = time.time()
    ctx.trace_request_uuid = str(uuid4())
    ctx.pid = os.getpid()

    log.debug("Request received, method=%s, url=%s, headers=%s." % (
        request.method, str(request.url), str(request.headers)))

    response = await call_next(request)

    request_elapsed_time = time.time() - ctx.request_start_time
    log.debug("Response sent, request_elapsed_time=%s, status=%s, headers=%s." % (
        request_elapsed_time, response.status_code, str(response.headers.raw)))

    return response
