import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setIsMobile } from './store/features/uiSlice';
import { RootState } from './store';
import Sidebar from './components/Sidebar/Sidebar';
import ChatArea from './components/Chat/ChatArea';
import Notifications from './components/common/Notifications';

/**
 * Componente principal de la aplicación
 * Maneja el layout principal y la lógica de responsive
 */
const App = () => {
  const dispatch = useDispatch();
  const { sidebarExpanded } = useSelector((state: RootState) => state.ui);

  // Manejar cambios de tamaño de ventana
  useEffect(() => {
    const handleResize = () => {
      dispatch(setIsMobile(window.innerWidth < 768));
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Verificar tamaño inicial

    return () => window.removeEventListener('resize', handleResize);
  }, [dispatch]);

  return (
    <div className="h-screen flex overflow-hidden bg-background">
      {/* Barra lateral */}
      <Sidebar />

      {/* Área principal */}
      <main 
        className={`
          flex-1 relative transition-all duration-300
          ${sidebarExpanded ? 'ml-sidebar-expanded' : 'ml-sidebar'}
        `}
      >
        <ChatArea />
      </main>

      {/* Sistema de notificaciones */}
      <Notifications />
    </div>
  );
};

export default App;
