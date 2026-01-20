import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, AlertTriangle } from "lucide-react";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  confidence?: number;
}

const ChatMessage = ({ role, content, sources, confidence }: ChatMessageProps) => {
  const getConfidenceColor = (score?: number) => {
    if (!score) return "secondary";
    if (score >= 0.8) return "default";
    if (score >= 0.5) return "secondary";
    return "destructive";
  };

  const getConfidenceIcon = (score?: number) => {
    if (!score) return null;
    if (score >= 0.8) return <CheckCircle className="h-3 w-3" />;
    return <AlertTriangle className="h-3 w-3" />;
  };

  // Don't show confidence for conversational responses (confidence = 1.0)
  const showConfidence = confidence !== undefined && confidence < 1.0;

  return (
    <div
      className={cn(
        "flex w-full",
        role === "user" ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3",
          role === "user"
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground"
        )}
      >
        {role === "assistant" && showConfidence && (
          <div className="flex items-center gap-2 mb-2">
            <Badge variant={getConfidenceColor(confidence)} className="text-xs">
              {getConfidenceIcon(confidence)}
              <span className="ml-1">
                {Math.round(confidence * 100)}% confidence
              </span>
            </Badge>
          </div>
        )}
        
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
        
        {sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-border/50">
            <p className="text-xs font-medium text-muted-foreground mb-2">
              References ({sources.length}):
            </p>
            <ul className="space-y-1">
              {sources.map((source, index) => (
                <li
                  key={index}
                  className="text-xs text-muted-foreground flex items-start gap-2"
                >
                  <span className="w-1 h-1 rounded-full bg-primary/60 mt-2 shrink-0" />
                  <span className="break-words">{source}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
