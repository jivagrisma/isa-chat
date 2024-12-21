from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional
from loguru import logger

from app.core.dependencies import (
    get_current_active_user,
    check_rate_limit,
    get_pagination,
    ws_manager
)
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    ChatCreate,
    ChatUpdate,
    Chat as ChatSchema,
    MessageCreate,
    Message as MessageSchema,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse
)
from app.services.chat_service import chat_service
from app.services.file_service import file_service
from app.services.web_search_service import web_search_service

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(check_rate_limit)]
)

@router.post(
    "",
    response_model=ChatSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def create_chat(
    chat_data: ChatCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Crea una nueva conversación.
    
    Args:
        chat_data: Datos de la conversación
        current_user: Usuario actual
        db: Sesión de base de datos
    """
    try:
        chat = await chat_service.create_chat(
            db,
            current_user.id,
            chat_data
        )
        return chat
        
    except Exception as e:
        logger.error(f"Error al crear chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la conversación"
        )

@router.get(
    "",
    response_model=PaginatedResponse,
    responses={
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_user_chats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(get_pagination),
    include_messages: bool = False
):
    """
    Obtiene las conversaciones del usuario.
    
    Args:
        current_user: Usuario actual
        db: Sesión de base de datos
        pagination: Parámetros de paginación
        include_messages: Si se deben incluir los mensajes
    """
    try:
        chats = await chat_service.get_user_chats(
            db,
            current_user.id,
            pagination['skip'],
            pagination['limit'],
            include_messages
        )
        return chats
        
    except Exception as e:
        logger.error(f"Error al obtener chats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las conversaciones"
        )

@router.get(
    "/{chat_id}",
    response_model=ChatSchema,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_chat(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una conversación por ID.
    
    Args:
        chat_id: ID de la conversación
        current_user: Usuario actual
        db: Sesión de base de datos
    """
    try:
        chat = await chat_service.get_chat(
            db,
            chat_id,
            current_user.id
        )
        return chat
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la conversación"
        )

@router.post(
    "/{chat_id}/messages",
    response_model=MessageSchema,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    system_prompt: Optional[str] = None,
    web_search: bool = False
):
    """
    Envía un mensaje en una conversación.
    
    Args:
        chat_id: ID de la conversación
        message_data: Datos del mensaje
        current_user: Usuario actual
        db: Sesión de base de datos
        system_prompt: Prompt del sistema opcional
        web_search: Si se debe realizar búsqueda web
    """
    try:
        # Verificar acceso al chat
        chat = await chat_service.get_chat(db, chat_id, current_user.id)
        
        # Realizar búsqueda web si está habilitada
        if web_search:
            search_results = await web_search_service.search(
                message_data.content,
                max_results=5
            )
            message_data.metadata = {
                "web_search_results": search_results
            }
        
        # Procesar mensaje
        response = await chat_service.process_message(
            db,
            current_user.id,
            message_data,
            system_prompt
        )
        
        # Notificar a clientes WebSocket
        await ws_manager.broadcast(
            json.dumps({
                "type": "new_message",
                "data": {
                    "chat_id": chat_id,
                    "message": response
                }
            })
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al enviar mensaje: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar el mensaje"
        )

@router.post(
    "/{chat_id}/messages/{message_id}/attachments",
    response_model=MessageSchema,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def upload_attachment(
    chat_id: int,
    message_id: int,
    file: UploadFile = File(...),
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Sube un archivo adjunto a un mensaje.
    
    Args:
        chat_id: ID de la conversación
        message_id: ID del mensaje
        file: Archivo a subir
        current_user: Usuario actual
        db: Sesión de base de datos
    """
    try:
        # Verificar acceso al chat
        chat = await chat_service.get_chat(db, chat_id, current_user.id)
        
        # Guardar archivo
        file_info = await file_service.save_file(
            file,
            current_user.id,
            chat_id
        )
        
        # Agregar adjunto al mensaje
        message = await chat_service.add_attachment(
            db,
            message_id,
            file_info
        )
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al subir archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar el archivo"
        )

@router.put(
    "/{chat_id}",
    response_model=ChatSchema,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def update_chat(
    chat_id: int,
    chat_data: ChatUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza una conversación.
    
    Args:
        chat_id: ID de la conversación
        chat_data: Datos a actualizar
        current_user: Usuario actual
        db: Sesión de base de datos
    """
    try:
        chat = await chat_service.update_chat(
            db,
            chat_id,
            current_user.id,
            chat_data
        )
        return chat
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la conversación"
        )

@router.delete(
    "/{chat_id}",
    response_model=SuccessResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def delete_chat(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina una conversación.
    
    Args:
        chat_id: ID de la conversación
        current_user: Usuario actual
        db: Sesión de base de datos
    """
    try:
        # Verificar acceso al chat
        chat = await chat_service.get_chat(db, chat_id, current_user.id)
        
        # Marcar como inactivo
        chat.is_active = False
        await db.commit()
        
        return {
            "success": True,
            "message": "Conversación eliminada correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la conversación"
        )

# WebSocket para chat en tiempo real
from fastapi import WebSocket, WebSocketDisconnect
import json

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: int,
    token: str
):
    """
    Endpoint WebSocket para chat en tiempo real.
    
    Args:
        websocket: Conexión WebSocket
        client_id: ID del cliente
        token: Token JWT
    """
    try:
        # Verificar token
        await auth_service.verify_token(token)
        
        # Aceptar conexión
        await ws_manager.connect(websocket)
        
        try:
            while True:
                # Recibir mensaje
                data = await websocket.receive_text()
                
                # Procesar mensaje
                # TODO: Implementar lógica de procesamiento
                
                # Enviar respuesta
                await websocket.send_text(
                    json.dumps({
                        "type": "message",
                        "data": data
                    })
                )
                
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
            
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        if websocket.client_state.connected:
            await websocket.close()
