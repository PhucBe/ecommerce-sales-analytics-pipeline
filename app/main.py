from fastapi import FastAPI

from app.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
)


@app.get("/")
def root() -> dict:
    return {
        "message": "E-Commerce Sales Analytics API",
        "env": settings.APP_ENV,
    }


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "fastapi",
        "project": settings.PROJECT_NAME,
    }