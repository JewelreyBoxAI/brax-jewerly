import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Loader2, Diamond } from 'lucide-react';
import { BraxChatClient, type ChatResponse, type ThreadMessage } from '../lib/client';

interface ChatWidgetProps {
  apiUrl?: string;
  apiKey?: string;
  position?: 'bottom-right' | 'bottom-left';
  theme?: 'light' | 'dark';
  userId?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  apiUrl = 'http://localhost:8080',
  apiKey,
  position = 'bottom-right',
  theme = 'light',
  userId
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const client = new BraxChatClient(apiUrl, apiKey);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Add welcome message
      const welcomeMessage: Message = {
        id: 'welcome',
        role: 'assistant',
        content: 'Welcome to Brax Fine Jewelers! I\'m here to help you discover the perfect piece of jewelry. How may I assist you today?',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    const loadingMessage: Message = {
      id: 'loading',
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response: ChatResponse = await client.sendMessage({
        message: userMessage.content,
        thread_id: threadId || undefined,
        user_id: userId
      });

      // Update thread ID if this is the first message
      if (!threadId) {
        setThreadId(response.thread_id);
      }

      const assistantMessage: Message = {
        id: response.message_id.toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp)
      };

      setMessages(prev => prev.filter(msg => msg.id !== 'loading').concat([assistantMessage]));

    } catch (err) {
      setError('Sorry, I encountered an error. Please try again.');
      setMessages(prev => prev.filter(msg => msg.id !== 'loading'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const positionClasses = position === 'bottom-right' 
    ? 'bottom-6 right-6' 
    : 'bottom-6 left-6';

  const formatMessage = (content: string) => {
    // Remove lead blocks from display
    return content.replace(/```lead\s*\n.*?\n```/gs, '').trim();
  };

  return (
    <div className={`fixed ${positionClasses} z-50`}>
      {/* Chat Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-yellow-500 hover:bg-yellow-600 text-white rounded-full p-4 shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl"
          aria-label="Open chat"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className={`bg-white rounded-lg shadow-2xl border border-gray-200 w-96 h-96 flex flex-col overflow-hidden animate-in slide-in-from-bottom-4 duration-300 ${theme === 'dark' ? 'bg-gray-800 border-gray-600' : ''}`}>
          {/* Header */}
          <div className="bg-slate-800 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Diamond size={20} className="text-yellow-400" />
              <div>
                <h3 className="font-serif font-semibold text-lg">Brax Concierge</h3>
                <p className="text-xs text-gray-300 opacity-90">Fine Jewelry Specialists</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-yellow-400 transition-colors p-1"
              aria-label="Close chat"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg animate-in slide-in-from-bottom-2 duration-200 ${
                    message.role === 'user'
                      ? 'bg-yellow-500 text-white'
                      : 'bg-white text-gray-800 shadow-sm border'
                  }`}
                >
                  {message.isLoading ? (
                    <div className="flex items-center gap-2">
                      <Loader2 size={16} className="animate-spin" />
                      <span className="text-sm">Thinking...</span>
                    </div>
                  ) : (
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {formatMessage(message.content)}
                    </p>
                  )}
                  {!message.isLoading && (
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  )}
                </div>
              </div>
            ))}
            {error && (
              <div className="flex justify-center">
                <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm">
                  {error}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4 bg-white">
            <div className="flex gap-2 items-end">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about engagement rings, watches, or custom jewelry..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent resize-none"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg p-2 transition-colors"
                aria-label="Send message"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};