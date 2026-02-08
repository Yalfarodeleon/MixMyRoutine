/**
 * How It Works Section
 * 
 * Simple step-by-step explanation of using the app.
 * Reduces friction by demonstrating how easy it is to use.
 */

const steps = [
  {
    number: '1',
    title: 'Search Ingredients',
    description: 'Type the name of any skincare ingredient you want to check.',
    emoji: '🔍',
  },
  {
    number: '2',
    title: 'Select Multiple',
    description: 'Add all the ingredients from your routine or products.',
    emoji: '✨',
  },
  {
    number: '3',
    title: 'See Results',
    description: 'Instantly see conflicts, cautions, and synergies with explanations.',
    emoji: '✅',
  },
];

export default function HowItWorks() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-600">
            Check your ingredients in three simple steps
          </p>
        </div>
        
        {/* Steps */}
        <div className="relative">
          {/* Connection line */}
          <div className="hidden md:block absolute top-8 left-1/6 right-1/6 h-0.5 bg-gradient-to-r from-primary-200 via-primary-400 to-primary-200" />
          
          <div className="grid md:grid-cols-3 gap-12">
            {steps.map((step, index) => (
              <div key={index} className="relative text-center">
                {/* Step Number */}
                <div className="relative inline-flex">
                  <div className="w-16 h-16 bg-primary-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold shadow-lg shadow-primary-200">
                    {step.number}
                  </div>
                  <span className="absolute -top-2 -right-2 text-2xl">{step.emoji}</span>
                </div>
                
                <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">
                  {step.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}