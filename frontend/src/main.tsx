import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import './index.css';

/**
 * Punto de entrada de la aplicación
 * Configura el Provider de Redux y el tema inicial
 */
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);

// Configurar el tema inicial basado en las preferencias del sistema
const setInitialTheme = () => {
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
  }
};

// Escuchar cambios en el tema del sistema
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
});

// Configurar el tema inicial al cargar la aplicación
setInitialTheme();

// Registrar service worker para PWA (opcional, para futura implementación)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((error) => {
      console.error('Error al registrar el service worker:', error);
    });
  });
}

// Manejar errores no capturados
window.addEventListener('unhandledrejection', (event) => {
  console.error('Error no manejado:', event.reason);
  // TODO: Enviar error a un servicio de monitoreo
});

// Configurar variables de entorno
declare global {
  interface Window {
    ENV: {
      API_URL: string;
      WS_URL: string;
    };
  }
}

// Valores por defecto para desarrollo
window.ENV = {
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
};
