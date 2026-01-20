import { useEffect } from "react";
import Header from "@/components/Header";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import EmptyState from "@/components/EmptyState";
import AppSidebar from "@/components/AppSidebar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SidebarProvider } from "@/components/ui/sidebar";
import { useChat } from "@/hooks/useChat";
import { useDocuments } from "@/hooks/useDocuments";

const Index = () => {
  const { 
    messages, 
    isLoading, 
    isBackendAvailable, 
    sendMessage, 
    clearChat, 
    checkBackend 
  } = useChat();
  
  const {
    documents,
    stats,
    isLoading: isUploadLoading,
    uploadDocument,
    removeDocument,
    uploadMultipleDocuments,
    loadStats,
  } = useDocuments();

  // Check backend and load stats on mount
  useEffect(() => {
    const initialize = async () => {
      await checkBackend();
      await loadStats();
    };
    initialize();
  }, [checkBackend, loadStats]);

  const handleSend = (content: string) => {
    sendMessage(content);
  };

  const handleExampleClick = (text: string) => {
    sendMessage(text);
  };

  const handleRefreshBackend = async () => {
    await checkBackend();
    await loadStats();
  };

  const hasDocuments = documents.length > 0 || (stats?.total_documents ?? 0) > 0;

  return (
    <SidebarProvider>
      <div className="flex h-screen w-full bg-background">
        <AppSidebar
          documents={documents}
          onUpload={uploadDocument}
          onUploadMultiple={uploadMultipleDocuments}
          onRemove={removeDocument}
          isUploading={isUploadLoading}
          totalDocuments={stats?.total_documents}
        />

        <div className="flex-1 flex flex-col min-w-0">
          <Header 
            isBackendAvailable={isBackendAvailable}
            onRefreshBackend={handleRefreshBackend}
          />

          <main className="flex-1 overflow-hidden flex flex-col">
            <div className="flex-1 overflow-hidden">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center p-4">
                  <EmptyState 
                    hasDocuments={hasDocuments}
                    isBackendAvailable={isBackendAvailable}
                    onExampleClick={handleExampleClick}
                  />
                </div>
              ) : (
                <ScrollArea className="h-full">
                  <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
                    {messages.map((message) => (
                      <ChatMessage
                        key={message.id}
                        role={message.role}
                        content={message.content}
                        sources={message.sources}
                        confidence={message.confidence}
                      />
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-muted rounded-2xl px-4 py-3">
                          <div className="flex gap-1">
                            <span
                              className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"
                              style={{ animationDelay: "0ms" }}
                            />
                            <span
                              className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"
                              style={{ animationDelay: "150ms" }}
                            />
                            <span
                              className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"
                              style={{ animationDelay: "300ms" }}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              )}
            </div>

            <div className="border-t border-border bg-card p-4 flex-shrink-0">
              <div className="max-w-3xl mx-auto">
                <ChatInput 
                  onSend={handleSend} 
                  disabled={isLoading || !isBackendAvailable} 
                />
                {!isBackendAvailable && (
                  <p className="text-xs text-muted-foreground mt-2 text-center">
                    Backend not available. Please start the Python server.
                  </p>
                )}
              </div>
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default Index;
