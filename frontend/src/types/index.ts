/**
 * TypeScript Types for Skincare Advisor
 * 
 * WHAT ARE THESE?
 * ===============
 * These interfaces define the "shape" of data in TypeScript.
 * They match the Pydantic schemas in the backend.
 * 
 * WHY USE TYPES?
 * ==============
 * 1. Your IDE knows what fields exist (autocomplete!)
 * 2. TypeScript catches errors before runtime
 * 3. Self-documenting code
 */

// =============================================================================
// ENUMS
// =============================================================================

export type SkinType = 'dry' | 'oily' | 'combination' | 'sensitive' | 'normal';

export type SkinConcern = 
  | 'acne' 
  | 'aging' 
  | 'hyperpigmentation' 
  | 'dryness' 
  | 'oiliness' 
  | 'sensitivity' 
  | 'dullness' 
  | 'texture' 
  | 'redness' 
  | 'dark_circles' 
  | 'pores';

export type InteractionType = 
  | 'conflicts' 
  | 'caution' 
  | 'synergizes' 
  | 'wait' 
  | 'deactivates' 
  | 'sensitizing';

export type RoutineTime = 'am' | 'pm';

// =============================================================================
// REQUEST TYPES (What we send TO the API)
// =============================================================================

export interface SkinProfile {
  skin_type: SkinType;
  concerns: SkinConcern[];
}

export interface CompatibilityCheckRequest {
  ingredients: string[];
}

export interface ProductRequest {
  name: string;
  ingredients: string[];
}

export interface RoutineBuildRequest {
  products: ProductRequest[];
  time: RoutineTime;
  profile?: SkinProfile;
}

export interface AdvisorQuestionRequest {
  question: string;
  profile?: SkinProfile;
}

// =============================================================================
// RESPONSE TYPES (What we get FROM the API)
// =============================================================================

export interface Interaction {
  ingredient_a: string;
  ingredient_b: string;
  interaction_type: InteractionType;
  severity: number;
  explanation: string;
  recommendation: string;
}

export interface CompatibilityCheckResponse {
  is_compatible: boolean;
  conflicts: Interaction[];
  cautions: Interaction[];
  synergies: Interaction[];
  wait_times: Array<{
    ingredient_a: string;
    ingredient_b: string;
    wait_minutes: number;
  }>;
}

export interface IngredientSummary {
  id: string;
  name: string;
  category: string;
  beginner_friendly: boolean;
}

export interface IngredientDetail {
  id: string;
  name: string;
  category: string;
  aliases: string[];
  description: string;
  how_it_works?: string;
  usage_tips: string[];
  time_of_day: string;
  addresses_concerns: string[];
  caution_skin_types: string[];
  beginner_friendly: boolean;
  max_concentration?: string;
}

export interface RoutineStep {
  order: number;
  product_name: string;
  ingredients: string[];
  wait_after: number;
  notes?: string;
}

export interface RoutineResponse {
  steps: RoutineStep[];
  is_valid: boolean;
  conflicts: Interaction[];
  cautions: Interaction[];
  synergies: Interaction[];
  missing_essentials: string[];
  suggestions: string[];
}

export interface AdvisorResponse {
  answer: string;
  confidence: number;
  query_type: string;
  sources: string[];
  follow_up_questions: string[];
}


// =============================================================================
// AUTH TYPES
// =============================================================================

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface UserProfile {
  skin_type: string | null;
  concerns: string[];
  favorite_ingredients: string[];
}

export interface UserWithProfile extends User {
  profile: UserProfile | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ProfileUpdateRequest {
  skin_type?: string;
  concerns?: string[];
  favorite_ingredients?: string[];
}