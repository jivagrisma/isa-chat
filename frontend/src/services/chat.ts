import { bedrockService } from './bedrock';
import { Chat, Message, WebSearchResult } from '../types';
import { store } from '../store';
import { addMessage, setLoading, setError } from '../store/features/chatSlice';
import { addNotification } from '../store/features/uiSlice';

/**
 * Servicio para manejar las operaciones del chat
 * Integra Bedrock y gestiona el estado local
 */
class ChatService {
  private messageQueue: Array<() => Promise<void>> = [];
  private isProcessing = false;

  /**
   * Procesa un nuevo mensaje del usuario
   * @param content - Contenido del mensaje
   * @param options - Opciones adicionales
   */
  async sendMessage(
    content: string,
    options: {
      webSearch?: boolean;
      attachments?: File[];
    } = {}
  ): Promise<void> {
    // Validar longitud del mensaje
    if (content.length > parseInt(import.meta.env.VITE_MESSAGE_MAX_LENGTH)) {
      this.showError('El mensaje excede la longitud máxima permitida');
      return;
    }

    // Agregar mensaje a la cola
    this.messageQueue.push(async () => {
      try {
        // Agregar mensaje del usuario al estado
        const userMessage: Message = {
          id: Date.now().toString(),
          content,
          role: 'user',
          timestamp: new Date().toISOString(),
        };
        store.dispatch(addMessage(userMessage));

        // Procesar archivos adjuntos si existen
        if (options.attachments?.length) {
          await this.processAttachments(options.attachments);
        }

        // Realizar búsqueda web si está habilitada
        let webSearchResults: WebSearchResult[] = [];
        if (options.webSearch) {
          webSearchResults = await this.performWebSearch(content);
        }

        // Preparar contexto para Bedrock
        const messages = this.prepareContext(content, webSearchResults);

        // Obtener respuesta de Bedrock
        store.dispatch(setLoading(true));
        const response = await bedrockService.processMessage(messages);

        // Agregar respuesta al estado
        const assistantMessage: Message = {
          id: Date.now().toString(),
          content: response.completion,
          role: 'assistant',
          timestamp: new Date().toISOString(),
          metadata: {
            webSearch: options.webSearch,
            sources: webSearchResults.map(result => result.url),
          },
        };
        store.dispatch(addMessage(assistantMessage));

      } catch (error) {
        console.error('Error al procesar mensaje:', error);
        this.showError('Error al procesar el mensaje');
      } finally {
        store.dispatch(setLoading(false));
      }
    });

    // Iniciar procesamiento si no hay mensajes en proceso
    if (!this.isProcessing) {
      this.processQueue();
    }
  }

  /**
   * Procesa la cola de mensajes
   */
  private async processQueue(): Promise<void> {
    if (this.messageQueue.length === 0) {
      this.isProcessing = false;
      return;
    }

    this.isProcessing = true;
    const nextMessage = this.messageQueue.shift();

    if (nextMessage) {
      await nextMessage();
      await this.processQueue();
    }
  }

  /**
   * Procesa archivos adjuntos
   */
  private async processAttachments(files: File[]): Promise<void> {
    // TODO: Implementar carga y procesamiento de archivos
    console.log('Procesando archivos:', files);
  }

  /**
   * Realiza búsqueda web
   */
  private async performWebSearch(query: string): Promise<WebSearchResult[]> {
    // TODO: Implementar integración con servicio de búsqueda
    return [];
  }

  /**
   * Prepara el contexto para el modelo
   */
  private prepareContext(
    content: string,
    webResults: WebSearchResult[]
  ): Array<{ role: 'user' | 'assistant'; content: string }> {
    const context = [];

    // Agregar resultados de búsqueda web si existen
    if (webResults.length > 0) {
      const webContext = webResults
        .map(result => `${result.title}\n${result.snippet}`)
        .join('\n\n');
      context.push({
        role: 'user',
        content: `Contexto de búsqueda web:\n${webContext}`,
      });
    }

    // Agregar el mensaje actual
    context.push({
      role: 'user',
      content,
    });

    return context;
  }

  /**
   * Muestra un error al usuario
   */
  private showError(message: string): void {
    store.dispatch(setError(message));
    store.dispatch(
      addNotification({
        type: 'error',
        message,
      })
    );
  }

  /**
   * Limpia el historial de chat
   */
  clearHistory(): void {
    // TODO: Implementar limpieza de historial
    console.log('Limpiando historial de chat');
  }

  /**
   * Exporta el chat actual
   */
  exportChat(): string {
    const state = store.getState();
    const currentChat = state.chat.currentChat;
    
    if (!currentChat) {
      throw new Error('No hay chat activo para exportar');
    }

    return JSON.stringify(currentChat, null, 2);
  }
}

// Exportar una instancia única del servicio
export const chatService = new ChatService();
