/**
 * API service for communicating with the Medical Guideline Assistant backend
 */

const API_BASE_URL = 'http://localhost:8000';

export interface QueryRequest {
  query: string;
}

export interface Citation {
  guideline_name: string;
  section: string;
  page_number?: number;
  organization: string;
  year: number;
  quote: string;
}

export interface SafetyCheck {
  is_safe: boolean;
  violations: string[];
  requires_disclaimer: boolean;
  refusal_reason?: string;
}

export interface QueryResponse {
  query: string;
  answer: string;
  citations: Citation[];
  confidence_score: number;
  safety_check: SafetyCheck;
  disclaimer: string;
}

export interface SystemStats {
  total_documents: number;
  supported_sources: string[];
  safety_checks_enabled: boolean;
  citations_required: boolean;
}

export interface UploadResponse {
  message: string;
}

export interface HealthResponse {
  status: string;
  system: string;
  version: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `HTTP error! status: ${response.status}`
      );
    }

    return response.json();
  }

  /**
   * Send a query to the medical assistant
   */
  async query(queryText: string): Promise<QueryResponse> {
    return this.request<QueryResponse>('/query', {
      method: 'POST',
      body: JSON.stringify({ query: queryText }),
    });
  }

  /**
   * Upload a medical guideline document
   */
  async uploadGuideline(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload-guideline`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Upload failed! status: ${response.status}`
      );
    }

    return response.json();
  }

  /**
   * Get system statistics
   */
  async getStats(): Promise<SystemStats> {
    return this.request<SystemStats>('/stats');
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  /**
   * Check if the backend is available
   */
  async isBackendAvailable(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }
}

export const apiService = new ApiService();