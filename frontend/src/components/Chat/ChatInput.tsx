import { useState, useRef, FormEvent } from 'react';
import { useDispatch } from 'react-redux';
import { 
  PaperAirplaneIcon, 
  PaperClipIcon,
  MicrophoneIcon,
  MagnifyingGlassIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { addMessage } from '../../store/features/chatSlice';

/**
 * Componente ChatInput: Área de entrada de mensajes
 * Maneja la entrada de texto y las acciones de envío
 */
const ChatInput = () => {
  const dispatch = useDispatch();
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Manejar envío de mensaje
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    dispatch(addMessage({
      content: message.trim(),
      role: 'user'
    }));
    setMessage('');
  };

  // Manejar carga de archivos
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;

    try {
      setIsUploading(true);
      // TODO: Implementar lógica de carga de archivos
      console.log('Archivos seleccionados:', files);
    } catch (error) {
      console.error('Error al cargar archivos:', error);
    } finally {
      setIsUploading(false);
    }
  };

  // Manejar grabación de voz
  const handleVoiceRecord = () => {
    setIsRecording(!isRecording);
    // TODO: Implementar lógica de grabación de voz
    console.log('Grabación de voz:', !isRecording);
  };

  // Manejar búsqueda web
  const handleWebSearch = () => {
    // TODO: Implementar lógica de búsqueda web
    console.log('Iniciando búsqueda web');
  };

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-4">
      <div className="max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Botones de acción superiores */}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleWebSearch}
              className="btn btn-secondary"
              title="Buscar en la web"
            >
              <MagnifyingGlassIcon className="w-5 h-5" />
              <span>Buscar</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              title="Modo pensamiento"
            >
              <SparklesIcon className="w-5 h-5" />
              <span>Pensar</span>
            </button>
          </div>

          {/* Área de entrada de mensaje */}
          <div className="relative flex items-end gap-2">
            <div className="flex-1 min-w-0">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Escribe un mensaje a ISA..."
                className="w-full resize-none rounded-lg border border-gray-200 
                         px-4 py-3 focus:outline-none focus:ring-2 
                         focus:ring-primary/50 min-h-[60px]"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />
            </div>

            {/* Botones de acción */}
            <div className="flex gap-2">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                className="hidden"
                multiple
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="btn btn-secondary"
                disabled={isUploading}
                title="Adjuntar archivo"
              >
                <PaperClipIcon className="w-5 h-5" />
              </button>

              <button
                type="button"
                onClick={handleVoiceRecord}
                className={`btn ${isRecording ? 'btn-primary' : 'btn-secondary'}`}
                title="Grabar mensaje de voz"
              >
                <MicrophoneIcon className="w-5 h-5" />
              </button>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={!message.trim()}
                title="Enviar mensaje"
              >
                <PaperAirplaneIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInput;
