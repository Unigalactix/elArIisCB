import { useState, useEffect, useCallback, useRef } from 'react';
import { Message, ChatSession } from '../types/chat';
import { apiService } from '../services/api';
import { ChatWebSocket } from '../services/websocket';

interface UseChatReturn {
  messages: Message[];
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  isConnected: boolean;
  isTyping: boolean;
  isLoading: boolean;
  error: string | null;
  createSession: (title: string) => Promise<ChatSession>;
  selectSession: (sessionId: number) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  endSession: (sessionId: number) => Promise<void>;
  refreshSessions: () => Promise<void>;
  clearError: () => void;
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<ChatWebSocket | null>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Load sessions on mount
  useEffect(() => {
    if (apiService.isAuthenticated()) {
      refreshSessions();
    }
  }, []);

  // WebSocket connection management
  useEffect(() => {
    if (currentSession) {
      connectWebSocket(currentSession.session_id);
    } else {
      disconnectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [currentSession]);

  const connectWebSocket = useCallback(async (sessionId: string) => {
    try {
      disconnectWebSocket();
      
      const ws = new ChatWebSocket(sessionId);
      wsRef.current = ws;

      // Set up event handlers
      ws.onMessage = (message: Message) => {
        setMessages(prev => [...prev, message]);
      };

      ws.onTyping = (typing: boolean) => {
        setIsTyping(typing);
        
        // Clear typing indicator after timeout
        if (typing) {
          if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
          }
          typingTimeoutRef.current = setTimeout(() => {
            setIsTyping(false);
          }, 3000);
        }
      };

      ws.onError = (errorMessage: string) => {
        setError(errorMessage);
      };

      ws.onConnectionChange = (connected: boolean) => {
        setIsConnected(connected);
      };

      await ws.connect();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      setError('Failed to connect to chat server');
    }
  }, []);

  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsTyping(false);
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
  }, []);

  const refreshSessions = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getChatSessions();
      setSessions(response.results);
    } catch (error: any) {
      setError('Failed to load chat sessions');
      console.error('Sessions refresh error:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createSession = useCallback(async (title: string): Promise<ChatSession> => {
    setIsLoading(true);
    try {
      const session = await apiService.createChatSession(title);
      setSessions(prev => [session, ...prev]);
      return session;
    } catch (error: any) {
      const errorMessage = 'Failed to create chat session';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const selectSession = useCallback(async (sessionId: number) => {
    setIsLoading(true);
    try {
      const session = await apiService.getChatSession(sessionId);
      setCurrentSession(session);
      setMessages(session.messages || []);
    } catch (error: any) {
      setError('Failed to load chat session');
      console.error('Session selection error:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!currentSession) {
      setError('No active chat session');
      return;
    }

    try {
      // Send via WebSocket for real-time experience
      if (wsRef.current && wsRef.current.isConnected()) {
        wsRef.current.sendMessage(content);
      } else {
        // Fallback to REST API
        const response = await apiService.sendMessage(currentSession.id, content);
        setMessages(prev => [...prev, response.user_message, response.assistant_message]);
      }
    } catch (error: any) {
      setError('Failed to send message');
      console.error('Send message error:', error);
    }
  }, [currentSession]);

  const endSession = useCallback(async (sessionId: number) => {
    try {
      await apiService.endChatSession(sessionId);
      setSessions(prev => prev.map(session => 
        session.id === sessionId 
          ? { ...session, is_active: false }
          : session
      ));
      
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
        disconnectWebSocket();
      }
    } catch (error: any) {
      setError('Failed to end chat session');
      console.error('End session error:', error);
    }
  }, [currentSession, disconnectWebSocket]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    sessions,
    currentSession,
    isConnected,
    isTyping,
    isLoading,
    error,
    createSession,
    selectSession,
    sendMessage,
    endSession,
    refreshSessions,
    clearError,
  };
};