/**
 * API Service Layer
 * 
 * This file handles ALL communication with the backend API.
 * Instead of calling fetch() everywhere, we centralize it here.
 */

import axios from 'axios';
import type {
  IngredientSummary,
  IngredientDetail,
  CompatibilityCheckRequest,
  CompatibilityCheckResponse,
  RoutineBuildRequest,
  RoutineResponse,
  AdvisorQuestionRequest,
  AdvisorResponse,
  TokenResponse,
  RegisterRequest,
  LoginRequest,
  UserWithProfile,
  UserProfile,
  ProfileUpdateRequest,
} from '../types';

// =============================================================================
// AXIOS INSTANCE
// =============================================================================

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// =============================================================================
// TOKEN INTERCEPTORS
// =============================================================================
// These run automatically on every request/response.
//
// REQUEST INTERCEPTOR: Before each request, check localStorage for a JWT token.
// If one exists, attach it to the Authorization header.
// This means individual API calls don't need to worry about auth.
//
// RESPONSE INTERCEPTOR: If the backend returns 401 (Unauthorized),
// the token is expired or invalid, so clear it from storage.

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
    }
    return Promise.reject(error);
  }
);

// =============================================================================
// INGREDIENTS API
// =============================================================================

export const ingredientsApi = {
  list: async (params?: {
    category?: string;
    concern?: string;
    search?: string;
  }): Promise<IngredientSummary[]> => {
    const response = await api.get<IngredientSummary[]>('/ingredients', { params });
    return response.data;
  },

  get: async (id: string): Promise<IngredientDetail> => {
    const response = await api.get<IngredientDetail>(`/ingredients/${id}`);
    return response.data;
  },

  checkCompatibility: async (
    ingredients: string[]
  ): Promise<CompatibilityCheckResponse> => {
    const response = await api.post<CompatibilityCheckResponse>(
      '/ingredients/check',
      { ingredients } as CompatibilityCheckRequest
    );
    return response.data;
  },
};

// =============================================================================
// ROUTINES API
// =============================================================================

export const routinesApi = {
  build: async (request: RoutineBuildRequest): Promise<RoutineResponse> => {
    const response = await api.post<RoutineResponse>('/routines/build', request);
    return response.data;
  },
};

// =============================================================================
// ADVISOR API
// =============================================================================

export const advisorApi = {
  ask: async (request: AdvisorQuestionRequest): Promise<AdvisorResponse> => {
    const response = await api.post<AdvisorResponse>('/advisor/ask', request);
    return response.data;
  },

  getExamples: async (): Promise<Record<string, string[]>> => {
    const response = await api.get<Record<string, string[]>>('/advisor/example-questions');
    return response.data;
  },
};

// =============================================================================
// AUTH API
// =============================================================================

export const authApi = {
  /** Register a new account. */
  register: async (data: RegisterRequest): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/register', data);
    return response.data;
  },

  /** Log in with email and password. */
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/login', data);
    return response.data;
  },

  /** Get the current authenticated user's data and profile. */
  getMe: async (): Promise<UserWithProfile> => {
    const response = await api.get<UserWithProfile>('/auth/me');
    return response.data;
  },

  /** Update the current user's skincare profile. */
  updateProfile: async (data: ProfileUpdateRequest): Promise<UserProfile> => {
    const response = await api.put<UserProfile>('/auth/profile', data);
    return response.data;
  },

  /** Get the current user's skincare profile. */
  getProfile: async (): Promise<UserProfile> => {
    const response = await api.get<UserProfile>('/auth/profile');
    return response.data;
  },
};

// =============================================================================
// EXPORT DEFAULT API OBJECT
// =============================================================================

export default {
  ingredients: ingredientsApi,
  routines: routinesApi,
  advisor: advisorApi,
  auth: authApi,
};