/**
 * Main App Component
 * 
 * This sets up:
 * - The layout (sidebar + main content)
 * - React Router for navigation
 * - The main pages
 */

import { Routes, Route, NavLink } from 'react-router-dom';
import { 
  Search, 
  ClipboardList, 
  MessageCircle, 
  BookOpen,
  Sparkles 
} from 'lucide-react';

// Import pages
import IngredientChecker from './pages/IngredientChecker';
import RoutineBuilder from './pages/RoutineBuilder';
import Advisor from './pages/Advisor';
import Library from './pages/Library';
import Home from './pages/Home';

/**
 * Navigation items configuration
 */
const navItems = [
  { path: '/', icon: Search, label: 'Checker' },
  { path: '/routine', icon: ClipboardList, label: 'Routine' },
  { path: '/advisor', icon: MessageCircle, label: 'Advisor' },
  { path: '/library', icon: BookOpen, label: 'Library' },
];

export default function App() {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="mb-8">
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary-500" />
            MixMyRoutine
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Mix smarter, glow better
          </p>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-lg font-medium transition-all ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="mt-auto pt-6 border-t border-gray-100">
          <p className="text-xs text-gray-400 text-center">
            Built with KBAI + HCI
            <br />
            26 ingredients • 41 interactions
          </p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 bg-gray-50 p-8 overflow-y-auto">
        <Routes>
          <Route path="/" element={<IngredientChecker />} />
          <Route path="/routine" element={<RoutineBuilder />} />
          <Route path="/advisor" element={<Advisor />} />
          <Route path="/library" element={<Library />} />
          <Route path="/" element={<Home />} />
        </Routes>
      </main>
    </div>
  );
}
