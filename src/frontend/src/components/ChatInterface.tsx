/**
 * Chat Interface Component
 * 
 * Conversational UI component for chatbot interactions.
 * Displays messages and handles user input.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import './ChatInterface.css';
import Button from './Button';

interface Message {
  id: string;
  role: 'user' | 'bot' | 'system';
  content: string;
  message_type?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

interface ChatInterfaceProps {
  sessionId: string | null;
  messages: Message[];
  onSendMessage: (message: string) => void;
  onFileUpload?: (file: File) => void;
  loading?: boolean;
  disabled?: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionId: _sessionId, // Reserved for future use
  messages,
  onSendMessage,
  onFileUpload,
  loading = false,
  disabled = false
}) => {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || disabled || loading) {
      return;
    }

    onSendMessage(inputValue.trim());
    setInputValue('');
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileUpload) {
      onFileUpload(file);
    }
    // Reset input to allow selecting same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-interface">
      {/* Messages Container */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <p>{t('chatbot.welcome_message', 'Welcome! Start the conversation by typing a message.')}</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.id}-${index}`}
              className={`chat-message chat-message--${message.role}`}
            >
              <div className="chat-message__content">
                <div className="chat-message__text">
                  {message.content.split('\n').map((line, idx) => (
                    <React.Fragment key={idx}>
                      {line}
                      {idx < message.content.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </div>
                <div className="chat-message__meta">
                  <span className="chat-message__time">
                    {formatTime(message.created_at)}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="chat-message chat-message--bot">
            <div className="chat-message__content">
              <div className="chat-message__text">
                <div className="chat-typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Container */}
      <form className="chat-input-container" onSubmit={handleSubmit}>
        <div className="chat-input-wrapper">
          {onFileUpload && (
            <button
              type="button"
              className="chat-file-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled || loading}
              title={t('chatbot.upload_file', 'Upload file')}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </button>
          )}
          
          <input
            ref={fileInputRef}
            type="file"
            className="chat-file-input"
            onChange={handleFileSelect}
            accept=".pdf,.docx"
            style={{ display: 'none' }}
          />
          
          <textarea
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={t('chatbot.input_placeholder', 'Type your message...')}
            disabled={disabled || loading}
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          
          <Button
            type="submit"
            disabled={!inputValue.trim() || disabled || loading}
            className="chat-send-button"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;

