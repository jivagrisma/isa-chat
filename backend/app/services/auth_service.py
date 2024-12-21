from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings, security_settings
from app.models.models import User, UserSession
from app.schemas.schemas import TokenData, UserCreate
from app.db.database import get_db

class AuthService:
    """
    Servicio para manejar la autenticación y seguridad.
    Gestiona tokens JWT, hashing de contraseñas y verificación de usuarios.
    """
    
    def __init__(self):
        """Inicializa el contexto de encriptación para contraseñas."""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12
        )
        self.oauth2_scheme = None  # Se inicializa en la aplicación principal

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña coincide con su hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Genera un hash para una contraseña."""
        return self.pwd_context.hash(password)

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un token JWT de acceso.
        
        Args:
            data: Datos a codificar en el token
            expires_delta: Tiempo de expiración opcional
            
        Returns:
            str: Token JWT codificado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or 
            timedelta(minutes=security_settings.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode,
            security_settings.secret_key,
            algorithm=security_settings.algorithm
        )

    async def verify_token(self, token: str) -> TokenData:
        """
        Verifica y decodifica un token JWT.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            TokenData: Datos decodificados del token
            
        Raises:
            HTTPException: Si el token es inválido o ha expirado
        """
        try:
            payload = jwt.decode(
                token,
                security_settings.secret_key,
                algorithms=[security_settings.algorithm]
            )
            user_id: int = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            token_data = TokenData(
                user_id=user_id,
                exp=datetime.fromtimestamp(payload.get("exp"))
            )
            return token_data
            
        except JWTError as e:
            logger.error(f"Error al verificar token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Autentica un usuario por email y contraseña.
        
        Args:
            db: Sesión de base de datos
            email: Email del usuario
            password: Contraseña sin procesar
            
        Returns:
            Optional[User]: Usuario autenticado o None si falla la autenticación
        """
        try:
            # Buscar usuario por email
            result = await db.execute(
                User.__table__.select().where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
                
            return user
            
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return None

    async def create_user_session(
        self,
        db: AsyncSession,
        user_id: int,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """
        Crea una nueva sesión de usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            token: Token de sesión
            ip_address: Dirección IP opcional
            user_agent: User agent opcional
            
        Returns:
            UserSession: Sesión creada
        """
        try:
            session = UserSession(
                user_id=user_id,
                session_token=token,
                expires_at=datetime.utcnow() + timedelta(
                    minutes=security_settings.access_token_expire_minutes
                ),
                ip_address=ip_address,
                user_agent=user_agent,
                is_active=True
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            return session
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al crear sesión: {e}")
            raise

    async def validate_password(self, password: str) -> bool:
        """
        Valida que una contraseña cumpla con los requisitos.
        
        Args:
            password: Contraseña a validar
            
        Returns:
            bool: True si la contraseña es válida
        """
        if len(password) < security_settings.password_min_length:
            return False
            
        if len(password) > security_settings.password_max_length:
            return False
            
        if not any(c.isupper() for c in password):
            return False
            
        if not any(c.islower() for c in password):
            return False
            
        if not any(c.isdigit() for c in password):
            return False
            
        return True

    async def register_user(
        self,
        db: AsyncSession,
        user_data: UserCreate
    ) -> User:
        """
        Registra un nuevo usuario.
        
        Args:
            db: Sesión de base de datos
            user_data: Datos del usuario a registrar
            
        Returns:
            User: Usuario creado
            
        Raises:
            HTTPException: Si el email ya está registrado o los datos son inválidos
        """
        try:
            # Verificar si el email ya existe
            result = await db.execute(
                User.__table__.select().where(User.email == user_data.email)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email ya registrado"
                )

            # Validar contraseña
            if not await self.validate_password(user_data.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La contraseña no cumple con los requisitos"
                )

            # Crear usuario
            user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=self.get_password_hash(user_data.password)
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al registrar usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al registrar usuario"
            )

# Instancia global del servicio
auth_service = AuthService()
