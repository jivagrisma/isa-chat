import os
import aiofiles
import magic
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from loguru import logger
import asyncio
from pathlib import Path

from app.core.config import settings

class FileService:
    """
    Servicio para manejar archivos adjuntos.
    Gestiona el procesamiento y almacenamiento de archivos.
    """

    def __init__(self):
        """Inicializa el servicio de archivos."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_file_size = settings.MAX_UPLOAD_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Asegura que el directorio de uploads exista."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        file: UploadFile,
        user_id: int,
        chat_id: int
    ) -> Dict[str, Any]:
        """
        Guarda un archivo adjunto.
        
        Args:
            file: Archivo a guardar
            user_id: ID del usuario
            chat_id: ID del chat
            
        Returns:
            Dict[str, Any]: Información del archivo guardado
        """
        try:
            # Validar archivo
            await self._validate_file(file)
            
            # Generar nombre único
            file_hash = await self._calculate_file_hash(file)
            extension = self._get_file_extension(file.filename)
            filename = f"{file_hash}{extension}"
            
            # Crear estructura de directorios
            year = datetime.utcnow().strftime('%Y')
            month = datetime.utcnow().strftime('%m')
            day = datetime.utcnow().strftime('%d')
            
            relative_path = Path(f"{year}/{month}/{day}/{chat_id}")
            full_path = self.upload_dir / relative_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            file_path = full_path / filename
            
            # Guardar archivo
            await self._save_file_content(file, file_path)
            
            # Obtener metadatos
            metadata = await self._get_file_metadata(file_path)
            
            return {
                'filename': file.filename,
                'path': str(relative_path / filename),
                'type': self._get_file_type(file.filename),
                'size': metadata['size'],
                'mime_type': metadata['mime_type'],
                'metadata': metadata
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al guardar archivo: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al procesar el archivo"
            )

    async def _validate_file(self, file: UploadFile):
        """
        Valida un archivo antes de guardarlo.
        
        Args:
            file: Archivo a validar
            
        Raises:
            HTTPException: Si el archivo no es válido
        """
        # Verificar tamaño
        try:
            size = 0
            chunk_size = 8192  # 8KB chunks
            
            while chunk := await file.read(chunk_size):
                size += len(chunk)
                if size > self.max_file_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Archivo demasiado grande. Máximo: {self.max_file_size/1024/1024}MB"
                    )
            
            await file.seek(0)  # Regresar al inicio del archivo
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al validar tamaño: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al procesar el archivo"
            )

        # Verificar extensión
        extension = self._get_file_extension(file.filename)
        if extension[1:] not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Permitidos: {', '.join(self.allowed_extensions)}"
            )

    async def _calculate_file_hash(self, file: UploadFile) -> str:
        """
        Calcula el hash SHA-256 de un archivo.
        
        Args:
            file: Archivo a procesar
            
        Returns:
            str: Hash del archivo
        """
        sha256_hash = hashlib.sha256()
        
        try:
            while chunk := await file.read(8192):
                sha256_hash.update(chunk)
            
            await file.seek(0)
            return sha256_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"Error al calcular hash: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al procesar el archivo"
            )

    def _get_file_extension(self, filename: str) -> str:
        """
        Obtiene la extensión de un archivo.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            str: Extensión del archivo
        """
        return os.path.splitext(filename)[1].lower()

    def _get_file_type(self, filename: str) -> str:
        """
        Determina el tipo de archivo basado en su extensión.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            str: Tipo de archivo (image, document, etc.)
        """
        extension = self._get_file_extension(filename)
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        document_extensions = ['.pdf', '.doc', '.docx', '.txt']
        
        if extension in image_extensions:
            return 'image'
        elif extension in document_extensions:
            return 'document'
        else:
            return 'other'

    async def _save_file_content(
        self,
        file: UploadFile,
        file_path: Path
    ):
        """
        Guarda el contenido de un archivo.
        
        Args:
            file: Archivo a guardar
            file_path: Ruta donde guardar
        """
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                while chunk := await file.read(8192):
                    await f.write(chunk)
                    
        except Exception as e:
            logger.error(f"Error al guardar archivo: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al guardar el archivo"
            )

    async def _get_file_metadata(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        Obtiene metadatos de un archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Dict[str, Any]: Metadatos del archivo
        """
        try:
            stats = os.stat(file_path)
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(str(file_path))
            
            metadata = {
                'size': stats.st_size,
                'created_at': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'mime_type': mime_type
            }
            
            # Metadatos específicos por tipo
            if mime_type.startswith('image/'):
                # TODO: Agregar metadatos de imagen (dimensiones, etc.)
                pass
                
            return metadata
            
        except Exception as e:
            logger.error(f"Error al obtener metadatos: {e}")
            return {
                'size': 0,
                'mime_type': 'application/octet-stream'
            }

    async def delete_file(
        self,
        file_path: str,
        user_id: int
    ) -> bool:
        """
        Elimina un archivo.
        
        Args:
            file_path: Ruta relativa del archivo
            user_id: ID del usuario para verificar permisos
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            full_path = self.upload_dir / file_path
            
            if not full_path.exists():
                return False
                
            # TODO: Verificar permisos del usuario
            
            os.remove(full_path)
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return False

    async def get_file_info(
        self,
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un archivo.
        
        Args:
            file_path: Ruta relativa del archivo
            
        Returns:
            Optional[Dict[str, Any]]: Información del archivo o None si no existe
        """
        try:
            full_path = self.upload_dir / file_path
            
            if not full_path.exists():
                return None
                
            metadata = await self._get_file_metadata(full_path)
            
            return {
                'path': file_path,
                'type': self._get_file_type(file_path),
                'size': metadata['size'],
                'mime_type': metadata['mime_type'],
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error al obtener info de archivo: {e}")
            return None

# Instancia global del servicio
file_service = FileService()
