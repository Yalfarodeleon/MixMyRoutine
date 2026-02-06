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