import { useDispatch } from 'react-redux';
import { 
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  GlobeAltIcon 
} from '@heroicons/react/24/outline';
import { createChat } from '../../store/features/chatSlice';

/**
 * Componente WelcomeScreen: Pantalla de bienvenida
 * Se muestra cuando no hay un chat activo
 */
const WelcomeScreen = () => {
  const dispatch = useDispatch();

  const features = [
    {
      icon: <ChatBubbleLeftRightIcon className="w-6 h-6" />,
      title: 'Conversación Natural',
      description: 'Interactúa de manera natural y obtén respuestas coherentes y contextuales.'
    },
    {
      icon: <DocumentTextIcon className="w-6 h-6" />,
      title: 'Procesamiento de Archivos',
      description: 'Carga documentos, imágenes y otros archivos para analizarlos.'
    },
    {
      icon: <GlobeAltIcon className="w-6 h-6" />,
      title: 'Búsqueda en Internet',
      description: 'Accede a información actualizada de la web para respuestas más precisas.'
    }
  ];

  return (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center">
        {/* Encabezado */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Hola, soy ISA
          </h1>
          <p className="text-xl text-gray-600">
            ¿En qué puedo ayudarte hoy?
          </p>
        </div>

        {/* Características */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {features.map((feature, index) => (
            <div
              key={index}
              className="p-6 rounded-xl bg-white border border-gray-100 
                       shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center 
                          justify-center text-primary mb-4 mx-auto">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Botón de inicio */}
        <button
          onClick={() => dispatch(createChat())}
          className="btn btn-primary text-lg px-8 py-3 mx-auto"
        >
          Iniciar Nueva Conversación
        </button>
      </div>

      {/* Pie de página */}
      <footer className="mt-auto text-center text-sm text-gray-500">
        Generado por Giroplay
      </footer>
    </div>
  );
};

export default WelcomeScreen;
