import { Upload, FileText, X, BookOpen, Loader2, CheckCircle, AlertCircle, PanelLeftClose, PanelLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  useSidebar,
} from "@/components/ui/sidebar";
import { useState } from "react";

export interface Document {
  id: string;
  name: string;
  size: string;
  uploadedAt: Date;
  status: 'uploading' | 'uploaded' | 'error';
}

interface AppSidebarProps {
  documents: Document[];
  onUpload: (file: File) => void;
  onUploadMultiple: (files: File[]) => void;
  onRemove: (id: string) => void;
  isUploading?: boolean;
  totalDocuments?: number;
}

const AppSidebar = ({ 
  documents, 
  onUpload, 
  onUploadMultiple, 
  onRemove, 
  isUploading = false,
  totalDocuments 
}: AppSidebarProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === "collapsed";

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      onUploadMultiple(files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      onUploadMultiple(files);
    }
    e.target.value = "";
  };

  const getStatusIcon = (status: Document['status']) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="h-3 w-3 animate-spin text-blue-500" />;
      case 'uploaded':
        return <CheckCircle className="h-3 w-3 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-3 w-3 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: Document['status']) => {
    switch (status) {
      case 'uploading':
        return 'secondary';
      case 'uploaded':
        return 'default';
      case 'error':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="p-4 border-b border-sidebar-border">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="shrink-0 h-8 w-8"
          >
            {isCollapsed ? (
              <PanelLeft className="h-4 w-4" />
            ) : (
              <PanelLeftClose className="h-4 w-4" />
            )}
          </Button>
          {!isCollapsed && (
            <div className="flex-1">
              <h2 className="text-sm font-semibold">Documents</h2>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          {!isCollapsed && (
            <>
              <SidebarGroupLabel>Medical Guidelines</SidebarGroupLabel>
              <SidebarGroupContent className="px-2">
                <div
                  className={`border-2 border-dashed rounded-xl p-4 text-center transition-colors ${
                    isDragging
                      ? "border-primary bg-primary/5"
                      : "border-sidebar-border hover:border-primary/50"
                  } ${isUploading ? "opacity-50 pointer-events-none" : ""}`}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setIsDragging(true);
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                >
                  {isUploading ? (
                    <Loader2 className="h-6 w-6 mx-auto text-primary animate-spin mb-2" />
                  ) : (
                    <Upload className="h-6 w-6 mx-auto text-muted-foreground mb-2" />
                  )}
                  <p className="text-xs text-muted-foreground mb-2">
                    {isUploading ? "Uploading..." : "Drag PDF files here or"}
                  </p>
                  {!isUploading && (
                    <label>
                      <input
                        type="file"
                        accept=".pdf"
                        multiple
                        onChange={handleFileInput}
                        className="hidden"
                      />
                      <Button variant="outline" size="sm" asChild>
                        <span className="cursor-pointer">Browse</span>
                      </Button>
                    </label>
                  )}
                </div>

                {documents.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center gap-2 p-2 rounded-lg bg-sidebar-accent group"
                      >
                        <FileText className="h-4 w-4 text-primary shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-xs font-medium truncate">
                              {doc.name}
                            </p>
                            {getStatusIcon(doc.status)}
                          </div>
                          <div className="flex items-center gap-2">
                            <p className="text-xs text-muted-foreground">
                              {doc.size}
                            </p>
                            <Badge 
                              variant={getStatusColor(doc.status)} 
                              className="text-xs h-4"
                            >
                              {doc.status}
                            </Badge>
                          </div>
                        </div>
                        <button
                          onClick={() => onRemove(doc.id)}
                          className="p-1 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
                          disabled={doc.status === 'uploading'}
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </SidebarGroupContent>
            </>
          )}

          {isCollapsed && (
            <SidebarGroupContent className="flex flex-col items-center gap-2 py-2">
              <label>
                <input
                  type="file"
                  accept=".pdf"
                  multiple
                  onChange={handleFileInput}
                  className="hidden"
                  disabled={isUploading}
                />
                <Button 
                  variant="ghost" 
                  size="icon" 
                  asChild 
                  className="cursor-pointer"
                  disabled={isUploading}
                >
                  <span>
                    {isUploading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Upload className="h-4 w-4" />
                    )}
                  </span>
                </Button>
              </label>
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="relative p-2 rounded-lg bg-sidebar-accent"
                  title={`${doc.name} - ${doc.status}`}
                >
                  <FileText className="h-4 w-4 text-primary" />
                  <div className="absolute -top-1 -right-1">
                    {getStatusIcon(doc.status)}
                  </div>
                </div>
              ))}
            </SidebarGroupContent>
          )}
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
};

export default AppSidebar;
