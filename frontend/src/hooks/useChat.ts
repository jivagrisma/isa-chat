import { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, Message, UseChat } from '../types';
import { chatService } from '../services/chat';
import { setError } from '../store/features/chatSlice';
import { addNotification } from '../store/features/uiSlice';

/**
 * Hook personalizado para manejar la lógica del chat
 * Proporciona una interfaz para interactuar con el servicio de chat
 */
export const useChat = (): UseChat => {
  const dispatch = useDispatch();
  const [isLoading, setIsLoading] = useState(false);
  
  const messages = useSelector((state: RootState) => 
    state.chat.currentChat?.messages || []
  );
  
  const error = useSelector((state: RootState) => 
    state.chat.error
  );

  /**
   * Envía un mensaje al chat
   */
  const sendMessage = useCallback(async (
    content: string,
    options: {
      webSearch?: boolean;
      attachments?: File[];
    } = {}
  ) => {
    try {
      setIsLoading(true);
      await chatService.sendMessage(content, options);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al enviar el mensaje';
      dispatch(setError(errorMessage));
      dispatch(addNotification({
        type: 'error',
        message: errorMessage
      }));
    } finally {
      setIsLoading(false);
    }
  }, [dispatch]);

  /**
   * Sube un archivo al chat
   */
  const uploadFile = useCallback(async (file: File) => {
    try {
      setIsLoading(true);
      
      // Validar tamaño del archivo
      const maxSize = parseInt(import.meta.env.VITE_MAX_FILE_SIZE);
      if (file.size > maxSize) {
        throw new Error(`El archivo excede el tamaño máximo permitido (${maxSize / 1024 / 1024}MB)`);
      }

      // Validar tipo de archivo
      const supportedTypes = import.meta.env.VITE_SUPPORTED_FILE_TYPES.split(',');
      const isSupported = supportedTypes.some(type => {
        if (type.includes('*')) {
          return file.type.startsWith(type.replace('*', ''));
        }
        return file.type === type || file.name.endsWith(type);
      });

      if (!isSupported) {
        throw new Error('Tipo de archivo no soportado');
      }

      await sendMessage('', { attachments: [file] });
      
      dispatch(addNotification({
        type: 'success',
        message: 'Archivo subido exitosamente'
      }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al subir el archivo';
      dispatch(setError(errorMessage));
      dispatch(addNotification({
        type: 'error',
        message: errorMessage
      }));
    } finally {
      setIsLoading(false);
    }
  }, [dispatch, sendMessage]);

  /**
   * Limpia el chat actual
   */
  const clearChat = useCallback(() => {
    try {
      chatService.clearHistory();
      dispatch(addNotification({
        type: 'success',
        message: 'Chat limpiado exitosamente'
      }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al limpiar el chat';
      dispatch(setError(errorMessage));
      dispatch(addNotification({
        type: 'error',
        message: errorMessage
      }));
    }
  }, [dispatch]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    uploadFile,
    clearChat,
  };
};
