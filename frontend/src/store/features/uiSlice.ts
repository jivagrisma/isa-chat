import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  sidebarExpanded: boolean;
  showChatHistory: boolean;
  theme: 'light' | 'dark';
  isMobile: boolean;
  isLoading: boolean;
  currentModal: string | null;
  notifications: {
    id: string;
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
  }[];
}

const initialState: UIState = {
  sidebarExpanded: false,
  showChatHistory: false,
  theme: 'light',
  isMobile: window.innerWidth < 768,
  isLoading: false,
  currentModal: null,
  notifications: [],
};

/**
 * Slice de Redux para manejar el estado de la interfaz de usuario
 * Controla la apariencia y comportamiento de la UI
 */
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Control de la barra lateral
    toggleSidebar: (state) => {
      state.sidebarExpanded = !state.sidebarExpanded;
    },
    setSidebarExpanded: (state, action: PayloadAction<boolean>) => {
      state.sidebarExpanded = action.payload;
    },

    // Control del historial de chat
    toggleChatHistory: (state) => {
      state.showChatHistory = !state.showChatHistory;
    },
    setChatHistoryVisible: (state, action: PayloadAction<boolean>) => {
      state.showChatHistory = action.payload;
    },

    // Control del tema
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
      // Actualizar el atributo data-theme en el HTML
      document.documentElement.setAttribute('data-theme', action.payload);
    },

    // Control de responsive
    setIsMobile: (state, action: PayloadAction<boolean>) => {
      state.isMobile = action.payload;
      // Si es móvil, cerrar la barra lateral automáticamente
      if (action.payload && state.sidebarExpanded) {
        state.sidebarExpanded = false;
      }
    },

    // Control de modales
    openModal: (state, action: PayloadAction<string>) => {
      state.currentModal = action.payload;
    },
    closeModal: (state) => {
      state.currentModal = null;
    },

    // Control de notificaciones
    addNotification: (state, action: PayloadAction<{
      type: 'success' | 'error' | 'info' | 'warning';
      message: string;
    }>) => {
      const id = Date.now().toString();
      state.notifications.push({
        id,
        ...action.payload
      });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        notification => notification.id !== action.payload
      );
    },

    // Control de estado de carga
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const {
  toggleSidebar,
  setSidebarExpanded,
  toggleChatHistory,
  setChatHistoryVisible,
  setTheme,
  setIsMobile,
  openModal,
  closeModal,
  addNotification,
  removeNotification,
  setLoading,
} = uiSlice.actions;

export default uiSlice.reducer;
