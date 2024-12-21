import { useState } from 'react';
import { 
  ChatBubbleLeftIcon,
  PlusCircleIcon,
  ChevronRightIcon,
  ChevronLeftIcon 
} from '@heroicons/react/24/outline';
import ChatHistoryList from './ChatHistoryList';
import UserProfile from './UserProfile';

/**
 * Componente Sidebar: Barra lateral principal de la aplicación
 * Maneja la expansión/contracción y muestra la lista de chats
 */
const Sidebar = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const toggleSidebar = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setShowHistory(true);
    }
  };

  const handleNewChat = () => {
    // TODO: Implementar lógica para nuevo chat
    console.log('Nuevo chat iniciado');
  };

  return (
    <aside 
      className={`
        fixed left-0 top-0 h-full bg-white shadow-lg transition-all duration-300
        ${isExpanded ? 'w-sidebar-expanded' : 'w-sidebar'}
        flex flex-col items-center gap-4 p-4 z-50
      `}
    >
      {/* Logo */}
      <div className="w-10 h-10">
        <img 
          src="/assets/logo.svg" 
          alt="ISA Logo" 
          className="w-full h-full"
        />
      </div>

      {/* Botones principales */}
      <div className="flex flex-col gap-4">
        <button
          onClick={toggleSidebar}
          className="sidebar-icon group relative"
          aria-label={isExpanded ? 'Contraer barra lateral' : 'Expandir barra lateral'}
        >
          {isExpanded ? (
            <ChevronLeftIcon className="w-6 h-6" />
          ) : (
            <ChevronRightIcon className="w-6 h-6" />
          )}
          {!isExpanded && (
            <span className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-sm 
                           rounded opacity-0 group-hover:opacity-100 transition-opacity">
              {isExpanded ? 'Contraer' : 'Expandir'}
            </span>
          )}
        </button>

        <button
          onClick={handleNewChat}
          className="sidebar-icon group relative"
          aria-label="Nuevo chat"
        >
          <PlusCircleIcon className="w-6 h-6" />
          {!isExpanded && (
            <span className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-sm 
                           rounded opacity-0 group-hover:opacity-100 transition-opacity">
              Nuevo chat
            </span>
          )}
        </button>

        <button
          onClick={() => setShowHistory(!showHistory)}
          className="sidebar-icon group relative"
          aria-label="Historial de chat"
        >
          <ChatBubbleLeftIcon className="w-6 h-6" />
          {!isExpanded && (
            <span className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-sm 
                           rounded opacity-0 group-hover:opacity-100 transition-opacity">
              Historial
            </span>
          )}
        </button>
      </div>

      {/* Lista de chats (visible solo cuando está expandido) */}
      {isExpanded && showHistory && (
        <div className="flex-1 w-full overflow-y-auto mt-4">
          <ChatHistoryList />
        </div>
      )}

      {/* Perfil de usuario */}
      <div className="mt-auto">
        <UserProfile isExpanded={isExpanded} />
      </div>
    </aside>
  );
};

export default Sidebar;
