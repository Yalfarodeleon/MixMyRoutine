/**
 * Library.tsx
 * 
 * Browse and learn about skincare ingredients with:
 * - Search functionality
 * - Category filter
 * - Expandable ingredient cards
 * - Detailed ingredient information
 */

import { useState } from 'react';
import { BookOpen, Search, ChevronDown, ChevronUp, Sun, Moon, Clock, Beaker, Lightbulb, Info } from 'lucide-react';
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

  // Clear all filters
  const clearFilters = () => {
    setSearch('');
    setCategoryFilter('');
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-primary-500" />
          Ingredient Library
        </h1>
        <p className="text-gray-600 mt-2">
          Browse and learn about skincare ingredients, their benefits, and how to use them.
        </p>
      </div>

      {/* Filters Card */}
      <div className="bg-white rounded-lg shadow-soft p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Ingredients
            </label>
            <div className="relative">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by name or alias..."
                className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            </div>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Category
            </label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
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

        {/* Active Filters */}
        {(search || categoryFilter) && (
          <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-200">
            <span className="text-sm text-gray-600">Active filters:</span>
            {search && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm">
                "{search}"
                <button onClick={() => setSearch('')} className="hover:text-primary-900 ml-1">×</button>
              </span>
            )}
            {categoryFilter && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm">
                {categoryFilter.replace('_', ' ')}
                <button onClick={() => setCategoryFilter('')} className="hover:text-primary-900 ml-1">×</button>
              </span>
            )}
            <button
              onClick={clearFilters}
              className="text-sm text-primary-600 hover:text-primary-700 underline ml-2"
            >
              Clear all
            </button>
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block w-8 h-8 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
          <p className="text-gray-500 mt-4">Loading ingredients...</p>
        </div>
      )}

      {/* Results */}
      {!isLoading && ingredients && (
        <>
          {/* Result Count */}
          <div className="mb-4 text-sm text-gray-600">
            Showing <span className="font-semibold">{ingredients.length}</span> ingredient{ingredients.length !== 1 ? 's' : ''}
          </div>

          {/* Ingredient Cards */}
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

          {/* Empty State */}
          {ingredients.length === 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Beaker className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No ingredients found
              </h3>
              <p className="text-gray-600 mb-4">
                Try adjusting your search or filters
              </p>
              <button
                onClick={clearFilters}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Clear all filters
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

/**
 * Ingredient Card Component
 * Shows summary with expand/collapse for details
 */
interface IngredientCardProps {
  ingredient: IngredientSummary;
  isExpanded: boolean;
  onToggle: () => void;
}

function IngredientCard({ ingredient, isExpanded, onToggle }: IngredientCardProps) {
  // Fetch full details when expanded
  const { data: details } = useIngredient(isExpanded ? ingredient.id : '');

  return (
    <div className="bg-white rounded-lg shadow-soft border border-gray-200 overflow-hidden transition-all duration-200 hover:shadow-md">
      {/* Card Header - Always Visible */}
      <button
        onClick={onToggle}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-4 flex-1 text-left">
          {/* Icon */}
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
              <Beaker className="w-5 h-5 text-primary-600" />
            </div>
          </div>

          {/* Name and Category */}
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900">
              {ingredient.name}
            </h3>
            <p className="text-sm text-gray-500">
              {ingredient.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </p>
          </div>

          {/* Badges */}
          <div className="flex items-center gap-2">
            {ingredient.beginner_friendly && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-50 text-green-700 border border-green-200 rounded-full text-xs font-medium">
                <span>✓</span>
                Beginner Friendly
              </span>
            )}
          </div>
        </div>

        {/* Expand/Collapse Icon */}
        <div className="ml-4">
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>

      {/* Card Details - Shown When Expanded */}
      {isExpanded && details && (
        <div className="px-6 pb-6 pt-2 border-t border-gray-100 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Left Column - Main Info (2/3 width) */}
            <div className="md:col-span-2 space-y-4">
              {/* Description */}
              <div>
                <p className="text-gray-700 leading-relaxed">
                  {details.description}
                </p>
              </div>

              {/* How It Works */}
              {details.how_it_works && (
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-2">
                    <Lightbulb className="w-4 h-4 text-primary-500" />
                    How It Works
                  </h4>
                  <p className="text-sm text-gray-600">
                    {details.how_it_works}
                  </p>
                </div>
              )}

              {/* Usage Tips */}
              {details.usage_tips && details.usage_tips.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-2">
                    <Info className="w-4 h-4 text-primary-500" />
                    Usage Tips
                  </h4>
                  <ul className="space-y-1">
                    {details.usage_tips.map((tip, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-primary-500 mt-1">•</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Right Column - Metadata (1/3 width) */}
            <div className="space-y-4">
              {/* Time of Day */}
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                  Best Time to Use
                </h4>
                <div className="flex items-center gap-2">
                  <TimeIcon time={details.time_of_day} />
                  <span className="text-sm text-gray-700">
                    {formatTimeOfDay(details.time_of_day)}
                  </span>
                </div>
              </div>

              {/* Addresses Concerns */}
              {details.addresses_concerns && details.addresses_concerns.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                    Good For
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {details.addresses_concerns.map(concern => (
                      <span
                        key={concern}
                        className="px-2 py-1 bg-primary-50 border border-primary-200 text-primary-700 rounded text-xs"
                      >
                        {concern.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Caution Skin Types */}
              {details.caution_skin_types && details.caution_skin_types.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                    Use Caution With
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {details.caution_skin_types.map(type => (
                      <span
                        key={type}
                        className="px-2 py-1 bg-amber-50 border border-amber-200 text-amber-700 rounded text-xs"
                      >
                        {type} skin
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Max Concentration */}
              {details.max_concentration && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                    Max Concentration
                  </h4>
                  <p className="text-sm text-gray-700">{details.max_concentration}</p>
                </div>
              )}

              {/* Aliases */}
              {details.aliases && details.aliases.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                    Also Known As
                  </h4>
                  <p className="text-sm text-gray-600">
                    {details.aliases.join(', ')}
                  </p>
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