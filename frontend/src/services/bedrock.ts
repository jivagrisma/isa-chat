import { Message } from '../types';

interface BedrockResponse {
  message: string;
  error?: string;
}

export async function invokeBedrock(messages: Message[]): Promise<BedrockResponse> {
  try {
    const response = await fetch('/api/bedrock/invoke', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ messages })
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
      error: 'Failed to invoke Bedrock'
    };
  }
}
