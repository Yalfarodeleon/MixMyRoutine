/**
 * UserMenu Component
 * 
 * Top-right user menu with collapsible dropdown.
 * - Logged in: Shows avatar with dropdown (Profile, Sign Out)
 * - Logged out: Shows Sign In / Create Account buttons
 * 
 * The dropdown closes when you click outside of it (useEffect listener).
 */

import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  User,
  LogOut,
  LogIn,
  UserPlus,
  ChevronDown,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';


export default function UserMenu() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    setIsOpen(false);
    logout();
    navigate('/');
  };

  // ─── Not logged in: Show Sign In + Create Account ───
  if (!isAuthenticated) {
    return (
      <div className="flex items-center gap-3">
        <Link
          to="/login"
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-all"
        >
          <LogIn className="w-4 h-4" />
          Sign In
        </Link>
        <Link
          to="/register"
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg hover:from-primary-600 hover:to-primary-700 transition-all shadow-sm"
        >
          <UserPlus className="w-4 h-4" />
          Create Account
        </Link>
      </div>
    );
  }

  // ─── Logged in: Show avatar with dropdown ───
  const initial = user?.email?.charAt(0).toUpperCase() || '?';

  return (
    <div ref={menuRef} className="relative">
      {/* Avatar Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2.5 px-3 py-2 rounded-xl transition-all ${
          isOpen
            ? 'bg-primary-50 ring-2 ring-primary-200'
            : 'hover:bg-gray-100'
        }`}
      >
        {/* Avatar circle */}
        <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
          <span className="text-white text-xs font-bold">{initial}</span>
        </div>
        {/* Email + chevron */}
        <span className="text-sm font-medium text-gray-700 max-w-[150px] truncate hidden sm:block">
          {user?.email}
        </span>
        <ChevronDown
          className={`w-4 h-4 text-gray-400 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50 animate-fade-in">
          {/* User info header */}
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-bold">{initial}</span>
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user?.email}
                </p>
                <p className="text-xs text-gray-400 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  MixMyRoutine Member
                </p>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="py-1">
            <Link
              to="/profile"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <User className="w-4 h-4 text-gray-400" />
              Your Profile
            </Link>
          </div>

          {/* Sign Out */}
          <div className="border-t border-gray-100 pt-1">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors w-full text-left"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}