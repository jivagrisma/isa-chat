from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from loguru import logger

from app.models.models import Chat, Message, User, Attachment
from app.schemas.schemas import ChatCreate, MessageCreate, ChatUpdate
from app.services.bedrock_service import bedrock_service
from app.core.config import settings

class ChatService:
    """
    Servicio para manejar las operaciones del chat.
    Gestiona conversaciones, mensajes y la integración con Bedrock.
    """

    async def create_chat(
        self,
        db: AsyncSession,
        user_id: int,
        chat_data: ChatCreate
    ) -> Chat:
        """
        Crea una nueva conversación.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            chat_data: Datos de la conversación
            
        Returns:
            Chat: Conversación creada
        """
        try:
            chat = Chat(
                user_id=user_id,
                title=chat_data.title,
                metadata=chat_data.metadata
            )
            
            db.add(chat)
            await db.commit()
            await db.refresh(chat)
            
            return chat
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al crear chat: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear la conversación"
            )

    async def get_chat(
        self,
        db: AsyncSession,
        chat_id: int,
        user_id: int
    ) -> Chat:
        """
        Obtiene una conversación por ID.
        
        Args:
            db: Sesión de base de datos
            chat_id: ID de la conversación
            user_id: ID del usuario para verificar acceso
            
        Returns:
            Chat: Conversación encontrada
        """
        try:
            result = await db.execute(
                select(Chat).where(
                    and_(
                        Chat.id == chat_id,
                        Chat.user_id == user_id,
                        Chat.is_active == True
                    )
                )
            )
            chat = result.scalar_one_or_none()
            
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversación no encontrada"
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

    async def get_user_chats(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        include_messages: bool = False
    ) -> List[Chat]:
        """
        Obtiene las conversaciones de un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            include_messages: Si se deben incluir los mensajes
            
        Returns:
            List[Chat]: Lista de conversaciones
        """
        try:
            query = select(Chat).where(
                and_(
                    Chat.user_id == user_id,
                    Chat.is_active == True
                )
            ).order_by(Chat.updated_at.desc())
            
            if not include_messages:
                query = query.options(
                    selectinload(Chat.messages).noload()
                )
                
            result = await db.execute(
                query.offset(skip).limit(limit)
            )
            
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error al obtener chats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al obtener las conversaciones"
            )

    async def update_chat(
        self,
        db: AsyncSession,
        chat_id: int,
        user_id: int,
        chat_data: ChatUpdate
    ) -> Chat:
        """
        Actualiza una conversación.
        
        Args:
            db: Sesión de base de datos
            chat_id: ID de la conversación
            user_id: ID del usuario para verificar acceso
            chat_data: Datos a actualizar
            
        Returns:
            Chat: Conversación actualizada
        """
        try:
            chat = await self.get_chat(db, chat_id, user_id)
            
            for field, value in chat_data.dict(exclude_unset=True).items():
                setattr(chat, field, value)
                
            chat.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(chat)
            
            return chat
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al actualizar chat: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar la conversación"
            )

    async def process_message(
        self,
        db: AsyncSession,
        user_id: int,
        message_data: MessageCreate,
        system_prompt: Optional[str] = None
    ) -> Message:
        """
        Procesa un mensaje y obtiene respuesta del modelo.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            message_data: Datos del mensaje
            system_prompt: Prompt del sistema opcional
            
        Returns:
            Message: Mensaje procesado con respuesta
        """
        try:
            # Verificar acceso al chat
            chat = await self.get_chat(db, message_data.chat_id, user_id)
            
            # Crear mensaje del usuario
            user_message = Message(
                content=message_data.content,
                role='user',
                chat_id=chat.id,
                user_id=user_id,
                metadata=message_data.metadata
            )
            
            db.add(user_message)
            await db.commit()
            await db.refresh(user_message)
            
            # Obtener contexto de la conversación
            context = await self._get_chat_context(db, chat.id)
            
            # Procesar con Bedrock
            response = await bedrock_service.process_message(
                messages=context,
                system_prompt=system_prompt
            )
            
            # Crear mensaje de respuesta
            assistant_message = Message(
                content=response['content'],
                role='assistant',
                chat_id=chat.id,
                metadata={
                    'model': response['model'],
                    'usage': response['usage'],
                    'stop_reason': response['stop_reason']
                }
            )
            
            db.add(assistant_message)
            await db.commit()
            await db.refresh(assistant_message)
            
            # Actualizar timestamp del chat
            chat.updated_at = datetime.utcnow()
            await db.commit()
            
            return assistant_message
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al procesar mensaje: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al procesar el mensaje"
            )

    async def _get_chat_context(
        self,
        db: AsyncSession,
        chat_id: int,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """
        Obtiene el contexto de una conversación.
        
        Args:
            db: Sesión de base de datos
            chat_id: ID de la conversación
            limit: Número de mensajes a incluir
            
        Returns:
            List[Dict[str, str]]: Lista de mensajes formateados
        """
        try:
            result = await db.execute(
                select(Message)
                .where(Message.chat_id == chat_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            
            messages = result.scalars().all()
            messages.reverse()  # Orden cronológico
            
            return [
                {
                    'role': msg.role,
                    'content': msg.content
                }
                for msg in messages
            ]
            
        except Exception as e:
            logger.error(f"Error al obtener contexto: {e}")
            return []

    async def add_attachment(
        self,
        db: AsyncSession,
        message_id: int,
        file_data: Dict[str, Any]
    ) -> Attachment:
        """
        Agrega un archivo adjunto a un mensaje.
        
        Args:
            db: Sesión de base de datos
            message_id: ID del mensaje
            file_data: Datos del archivo
            
        Returns:
            Attachment: Archivo adjunto creado
        """
        try:
            attachment = Attachment(
                message_id=message_id,
                file_name=file_data['filename'],
                file_path=file_data['path'],
                file_type=file_data['type'],
                file_size=file_data['size'],
                mime_type=file_data['mime_type'],
                metadata=file_data.get('metadata', {})
            )
            
            db.add(attachment)
            await db.commit()
            await db.refresh(attachment)
            
            return attachment
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al agregar adjunto: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al agregar el archivo adjunto"
            )

# Instancia global del servicio
chat_service = ChatService()
