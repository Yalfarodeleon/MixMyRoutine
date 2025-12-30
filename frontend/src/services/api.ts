/**
 * API Service Layer
 * 
 * WHAT IS THIS?
 * =============
 * This file handles ALL communication with the backend API.
 * Instead of calling fetch() everywhere, we centralize it here.
 * 
 * WHY CENTRALIZE?
 * ===============
 * 1. One place to set base URL, headers, auth tokens
 * 2. Consistent error handling
 * 3. Easy to mock for testing
 * 4. Type-safe responses
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
} from '../types';

// =============================================================================
// AXIOS INSTANCE
// =============================================================================

/**
 * Create a configured Axios instance.
 * 
 * WHY NOT JUST USE fetch()?
 * -------------------------
 * Axios provides:
 * - Automatic JSON parsing
 * - Request/response interceptors
 * - Better error handling
 * - Easier configuration
 */
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',  // Vite proxies this to localhost:8000
  headers: {
    'Content-Type': 'application/json',
  },
});

// =============================================================================
// INGREDIENTS API
// =============================================================================

export const ingredientsApi = {
  /**
   * Get all ingredients with optional filtering.
   */
  list: async (params?: {
    category?: string;
    concern?: string;
    search?: string;
  }): Promise<IngredientSummary[]> => {
    const response = await api.get<IngredientSummary[]>('/ingredients', { params });
    return response.data;
  },

  /**
   * Get a single ingredient by ID.
   */
  get: async (id: string): Promise<IngredientDetail> => {
    const response = await api.get<IngredientDetail>(`/ingredients/${id}`);
    return response.data;
  },

  /**
   * Check compatibility between ingredients.
   */
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
  /**
   * Build an optimized routine.
   */
  build: async (request: RoutineBuildRequest): Promise<RoutineResponse> => {
    const response = await api.post<RoutineResponse>('/routines/build', request);
    return response.data;
  },
};

// =============================================================================
// ADVISOR API
// =============================================================================

export const advisorApi = {
  /**
   * Ask a skincare question.
   */
  ask: async (request: AdvisorQuestionRequest): Promise<AdvisorResponse> => {
    const response = await api.post<AdvisorResponse>('/advisor/ask', request);
    return response.data;
  },

  /**
   * Get example questions.
   */
  getExamples: async (): Promise<Record<string, string[]>> => {
    const response = await api.get<Record<string, string[]>>('/advisor/example-questions');
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
};
