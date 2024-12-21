import { BedrockConfig, BedrockMessage, BedrockResponse } from '../types';

/**
 * Servicio para interactuar con AWS Bedrock
 * Maneja la comunicación con los modelos de lenguaje
 */
class BedrockService {
  private config: BedrockConfig;
  private baseUrl: string;

  constructor() {
    this.config = {
      accessKey: import.meta.env.VITE_AWS_ACCESS_KEY,
      secretKey: import.meta.env.VITE_AWS_SECRET_KEY,
      region: import.meta.env.VITE_AWS_REGION,
    };
    this.baseUrl = `https://bedrock-runtime.${this.config.region}.amazonaws.com`;
  }

  /**
   * Genera los headers necesarios para la autenticación con AWS
   */
  private async generateHeaders(body: string): Promise<Headers> {
    const headers = new Headers();
    headers.append('Content-Type', 'application/json');
    headers.append('X-Amz-Access-Token', this.config.accessKey);
    // TODO: Implementar firma AWS v4 para autenticación segura
    return headers;
  }

  /**
   * Procesa un mensaje utilizando el modelo Claude
   * @param messages - Array de mensajes del chat
   * @param options - Opciones adicionales para la generación
   */
  async processMessage(
    messages: BedrockMessage[],
    options: {
      temperature?: number;
      maxTokens?: number;
      topP?: number;
      webSearch?: boolean;
    } = {}
  ): Promise<BedrockResponse> {
    try {
      const body = JSON.stringify({
        prompt: this.formatMessages(messages),
        max_tokens_to_sample: options.maxTokens || 2000,
        temperature: options.temperature || 0.7,
        top_p: options.topP || 0.9,
      });

      const headers = await this.generateHeaders(body);
      
      const response = await fetch(
        `${this.baseUrl}/model/anthropic.claude-3-sonnet-20240229-v1:0/invoke`,
        {
          method: 'POST',
          headers,
          body,
        }
      );

      if (!response.ok) {
        throw new Error(`Error en la respuesta: ${response.statusText}`);
      }

      const data = await response.json();
      return this.parseResponse(data);

    } catch (error) {
      console.error('Error al procesar mensaje con Bedrock:', error);
      throw new Error('Error al procesar el mensaje');
    }
  }

  /**
   * Formatea los mensajes para el modelo Claude
   */
  private formatMessages(messages: BedrockMessage[]): string {
    return messages
      .map(msg => `\n\n${msg.role === 'user' ? 'Human' : 'Assistant'}: ${msg.content}`)
      .join('') + '\n\nAssistant:';
  }

  /**
   * Parsea la respuesta del modelo
   */
  private parseResponse(response: any): BedrockResponse {
    return {
      completion: response.completion || response.content,
      stop_reason: response.stop_reason || 'stop_sequence',
      stop_sequence: response.stop_sequence,
    };
  }

  /**
   * Verifica el estado de la conexión con Bedrock
   */
  async checkConnection(): Promise<boolean> {
    try {
      const headers = await this.generateHeaders('');
      const response = await fetch(`${this.baseUrl}/models`, {
        headers,
      });
      return response.ok;
    } catch (error) {
      console.error('Error al verificar conexión con Bedrock:', error);
      return false;
    }
  }

  /**
   * Estima el costo de una solicitud basado en los tokens
   */
  estimateCost(tokens: number): number {
    // Precio aproximado por 1K tokens (ajustar según precios actuales)
    const pricePerThousandTokens = 0.008;
    return (tokens / 1000) * pricePerThousandTokens;
  }
}

// Exportar una instancia única del servicio
export const bedrockService = new BedrockService();
