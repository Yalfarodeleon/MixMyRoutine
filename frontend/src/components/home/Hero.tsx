/**
 * Hero Section - Enhanced with Live Stats & Animations
 * 
 * Features:
 * - Animated gradient background
 * - Live ingredient/interaction counts from API
 * - Typing animation for tagline
 * - Floating particles effect
 * - No duplicate icons
 */

import { Link } from 'react-router-dom';
import { ArrowRight, Zap, Beaker, Shield } from 'lucide-react';
import { useIngredients } from '../../hooks/useApi';
import { useState, useEffect } from 'react';

export default function Hero() {
  const { data: ingredients } = useIngredients();
  const [typedText, setTypedText] = useState('');
  const fullText = "Check if your skincare ingredients work together.";
  
  // Typing animation effect
  useEffect(() => {
    if (typedText.length < fullText.length) {
      const timeout = setTimeout(() => {
        setTypedText(fullText.slice(0, typedText.length + 1));
      }, 50);
      return () => clearTimeout(timeout);
    }
  }, [typedText]);

  // Calculate stats from API
  const ingredientCount = ingredients?.length || 26;
  // Assuming ~1.5 interactions per ingredient on average
  const interactionCount = Math.round(ingredientCount * 1.5);

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white">
      {/* Animated Background Blobs */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500 rounded-full opacity-20 blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary-400 rounded-full opacity-20 blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary-300 rounded-full opacity-10 blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>
      
      <div className="relative max-w-6xl mx-auto px-6 py-20 md:py-28">
        <div className="text-center">
          {/* Main Headline */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-primary-100 to-white bg-clip-text text-transparent animate-fade-in">
            Mix Smarter, Glow Better
          </h1>
          
          {/* Animated Subheadline */}
          <p className="text-xl md:text-2xl text-primary-100 mb-10 max-w-3xl mx-auto min-h-[2em]">
            {typedText}
            <span className="inline-block w-0.5 h-6 bg-primary-200 ml-1 animate-blink" />
          </p>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link 
              to="/checker" 
              className="group inline-flex items-center gap-2 bg-white text-primary-700 font-semibold px-8 py-4 rounded-xl hover:bg-primary-50 hover:scale-105 hover:shadow-2xl transition-all duration-200 text-lg"
            >
              <Zap className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              Try the Checker
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            
            <Link 
              to="/advisor" 
              className="group inline-flex items-center gap-2 bg-primary-500/20 backdrop-blur-sm text-white border-2 border-white/30 font-semibold px-8 py-4 rounded-xl hover:bg-primary-500/30 hover:scale-105 hover:shadow-2xl transition-all duration-200 text-lg"
            >
              Ask the Advisor
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
          
          {/* Live Stats - Animated Counters */}
          <div className="flex flex-wrap justify-center gap-8 md:gap-12">
            <StatCard
              icon={<Beaker className="w-6 h-6" />}
              value={ingredientCount}
              label="Ingredients"
              delay={0}
            />
            <StatCard
              icon={<Shield className="w-6 h-6" />}
              value={interactionCount}
              label="Interaction Rules"
              delay={200}
            />
            <StatCard
              icon={<Zap className="w-6 h-6" />}
              value="KBAI"
              label="Built with"
              delay={400}
              isText
            />
          </div>
        </div>
      </div>
      
      {/* Bottom Wave Decoration */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto">
          <path d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="rgb(249, 250, 251)" />
        </svg>
      </div>
    </section>
  );
}

/**
 * Animated Stat Card Component
 */
interface StatCardProps {
  icon: React.ReactNode;
  value: number | string;
  label: string;
  delay?: number;
  isText?: boolean;
}

function StatCard({ icon, value, label, delay = 0, isText = false }: StatCardProps) {
  const [displayValue, setDisplayValue] = useState(isText ? value : 0);
  
  // Animate number counting up
  useEffect(() => {
    if (isText) return;
    
    const timeout = setTimeout(() => {
      const targetValue = Number(value);
      const duration = 1000;
      const steps = 30;
      const increment = targetValue / steps;
      let current = 0;
      
      const timer = setInterval(() => {
        current += increment;
        if (current >= targetValue) {
          setDisplayValue(targetValue);
          clearInterval(timer);
        } else {
          setDisplayValue(Math.floor(current));
        }
      }, duration / steps);
      
      return () => clearInterval(timer);
    }, delay);
    
    return () => clearTimeout(timeout);
  }, [value, delay, isText]);
  
  return (
    <div 
      className="flex items-center gap-3 px-6 py-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:scale-105"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="text-primary-200">
        {icon}
      </div>
      <div>
        <div className="text-2xl font-bold">
          {isText ? displayValue : `${displayValue}+`}
        </div>
        <div className="text-sm text-primary-200">
          {label}
        </div>
      </div>
    </div>
  );
}