from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from app.context import get_ctx
from app.routers import hello_routers
from app.routers import user_routers
from app.config import get_cfg
from app.logger import get_log
from uuid import uuid4
import os
import time
from app.session import Base, async_engine
from app.errors import E
from fastapi.staticfiles import StaticFiles


cfg = get_cfg()
log = get_log()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create SQLAlchemy tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, summary=cfg.APP_SUMMARY, version=cfg.APP_VERSION)
app.mount(cfg.MFA_PREFIX, StaticFiles(directory=cfg.MFA_PATH, html=False), name=cfg.MFA_PATH)
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


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, e: Exception):
    """Process validation error."""
    log.error('Internal server error, exception=%s.' % str(e))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"detail": E.INTERNAL_SERVER_ERROR}),
    )
