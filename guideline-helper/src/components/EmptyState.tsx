import { FileText, Shield, BookOpen, Upload, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface EmptyStateProps {
  hasDocuments?: boolean;
  isBackendAvailable?: boolean;
  onExampleClick?: (text: string) => void;
}

const EmptyState = ({ hasDocuments = false, isBackendAvailable = false, onExampleClick }: EmptyStateProps) => {
  const handleExampleClick = (text: string) => {
    if (onExampleClick) {
      onExampleClick(text);
    }
  };

  if (!isBackendAvailable) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4">
        <div className="h-16 w-16 rounded-2xl bg-destructive/10 flex items-center justify-center mb-6">
          <AlertTriangle className="h-8 w-8 text-destructive" />
        </div>
        <h2 className="text-xl font-semibold text-foreground mb-2">
          Backend Not Available
        </h2>
        <p className="text-muted-foreground text-sm max-w-md mb-4">
          The Medical Guideline Assistant backend is not running. Please start the Python server to use the chat functionality.
        </p>
        <div className="bg-muted/50 border border-border rounded-lg p-4 max-w-md">
          <p className="text-xs text-muted-foreground mb-2">To start the backend:</p>
          <code className="text-xs bg-background px-2 py-1 rounded border">
            python main.py
          </code>
        </div>
      </div>
    );
  }

  if (!hasDocuments) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4">
        <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
          <Upload className="h-8 w-8 text-primary" />
        </div>
        <h2 className="text-xl font-semibold text-foreground mb-2">
          Upload Medical Guidelines
        </h2>
        <p className="text-muted-foreground text-sm max-w-md mb-4">
          Upload PDF documents containing medical guidelines (WHO, CDC, NICE, etc.) to get started. The system will analyze them and provide evidence-based answers.
        </p>
        <Badge variant="outline" className="mb-8">
          <BookOpen className="h-3 w-3 mr-1" />
          Drag & drop PDFs to the sidebar
        </Badge>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
        <BookOpen className="h-8 w-8 text-primary" />
      </div>
      <h2 className="text-xl font-semibold text-foreground mb-2">
        Ask About Medical Guidelines
      </h2>
      <p className="text-muted-foreground text-sm max-w-md mb-8">
        Get evidence-based answers from your uploaded medical guidelines. 
        All responses are sourced from official documentation with citations.
      </p>
      
      <div className="grid gap-3 w-full max-w-md">
        <ExampleCard
          icon={<FileText className="h-4 w-4" />}
          text="What are the WHO guidelines for hypertension management?"
          onClick={() => handleExampleClick("What are the WHO guidelines for hypertension management?")}
        />
        <ExampleCard
          icon={<Shield className="h-4 w-4" />}
          text="What vaccinations are recommended for adults?"
          onClick={() => handleExampleClick("What vaccinations are recommended for adults?")}
        />
        <ExampleCard
          icon={<BookOpen className="h-4 w-4" />}
          text="What are the screening guidelines for diabetes?"
          onClick={() => handleExampleClick("What are the screening guidelines for diabetes?")}
        />
      </div>

      <p className="text-xs text-muted-foreground mt-8 max-w-sm">
        ⚠️ For educational purposes only. Always consult healthcare professionals for medical advice.
      </p>
    </div>
  );
};

const ExampleCard = ({ 
  icon, 
  text, 
  onClick 
}: { 
  icon: React.ReactNode; 
  text: string;
  onClick?: () => void;
}) => (
  <div 
    className="flex items-center gap-3 p-3 rounded-xl bg-muted/50 border border-border/50 text-left hover:bg-muted transition-colors cursor-pointer"
    onClick={onClick}
  >
    <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 text-primary">
      {icon}
    </div>
    <p className="text-sm text-foreground">{text}</p>
  </div>
);

export default EmptyState;
