import React from 'react';

interface ChatHeaderProps {
  title: string;
  subtitle?: string;
  updatedAt?: string;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({ title, subtitle, updatedAt }) => {
  return (
    <div className="chat-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <p className="subtitle">{subtitle}</p>}
      </div>
      {updatedAt && <span className="updated-at">{updatedAt}</span>}
    </div>
  );
};

export default ChatHeader;
