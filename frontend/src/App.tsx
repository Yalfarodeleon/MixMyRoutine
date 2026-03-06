/**
 * Main App Component
 * 
 * This sets up:
 * - AuthProvider for global auth state
 * - The layout (sidebar + main content)
 * - React Router for navigation
 * - Auth pages (Login, Register, Profile)
 */
import { Routes, Route, NavLink, Link, useLocation } from 'react-router-dom';
import { 
  Search, 
  ClipboardList, 
  MessageCircle, 
  BookOpen,
  Sparkles,
  LogIn,
} from 'lucide-react';

// Auth
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Import pages
import IngredientChecker from './pages/IngredientChecker';
import RoutineBuilder from './pages/RoutineBuilder';
import Advisor from './pages/Advisor';
import Library from './pages/Library';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';

/**
 * Navigation items configuration
 */
const navItems = [
  { path: '/checker', icon: Search, label: 'Checker' },
  { path: '/routine', icon: ClipboardList, label: 'Routine' },
  { path: '/advisor', icon: MessageCircle, label: 'Advisor' },
  { path: '/library', icon: BookOpen, label: 'Library' },
];

/**
 * Pages that render WITHOUT the sidebar (full-screen layout)
 */
const fullScreenPages = ['/login', '/register'];


/**
 * Inner app component that has access to AuthContext
 */
function AppContent() {
  const location = useLocation();
  const { isAuthenticated, user, isLoading } = useAuth();
  const isFullScreen = fullScreenPages.includes(location.pathname);

  // Show spinner while checking auth status (prevents flash of wrong UI)
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-8 h-8 border-3 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
      </div>
    );
  }

  // Full-screen layout for login/register (no sidebar)
  if (isFullScreen) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    );
  }

  // Standard layout with sidebar
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col p-6 shadow-sm">
        {/* Logo - clickable to go Home */}
        <Link to="/" className="mb-8 block group">
          <div className="flex flex-col items-center">
            {/* Icon */}
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            {/* Brand Name */}
            <h1 className="text-lg font-bold bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent text-center leading-tight">
              MixMyRoutine
            </h1>
            {/* Tagline */}
            <p className="text-xs text-gray-500 text-center mt-1">
              Mix smarter, glow better
            </p>
          </div>
        </Link>

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

        {/* Spacer pushes auth section to the bottom */}
        <div className="flex-1" />

        {/* Auth Section at bottom of sidebar */}
        <div className="border-t border-gray-200 pt-4 mt-4">
          {isAuthenticated ? (
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-lg font-medium transition-all ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50'
                }`
              }
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white text-xs font-bold">
                  {user?.email?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{user?.email}</p>
                <p className="text-xs text-gray-400">View profile</p>
              </div>
            </NavLink>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-3 px-4 py-2.5 rounded-lg font-medium text-gray-600 hover:bg-gray-50 transition-all"
            >
              <LogIn className="w-5 h-5" />
              Sign In
            </Link>
          )}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 bg-gray-50 p-8 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/checker" element={<IngredientChecker />} />
          <Route path="/routine" element={<RoutineBuilder />} />
          <Route path="/advisor" element={<Advisor />} />
          <Route path="/library" element={<Library />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
    </div>
  );
}


/**
 * Root App component — wraps everything in AuthProvider
 */
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}