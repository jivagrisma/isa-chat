from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
import re

# Esquemas base
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Esquemas para Usuario
class UserBase(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$', v):
            raise ValueError(
                'La contraseña debe contener al menos 8 caracteres, '
                'incluyendo letras y números'
            )
        return v

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class User(UserInDB):
    pass

# Esquemas para Chat
class ChatBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatCreate(ChatBase):
    pass

class ChatUpdate(BaseSchema):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatInDB(ChatBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

class Chat(ChatInDB):
    messages: List["Message"] = []

# Esquemas para Mensaje
class MessageBase(BaseSchema):
    content: str = Field(..., min_length=1)
    role: str = Field(..., regex='^(user|assistant)$')
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MessageCreate(MessageBase):
    chat_id: int

class MessageUpdate(BaseSchema):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageInDB(MessageBase):
    id: int
    chat_id: int
    user_id: Optional[int]
    created_at: datetime

class Message(MessageInDB):
    attachments: List["Attachment"] = []

# Esquemas para Archivo Adjunto
class AttachmentBase(BaseSchema):
    file_name: str
    file_type: str
    mime_type: str
    file_size: int
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AttachmentCreate(AttachmentBase):
    message_id: int
    file_path: str

class AttachmentInDB(AttachmentBase):
    id: int
    message_id: int
    file_path: str
    created_at: datetime

class Attachment(AttachmentInDB):
    pass

# Esquemas para Sesión de Usuario
class UserSessionBase(BaseSchema):
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserSessionCreate(UserSessionBase):
    session_token: str
    expires_at: datetime

class UserSessionInDB(UserSessionBase):
    id: int
    session_token: str
    expires_at: datetime
    created_at: datetime
    last_activity: Optional[datetime] = None
    is_active: bool

class UserSession(UserSessionInDB):
    pass

# Esquemas para Log de Auditoría
class AuditLogBase(BaseSchema):
    action: str
    entity_type: str
    entity_id: int
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    ip_address: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    user_id: int

class AuditLogInDB(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime

class AuditLog(AuditLogInDB):
    pass

# Esquemas para respuestas de la API
class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseSchema):
    user_id: int
    exp: datetime

class SuccessResponse(BaseSchema):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseSchema):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

# Esquemas para paginación
class PaginationParams(BaseSchema):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)

class PaginatedResponse(BaseSchema):
    total: int
    items: List[Any]
    page: int
    pages: int
    has_next: bool
    has_prev: bool

# Actualizar referencias circulares
Chat.update_forward_refs()
Message.update_forward_refs()
