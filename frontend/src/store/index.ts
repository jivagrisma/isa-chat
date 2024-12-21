import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './features/chatSlice';
import uiReducer from './features/uiSlice';

/**
 * Store principal de Redux
 * Combina todos los reducers y configura el middleware
 */
export const store = configureStore({
  reducer: {
    chat: chatReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignorar acciones no serializables específicas si es necesario
        ignoredActions: ['chat/setSocket'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
