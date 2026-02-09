/**
 * Ingredient Checker Page
 * 
 * Main page where users check if ingredients are compatible.
 */

import { useState } from 'react';
import { Search, AlertTriangle, CheckCircle, Sparkles, X, Beaker, Info } from 'lucide-react';
import { useIngredients, useCompatibilityCheck } from '../hooks/useApi';
import type { Interaction } from '../types';

export default function IngredientChecker() {
  const [selected, setSelected] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  const { data: ingredients, isLoading: loadingIngredients } = useIngredients();
  const { 
    mutate: checkCompatibility, 
    data: result, 
    isPending: checking,
    reset: resetResult 
  } = useCompatibilityCheck();

  const filteredIngredients = ingredients?.filter(ing =>
    ing.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const addIngredient = (id: string) => {
    if (!selected.includes(id) && selected.length < 10) {
      const newSelected = [...selected, id];
      setSelected(newSelected);
      if (newSelected.length >= 2) {
        checkCompatibility(newSelected);
      }
    }
    setSearchTerm('');
  };

  const removeIngredient = (id: string) => {
    const newSelected = selected.filter(s => s !== id);
    setSelected(newSelected);
    if (newSelected.length >= 2) {
      checkCompatibility(newSelected);
    } else {
      resetResult();
    }
  };

  const clearAll = () => {
    setSelected([]);
    resetResult();
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
            <Search className="w-5 h-5 text-primary-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            Ingredient Compatibility Checker
          </h1>
        </div>
        <p className="text-gray-500 ml-13">
          Check if your skincare ingredients can be safely used together
        </p>
      </div>

      {/* Main Card */}
      <div className="card p-6 mb-6">
        {/* Search Input */}
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Search and select ingredients
        </label>
        <div className="relative">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Type to search (e.g., retinol, niacinamide)..."
            className="input pl-10"
          />
          <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
        </div>

        {/* Search Results Dropdown */}
        {searchTerm && (
          <div className="mt-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
            {filteredIngredients.length === 0 ? (
              <div className="p-4 text-gray-500 text-sm text-center">
                No ingredients found for "{searchTerm}"
              </div>
            ) : (
              filteredIngredients.map(ing => (
                <button
                  key={ing.id}
                  onClick={() => addIngredient(ing.id)}
                  disabled={selected.includes(ing.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-primary-50 flex items-center justify-between transition-colors ${
                    selected.includes(ing.id) ? 'opacity-50 bg-gray-50' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Beaker className="w-4 h-4 text-gray-400" />
                    <span className="font-medium">{ing.name}</span>
                  </div>
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                    {ing.category}
                  </span>
                </button>
              ))
            )}
          </div>
        )}

        {/* Selected Ingredients */}
        {selected.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-100">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-gray-700">
                Selected Ingredients ({selected.length}/10)
              </span>
              <button 
                onClick={clearAll} 
                className="text-sm text-gray-500 hover:text-red-600 transition-colors"
              >
                Clear all
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {selected.map(id => {
                const ing = ingredients?.find(i => i.id === id);
                return (
                  <span
                    key={id}
                    className="inline-flex items-center gap-2 bg-primary-100 text-primary-700 pl-3 pr-2 py-1.5 rounded-full text-sm font-medium group"
                  >
                    {ing?.name || id}
                    <button
                      onClick={() => removeIngredient(id)}
                      className="w-5 h-5 bg-primary-200 hover:bg-red-200 hover:text-red-600 rounded-full flex items-center justify-center transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Empty State / Prompt */}
        {selected.length < 2 && (
          <div className="mt-6 bg-gradient-to-r from-primary-50 to-violet-50 border border-primary-100 rounded-xl p-5">
            <div className="flex gap-4">
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Info className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-1">
                  {selected.length === 0 
                    ? "Start by adding ingredients" 
                    : "Add one more ingredient"}
                </h4>
                <p className="text-sm text-gray-600">
                  {selected.length === 0
                    ? "Search and select at least 2 ingredients to check their compatibility."
                    : "Select one more ingredient to see if they work well together."}
                </p>
                {selected.length === 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="text-xs text-gray-500">Popular:</span>
                    {['retinol', 'vitamin_c', 'niacinamide', 'hyaluronic_acid'].map(id => (
                      <button
                        key={id}
                        onClick={() => addIngredient(id)}
                        className="text-xs bg-white border border-gray-200 hover:border-primary-300 hover:bg-primary-50 px-2 py-1 rounded-full transition-colors"
                      >
                        {ingredients?.find(i => i.id === id)?.name || id}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading State */}
      {checking && (
        <div className="card p-8 text-center">
          <div className="inline-flex items-center gap-3 text-primary-600">
            <div className="w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
            <span className="font-medium">Analyzing compatibility...</span>
          </div>
        </div>
      )}

      {/* Results */}
      {result && !checking && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Overall Status */}
          <div className={`card p-6 ${
            result.is_compatible 
              ? result.synergies.length > 0 
                ? 'bg-gradient-to-r from-purple-50 to-violet-50 border-purple-200' 
                : 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
              : 'bg-gradient-to-r from-red-50 to-rose-50 border-red-200'
          }`}>
            <div className="flex items-start gap-4">
              {result.is_compatible ? (
                result.synergies.length > 0 ? (
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-6 h-6 text-purple-600" />
                  </div>
                ) : (
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                )
              ) : (
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
              )}
              <div>
                <h2 className={`text-xl font-bold ${
                  result.is_compatible 
                    ? result.synergies.length > 0 ? 'text-purple-700' : 'text-green-700'
                    : 'text-red-700'
                }`}>
                  {result.is_compatible 
                    ? result.synergies.length > 0 
                      ? 'Great combination!' 
                      : 'All clear!'
                    : 'Conflicts detected'}
                </h2>
                <p className={`mt-1 ${
                  result.is_compatible 
                    ? result.synergies.length > 0 ? 'text-purple-600' : 'text-green-600'
                    : 'text-red-600'
                }`}>
                  {result.is_compatible 
                    ? result.synergies.length > 0
                      ? 'These ingredients are compatible and some work synergistically together!'
                      : 'These ingredients can be safely used together.'
                    : 'Some ingredients should NOT be used together. See details below.'}
                </p>
              </div>
            </div>
          </div>

          {/* Detailed Results Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Conflicts */}
            {result.conflicts.length > 0 && (
              <div className="card p-6 border-red-100">
                <h3 className="font-bold text-red-700 mb-4 flex items-center gap-2">
                  <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  Conflicts ({result.conflicts.length})
                </h3>
                <div className="space-y-3">
                  {result.conflicts.map((conflict, i) => (
                    <InteractionCard key={i} interaction={conflict} type="conflict" />
                  ))}
                </div>
              </div>
            )}

            {/* Cautions */}
            {result.cautions.length > 0 && (
              <div className="card p-6 border-amber-100">
                <h3 className="font-bold text-amber-700 mb-4 flex items-center gap-2">
                  <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  Use with Caution ({result.cautions.length})
                </h3>
                <div className="space-y-3">
                  {result.cautions.map((caution, i) => (
                    <InteractionCard key={i} interaction={caution} type="caution" />
                  ))}
                </div>
              </div>
            )}

            {/* Synergies */}
            {result.synergies.length > 0 && (
              <div className="card p-6 border-purple-100">
                <h3 className="font-bold text-purple-700 mb-4 flex items-center gap-2">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  Great Together ({result.synergies.length})
                </h3>
                <div className="space-y-3">
                  {result.synergies.map((synergy, i) => (
                    <InteractionCard key={i} interaction={synergy} type="synergy" />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Loading ingredients */}
      {loadingIngredients && (
        <div className="text-center py-12 text-gray-500">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          Loading ingredients...
        </div>
      )}
    </div>
  );
}

/**
 * Interaction Card Component
 */
function InteractionCard({ 
  interaction, 
  type 
}: { 
  interaction: Interaction; 
  type: 'conflict' | 'caution' | 'synergy';
}) {
  const styles = {
    conflict: 'border-red-200 bg-red-50/50',
    caution: 'border-amber-200 bg-amber-50/50',
    synergy: 'border-purple-200 bg-purple-50/50',
  };

  const pillStyles = {
    conflict: 'bg-red-100 text-red-700',
    caution: 'bg-amber-100 text-amber-700',
    synergy: 'bg-purple-100 text-purple-700',
  };

  return (
    <div className={`p-4 rounded-xl border ${styles[type]}`}>
      <div className={`inline-block text-xs font-semibold px-2 py-1 rounded-full mb-2 ${pillStyles[type]}`}>
        {interaction.ingredient_a} + {interaction.ingredient_b}
      </div>
      <p className="text-sm text-gray-700 mb-2">{interaction.explanation}</p>
      {interaction.recommendation && (
        <p className="text-sm font-medium text-gray-900 flex items-start gap-2">
          <span>💡</span>
          <span>{interaction.recommendation}</span>
        </p>
      )}
    </div>
  );
}