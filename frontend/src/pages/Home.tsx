/**
 * Home Page
 * 
 * Landing page that introduces the app and its features.
 * This is what users see when they first visit.
 */

import Hero from '../components/home/Hero';
import Features from '../components/home/Features';
import HowItWorks from '../components/home/HowItWorks';
import CTA from '../components/home/CTA';

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero - Main banner with tagline */}
      <Hero />
      
      {/* Features - What the app does */}
      <Features />
      
      {/* How It Works - Step by step */}
      <HowItWorks />
      
      {/* CTA - Final push to try it */}
      <CTA />
    </div>
  );
}