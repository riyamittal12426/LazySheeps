import React from 'react';
import { useNavigate } from 'react-router-dom';
import SplashCursor from '../components/SplashCursor';
import { 
  SparklesIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const PricingPage = () => {
  const navigate = useNavigate();

  const pricingPlans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for small teams getting started',
      features: [
        { name: 'Up to 5 team members', included: true },
        { name: 'Basic DORA metrics', included: true },
        { name: '3 repositories', included: true },
        { name: 'Community support', included: true },
        { name: 'Release readiness score', included: false },
        { name: 'Sprint Planner AI', included: false },
        { name: 'Advanced analytics', included: false },
        { name: 'Custom integrations', included: false }
      ],
      cta: 'Get Started',
      popular: false
    },
    {
      name: 'Pro',
      price: '$29',
      period: 'per user/month',
      description: 'For growing teams that need more power',
      features: [
        { name: 'Unlimited team members', included: true },
        { name: 'Full DORA metrics suite', included: true },
        { name: 'Unlimited repositories', included: true },
        { name: 'Priority support', included: true },
        { name: 'Release readiness score', included: true },
        { name: 'Sprint Planner AI', included: true },
        { name: 'Advanced analytics', included: true },
        { name: 'Custom integrations', included: false }
      ],
      cta: 'Start Free Trial',
      popular: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: 'contact sales',
      description: 'For large organizations with custom needs',
      features: [
        { name: 'Everything in Pro', included: true },
        { name: 'Dedicated support', included: true },
        { name: 'Custom integrations', included: true },
        { name: 'SLA guarantees', included: true },
        { name: 'On-premise deployment', included: true },
        { name: 'Advanced security', included: true },
        { name: 'Custom training', included: true },
        { name: 'White-label options', included: true }
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ];

  const faqs = [
    {
      question: 'Can I try before I buy?',
      answer: 'Yes! We offer a 14-day free trial on all paid plans. No credit card required.'
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards, PayPal, and can arrange invoicing for Enterprise customers.'
    },
    {
      question: 'Can I change plans later?',
      answer: 'Absolutely! You can upgrade or downgrade your plan at any time. Changes take effect immediately.'
    },
    {
      question: 'What kind of support do you offer?',
      answer: 'Free users get community support, Pro users get priority email support, and Enterprise customers get dedicated support with SLA guarantees.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white relative">
      <SplashCursor />
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-gray-900 border-b border-gray-700 z-50 relative">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 cursor-pointer" onClick={() => navigate('/')}>
              <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                <SparklesIcon className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold">Katalyst</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="/#features" className="text-gray-300 hover:text-white transition">Features</a>
              <a href="/pricing" className="text-indigo-400 font-semibold">Pricing</a>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 text-gray-300 hover:text-white transition"
              >
                Sign In
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold transition"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 text-white">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto">
            Choose the perfect plan for your team. Start free, upgrade when you need more.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <div
                key={index}
                className={`relative bg-gray-800 rounded-2xl border ${
                  plan.popular ? 'border-indigo-500 scale-105' : 'border-gray-700'
                } p-8 transition-all hover:border-indigo-500`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="mb-2">
                    <span className="text-5xl font-bold">{plan.price}</span>
                    {plan.period !== 'contact sales' && plan.price !== '$0' && (
                      <span className="text-gray-400 text-lg">/{plan.period}</span>
                    )}
                  </div>
                  <p className="text-gray-400 text-sm">{plan.period}</p>
                  <p className="text-gray-300 mt-4">{plan.description}</p>
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start space-x-3">
                      {feature.included ? (
                        <CheckCircleIcon className="h-6 w-6 text-green-500 flex-shrink-0 mt-0.5" />
                      ) : (
                        <XMarkIcon className="h-6 w-6 text-gray-600 flex-shrink-0 mt-0.5" />
                      )}
                      <span className={feature.included ? 'text-gray-300' : 'text-gray-600'}>
                        {feature.name}
                      </span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => navigate('/dashboard')}
                  className={`w-full py-3 rounded-lg font-semibold transition ${
                    plan.popular
                      ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                      : 'bg-gray-700 hover:bg-gray-600 text-white'
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-6 bg-gray-800">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-gray-800 rounded-xl border border-gray-700 p-6"
              >
                <h3 className="text-xl font-semibold mb-3 text-white">
                  {faq.question}
                </h3>
                <p className="text-gray-400">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-3xl p-12 relative overflow-hidden">
            <div className="relative z-10">
              <h2 className="text-4xl md:text-5xl font-bold mb-6">
                Still Have Questions?
              </h2>
              <p className="text-xl mb-8 text-gray-100">
                Our team is here to help you find the perfect plan.
              </p>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-8 py-3 bg-white text-indigo-600 hover:bg-gray-100 rounded-lg font-bold transition"
              >
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <SparklesIcon className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">Katalyst</span>
          </div>
          <p className="text-gray-400 text-sm">
            &copy; 2024 Katalyst. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default PricingPage;
