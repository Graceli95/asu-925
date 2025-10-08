import React from 'react';
import { Navbar } from './Navbar';
import { Footer } from './Footer';

/**
 * MainLayout component that wraps pages with navbar and footer
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Page content
 */
export function MainLayout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-8">
        {children}
      </main>
      <Footer />
    </div>
  );
}
