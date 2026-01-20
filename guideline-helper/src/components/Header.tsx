import { BookOpen, PanelLeftClose, PanelLeft, Wifi, WifiOff, RefreshCw } from "lucide-react";
import { useSidebar } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { apiService } from "@/services/api";

interface HeaderProps {
  isBackendAvailable?: boolean;
  onRefreshBackend?: () => void;
}

const Header = ({ isBackendAvailable, onRefreshBackend }: HeaderProps) => {
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === "collapsed";
  const [isChecking, setIsChecking] = useState(false);

  const handleRefreshBackend = async () => {
    if (onRefreshBackend) {
      setIsChecking(true);
      await onRefreshBackend();
      setIsChecking(false);
    }
  };

  return (
    <header className="border-b border-border bg-card">
      <div className="px-4 py-3 flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="shrink-0"
        >
          {isCollapsed ? (
            <PanelLeft className="h-5 w-5" />
          ) : (
            <PanelLeftClose className="h-5 w-5" />
          )}
        </Button>
        <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center">
          <BookOpen className="h-4 w-4 text-primary" />
        </div>
        <div className="flex-1">
          <h1 className="text-base font-semibold text-foreground">
            Medical Guideline Assistant
          </h1>
          <p className="text-xs text-muted-foreground">
            Educational answers from official health guidelines
          </p>
        </div>
        
        {/* Backend Status */}
        <div className="flex items-center gap-2">
          <Badge 
            variant={isBackendAvailable ? "default" : "destructive"}
            className="text-xs"
          >
            {isBackendAvailable ? (
              <>
                <Wifi className="h-3 w-3 mr-1" />
                Connected
              </>
            ) : (
              <>
                <WifiOff className="h-3 w-3 mr-1" />
                Disconnected
              </>
            )}
          </Badge>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefreshBackend}
            disabled={isChecking}
            className="h-8 w-8"
            title="Check backend connection"
          >
            <RefreshCw className={`h-4 w-4 ${isChecking ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;
