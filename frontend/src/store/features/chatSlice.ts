import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

interface ChatState {
  currentChat: Chat | null;
  chatHistory: Chat[];
  isLoading: boolean;
  error: string | null;
}

const initialState: ChatState = {
  currentChat: null,
  chatHistory: [],
  isLoading: false,
  error: null,
};

/**
 * Slice de Redux para manejar el estado del chat
 * Incluye reducers para todas las operaciones relacionadas con el chat
 */
const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    // Crear un nuevo chat
    createChat: (state) => {
      const newChat: Chat = {
        id: Date.now().toString(),
        title: 'Nuevo Chat',
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      state.currentChat = newChat;
      state.chatHistory.unshift(newChat);
    },

    // Establecer el chat actual
    setCurrentChat: (state, action: PayloadAction<string>) => {
      const chat = state.chatHistory.find(c => c.id === action.payload);
      if (chat) {
        state.currentChat = chat;
      }
    },

    // Añadir un mensaje al chat actual
    addMessage: (state, action: PayloadAction<Omit<Message, 'id' | 'timestamp'>>) => {
      if (state.currentChat) {
        const newMessage: Message = {
          id: Date.now().toString(),
          ...action.payload,
          timestamp: new Date().toISOString(),
        };
        state.currentChat.messages.push(newMessage);
        state.currentChat.updatedAt = new Date().toISOString();
      }
    },

    // Establecer el historial de chat
    setChatHistory: (state, action: PayloadAction<Chat[]>) => {
      state.chatHistory = action.payload;
    },

    // Eliminar un chat
    deleteChat: (state, action: PayloadAction<string>) => {
      state.chatHistory = state.chatHistory.filter(chat => chat.id !== action.payload);
      if (state.currentChat?.id === action.payload) {
        state.currentChat = null;
      }
    },

    // Actualizar el título del chat actual
    updateChatTitle: (state, action: PayloadAction<string>) => {
      if (state.currentChat) {
        state.currentChat.title = action.payload;
        const chatIndex = state.chatHistory.findIndex(c => c.id === state.currentChat?.id);
        if (chatIndex !== -1) {
          state.chatHistory[chatIndex].title = action.payload;
        }
      }
    },

    // Manejar estados de carga
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    // Manejar errores
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },

    // Limpiar el chat actual
    clearCurrentChat: (state) => {
      state.currentChat = null;
    },
  },
});

export const {
  createChat,
  setCurrentChat,
  addMessage,
  setChatHistory,
  deleteChat,
  updateChatTitle,
  setLoading,
  setError,
  clearCurrentChat,
} = chatSlice.actions;

export default chatSlice.reducer;
