import { useDispatch } from 'react-redux';
import { 
  ShareIcon, 
  DocumentDuplicateIcon,
  EllipsisHorizontalIcon 
} from '@heroicons/react/24/outline';
import { useState } from 'react';

interface ChatHeaderProps {
  title: string;
  updatedAt: string;
}

/**
 * Componente ChatHeader: Encabezado del área de chat
 * Muestra el título del chat y opciones adicionales
 */
const ChatHeader = ({ title, updatedAt }: ChatHeaderProps) => {
  const dispatch = useDispatch();
  const [showOptions, setShowOptions] = useState(false);

  const handleCopyChat = async () => {
    try {
      await navigator.clipboard.writeText(title);
      // TODO: Mostrar notificación de éxito
    } catch (error) {
      console.error('Error al copiar:', error);
      // TODO: Mostrar notificación de error
    }
  };

  const handleShare = () => {
    // TODO: Implementar funcionalidad de compartir
    console.log('Compartir chat');
  };

  return (
    <header className="border-b border-gray-200 bg-white px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            {title}
          </h1>
          <p className="text-sm text-gray-500">
            Última actualización: {new Date(updatedAt).toLocaleString()}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyChat}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 
                     rounded-lg transition-colors"
            title="Copiar chat"
          >
            <DocumentDuplicateIcon className="w-5 h-5" />
          </button>

          <button
            onClick={handleShare}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 
                     rounded-lg transition-colors"
            title="Compartir chat"
          >
            <ShareIcon className="w-5 h-5" />
          </button>

          <div className="relative">
            <button
              onClick={() => setShowOptions(!showOptions)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 
                       rounded-lg transition-colors"
              title="Más opciones"
            >
              <EllipsisHorizontalIcon className="w-5 h-5" />
            </button>

            {showOptions && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg 
                            border border-gray-100 py-1 z-10">
                <button
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 
                           hover:bg-gray-50"
                  onClick={() => {
                    // TODO: Implementar renombrar chat
                    console.log('Renombrar chat');
                  }}
                >
                  Renombrar chat
                </button>
                <button
                  className="w-full px-4 py-2 text-left text-sm text-red-600 
                           hover:bg-gray-50"
                  onClick={() => {
                    // TODO: Implementar eliminar chat
                    console.log('Eliminar chat');
                  }}
                >
                  Eliminar chat
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default ChatHeader;
