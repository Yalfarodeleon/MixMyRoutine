/**
 * Hero Section
 * 
 * The first thing users see. Should:
 * - Clearly explain what the app does
 * - Have a strong call-to-action
 * - Be visually appealing
 */

import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, Zap } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500 rounded-full opacity-20 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary-400 rounded-full opacity-20 blur-3xl" />
      </div>
      
      <div className="relative max-w-6xl mx-auto px-6 py-24 text-center">
        {/* Logo/Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
        </div>
        
        {/* Main Headline */}
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          Mix Smarter, Glow Better
        </h1>
        
        {/* Subheadline */}
        <p className="text-xl md:text-2xl text-primary-100 mb-10 max-w-2xl mx-auto">
          Check if your skincare ingredients work together. 
          Powered by AI and backed by science.
        </p>
        
        {/* CTA Buttons - FIXED */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link 
            to="/checker" 
            className="inline-flex items-center justify-center gap-2 bg-white text-primary-700 font-semibold text-lg px-8 py-4 rounded-xl hover:bg-primary-50 hover:scale-105 transition-all duration-200 shadow-lg"
          >
            <Zap className="w-5 h-5" />
            Try the Checker
          </Link>
          <Link 
            to="/advisor" 
            className="inline-flex items-center justify-center gap-2 bg-primary-500/30 backdrop-blur-sm text-white font-semibold text-lg px-8 py-4 rounded-xl border-2 border-white/30 hover:bg-primary-500/50 hover:border-white/50 transition-all duration-200"
          >
            Ask the Advisor
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
        
        {/* Trust indicators */}
        <div className="mt-16 flex flex-wrap justify-center gap-8 text-primary-200 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full" />
            26 ingredients
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full" />
            41 interaction rules
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full" />
            Built with KBAI
          </div>
        </div>
      </div>
    </section>
  );
}