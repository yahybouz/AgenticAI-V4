import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  Agent,
  CreateAgentRequest,
  Document,
  SearchRequest,
  SearchResponse,
  UserStats,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/auth/login', data);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/auth/register', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/auth/me');
    return response.data;
  }

  async getUserStats(): Promise<UserStats> {
    const response = await this.client.get<UserStats>('/api/auth/stats');
    return response.data;
  }

  async generateApiKey(): Promise<{ api_key: string }> {
    const response = await this.client.post<{ api_key: string }>('/api/auth/api-key');
    return response.data;
  }

  // Agent endpoints
  async getAgents(): Promise<Agent[]> {
    const response = await this.client.get<Agent[]>('/api/agents/');
    return response.data;
  }

  async getAgent(id: string): Promise<Agent> {
    const response = await this.client.get<Agent>(`/api/agents/${id}`);
    return response.data;
  }

  async createAgent(data: CreateAgentRequest): Promise<Agent> {
    const response = await this.client.post<Agent>('/api/agents/', data);
    return response.data;
  }

  async deleteAgent(id: string): Promise<void> {
    await this.client.delete(`/api/agents/${id}`);
  }

  // Document endpoints
  async getDocuments(collectionName?: string): Promise<Document[]> {
    const params = collectionName ? { collection_name: collectionName } : {};
    const response = await this.client.get<Document[]>('/api/documents/', { params });
    return response.data;
  }

  async uploadDocument(file: File, collectionName: string = 'documents'): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('collection_name', collectionName);

    const response = await this.client.post<Document>('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async searchDocuments(data: SearchRequest): Promise<SearchResponse> {
    const response = await this.client.post<SearchResponse>('/api/documents/search', data);
    return response.data;
  }

  async deleteDocument(documentId: string): Promise<void> {
    await this.client.delete(`/api/documents/${documentId}`);
  }

  // System info
  async getSystemInfo(): Promise<any> {
    const response = await this.client.get('/info');
    return response.data;
  }

  async getHealthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new ApiService();
