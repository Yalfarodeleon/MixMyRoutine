/**
 * CTA Section
 * 
 * Final call-to-action that adapts based on auth state.
 * - Logged out: Encourages sign-up + trying the checker
 * - Logged in: Encourages exploring tools
 */

import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle, UserPlus } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export default function CTA() {
  const { isAuthenticated } = useAuth();

  return (
    <section className="py-20 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
          {isAuthenticated
            ? 'Your Routine Awaits'
            : 'Ready to Build Your Perfect Routine?'}
        </h2>
        
        {/* Value props */}
        <div className="flex flex-wrap justify-center gap-6 mb-8 text-primary-100">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span>Free to use</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span>Save your skin profile</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span>Science-backed data</span>
          </div>
        </div>
        
        {/* Buttons adapt to auth state */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link 
            to="/checker" 
            className="inline-flex items-center justify-center gap-2 bg-white text-primary-700 font-semibold px-8 py-4 rounded-xl hover:bg-primary-50 hover:scale-105 transition-all duration-200 text-lg shadow-lg"
          >
            Start Checking Ingredients
            <ArrowRight className="w-5 h-5" />
          </Link>

          {!isAuthenticated && (
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 bg-primary-500/20 backdrop-blur-sm text-white border-2 border-white/30 font-semibold px-8 py-4 rounded-xl hover:bg-primary-500/30 hover:scale-105 transition-all duration-200 text-lg"
            >
              <UserPlus className="w-5 h-5" />
              Create Free Account
            </Link>
          )}
        </div>
      </div>
    </section>
  );
}