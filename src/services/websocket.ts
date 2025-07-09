import { Message, WebSocketMessage } from '../types/chat';

export class ChatWebSocket {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private baseURL: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;

  // Event handlers
  public onMessage: ((message: Message) => void) | null = null;
  public onTyping: ((isTyping: boolean, userId?: number) => void) | null = null;
  public onError: ((error: string) => void) | null = null;
  public onConnectionChange: ((connected: boolean) => void) | null = null;

  constructor(sessionId: string, baseURL: string = 'ws://localhost:8000') {
    this.sessionId = sessionId;
    this.baseURL = baseURL.replace('http://', 'ws://').replace('https://', 'wss://');
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
        resolve();
        return;
      }

      this.isConnecting = true;
      const wsURL = `${this.baseURL}/ws/chat/${this.sessionId}/`;
      
      try {
        this.ws = new WebSocket(wsURL);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.onConnectionChange?.(true);
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
            this.onError?.('Failed to parse message');
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          this.onConnectionChange?.(false);
          
          // Attempt to reconnect if not a normal closure
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          this.onError?.('Connection error');
          reject(new Error('WebSocket connection failed'));
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  private handleMessage(data: WebSocketMessage) {
    switch (data.type) {
      case 'message':
        if (data.message) {
          this.onMessage?.(data.message);
        }
        break;
      case 'typing':
        this.onTyping?.(data.is_typing || false, data.user_id);
        break;
      case 'error':
        this.onError?.(data.error || 'Unknown error');
        break;
      default:
        console.warn('Unknown message type:', data);
    }
  }

  private scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect().catch((error) => {
        console.error('Reconnection failed:', error);
      });
    }, delay);
  }

  sendMessage(content: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'message',
        content,
      }));
    } else {
      console.error('WebSocket is not connected');
      this.onError?.('Not connected to chat server');
    }
  }

  sendTyping(isTyping: boolean) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping,
      }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'User disconnected');
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}