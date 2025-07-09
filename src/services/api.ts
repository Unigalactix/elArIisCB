import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  ChatSession, 
  Message, 
  AuthResponse, 
  SendMessageRequest, 
  SendMessageResponse 
} from '../types/chat';

class APIService {
  private api: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage
    this.token = localStorage.getItem('auth_token');
    if (this.token) {
      this.setAuthToken(this.token);
    }

    // Request interceptor to add auth token
    this.api.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Token ${this.token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  private setAuthToken(token: string) {
    this.token = token;
    this.api.defaults.headers.common['Authorization'] = `Token ${token}`;
    localStorage.setItem('auth_token', token);
  }

  private removeAuthToken() {
    this.token = null;
    delete this.api.defaults.headers.common['Authorization'];
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  // Authentication methods
  async login(username: string, password: string): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.api.post('/api/v1/auth/login/', {
      username,
      password,
    });
    
    const { token, user } = response.data;
    this.setAuthToken(token);
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    employee_id?: string;
    department?: string;
    position?: string;
  }): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.api.post('/api/v1/auth/register/', userData);
    
    const { token, user } = response.data;
    this.setAuthToken(token);
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/api/v1/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.removeAuthToken();
    }
  }

  async getProfile(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/api/v1/auth/profile/');
    return response.data;
  }

  // Chat session methods
  async getChatSessions(): Promise<{ results: ChatSession[]; count: number }> {
    const response = await this.api.get('/api/v1/chat/sessions/');
    return response.data;
  }

  async createChatSession(title: string): Promise<ChatSession> {
    const response: AxiosResponse<ChatSession> = await this.api.post('/api/v1/chat/sessions/', {
      title,
    });
    return response.data;
  }

  async getChatSession(sessionId: number): Promise<ChatSession> {
    const response: AxiosResponse<ChatSession> = await this.api.get(`/api/v1/chat/sessions/${sessionId}/`);
    return response.data;
  }

  async sendMessage(sessionId: number, content: string): Promise<SendMessageResponse> {
    const response: AxiosResponse<SendMessageResponse> = await this.api.post(
      `/api/v1/chat/sessions/${sessionId}/send_message/`,
      { content }
    );
    return response.data;
  }

  async getSessionMessages(sessionId: number): Promise<Message[]> {
    const response: AxiosResponse<Message[]> = await this.api.get(
      `/api/v1/chat/sessions/${sessionId}/messages/`
    );
    return response.data;
  }

  async endChatSession(sessionId: number): Promise<void> {
    await this.api.post(`/api/v1/chat/sessions/${sessionId}/end_session/`);
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.token;
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  getAuthToken(): string | null {
    return this.token;
  }
}

export const apiService = new APIService();
export default APIService;