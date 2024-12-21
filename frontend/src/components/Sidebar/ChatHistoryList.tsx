import { useState, useEffect } from 'react';
import { ChatBubbleLeftIcon, TrashIcon } from '@heroicons/react/24/outline';

interface ChatHistory {
  id: string;
  title: string;
  date: string;
  preview: string;
}

/**
 * Componente ChatHistoryList: Muestra la lista de chats históricos
 * Permite ver y eliminar conversaciones anteriores
 */
const ChatHistoryList = () => {
  const [chats, setChats] = useState<ChatHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Implementar llamada a API para obtener historial
    // Simulación de datos para desarrollo
    const mockChats: ChatHistory[] = [
      {
        id: '1',
        title: 'Consulta sobre IA',
        date: '2024-02-20',
        preview: '¿Cuáles son las aplicaciones más comunes de la IA?'
      },
      {
        id: '2',
        title: 'Desarrollo Web',
        date: '2024-02-19',
        preview: '¿Cuáles son las mejores prácticas en React?'
      },
      // Más chats de ejemplo...
    ];

    setTimeout(() => {
      setChats(mockChats);
      setLoading(false);
    }, 1000);
  }, []);

  const handleDeleteChat = (id: string) => {
    // TODO: Implementar eliminación real con la API
    setChats(chats.filter(chat => chat.id !== id));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-500 px-2">
        Historial de Chat
      </h3>
      {chats.length === 0 ? (
        <p className="text-sm text-gray-400 px-2">
          No hay conversaciones previas
        </p>
      ) : (
        <ul className="space-y-1">
          {chats.map((chat) => (
            <li 
              key={chat.id}
              className="group px-2 py-2 rounded-lg hover:bg-gray-50 cursor-pointer"
            >
              <div className="flex items-start gap-3">
                <ChatBubbleLeftIcon className="w-5 h-5 text-gray-400 flex-shrink-0 mt-1" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {chat.title}
                    </h4>
                    <span className="text-xs text-gray-500">
                      {new Date(chat.date).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 truncate mt-1">
                    {chat.preview}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteChat(chat.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 
                           rounded transition-opacity"
                  aria-label="Eliminar chat"
                >
                  <TrashIcon className="w-4 h-4 text-gray-400 hover:text-red-500" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ChatHistoryList;
