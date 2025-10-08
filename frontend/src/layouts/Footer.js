import React from 'react';
import { Music } from 'lucide-react';

/**
 * Footer component
 */
export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Music className="h-4 w-4" />
            <span className="text-sm">Songs App</span>
          </div>
          <div className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Songs App. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
