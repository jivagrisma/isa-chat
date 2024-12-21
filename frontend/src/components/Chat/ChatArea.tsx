import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import ChatHeader from './ChatHeader';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import WelcomeScreen from './WelcomeScreen';

/**
 * Componente ChatArea: Área principal del chat
 * Maneja la visualización de mensajes y la entrada de texto
 */
const ChatArea = () => {
  const currentChat = useSelector((state: RootState) => state.chat.currentChat);
  const isLoading = useSelector((state: RootState) => state.chat.isLoading);

  return (
    <div className="h-full flex flex-col">
      {currentChat ? (
        <>
          <ChatHeader 
            title={currentChat.title}
            updatedAt={currentChat.updatedAt}
          />
          
          <div className="flex-1 overflow-hidden">
            <MessageList 
              messages={currentChat.messages}
              isLoading={isLoading}
            />
          </div>

          <ChatInput />
        </>
      ) : (
        <WelcomeScreen />
      )}
    </div>
  );
};

export default ChatArea;
