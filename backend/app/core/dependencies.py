from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db.database import get_db
from app.services.auth_service import auth_service
from app.models.models import User
from app.core.config import settings

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{settings.API_VERSION}/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependencia para obtener el usuario actual basado en el token JWT.
    
    Args:
        token: Token JWT de acceso
        db: Sesión de base de datos
        
    Returns:
        User: Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    try:
        token_data = await auth_service.verify_token(token)
        
        result = await db.execute(
            User.__table__.select().where(
                User.id == token_data.user_id,
                User.is_active == True
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
            
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación"
        )

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependencia para obtener el usuario actual y verificar que esté activo.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        User: Usuario activo
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependencia para obtener el usuario actual y verificar que sea superusuario.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        User: Usuario superusuario
        
    Raises:
        HTTPException: Si el usuario no es superusuario
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes"
        )
    return current_user

# Rate limiting
from fastapi import Request
from collections import defaultdict
import time

class RateLimiter:
    """Implementación simple de rate limiting."""
    
    def __init__(
        self,
        requests: int = 100,
        window: int = 60
    ):
        self.requests = requests  # Número máximo de solicitudes
        self.window = window     # Ventana de tiempo en segundos
        self.clients = defaultdict(list)

    async def is_allowed(self, client_id: str) -> bool:
        """
        Verifica si un cliente puede realizar una solicitud.
        
        Args:
            client_id: Identificador del cliente
            
        Returns:
            bool: True si la solicitud está permitida
        """
        now = time.time()
        
        # Limpiar solicitudes antiguas
        self.clients[client_id] = [
            timestamp for timestamp in self.clients[client_id]
            if now - timestamp < self.window
        ]
        
        # Verificar límite
        if len(self.clients[client_id]) >= self.requests:
            return False
            
        # Registrar solicitud
        self.clients[client_id].append(now)
        return True

# Instancia global del rate limiter
rate_limiter = RateLimiter(
    requests=settings.RATE_LIMIT_REQUESTS,
    window=settings.RATE_LIMIT_PERIOD
)

async def check_rate_limit(request: Request):
    """
    Dependencia para verificar rate limiting.
    
    Args:
        request: Objeto Request de FastAPI
        
    Raises:
        HTTPException: Si se excede el límite de solicitudes
    """
    client_id = request.client.host
    
    if not await rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas solicitudes"
        )

# Utilidades para paginación
from app.schemas.schemas import PaginationParams

async def get_pagination(
    skip: int = 0,
    limit: int = 10
) -> PaginationParams:
    """
    Dependencia para obtener parámetros de paginación.
    
    Args:
        skip: Número de registros a saltar
        limit: Límite de registros a retornar
        
    Returns:
        PaginationParams: Parámetros de paginación validados
    """
    return PaginationParams(skip=skip, limit=limit)

# Utilidades para logging
from fastapi import Request, Response
import uuid

async def log_request(request: Request, response: Response):
    """
    Middleware para logging de solicitudes.
    
    Args:
        request: Objeto Request de FastAPI
        response: Objeto Response de FastAPI
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Agregar request_id a los headers
    response.headers["X-Request-ID"] = request_id
    
    # Log de inicio de solicitud
    logger.info(
        f"Request started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    # Procesar solicitud
    try:
        response = await response
        
        # Log de fin de solicitud
        logger.info(
            f"Request completed",
            request_id=request_id,
            status_code=response.status_code,
            duration=time.time() - start_time
        )
        
        return response
        
    except Exception as e:
        # Log de error
        logger.error(
            f"Request failed",
            request_id=request_id,
            error=str(e),
            duration=time.time() - start_time
        )
        raise

# Utilidades para websockets
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    """Gestor de conexiones WebSocket."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Conecta un nuevo cliente WebSocket."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Desconecta un cliente WebSocket."""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envía un mensaje a un cliente específico."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Envía un mensaje a todos los clientes conectados."""
        for connection in self.active_connections:
            await connection.send_text(message)

# Instancia global del gestor de conexiones
ws_manager = ConnectionManager()
