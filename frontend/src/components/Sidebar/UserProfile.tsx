import { useState } from 'react';
import { 
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon 
} from '@heroicons/react/24/outline';

interface UserProfileProps {
  isExpanded: boolean;
}

/**
 * Componente UserProfile: Muestra la información del usuario y opciones de perfil
 * @param {boolean} isExpanded - Indica si la barra lateral está expandida
 */
const UserProfile = ({ isExpanded }: UserProfileProps) => {
  const [showOptions, setShowOptions] = useState(false);

  // TODO: Obtener datos reales del usuario desde el estado global
  const user = {
    name: 'Usuario',
    email: 'usuario@ejemplo.com',
    avatar: null // URL de avatar cuando esté disponible
  };

  const handleLogout = () => {
    // TODO: Implementar lógica de cierre de sesión
    console.log('Cerrando sesión...');
  };

  const handleSettings = () => {
    // TODO: Implementar navegación a configuración
    console.log('Abriendo configuración...');
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowOptions(!showOptions)}
        className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 
                   transition-colors duration-200 group"
        aria-label="Perfil de usuario"
      >
        {user.avatar ? (
          <img
            src={user.avatar}
            alt="Avatar"
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <UserCircleIcon className="w-8 h-8 text-gray-400" />
        )}
        
        {isExpanded && (
          <div className="flex-1 text-left min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user.name}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {user.email}
            </p>
          </div>
        )}

        {!isExpanded && (
          <span className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white 
                         text-sm rounded opacity-0 group-hover:opacity-100 
                         transition-opacity whitespace-nowrap">
            Perfil de usuario
          </span>
        )}
      </button>

      {/* Menú desplegable de opciones */}
      {showOptions && (
        <div className={`
          absolute bottom-full mb-2 
          ${isExpanded ? 'w-full' : 'left-0 w-48'}
          bg-white rounded-lg shadow-lg border border-gray-100 py-1
          animate-fade-in
        `}>
          <button
            onClick={handleSettings}
            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 
                     hover:bg-gray-50"
          >
            <Cog6ToothIcon className="w-5 h-5" />
            Configuración
          </button>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 
                     hover:bg-gray-50"
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5" />
            Cerrar sesión
          </button>
        </div>
      )}
    </div>
  );
};

export default UserProfile;
