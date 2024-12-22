import { Message } from '../types';

interface ChatResponse {
  message: string;
  error?: string;
}

export async function sendMessage(messages: Message[]): Promise<ChatResponse> {
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages.map(msg => ({
          role: msg.role as "user" | "assistant",
          content: msg.content
        }))
      }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    return {
      message: '',
      error: 'Failed to send message'
    };
  }
}
