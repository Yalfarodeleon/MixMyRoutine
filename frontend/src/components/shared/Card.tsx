/**
 * Reusable Card Component
 * 
 * Provides consistent card styling.
 * Supports different variants and optional hover effects.
 */

import { ReactNode } from 'react';

interface CardProps {
  variant?: 'default' | 'bordered' | 'elevated';
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
  children: ReactNode;
  onClick?: () => void;
}

export default function Card({
  variant = 'default',
  hover = false,
  padding = 'md',
  className = '',
  children,
  onClick,
}: CardProps) {
  // Base styles
  const baseStyles = 'bg-white rounded-2xl';
  
  // Variant styles
  const variants = {
    default: 'border border-gray-100 shadow-soft',
    bordered: 'border-2 border-gray-200',
    elevated: 'shadow-soft-lg',
  };
  
  // Padding styles
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  // Hover effect
  const hoverStyles = hover 
    ? 'cursor-pointer hover:shadow-soft-lg hover:border-primary-200 transition-all duration-200' 
    : '';
  
  return (
    <div
      className={`${baseStyles} ${variants[variant]} ${paddings[padding]} ${hoverStyles} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}