/**
 * Advisor.tsx
 * 
 * AI-powered skincare Q&A interface with:
 * - Chat-based conversation
 * - Example questions to get started
 * - Confidence indicators
 * - Follow-up suggestions
 * - Markdown rendering for rich responses
 */

import { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Sparkles, AlertCircle, Lightbulb } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useAdvisor } from '../hooks/useApi';
import type { AdvisorResponse } from '../types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  confidence?: number;
  followUps?: string[];
}

const EXAMPLE_QUESTIONS = [
  {
    category: 'Compatibility',
    icon: '🔬',
    questions: [
      'Can I use retinol with vitamin C?',
      'Is niacinamide safe with AHA?',
      'Can I mix benzoyl peroxide and salicylic acid?',
    ],
  },
  {
    category: 'Recommendations',
    icon: '✨',
    questions: [
      'What should I use for acne-prone skin?',
      'What order should I apply my products?',
      'What\'s good for hyperpigmentation?',
    ],
  },
];

export default function Advisor() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { mutate: askQuestion, isPending } = useAdvisor();

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle sending a message
  const handleSend = (question?: string) => {
    const text = question || input.trim();
    if (!text || isPending) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    // Ask the API
    askQuestion(
      { question: text },
      {
        onSuccess: (response: AdvisorResponse) => {
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: response.answer,
            confidence: response.confidence,
            followUps: response.follow_up_questions,
          };
          setMessages(prev => [...prev, assistantMessage]);
        },
        onError: () => {
          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: "Sorry, I couldn't process that question. Please try again.",
          };
          setMessages(prev => [...prev, errorMessage]);
        },
      }
    );
  };

  // Handle key press (Enter to send)
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle example question click
  const handleExampleClick = (question: string) => {
    handleSend(question);
  };

  return (
    <div className="max-w-4xl mx-auto h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <MessageCircle className="w-8 h-8 text-primary-500" />
          Skincare Advisor
        </h1>
        <p className="text-gray-600 mt-2">
          Ask me anything about ingredients, compatibility, routines, and skincare science.
        </p>
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col bg-white rounded-lg shadow-soft overflow-hidden">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            // Empty State with Example Questions
            <div className="h-full flex flex-col items-center justify-center space-y-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-primary-500" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Start a Conversation
                </h2>
                <p className="text-gray-600 max-w-md">
                  Ask me anything about skincare ingredients, product recommendations, or routine advice.
                </p>
              </div>

              {/* Example Questions */}
              <div className="w-full max-w-2xl space-y-6">
                {EXAMPLE_QUESTIONS.map((category) => (
                  <div key={category.category}>
                    <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                      <span className="text-lg">{category.icon}</span>
                      {category.category}
                    </h3>
                    <div className="grid gap-2">
                      {category.questions.map((question) => (
                        <button
                          key={question}
                          onClick={() => handleExampleClick(question)}
                          className="text-left p-3 bg-gray-50 hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-lg transition-all duration-200 text-sm text-gray-700 hover:text-primary-700"
                        >
                          {question}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            // Messages
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    {message.role === 'user' ? (
                      <p className="text-sm">{message.content}</p>
                    ) : (
                      <div className="space-y-3">
                        {/* Main Response */}
                        <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:text-gray-700">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>

                        {/* Low Confidence Warning */}
                        {message.confidence !== undefined && message.confidence < 0.5 && (
                          <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-md">
                            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                            <p className="text-xs text-amber-800">
                              I'm not fully confident about this answer. Consider consulting a dermatologist for personalized advice.
                            </p>
                          </div>
                        )}

                        {/* Follow-up Questions */}
                        {message.followUps && message.followUps.length > 0 && (
                          <div className="pt-2 border-t border-gray-200">
                            <div className="flex items-center gap-2 mb-2">
                              <Lightbulb className="w-4 h-4 text-primary-500" />
                              <p className="text-xs font-medium text-gray-700">
                                You might also want to know:
                              </p>
                            </div>
                            <div className="space-y-1">
                              {message.followUps.slice(0, 3).map((followUp, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => handleExampleClick(followUp)}
                                  className="block w-full text-left text-xs text-primary-600 hover:text-primary-700 hover:underline"
                                >
                                  • {followUp}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Loading Indicator */}
              {isPending && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-lg px-4 py-3 bg-gray-100">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                      <span className="text-xs text-gray-500">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about ingredients, routines, or products..."
              disabled={isPending}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-sm"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isPending}
              className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2 font-medium text-sm"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Helper Text */}
      <p className="text-xs text-gray-500 text-center mt-4">
        Advice is based on general skincare knowledge. Always patch test new products and consult a dermatologist for personalized recommendations.
      </p>
    </div>
  );
}