/**
 * Reusable Badge Component
 * 
 * For displaying status indicators like:
 * - Compatibility results (safe, caution, conflict)
 * - Categories
 * - Tags
 */

import { ReactNode } from 'react';

interface BadgeProps {
  variant?: 'safe' | 'caution' | 'conflict' | 'synergy' | 'neutral' | 'primary';
  size?: 'sm' | 'md';
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
}

export default function Badge({
  variant = 'neutral',
  size = 'md',
  icon,
  children,
  className = '',
}: BadgeProps) {
  // Variant styles
  const variants = {
    safe: 'bg-green-100 text-green-700 border-green-200',
    caution: 'bg-amber-100 text-amber-700 border-amber-200',
    conflict: 'bg-red-100 text-red-700 border-red-200',
    synergy: 'bg-primary-100 text-primary-700 border-primary-200',
    neutral: 'bg-gray-100 text-gray-700 border-gray-200',
    primary: 'bg-primary-100 text-primary-700 border-primary-200',
  };
  
  // Size styles
  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
  };
  
  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {icon}
      {children}
    </span>
  );
}