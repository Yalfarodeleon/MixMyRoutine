/**
 * 
 * Showcases the main features of the app.
 * Uses cards with icons for visual appeal.
 */

import { Search, FlaskConical, MessageCircle, BookOpen } from 'lucide-react';

const features = [
    {
    icon: Search,
    title: 'Ingredient Checker',
    description: 'Select multiple ingredients and instantly see if they conflict, need caution, or work great together.',
  },
  {
    icon: FlaskConical,
    title: 'Routine Builder',
    description: 'Build your AM and PM routines with automatic conflict detection and optimal ordering.',
  },
  {
    icon: MessageCircle,
    title: 'AI Advisor',
    description: 'Ask natural language questions like "Can I use retinol with vitamin C?" and get instant answers.',
  },
  {
    icon: BookOpen,
    title: 'Ingredient Library',
    description: 'Browse 26+ ingredients with detailed information on usage, benefits, and interactions.',
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
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="card p-6 text-center hover:shadow-soft-lg transition-shadow"
            >
              <div className="w-14 h-14 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <feature.icon className="w-7 h-7 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}