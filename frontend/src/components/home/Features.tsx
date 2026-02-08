/**
 * 
 * Showcases the main features of the app.
 * Uses cards with icons for visual appeal.
 */

import { Search, FlaskConical, MessageCircle, BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  {
    icon: Search,
    title: 'Ingredient Checker',
    description: 'Select multiple ingredients and instantly see conflicts, cautions, and synergies.',
    link: '/checker',
    color: 'bg-violet-100 text-violet-600',
  },
  {
    icon: FlaskConical,
    title: 'Routine Builder',
    description: 'Build AM and PM routines with automatic conflict detection and optimal ordering.',
    link: '/routine',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    icon: MessageCircle,
    title: 'AI Advisor',
    description: 'Ask natural language questions and get instant, science-backed answers.',
    link: '/advisor',
    color: 'bg-emerald-100 text-emerald-600',
  },
  {
    icon: BookOpen,
    title: 'Ingredient Library',
    description: 'Browse 26+ ingredients with detailed info on usage, benefits, and interactions.',
    link: '/library',
    color: 'bg-amber-100 text-amber-600',
  },
];

export default function Features() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Everything You Need
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Powerful tools to help you build a safe, effective skincare routine
          </p>
        </div>
        
        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Link
              key={index}
              to={feature.link}
              className="group bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl hover:border-primary-200 hover:-translate-y-1 transition-all duration-300"
            >
              {/* Icon */}
              <div className={`w-14 h-14 ${feature.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className="w-7 h-7" />
              </div>
              
              {/* Content */}
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                {feature.description}
              </p>
              
              {/* Hover indicator */}
              <div className="mt-4 text-primary-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                Try it →
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}