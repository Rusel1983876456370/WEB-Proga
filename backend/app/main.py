"""Запуск: python -m uvicorn backend.app.main:app --reload (из корня проекта)."""
from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from .database import PROJECT_ROOT, engine
from .seed import init_db
from .routers import parts, categories

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    init_db(engine)
    yield

app = FastAPI(title="АвтоДеталь — REST API", version="3.0.0", description="Учебный каталог автозапчастей. ЛР3: FastAPI, SQLAlchemy, SQLite. Цены указаны в рублях; Decimal в ответах сериализуется строкой.", lifespan=lifespan, docs_url=None, redoc_url="/redoc")
origins = [value.strip() for value in os.getenv("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500").split(",") if value.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Content-Type"])
app.include_router(parts.router, prefix="/api")
app.include_router(categories.router, prefix="/api")

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    if any(error.get("type") == "json_invalid" for error in exc.errors()):
        return JSONResponse(status_code=400, content={"detail": "Тело запроса содержит некорректный JSON"})
    # Не сериализуем объект ValueError из ctx и не отражаем входные данные.
    errors = [{key: value for key, value in error.items() if key in {"type", "loc", "msg"}} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})

@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError):
    logger.error("Ошибка базы данных", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка базы данных"})

@app.exception_handler(Exception)
async def server_error(request: Request, exc: Exception):
    logger.error("Внутренняя ошибка сервера", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})

@app.get("/api/health", tags=["Сервис"], summary="Проверить доступность сервера и БД")
def health():
    from sqlalchemy import text
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}

app.mount("/swagger-assets", StaticFiles(directory=PROJECT_ROOT / "backend/static/swagger"), name="swagger-assets")

@app.get("/docs", include_in_schema=False)
def swagger_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="АвтоДеталь — Swagger UI", swagger_js_url="/swagger-assets/swagger-ui-bundle.js", swagger_css_url="/swagger-assets/swagger-ui.css", swagger_favicon_url="/assets/images/filter.svg", swagger_ui_parameters={"docExpansion": "list", "defaultModelsExpandDepth": -1, "persistAuthorization": False})

# API регистрируется раньше статики, чтобы /api/... не перехватывался frontend.
app.mount("/", StaticFiles(directory=PROJECT_ROOT / "frontend", html=True), name="frontend")
