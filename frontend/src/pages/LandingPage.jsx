import React from 'react';
import { useNavigate } from 'react-router-dom';
import SplashCursor from '../components/SplashCursor';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  ShieldCheckIcon, 
  RocketLaunchIcon,
  CodeBracketIcon,
  SparklesIcon,
  ArrowTrendingUpIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';

const LandingPage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: ChartBarIcon,
      title: 'DORA Metrics',
      description: 'Track deployment frequency, lead time, and change failure rate in real-time.',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: RocketLaunchIcon,
      title: 'Release Readiness',
      description: 'Get instant insights into your release quality with AI-powered scoring.',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: BeakerIcon,
      title: 'Sprint Planner AI',
      description: 'Optimize sprint planning with intelligent task allocation and predictions.',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: UserGroupIcon,
      title: 'Team Analytics',
      description: 'Understand team performance and collaboration patterns with deep insights.',
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: ShieldCheckIcon,
      title: 'RBAC & Security',
      description: 'Enterprise-grade role-based access control and security features.',
      color: 'from-indigo-500 to-purple-500'
    },
    {
      icon: ArrowTrendingUpIcon,
      title: 'GitHub Integration',
      description: 'Seamlessly sync with GitHub repositories and track all activities.',
      color: 'from-pink-500 to-rose-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white overflow-x-hidden relative">
      <SplashCursor />
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-gray-900 border-b border-gray-700 z-50 relative">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                <SparklesIcon className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold">Katalyst</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-300 hover:text-white transition cursor-pointer">Features</a>
              <a onClick={() => navigate('/pricing')} className="text-gray-300 hover:text-white transition cursor-pointer">Pricing</a>
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
      <section className="pt-32 pb-20 px-6 relative">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 text-white leading-tight">
            Katalyst
            <br />
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
           Understand your code. Connect your contributors.Amplify your development velocity.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-bold text-lg transition"
            >
              Start Free Trial
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-8 py-4 bg-gray-800 hover:bg-gray-700 rounded-lg font-bold text-lg transition border border-gray-600"
            >
              View Demo
            </button>
          </div>

          {/* Code Visualization Box */}
          <div className="max-w-4xl mx-auto bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
            <div className="bg-gray-800 px-4 py-3 flex items-center space-x-2 border-b border-gray-700">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="ml-4 text-sm text-gray-400 font-mono">katalyst-dashboard.tsx</span>
            </div>
            <div className="p-8 font-mono text-sm text-left overflow-x-auto">
              <div className="text-purple-400">
                <span className="text-gray-500">// AI-Powered Release Readiness</span>
              </div>
              <div className="text-blue-400">
                const <span className="text-white">score</span> = await <span className="text-yellow-400">analyzeRelease</span>();
              </div>
              <div className="text-gray-400 mt-2">
                {'{'} 
                <span className="text-green-400"> ready</span>: <span className="text-orange-400">true</span>, 
                <span className="text-green-400"> score</span>: <span className="text-orange-400">95</span> 
                {'}'}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-6 overflow-visible relative">
        <div className="max-w-[1400px] mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-400">
              Everything you need to ship faster and smarter
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-12 py-8 px-4">
            {features.map((feature, index) => (
              <div
                key={index}
                className="relative bg-gray-800 rounded-2xl border border-gray-700 p-10 min-h-[320px]"
              >
                <div>
                  <div className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-xl flex items-center justify-center mb-6 shadow-lg`}>
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>
                  
                  <h3 className="text-2xl font-bold mb-4 text-white">
                    {feature.title}
                  </h3>
                  
                  <p className="text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 relative">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-3xl p-12 relative overflow-hidden">
            <div className="relative z-10">
              <h2 className="text-4xl md:text-5xl font-bold mb-6">
                Ready to Transform Your Workflow?
              </h2>
              <p className="text-xl mb-8 text-gray-100">
                Join thousands of teams already shipping faster with Katalyst.
              </p>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-8 py-4 bg-white text-indigo-600 hover:bg-gray-100 rounded-lg font-bold text-lg transition"
              >
                Get Started Free
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <SparklesIcon className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold">Katalyst</span>
              </div>
              <p className="text-gray-400 text-sm">
                Amplify your organization's development velocity with AI-powered insights.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#features" className="hover:text-white transition cursor-pointer">Features</a></li>
                <li><a onClick={() => navigate('/pricing')} className="hover:text-white transition cursor-pointer">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">Integrations</a></li>
                <li><a href="#" className="hover:text-white transition">Changelog</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition">API Reference</a></li>
                <li><a href="#" className="hover:text-white transition">Guides</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Careers</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
                <li><a href="#" className="hover:text-white transition">Privacy</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
            <p>&copy; 2024 Katalyst. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
