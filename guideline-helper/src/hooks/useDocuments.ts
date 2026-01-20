import { useState, useCallback } from 'react';
import { apiService, SystemStats } from '@/services/api';
import { toast } from '@/hooks/use-toast';

export interface Document {
  id: string;
  name: string;
  size: string;
  uploadedAt: Date;
  status: 'uploading' | 'uploaded' | 'error';
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

export const useDocuments = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load system stats
  const loadStats = useCallback(async () => {
    try {
      const systemStats = await apiService.getStats();
      setStats(systemStats);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  }, []);

  // Upload a document
  const uploadDocument = useCallback(async (file: File) => {
    if (!file.type.includes('pdf')) {
      toast({
        title: "Invalid File Type",
        description: "Only PDF files are supported.",
        variant: "destructive",
      });
      return;
    }

    const newDoc: Document = {
      id: `doc-${Date.now()}`,
      name: file.name,
      size: formatFileSize(file.size),
      uploadedAt: new Date(),
      status: 'uploading',
    };

    // Add document with uploading status
    setDocuments(prev => [...prev, newDoc]);
    setIsLoading(true);

    try {
      const response = await apiService.uploadGuideline(file);
      
      // Update document status to uploaded
      setDocuments(prev => 
        prev.map(doc => 
          doc.id === newDoc.id 
            ? { ...doc, status: 'uploaded' as const }
            : doc
        )
      );

      toast({
        title: "Upload Successful",
        description: response.message,
      });

      // Reload stats to get updated document count
      await loadStats();

    } catch (error) {
      console.error('Error uploading document:', error);
      
      // Update document status to error
      setDocuments(prev => 
        prev.map(doc => 
          doc.id === newDoc.id 
            ? { ...doc, status: 'error' as const }
            : doc
        )
      );

      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "Failed to upload document",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [loadStats]);

  // Remove a document (frontend only - backend doesn't support deletion yet)
  const removeDocument = useCallback((id: string) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id));
    
    toast({
      title: "Document Removed",
      description: "Document removed from the list. Note: It may still be available in the backend.",
    });
  }, []);

  // Upload multiple documents
  const uploadMultipleDocuments = useCallback(async (files: File[]) => {
    const pdfFiles = files.filter(file => file.type.includes('pdf'));
    
    if (pdfFiles.length === 0) {
      toast({
        title: "No Valid Files",
        description: "No PDF files found in the selection.",
        variant: "destructive",
      });
      return;
    }

    if (pdfFiles.length !== files.length) {
      toast({
        title: "Some Files Skipped",
        description: `${files.length - pdfFiles.length} non-PDF files were skipped.`,
      });
    }

    // Upload files sequentially to avoid overwhelming the backend
    for (const file of pdfFiles) {
      await uploadDocument(file);
    }
  }, [uploadDocument]);

  return {
    documents,
    stats,
    isLoading,
    uploadDocument,
    removeDocument,
    uploadMultipleDocuments,
    loadStats,
  };
};