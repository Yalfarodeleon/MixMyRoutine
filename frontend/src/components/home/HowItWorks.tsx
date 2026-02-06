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
  },
  {
    number: '2',
    title: 'Select Multiple',
    description: 'Add all the ingredients from your routine or products.',
  },
  {
    number: '3',
    title: 'See Results',
    description: 'Instantly see conflicts, cautions, and synergies with explanations.',
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
            Check your ingredients in seconds
          </p>
        </div>
        
        {/* Steps */}
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="text-center">
              {/* Step Number */}
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                {step.number}
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {step.title}
              </h3>
              <p className="text-gray-600">
                {step.description}
              </p>
              
              {/* Connector line (except last) */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-6 left-full w-full h-0.5 bg-primary-200" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}