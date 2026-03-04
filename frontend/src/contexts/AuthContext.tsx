/**
 * Auth Context
 * 
 * WHAT IS THIS?
 * =============
 * React Context that manages authentication state across the entire app.
 * Any component can access the current user, login/logout functions, etc.
 * by calling useAuth().
 * 
 * HOW IT WORKS:
 * =============
 * 1. On app load, check if a token exists in localStorage
 * 2. If yes, validate it by calling GET /auth/me
 * 3. If valid, set the user in state (user is logged in)
 * 4. If invalid, clear the token (user needs to log in again)
 * 
 * WHY CONTEXT?
 * ============
 * Without Context, you'd have to pass user data through every component
 * as props ("prop drilling"). Context makes it available everywhere.
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import { authApi } from '../services/api';
import type { User, UserProfile } from '../types';


// =============================================================================
// TYPES
// =============================================================================

interface AuthContextType {
  /** The currently logged-in user, or null if not authenticated */
  user: User | null;
  /** The user's skincare profile */
  profile: UserProfile | null;
  /** Whether we're still checking if the user is logged in */
  isLoading: boolean;
  /** Whether the user is authenticated */
  isAuthenticated: boolean;
  /** Register a new account */
  register: (email: string, password: string) => Promise<void>;
  /** Log in with email and password */
  login: (email: string, password: string) => Promise<void>;
  /** Log out and clear the session */
  logout: () => void;
  /** Refresh the user's profile data */
  refreshProfile: () => Promise<void>;
}


// =============================================================================
// CONTEXT
// =============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);


// =============================================================================
// PROVIDER
// =============================================================================

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Check if the user has a valid session on app load.
   * Runs once when the app starts.
   */
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // Validate token by fetching current user
        const data = await authApi.getMe();
        setUser({
          id: data.id,
          email: data.email,
          is_active: data.is_active,
          created_at: data.created_at,
        });
        setProfile(data.profile);
      } catch {
        // Token is invalid or expired — clear it
        localStorage.removeItem('access_token');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  /**
   * Register a new account and automatically log in.
   */
  const register = useCallback(async (email: string, password: string) => {
    const data = await authApi.register({ email, password });
    localStorage.setItem('access_token', data.access_token);
    setUser(data.user);
    // Fetch full profile after registration
    try {
      const profileData = await authApi.getProfile();
      setProfile(profileData);
    } catch {
      setProfile(null);
    }
  }, []);

  /**
   * Log in with email and password.
   */
  const login = useCallback(async (email: string, password: string) => {
    const data = await authApi.login({ email, password });
    localStorage.setItem('access_token', data.access_token);
    setUser(data.user);
    // Fetch profile after login
    try {
      const meData = await authApi.getMe();
      setProfile(meData.profile);
    } catch {
      setProfile(null);
    }
  }, []);

  /**
   * Log out: clear token and reset state.
   */
  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setUser(null);
    setProfile(null);
  }, []);

  /**
   * Refresh profile data (e.g., after updating profile).
   */
  const refreshProfile = useCallback(async () => {
    try {
      const data = await authApi.getMe();
      setProfile(data.profile);
    } catch {
      // Silently fail — profile will remain stale
    }
  }, []);

  const value: AuthContextType = {
    user,
    profile,
    isLoading,
    isAuthenticated: !!user,
    register,
    login,
    logout,
    refreshProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}


// =============================================================================
// HOOK
// =============================================================================

/**
 * Custom hook to access auth state from any component.
 * 
 * Usage:
 *   const { user, login, logout } = useAuth();
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}