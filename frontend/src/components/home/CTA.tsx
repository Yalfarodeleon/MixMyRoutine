/**
 * CTA Section
 * 
 * Final call-to-action - different from Hero
 */

import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle } from 'lucide-react';

export default function CTA() {
  return (
    <section className="py-20 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
          Ready to Build Your Perfect Routine?
        </h2>
        
        {/* Value props */}
        <div className="flex flex-wrap justify-center gap-6 mb-8 text-primary-100">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span>Free to use</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span>No account needed</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span>Science-backed data</span>
          </div>
        </div>
        
        <Link 
          to="/checker" 
          className="inline-flex items-center gap-2 bg-white text-primary-700 font-semibold px-8 py-4 rounded-xl hover:bg-primary-50 hover:scale-105 transition-all duration-200 text-lg shadow-lg"
        >
          Start Checking Ingredients
          <ArrowRight className="w-5 h-5" />
        </Link>
      </div>
    </section>
  );
}