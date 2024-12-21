import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
import json
from pathlib import Path
import hashlib
import secrets
from loguru import logger

# Utilidades de validación
def validate_email(email: str) -> bool:
    """
    Valida un correo electrónico.
    
    Args:
        email: Correo a validar
        
    Returns:
        bool: True si el correo es válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """
    Valida una contraseña según los requisitos.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        bool: True si la contraseña cumple los requisitos
    """
    # Mínimo 8 caracteres, al menos una letra y un número
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$'
    return bool(re.match(pattern, password))

def validate_username(username: str) -> bool:
    """
    Valida un nombre de usuario.
    
    Args:
        username: Nombre de usuario a validar
        
    Returns:
        bool: True si el nombre de usuario es válido
    """
    # Letras, números, guiones y guiones bajos, 3-30 caracteres
    pattern = r'^[a-zA-Z0-9_-]{3,30}$'
    return bool(re.match(pattern, username))

# Utilidades de formateo
def format_datetime(dt: datetime) -> str:
    """
    Formatea una fecha y hora en ISO 8601.
    
    Args:
        dt: Fecha y hora a formatear
        
    Returns:
        str: Fecha y hora formateada
    """
    return dt.astimezone(timezone.utc).isoformat()

def format_file_size(size: int) -> str:
    """
    Formatea un tamaño de archivo.
    
    Args:
        size: Tamaño en bytes
        
    Returns:
        str: Tamaño formateado
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"

# Utilidades de seguridad
def generate_random_string(length: int = 32) -> str:
    """
    Genera una cadena aleatoria segura.
    
    Args:
        length: Longitud de la cadena
        
    Returns:
        str: Cadena aleatoria
    """
    return secrets.token_urlsafe(length)

def hash_content(content: Union[str, bytes]) -> str:
    """
    Genera un hash SHA-256 de un contenido.
    
    Args:
        content: Contenido a hashear
        
    Returns:
        str: Hash del contenido
    """
    if isinstance(content, str):
        content = content.encode()
    return hashlib.sha256(content).hexdigest()

# Utilidades de manejo de errores
class AppError(Exception):
    """Excepción base para errores de la aplicación."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

def handle_app_error(error: AppError) -> HTTPException:
    """
    Convierte un AppError en HTTPException.
    
    Args:
        error: Error a convertir
        
    Returns:
        HTTPException: Excepción HTTP
    """
    return HTTPException(
        status_code=error.status_code,
        detail={
            'message': error.message,
            'details': error.details
        }
    )

# Utilidades de paginación
def paginate_results(
    items: List[Any],
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """
    Pagina una lista de resultados.
    
    Args:
        items: Lista de items
        page: Número de página
        page_size: Tamaño de página
        
    Returns:
        Dict[str, Any]: Resultados paginados
    """
    start = (page - 1) * page_size
    end = start + page_size
    
    total = len(items)
    items_page = items[start:end]
    
    return {
        'items': items_page,
        'total': total,
        'page': page,
        'pages': (total + page_size - 1) // page_size,
        'has_next': end < total,
        'has_prev': page > 1
    }

# Utilidades de caché
class SimpleCache:
    """Implementación simple de caché en memoria."""
    
    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        if key in self.cache:
            item = self.cache[key]
            if datetime.now().timestamp() - item['timestamp'] < self.ttl:
                return item['value']
            del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """Guarda un valor en el caché."""
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now().timestamp()
        }

    def delete(self, key: str):
        """Elimina un valor del caché."""
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """Limpia todo el caché."""
        self.cache.clear()

# Utilidades de logging
def setup_logger(
    log_file: Optional[Path] = None,
    level: str = "INFO"
):
    """
    Configura el logger de la aplicación.
    
    Args:
        log_file: Archivo de log opcional
        level: Nivel de logging
    """
    config = {
        "handlers": [
            {
                "sink": "sys.stdout",
                "format": "{time} | {level} | {message}",
                "level": level,
            }
        ]
    }
    
    if log_file:
        config["handlers"].append({
            "sink": log_file,
            "format": "{time} | {level} | {message}",
            "level": level,
            "rotation": "1 day",
            "retention": "1 month",
        })
    
    logger.configure(**config)

# Utilidades de serialización
def serialize_model(model: BaseModel) -> Dict[str, Any]:
    """
    Serializa un modelo Pydantic.
    
    Args:
        model: Modelo a serializar
        
    Returns:
        Dict[str, Any]: Modelo serializado
    """
    return json.loads(model.json(by_alias=True))

def deserialize_model(
    data: Dict[str, Any],
    model_class: type[BaseModel]
) -> BaseModel:
    """
    Deserializa datos en un modelo Pydantic.
    
    Args:
        data: Datos a deserializar
        model_class: Clase del modelo
        
    Returns:
        BaseModel: Modelo deserializado
    """
    return model_class.parse_obj(data)

# Utilidades de texto
def truncate_text(
    text: str,
    max_length: int,
    suffix: str = "..."
) -> str:
    """
    Trunca un texto a una longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo para indicar truncamiento
        
    Returns:
        str: Texto truncado
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def sanitize_text(text: str) -> str:
    """
    Sanitiza un texto eliminando caracteres no deseados.
    
    Args:
        text: Texto a sanitizar
        
    Returns:
        str: Texto sanitizado
    """
    # Eliminar HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalizar espacios
    text = ' '.join(text.split())
    
    # Eliminar caracteres especiales
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text.strip()

# Instancia global de caché
app_cache = SimpleCache()
