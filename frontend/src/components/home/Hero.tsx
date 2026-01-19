/**
 * Hero Section
 * 
 * The first thing users see. Should:
 * - Clearly explain what the app does
 * - Have a strong call-to-action
 * - Be visually appealing
 */

import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 to-primary-800 text-white">
      <div className="max-w-6xl mx-auto px-6 py-24 text-center">
        {/* Logo/Icon */}
        <div className="flex justify-center mb-6">
          <Sparkles className="w-16 h-16 text-primary-200" />
        </div>
        
        {/* Main Headline */}
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          Mix Smarter, Glow Better
        </h1>
        
        {/* Subheadline */}
        <p className="text-xl md:text-2xl text-primary-100 mb-8 max-w-2xl mx-auto">
          Check if your skincare ingredients work together. 
          Powered by AI and backed by science.
        </p>
        
        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link 
            to="/checker" 
            className="btn-primary text-lg px-8 py-3"
          >
            Try the Checker
          </Link>
          <Link 
            to="/advisor" 
            className="btn-secondary bg-white/10 border-white/20 text-white hover:bg-white/20 text-lg px-8 py-3"
          >
            Ask the Advisor
          </Link>
        </div>
        
        {/* Trust indicators */}
        <p className="mt-12 text-primary-200 text-sm">
          26 ingredients • 41 interaction rules • Built with KBAI
        </p>
      </div>
    </section>
  );
}