// User types
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  role: 'ADMIN' | 'USER' | 'GUEST';
  status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';
  created_at: string;
  updated_at: string;
  last_login?: string;
  max_agents: number;
  max_documents: number;
  max_storage_mb: number;
  default_model?: string;
  language?: string;
  timezone?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// Agent types
export interface Agent {
  id: string;
  name: string;
  domain: string;
  skills: string[];
  description: string;
  input_schema: Record<string, any>;
  output_schema: Record<string, any>;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  is_active: boolean;
  created_at: string;
}

export interface CreateAgentRequest {
  name: string;
  domain: string;
  skills: string[];
  description: string;
  input_schema?: Record<string, any>;
  output_schema?: Record<string, any>;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
}

// Document types
export interface Document {
  id: string;
  filename: string;
  collection_name: string;
  file_size: number;
  file_type: string;
  chunks_count: number;
  uploaded_at: string;
  metadata?: Record<string, any>;
}

export interface SearchRequest {
  query: string;
  collection_name?: string;
  top_k?: number;
  enable_reranking?: boolean;
  filters?: Record<string, any>;
}

export interface SearchResult {
  content: string;
  score: float;
  metadata: Record<string, any>;
  document_id?: string;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total_found: number;
  search_time_ms: number;
  reranked?: boolean;
}

// Chat types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  agent_id?: string;
}

export interface ChatRequest {
  message: string;
  agent_id?: string;
  context?: Record<string, any>;
}

// Stats types
export interface UserStats {
  agents_count: number;
  documents_count: number;
  storage_used_mb: number;
  total_queries: number;
  last_activity?: string;
}
