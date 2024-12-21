from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import time
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings, api_settings
from app.core.dependencies import log_request
from app.core.utils import setup_logger, AppError
from app.db.database import init_db, close_db
from app.api import auth, chat

# Configurar logger
setup_logger(
    log_file=settings.LOG_FILE,
    level=settings.LOG_LEVEL
)

# Crear aplicación FastAPI
app = FastAPI(
    title=api_settings.title,
    version=api_settings.version,
    description=api_settings.description,
    openapi_url=api_settings.openapi_url,
    docs_url=api_settings.docs_url,
    redoc_url=api_settings.redoc_url
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_settings.allow_origins,
    allow_credentials=api_settings.allow_credentials,
    allow_methods=api_settings.allow_methods,
    allow_headers=api_settings.allow_headers,
)

# Middleware para logging
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    return await log_request(request, call_next)

# Middleware para métricas de rendimiento
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log de rendimiento si el tiempo excede el umbral
    if process_time > 1.0:  # 1 segundo
        logger.warning(
            f"Solicitud lenta",
            path=request.url.path,
            method=request.method,
            duration=process_time
        )
    
    return response

# Manejo de errores
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de datos."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Error de validación",
            "details": exc.errors()
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Maneja errores de base de datos."""
    logger.error(f"Error de base de datos: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error de base de datos",
            "details": str(exc)
        }
    )

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Maneja errores personalizados de la aplicación."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Maneja errores no controlados."""
    logger.error(f"Error no controlado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "details": str(exc) if settings.DEBUG else None
        }
    )

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    """Inicialización de la aplicación."""
    try:
        # Inicializar base de datos
        await init_db()
        logger.info("Base de datos inicializada")
        
        # Configurar métricas si están habilitadas
        if settings.ENABLE_METRICS:
            Instrumentator().instrument(app).expose(
                app,
                endpoint=settings.METRICS_PATH,
                tags=["monitoring"]
            )
            logger.info("Métricas habilitadas")
            
    except Exception as e:
        logger.error(f"Error en inicialización: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la aplicación."""
    try:
        # Cerrar conexiones de base de datos
        await close_db()
        logger.info("Conexiones de base de datos cerradas")
        
    except Exception as e:
        logger.error(f"Error en cierre: {e}")

# Rutas base
@app.get(
    "/",
    tags=["estado"]
)
async def root():
    """Endpoint raíz para verificar el estado del servidor."""
    return {
        "name": settings.APP_NAME,
        "version": api_settings.version,
        "status": "running"
    }

@app.get(
    settings.HEALTH_CHECK_PATH,
    tags=["estado"]
)
async def health_check():
    """Endpoint para verificación de salud."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

# Incluir routers
app.include_router(
    auth.router,
    prefix=f"/api/{settings.API_VERSION}"
)

app.include_router(
    chat.router,
    prefix=f"/api/{settings.API_VERSION}"
)

# Exportar aplicación
api = app
