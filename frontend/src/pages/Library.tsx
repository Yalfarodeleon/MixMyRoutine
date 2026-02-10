/**
 * Library.tsx
 * 
 * Browse and learn about skincare ingredients with:
 * - Search functionality
 * - Category and concern filers
 * - Expandable ingredient information
 * - Detailed ingredient information
 */

import { useState } from 'react';
import { BookOpen, Search, ChevronDown, ChevronUp, Sun, Moon, Clock } from 'lucide-react';
import { useIngredients, useIngredient } from '../hooks/useApi';
import type { IngredientSummary } from '../types';

export default function Library() {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: ingredients, isLoading } = useIngredients({
    search: search || undefined,
    category: categoryFilter || undefined,
  });

  // Get unique categories
  const categories = [...new Set(ingredients?.map(i => i.category) || [])].sort();

  // Toggle expanded ingredient
  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-primary-500" />
          Ingredient Library
        </h1>
        <p className="text-gray-500 mt-1">
          Browse and learn about skincare ingredients
        </p>
      </div>

      {/* Filters */}
      <div className="card p-4 mb-6">
        <div className="flex flex-wrap gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search ingredients..."
                className="input pl-10"
              />
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            </div>
          </div>

          {/* Category Filter */}
          <div className="w-48">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="input"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12 text-gray-500">
          Loading ingredients...
        </div>
      )}

      {/* Results */}
      {!isLoading && ingredients && (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Showing {ingredients.length} ingredient{ingredients.length !== 1 ? 's' : ''}
          </p>

          <div className="space-y-3">
            {ingredients.map(ingredient => (
              <IngredientCard
                key={ingredient.id}
                ingredient={ingredient}
                isExpanded={expandedId === ingredient.id}
                onToggle={() => toggleExpand(ingredient.id)}
              />
            ))}
          </div>

          {ingredients.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No ingredients match your search.
            </div>
          )}
        </>
      )}
    </div>
  );
}

/**
 * Ingredient Card Component
 */
function IngredientCard({
  ingredient,
  isExpanded,
  onToggle,
}: {
  ingredient: IngredientSummary;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  // Fetch full details when expanded
  const { data: details } = useIngredient(isExpanded ? ingredient.id : '');

  return (
    <div className="card overflow-hidden">
      {/* Header (always visible) */}
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div>
            <h3 className="font-medium text-gray-900 text-left">{ingredient.name}</h3>
            <p className="text-sm text-gray-500">
              {ingredient.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {ingredient.beginner_friendly && (
            <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full">
              Beginner Friendly
            </span>
          )}
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>

      {/* Expanded Details */}
      {isExpanded && details && (
        <div className="px-4 pb-4 border-t border-gray-100">
          <div className="pt-4 grid md:grid-cols-2 gap-6">
            {/* Left column */}
            <div>
              <p className="text-gray-600 mb-4">{details.description}</p>

              {details.how_it_works && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-1">How it works</h4>
                  <p className="text-sm text-gray-600">{details.how_it_works}</p>
                </div>
              )}

              {details.usage_tips.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-1">Usage tips</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {details.usage_tips.map((tip, i) => (
                      <li key={i}>• {tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Right column */}
            <div className="space-y-4">
              {/* Time of day */}
              <div className="flex items-center gap-2 text-sm">
                <TimeIcon time={details.time_of_day} />
                <span className="text-gray-600">
                  {formatTimeOfDay(details.time_of_day)}
                </span>
              </div>

              {/* Addresses concerns */}
              {details.addresses_concerns.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Good for</h4>
                  <div className="flex flex-wrap gap-2">
                    {details.addresses_concerns.map(concern => (
                      <span
                        key={concern}
                        className="text-xs bg-primary-50 text-primary-700 px-2 py-1 rounded-full"
                      >
                        {concern.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Caution skin types */}
              {details.caution_skin_types.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Use caution with</h4>
                  <div className="flex flex-wrap gap-2">
                    {details.caution_skin_types.map(type => (
                      <span
                        key={type}
                        className="text-xs bg-amber-50 text-amber-700 px-2 py-1 rounded-full"
                      >
                        {type} skin
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Aliases */}
              {details.aliases.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-1">Also known as</h4>
                  <p className="text-sm text-gray-500">{details.aliases.join(', ')}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Time icon based on time of day
 */
function TimeIcon({ time }: { time: string }) {
  switch (time) {
    case 'morning_only':
      return <Sun className="w-4 h-4 text-amber-500" />;
    case 'evening_only':
      return <Moon className="w-4 h-4 text-indigo-500" />;
    default:
      return <Clock className="w-4 h-4 text-gray-500" />;
  }
}

/**
 * Format time of day for display
 */
function formatTimeOfDay(time: string): string {
  switch (time) {
    case 'morning_only':
      return 'Morning only';
    case 'evening_only':
      return 'Evening only';
    case 'either':
      return 'Morning or evening';
    case 'both':
      return 'Both morning and evening';
    default:
      return 'Any time';
  }
}
