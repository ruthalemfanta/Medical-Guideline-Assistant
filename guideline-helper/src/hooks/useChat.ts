import { useState, useCallback } from 'react';
import { apiService, QueryResponse } from '@/services/api';
import { toast } from '@/hooks/use-toast';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  confidence?: number;
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  isBackendAvailable: boolean;
}

export const useChat = () => {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    isBackendAvailable: false,
  });

  // Check backend availability
  const checkBackend = useCallback(async () => {
    try {
      const available = await apiService.isBackendAvailable();
      setState(prev => ({ ...prev, isBackendAvailable: available }));
      return available;
    } catch (error) {
      setState(prev => ({ ...prev, isBackendAvailable: false }));
      return false;
    }
  }, []);

  // Send a message
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
    }));

    try {
      // Check if backend is available
      const backendAvailable = await checkBackend();
      
      if (!backendAvailable) {
        throw new Error('Backend service is not available. Please make sure the Python server is running on http://localhost:8000');
      }

      // Send query to backend
      const response: QueryResponse = await apiService.query(content.trim());

      // Create assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        sources: response.citations
          .filter(citation => citation.guideline_name)
          .map(citation => {
            const source = citation.guideline_name || 'Unknown Source';
            return citation.page_number 
              ? `${source} (Page ${citation.page_number})`
              : source;
          }),
        confidence: response.confidence_score,
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));

      // Show warning if confidence is low
      if (response.confidence_score < 0.5) {
        toast({
          title: "Low Confidence Response",
          description: "The response has low confidence. Please verify the information.",
          variant: "destructive",
        });
      }

      // Show safety warnings if any
      if (!response.safety_check.is_safe) {
        toast({
          title: "Safety Check Failed",
          description: response.safety_check.refusal_reason || "The query was flagged for safety reasons.",
          variant: "destructive",
        });
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please make sure the backend server is running and try again.`,
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isLoading: false,
      }));

      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send message",
        variant: "destructive",
      });
    }
  }, [checkBackend]);

  // Clear chat
  const clearChat = useCallback(() => {
    setState(prev => ({
      ...prev,
      messages: [],
    }));
  }, []);

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    isBackendAvailable: state.isBackendAvailable,
    sendMessage,
    clearChat,
    checkBackend,
  };
};