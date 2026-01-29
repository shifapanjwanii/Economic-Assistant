import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Send, User, Bot, TrendingUp, AlertCircle, Settings, BarChart3, Trash2 } from 'lucide-react';
import ProfileModal from './ProfileModal';
import Dashboard from './Dashboard';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [userId] = useState('default_user');
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [hasProfile, setHasProfile] = useState(false);
  const [currentView, setCurrentView] = useState('chat'); // 'chat' or 'dashboard'
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load conversation history on mount
    loadHistory();
    checkProfile();
  }, []);

  const checkProfile = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/users/${userId}/profile`);
      setHasProfile(true);
    } catch (error) {
      setHasProfile(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/users/${userId}/history`);
      const history = response.data.conversations;
      
      // Convert history to message format
      const formattedMessages = history.map(conv => ({
        role: conv.role,
        content: conv.message,
        tools_used: conv.tools_used,
        timestamp: conv.timestamp
      }));
      
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        user_id: userId,
        message: input
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        tools_used: response.data.tools_used,
        iterations: response.data.iterations,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please make sure the backend server is running and API keys are configured.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = async () => {
    if (window.confirm('Are you sure you want to clear all messages? This cannot be undone.')) {
      try {
        await axios.delete(`${API_BASE_URL}/api/users/${userId}/history`);
        setMessages([]);
      } catch (error) {
        console.error('Failed to clear chat:', error);
        alert('Failed to clear chat history');
      }
    }
  };

  const suggestedQuestions = [
    "Is now a good time to save or pay down debt?",
    "How does current inflation affect my purchasing power?",
    "What recent economic news should influence my spending decisions?",
    "Should I be worried about the current unemployment rate?"
  ];

  const handleSuggestedQuestion = (question) => {
    setInput(question);
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <TrendingUp size={32} className="header-icon" />
          <div>
            <h1>Pulse</h1>
            <p>Read between the rates</p>
          </div>
        </div>
        
        <div className="header-right">
          <nav className="view-toggle">
            <button 
              className={`nav-button ${currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('dashboard')}
              title="View economic dashboard"
            >
              <BarChart3 size={18} />
              Dashboard
            </button>
            <button 
              className={`nav-button ${currentView === 'chat' ? 'active' : ''}`}
              onClick={() => setCurrentView('chat')}
              title="Chat with economic advisor"
            >
              <Bot size={18} />
              Chat
            </button>
          </nav>

          <button 
            className="profile-button"
            onClick={() => setIsProfileModalOpen(true)}
            title="Manage your financial profile"
          >
            <Settings size={20} />
            {hasProfile ? 'Edit Profile' : 'Set Up Profile'}
          </button>
        </div>
      </header>

      {currentView === 'dashboard' ? (
        <Dashboard />
      ) : (
        <div className="chat-container">
          {messages.length > 0 && (
            <div className="chat-header">
              <button 
                className="clear-chat-button"
                onClick={clearChat}
                title="Clear all messages"
              >
                <Trash2 size={18} />
                Clear Chat
              </button>
            </div>
          )}
          <div className="messages-container">
            {messages.length === 0 && (
              <div className="welcome-message">
                <h2>Welcome to Pulse</h2>
                <p>Ask me about inflation, interest rates, economic news, or get personalized financial guidance based on current macroeconomic conditions.</p>
                
                <div className="suggested-questions">
                  <h3>Try asking:</h3>
                  {suggestedQuestions.map((question, idx) => (
                    <button
                      key={idx}
                      className="suggested-question"
                      onClick={() => handleSuggestedQuestion(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.role} ${message.isError ? 'error' : ''}`}
              >
                <div className="message-icon">
                  {message.role === 'user' ? (
                    <User size={20} />
                  ) : message.isError ? (
                    <AlertCircle size={20} />
                  ) : (
                    <Bot size={20} />
                  )}
                </div>
                
                <div className="message-content">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                  
                  {message.tools_used && message.tools_used.length > 0 && (
                    <div className="tools-used">
                      <span className="tools-label">Data sources:</span>
                      {message.tools_used.map((tool, idx) => (
                        <span key={idx} className="tool-badge">
                          {tool.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  <div className="message-timestamp">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="message assistant loading">
                <div className="message-icon">
                  <Bot size={20} />
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <p className="loading-text">Analyzing economic data...</p>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="input-container">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about economic conditions, inflation, interest rates, or get financial guidance..."
              disabled={loading}
              rows={1}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="send-button"
            >
              <Send size={20} />
            </button>
          </div>

          <footer className="app-footer">
            <p>
              Data from FRED, NewsAPI, and Exchange Rate APIs
            </p>
          </footer>
        </div>
      )}

      <ProfileModal
        userId={userId}
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
        onSave={() => {
          checkProfile();
          // Clear conversation to use updated profile context
          setMessages([]);
          // Add a system message
          setTimeout(() => {
            setMessages([{
              role: 'assistant',
              content: 'Your profile has been updated! I\'ll now provide personalized recommendations based on your new information. Feel free to ask me anything.',
              timestamp: new Date().toISOString()
            }]);
          }, 100);
        }}
      />
    </div>
  );
}

export default App;
