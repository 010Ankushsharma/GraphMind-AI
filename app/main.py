"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.bootstrap import configure_logging, get_graph, get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging(get_settings())
    get_graph()
    yield


app = FastAPI(
    title="E-Commerce Knowledge Graph AI",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)
