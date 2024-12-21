// Tipos para el estado global
export interface RootState {
  chat: ChatState;
  ui: UIState;
}

// Tipos para el chat
export interface ChatState {
  currentChat: Chat | null;
  chatHistory: Chat[];
  isLoading: boolean;
  error: string | null;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  attachments?: Attachment[];
  metadata?: MessageMetadata;
}

export interface Attachment {
  id: string;
  type: 'image' | 'document' | 'audio';
  url: string;
  thumbnailUrl?: string;
  name: string;
  size: number;
  mimeType: string;
  metadata?: {
    width?: number;
    height?: number;
    duration?: number;
    pageCount?: number;
    preview?: string;
  };
  status?: 'uploading' | 'processing' | 'ready' | 'error';
  error?: string;
}

export interface MessageMetadata {
  webSearch?: boolean;
  thinking?: boolean;
  sources?: string[];
  processingTime?: number;
  attachmentProcessing?: boolean;
}

// Tipos para la UI
export interface UIState {
  sidebarExpanded: boolean;
  showChatHistory: boolean;
  theme: 'light' | 'dark';
  isMobile: boolean;
  isLoading: boolean;
  currentModal: string | null;
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Tipos para la API
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

// Tipos para AWS Bedrock
export interface BedrockConfig {
  accessKey: string;
  secretKey: string;
  region: string;
}

export interface BedrockMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface BedrockResponse {
  completion: string;
  stop_reason: string;
  stop_sequence?: string;
}

// Tipos para el servicio de archivos
export interface FileUploadResponse {
  id: string;
  url: string;
  thumbnailUrl?: string;
  name: string;
  size: number;
  mimeType: string;
  metadata?: {
    width?: number;
    height?: number;
    duration?: number;
    pageCount?: number;
  };
}

// Tipos para el servicio de búsqueda web
export interface WebSearchResult {
  title: string;
  url: string;
  snippet: string;
  source: string;
  timestamp?: string;
  score?: number;
}

// Tipos para los eventos de WebSocket
export interface WebSocketEvent {
  type: 'message' | 'typing' | 'error';
  payload: unknown;
}

// Tipos para el contexto de la aplicación
export interface AppConfig {
  API_URL: string;
  WS_URL: string;
  APP_NAME: string;
  APP_VERSION: string;
  MAX_FILE_SIZE: number;
  SUPPORTED_FILE_TYPES: string[];
  MESSAGE_MAX_LENGTH: number;
  TYPING_TIMEOUT: number;
  CHAT_HISTORY_DAYS: number;
}

// Tipos para los hooks personalizados
export interface UseChat {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string, options?: {
    webSearch?: boolean;
    attachments?: File[];
  }) => Promise<void>;
  uploadFile: (file: File) => Promise<void>;
  clearChat: () => void;
}

export interface UseWebSearch {
  results: WebSearchResult[];
  isSearching: boolean;
  error: string | null;
  search: (query: string) => Promise<void>;
}

// Declaraciones para variables de entorno
declare global {
  interface ImportMetaEnv {
    VITE_API_URL: string;
    VITE_WS_URL: string;
    VITE_AWS_ACCESS_KEY: string;
    VITE_AWS_SECRET_KEY: string;
    VITE_AWS_REGION: string;
    VITE_APP_NAME: string;
    VITE_APP_VERSION: string;
    VITE_MAX_FILE_SIZE: string;
    VITE_SUPPORTED_FILE_TYPES: string;
    VITE_MESSAGE_MAX_LENGTH: string;
    VITE_TYPING_TIMEOUT: string;
    VITE_CHAT_HISTORY_DAYS: string;
  }
}
