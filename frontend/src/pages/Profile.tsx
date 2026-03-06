/**
 * Profile Page
 * 
 * Lets authenticated users view and edit their skincare profile:
 * - Skin type selection
 * - Skin concerns (multi-select)
 * - Favorite ingredients
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User as UserIcon,
  Save,
  LogOut,
  Droplets,
  AlertCircle,
  Check,
  Heart,
  X,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { authApi, ingredientsApi } from '../services/api';
import type { IngredientSummary } from '../types';


// =============================================================================
// SKINCARE OPTIONS
// =============================================================================

const SKIN_TYPES = [
  { value: 'normal', label: 'Normal', emoji: '✨' },
  { value: 'dry', label: 'Dry', emoji: '🏜️' },
  { value: 'oily', label: 'Oily', emoji: '💧' },
  { value: 'combination', label: 'Combination', emoji: '⚖️' },
  { value: 'sensitive', label: 'Sensitive', emoji: '🌸' },
];

const CONCERNS = [
  { value: 'acne', label: 'Acne' },
  { value: 'aging', label: 'Aging' },
  { value: 'hyperpigmentation', label: 'Dark Spots' },
  { value: 'dryness', label: 'Dryness' },
  { value: 'oiliness', label: 'Oiliness' },
  { value: 'sensitivity', label: 'Sensitivity' },
  { value: 'dullness', label: 'Dullness' },
  { value: 'texture', label: 'Texture' },
  { value: 'redness', label: 'Redness' },
  { value: 'dark_circles', label: 'Dark Circles' },
  { value: 'pores', label: 'Large Pores' },
];


export default function Profile() {
  const navigate = useNavigate();
  const { user, profile, logout, refreshProfile } = useAuth();

  // Form state
  const [skinType, setSkinType] = useState<string>('');
  const [concerns, setConcerns] = useState<string[]>([]);
  const [favoriteIngredients, setFavoriteIngredients] = useState<string[]>([]);

  // UI state
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState('');
  const [allIngredients, setAllIngredients] = useState<IngredientSummary[]>([]);
  const [ingredientSearch, setIngredientSearch] = useState('');

  // Load profile data into form
  useEffect(() => {
    if (profile) {
      setSkinType(profile.skin_type || '');
      setConcerns(profile.concerns || []);
      setFavoriteIngredients(profile.favorite_ingredients || []);
    }
  }, [profile]);

  // Load all ingredients for the favorites selector
  useEffect(() => {
    ingredientsApi.list().then(setAllIngredients).catch(() => {});
  }, []);

  // Redirect if not authenticated
  if (!user) {
    navigate('/login');
    return null;
  }

  const toggleConcern = (concern: string) => {
    setConcerns((prev) =>
      prev.includes(concern)
        ? prev.filter((c) => c !== concern)
        : [...prev, concern]
    );
  };

  const toggleFavorite = (ingredientId: string) => {
    setFavoriteIngredients((prev) =>
      prev.includes(ingredientId)
        ? prev.filter((i) => i !== ingredientId)
        : [...prev, ingredientId]
    );
  };

  const filteredIngredients = allIngredients.filter((ing) =>
    ing.name.toLowerCase().includes(ingredientSearch.toLowerCase())
  );

  const handleSave = async () => {
    setError('');
    setSaveSuccess(false);
    setIsSaving(true);

    try {
      await authApi.updateProfile({
        skin_type: skinType || undefined,
        concerns,
        favorite_ingredients: favoriteIngredients,
      });
      await refreshProfile();
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save profile.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Profile</h1>
          <p className="text-gray-500 mt-1">{user.email}</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all text-sm font-medium"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>

      {/* Error / Success Messages */}
      {error && (
        <div className="flex items-center gap-2 bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}
      {saveSuccess && (
        <div className="flex items-center gap-2 bg-green-50 text-green-700 px-4 py-3 rounded-lg text-sm">
          <Check className="w-4 h-4 flex-shrink-0" />
          Profile saved successfully!
        </div>
      )}

      {/* Skin Type */}
      <div className="bg-white rounded-2xl shadow-soft p-6">
        <div className="flex items-center gap-2 mb-4">
          <Droplets className="w-5 h-5 text-primary-500" />
          <h2 className="text-lg font-semibold text-gray-900">Skin Type</h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {SKIN_TYPES.map((type) => (
            <button
              key={type.value}
              onClick={() => setSkinType(type.value)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl border-2 transition-all text-sm font-medium ${
                skinType === type.value
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">{type.emoji}</span>
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* Skin Concerns */}
      <div className="bg-white rounded-2xl shadow-soft p-6">
        <div className="flex items-center gap-2 mb-4">
          <UserIcon className="w-5 h-5 text-primary-500" />
          <h2 className="text-lg font-semibold text-gray-900">Skin Concerns</h2>
        </div>
        <p className="text-sm text-gray-500 mb-4">Select all that apply to you.</p>
        <div className="flex flex-wrap gap-2">
          {CONCERNS.map((concern) => {
            const isSelected = concerns.includes(concern.value);
            return (
              <button
                key={concern.value}
                onClick={() => toggleConcern(concern.value)}
                className={`px-3.5 py-2 rounded-full text-sm font-medium transition-all ${
                  isSelected
                    ? 'bg-primary-500 text-white shadow-sm'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {concern.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Favorite Ingredients */}
      <div className="bg-white rounded-2xl shadow-soft p-6">
        <div className="flex items-center gap-2 mb-4">
          <Heart className="w-5 h-5 text-primary-500" />
          <h2 className="text-lg font-semibold text-gray-900">Favorite Ingredients</h2>
        </div>
        <p className="text-sm text-gray-500 mb-4">
          Pick ingredients you love or want to include in your routines.
        </p>

        {/* Selected favorites */}
        {favoriteIngredients.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {favoriteIngredients.map((id) => {
              const ing = allIngredients.find((i) => i.id === id);
              return (
                <span
                  key={id}
                  className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
                >
                  {ing?.name || id}
                  <button
                    onClick={() => toggleFavorite(id)}
                    className="hover:bg-primary-200 rounded-full p-0.5 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              );
            })}
          </div>
        )}

        {/* Search & add */}
        <input
          type="text"
          value={ingredientSearch}
          onChange={(e) => setIngredientSearch(e.target.value)}
          placeholder="Search ingredients..."
          className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all text-sm mb-3"
        />

        <div className="max-h-48 overflow-y-auto rounded-lg border border-gray-200">
          {filteredIngredients.length === 0 ? (
            <p className="px-4 py-3 text-sm text-gray-400">No ingredients found</p>
          ) : (
            filteredIngredients.map((ing) => {
              const isFavorite = favoriteIngredients.includes(ing.id);
              return (
                <button
                  key={ing.id}
                  onClick={() => toggleFavorite(ing.id)}
                  className={`w-full flex items-center justify-between px-4 py-2.5 text-sm text-left hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0 ${
                    isFavorite ? 'bg-primary-50/50' : ''
                  }`}
                >
                  <div>
                    <span className="font-medium text-gray-700">{ing.name}</span>
                    <span className="text-gray-400 ml-2 text-xs">{ing.category}</span>
                  </div>
                  {isFavorite && <Check className="w-4 h-4 text-primary-500" />}
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        disabled={isSaving}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-medium hover:from-primary-600 hover:to-primary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm text-base"
      >
        {isSaving ? (
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        ) : (
          <>
            <Save className="w-5 h-5" />
            Save Profile
          </>
        )}
      </button>
    </div>
  );
}