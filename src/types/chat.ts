export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  employee_id: string;
  department: string;
  position: string;
  phone: string;
  avatar?: string;
  is_hr: boolean;
  is_it_support: boolean;
  created_at: string;
}

export interface Message {
  id: number;
  message_type: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface ChatSession {
  id: number;
  session_id: string;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  messages?: Message[];
  message_count?: number;
  last_message?: Message;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface WebSocketMessage {
  type: 'message' | 'typing' | 'error';
  message?: Message;
  is_typing?: boolean;
  user_id?: number;
  error?: string;
}

export interface SendMessageRequest {
  content: string;
}

export interface SendMessageResponse {
  user_message: Message;
  assistant_message: Message;
}