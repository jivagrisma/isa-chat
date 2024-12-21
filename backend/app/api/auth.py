from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from loguru import logger

from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    check_rate_limit
)
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    Token,
    UserCreate,
    User as UserSchema,
    SuccessResponse,
    ErrorResponse
)
from app.services.auth_service import auth_service
from app.core.utils import validate_email, validate_password

router = APIRouter(
    prefix="/auth",
    tags=["autenticación"],
    dependencies=[Depends(check_rate_limit)]
)

@router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra un nuevo usuario.
    
    Args:
        user_data: Datos del usuario
        request: Objeto Request
        db: Sesión de base de datos
    """
    try:
        # Validar email y contraseña
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
            
        if not validate_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña no cumple con los requisitos"
            )
            
        # Registrar usuario
        user = await auth_service.register_user(db, user_data)
        
        # Log de registro exitoso
        logger.info(
            f"Usuario registrado",
            email=user.email,
            ip=request.client.host
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar usuario"
        )

@router.post(
    "/login",
    response_model=Token,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia sesión y obtiene token JWT.
    
    Args:
        form_data: Datos del formulario
        request: Objeto Request
        db: Sesión de base de datos
    """
    try:
        # Autenticar usuario
        user = await auth_service.authenticate_user(
            db,
            form_data.username,  # El username puede ser email
            form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
            
        # Generar token
        token = auth_service.create_access_token(
            data={"sub": str(user.id)}
        )
        
        # Crear sesión
        await auth_service.create_user_session(
            db,
            user.id,
            token,
            request.client.host,
            request.headers.get("user-agent")
        )
        
        # Log de inicio de sesión exitoso
        logger.info(
            f"Inicio de sesión exitoso",
            user_id=user.id,
            ip=request.client.host
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": auth_service.oauth2_scheme.expires_in
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al iniciar sesión"
        )

@router.post(
    "/logout",
    response_model=SuccessResponse,
    responses={
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def logout(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Cierra la sesión actual.
    
    Args:
        request: Objeto Request
        current_user: Usuario actual
        db: Sesión de base de datos
    """
    try:
        # Obtener token del header
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        # Buscar y desactivar sesión
        result = await db.execute(
            """
            UPDATE user_sessions
            SET is_active = false
            WHERE user_id = :user_id AND session_token = :token
            """,
            {"user_id": current_user.id, "token": token}
        )
        await db.commit()
        
        # Log de cierre de sesión
        logger.info(
            f"Cierre de sesión",
            user_id=current_user.id,
            ip=request.client.host
        )
        
        return {
            "success": True,
            "message": "Sesión cerrada correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cerrar sesión"
        )

@router.get(
    "/me",
    response_model=UserSchema,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Obtiene información del usuario actual.
    
    Args:
        current_user: Usuario actual
    """
    return current_user

@router.post(
    "/refresh",
    response_model=Token,
    responses={
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def refresh_token(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Refresca el token JWT.
    
    Args:
        request: Objeto Request
        current_user: Usuario actual
        db: Sesión de base de datos
    """
    try:
        # Generar nuevo token
        token = auth_service.create_access_token(
            data={"sub": str(current_user.id)}
        )
        
        # Crear nueva sesión
        await auth_service.create_user_session(
            db,
            current_user.id,
            token,
            request.client.host,
            request.headers.get("user-agent")
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": auth_service.oauth2_scheme.expires_in
        }
        
    except Exception as e:
        logger.error(f"Error al refrescar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al refrescar token"
        )
