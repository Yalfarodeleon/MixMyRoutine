/**
 * Reusable Container Component
 * 
 * Provides consistent max-width and padding.
 * Use for page sections to maintain alignment.
 */

import { ReactNode } from 'react';

interface ContainerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  className?: string;
  children: ReactNode;
}

export default function Container({
  size = 'lg',
  className = '',
  children,
}: ContainerProps) {
  // Max-width based on size
  const sizes = {
    sm: 'max-w-2xl',
    md: 'max-w-4xl',
    lg: 'max-w-6xl',
    xl: 'max-w-7xl',
    full: 'max-w-full',
  };
  
  return (
    <div className={`mx-auto px-4 sm:px-6 lg:px-8 ${sizes[size]} ${className}`}>
      {children}
    </div>
  );
}