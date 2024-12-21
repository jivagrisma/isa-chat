import json
import boto3
from typing import List, Dict, Any, Optional
from botocore.config import Config
from loguru import logger

from app.core.config import settings, aws_settings

class BedrockService:
    """
    Servicio para interactuar con AWS Bedrock.
    Maneja la comunicación con el modelo de lenguaje Claude.
    """

    def __init__(self):
        """Inicializa el cliente de Bedrock con las credenciales configuradas."""
        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                aws_access_key_id=aws_settings.access_key_id,
                aws_secret_access_key=aws_settings.secret_access_key,
                region_name=aws_settings.region,
                config=Config(
                    retries={'max_attempts': 3, 'mode': 'standard'},
                    connect_timeout=5,
                    read_timeout=30,
                )
            )
            logger.info("Cliente de AWS Bedrock inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar el cliente de AWS Bedrock: {e}")
            raise

    async def process_message(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje usando el modelo Claude de Anthropic.
        
        Args:
            messages: Lista de mensajes previos en formato [{role: str, content: str}]
            system_prompt: Prompt del sistema para establecer el contexto
            temperature: Control de aleatoriedad (0-1)
            max_tokens: Número máximo de tokens en la respuesta
            top_p: Núcleo de probabilidad para muestreo (0-1)
            
        Returns:
            Dict con la respuesta del modelo
        """
        try:
            # Construir el prompt
            formatted_messages = self._format_messages(messages, system_prompt)
            
            # Preparar los parámetros del modelo
            request_body = {
                "prompt": formatted_messages,
                "max_tokens": max_tokens or aws_settings.max_tokens,
                "temperature": temperature or aws_settings.temperature,
                "top_p": top_p or aws_settings.top_p,
                "stop_sequences": ["\n\nHuman:", "\n\nAssistant:"],
                "anthropic_version": "bedrock-2023-05-31"
            }

            # Invocar el modelo
            response = self.client.invoke_model(
                modelId=aws_settings.bedrock_model,
                body=json.dumps(request_body)
            )

            # Procesar la respuesta
            response_body = json.loads(response.get('body').read())
            
            return {
                'content': response_body.get('completion', ''),
                'stop_reason': response_body.get('stop_reason'),
                'model': aws_settings.bedrock_model,
                'usage': response_body.get('usage', {}),
            }

        except Exception as e:
            logger.error(f"Error al procesar mensaje con Bedrock: {e}")
            raise

    def _format_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Formatea los mensajes para el modelo Claude.
        
        Args:
            messages: Lista de mensajes
            system_prompt: Prompt del sistema
            
        Returns:
            String con el prompt formateado
        """
        formatted_prompt = ""
        
        # Agregar el prompt del sistema si existe
        if system_prompt:
            formatted_prompt += f"\n\nHuman: {system_prompt}\n\nAssistant: Entendido, seguiré esas instrucciones."

        # Formatear los mensajes
        for message in messages:
            role = "Human" if message['role'] == 'user' else "Assistant"
            formatted_prompt += f"\n\n{role}: {message['content']}"

        # Agregar el indicador para la respuesta
        formatted_prompt += "\n\nAssistant:"
        
        return formatted_prompt

    async def check_connection(self) -> bool:
        """
        Verifica la conexión con AWS Bedrock.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            # Intenta listar los modelos disponibles
            self.client.list_foundation_models()
            return True
        except Exception as e:
            logger.error(f"Error al verificar conexión con Bedrock: {e}")
            return False

    async def estimate_tokens(self, text: str) -> int:
        """
        Estima el número de tokens en un texto.
        Esta es una implementación simple, para una estimación más precisa
        se debería usar un tokenizador específico del modelo.
        
        Args:
            text: Texto a analizar
            
        Returns:
            int: Número estimado de tokens
        """
        # Estimación simple: aproximadamente 4 caracteres por token
        return len(text) // 4

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el modelo configurado.
        
        Returns:
            Dict con información del modelo
        """
        try:
            response = self.client.describe_foundation_model(
                modelId=aws_settings.bedrock_model
            )
            return {
                'name': response.get('modelName'),
                'provider': response.get('providerName'),
                'input_modalities': response.get('inputModalities', []),
                'output_modalities': response.get('outputModalities', []),
                'customizations': response.get('customizations', []),
            }
        except Exception as e:
            logger.error(f"Error al obtener información del modelo: {e}")
            raise

    def __del__(self):
        """Limpieza al destruir la instancia."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            logger.error(f"Error al cerrar el cliente de Bedrock: {e}")

# Instancia global del servicio
bedrock_service = BedrockService()
