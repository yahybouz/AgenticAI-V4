import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import type { Message } from '../types';

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Bonjour ! Je suis votre assistant AgenticAI. Comment puis-je vous aider aujourd\'hui ?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const history = await api.getChatHistory();
      if (history && history.length > 0) {
        setMessages(history);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      // Keep default welcome message if history fails
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('Êtes-vous sûr de vouloir effacer tout l\'historique de chat ?')) return;

    try {
      await api.clearChatHistory();
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: 'Bonjour ! Je suis votre assistant AgenticAI. Comment puis-je vous aider aujourd\'hui ?',
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.error('Error clearing chat history:', error);
      alert('Erreur lors de la suppression de l\'historique');
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsTyping(true);

    // Create a placeholder message for streaming
    const aiMessageId = (Date.now() + 1).toString();
    const placeholderMessage: Message = {
      id: aiMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    };

    if (useStreaming) {
      // Streaming mode
      setMessages((prev) => [...prev, placeholderMessage]);

      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/chat/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ content: currentInput, context: {} }),
        });

        if (!response.ok) throw new Error('Stream failed');

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let accumulatedContent = '';

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  if (data.content) {
                    accumulatedContent += data.content;
                    // Update the message in real-time
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMessageId
                          ? { ...msg, content: accumulatedContent }
                          : msg
                      )
                    );
                  }
                  if (data.done) {
                    break;
                  }
                } catch (e) {
                  // Ignore JSON parse errors
                }
              }
            }
          }
        }
      } catch (error) {
        console.error('Error streaming message:', error);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === aiMessageId
              ? {
                  ...msg,
                  content: 'Désolé, une erreur est survenue lors du streaming. Veuillez réessayer.',
                }
              : msg
          )
        );
      } finally {
        setIsTyping(false);
      }
    } else {
      // Non-streaming mode (original)
      try {
        const response = await api.sendChatMessage(currentInput);

        const aiMessage: Message = {
          id: aiMessageId,
          role: 'assistant',
          content: response.message,
          timestamp: response.timestamp,
        };

        setMessages((prev) => [...prev, aiMessage]);
      } catch (error) {
        console.error('Error sending message:', error);

        const errorMessage: Message = {
          id: aiMessageId,
          role: 'assistant',
          content: 'Désolé, une erreur est survenue lors du traitement de votre message. Veuillez réessayer.',
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsTyping(false);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Chat</h1>
          <p className="text-gray-600">
            Interagissez avec vos agents intelligents
          </p>
        </div>
        <button
          onClick={handleClearHistory}
          className="btn btn-secondary flex items-center gap-2"
          title="Effacer l'historique"
        >
          <Trash2 className="w-4 h-4" />
          Effacer l'historique
        </button>
      </div>

      {/* Chat Container */}
      <div className="card h-[calc(100vh-16rem)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'user'
                    ? 'bg-primary-100'
                    : 'bg-gray-100'
                }`}
              >
                {message.role === 'user' ? (
                  <User className="w-5 h-5 text-primary-700" />
                ) : (
                  <Bot className="w-5 h-5 text-gray-700" />
                )}
              </div>
              <div
                className={`flex-1 max-w-2xl ${
                  message.role === 'user' ? 'text-right' : 'text-left'
                }`}
              >
                <div
                  className={`inline-block px-4 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString('fr-FR', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-gray-700" />
              </div>
              <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Tapez votre message..."
              className="input flex-1"
              disabled={isTyping}
            />
            <button
              type="submit"
              disabled={isTyping || !inputMessage.trim()}
              className="btn btn-primary"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
          <div className="flex items-center justify-between mt-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useStreaming}
                onChange={(e) => setUseStreaming(e.target.checked)}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <span className="text-xs text-gray-600">Streaming activé</span>
            </label>
            <p className="text-xs text-gray-500">
              Propulsé par AgenticAI - Orchestrateur multi-agents intelligent
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
