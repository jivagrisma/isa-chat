from typing import List, Union
from pydantic import AnyHttpUrl, BaseModel, EmailStr, validator
from pydantic_settings import BaseSettings
import json
from pathlib import Path

class Settings(BaseSettings):
    # Configuración básica
    APP_NAME: str
    ENVIRONMENT: str
    DEBUG: bool
    API_VERSION: str
    HOST: str
    PORT: int

    # Seguridad
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    CORS_ORIGINS: Union[str, List[str]]

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return json.loads(v)
        return v

    # Base de datos
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    DATABASE_URL: str

    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v: str, values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_HOST')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"

    # AWS Bedrock
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BEDROCK_MODEL: str

    # Configuración de archivos
    UPLOAD_DIR: Path
    MAX_UPLOAD_SIZE: int
    ALLOWED_EXTENSIONS: List[str]

    @validator("UPLOAD_DIR", pre=True)
    def create_upload_dir(cls, v: str) -> Path:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return json.loads(v)
        return v

    # Configuración de caché
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    CACHE_TTL: int

    # Logging
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_FILE: Path

    @validator("LOG_FILE", pre=True)
    def create_log_dir(cls, v: str) -> Path:
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    # Límites y timeouts
    REQUEST_TIMEOUT: int
    RATE_LIMIT_REQUESTS: int
    RATE_LIMIT_PERIOD: int
    MAX_CONNECTIONS: int

    # Configuración de WebSocket
    WS_HEARTBEAT_INTERVAL: int
    WS_CLOSE_TIMEOUT: int

    # Monitoreo
    ENABLE_METRICS: bool
    METRICS_PATH: str
    HEALTH_CHECK_PATH: str

    class Config:
        env_file = ".env"
        case_sensitive = True

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name in ["CORS_ORIGINS", "ALLOWED_EXTENSIONS"]:
                return json.loads(raw_val)
            return raw_val

# Instancia global de configuración
settings = Settings()

# Configuración de API
class APISettings(BaseModel):
    title: str = settings.APP_NAME
    version: str = settings.API_VERSION
    description: str = """
    API del backend de ISA Chat.
    Proporciona endpoints para:
    * Autenticación y gestión de usuarios
    * Gestión de conversaciones
    * Integración con AWS Bedrock
    * Manejo de archivos
    * WebSockets para chat en tiempo real
    """
    openapi_url: str = f"/api/{settings.API_VERSION}/openapi.json"
    docs_url: str = f"/api/{settings.API_VERSION}/docs"
    redoc_url: str = f"/api/{settings.API_VERSION}/redoc"
    
    # CORS
    allow_origins: List[str] = settings.CORS_ORIGINS
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]

api_settings = APISettings()

# Configuración de seguridad
class SecuritySettings(BaseModel):
    secret_key: str = settings.SECRET_KEY
    algorithm: str = settings.ALGORITHM
    access_token_expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    # Configuración de contraseñas
    password_min_length: int = 8
    password_max_length: int = 50
    password_regex: str = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$"

security_settings = SecuritySettings()

# Configuración de AWS
class AWSSettings(BaseModel):
    access_key_id: str = settings.AWS_ACCESS_KEY_ID
    secret_access_key: str = settings.AWS_SECRET_ACCESS_KEY
    region: str = settings.AWS_REGION
    bedrock_model: str = settings.AWS_BEDROCK_MODEL
    
    # Configuración del modelo
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

aws_settings = AWSSettings()
