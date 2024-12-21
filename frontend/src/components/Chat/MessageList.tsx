import { useEffect, useRef } from 'react';
import { CheckIcon, ClockIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

/**
 * Componente MessageList: Lista de mensajes del chat
 * Muestra los mensajes del usuario y del asistente
 */
const MessageList = ({ messages, isLoading }: MessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll automático al último mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="h-full overflow-y-auto px-4 py-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`
                message-bubble
                ${message.role === 'user' ? 'message-user' : 'message-assistant'}
                max-w-[80%]
              `}
            >
              {/* Contenido del mensaje con soporte para Markdown */}
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>

              {/* Metadatos del mensaje */}
              <div
                className={`
                  flex items-center gap-1 mt-2 text-xs
                  ${message.role === 'user' ? 'text-white/80' : 'text-gray-400'}
                `}
              >
                <span>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
                {message.role === 'user' && (
                  <CheckIcon className="w-4 h-4" />
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Indicador de escritura */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="message-bubble message-assistant">
              <div className="flex items-center gap-2">
                <ClockIcon className="w-5 h-5 text-gray-400 animate-spin" />
                <span className="text-gray-500">ISA está escribiendo...</span>
              </div>
            </div>
          </div>
        )}

        {/* Elemento para scroll automático */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;
