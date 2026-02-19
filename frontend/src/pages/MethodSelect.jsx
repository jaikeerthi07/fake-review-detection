import React from 'react';
import { Keyboard, Globe } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function MethodSelect() {
    return (
        <div className="max-w-5xl mx-auto text-center py-10">
            <h1 className="text-4xl font-serif font-bold text-gray-900 mb-4">Choose Prediction Method</h1>
            <p className="text-gray-500 mb-12">Select how you want to analyze reviews for authenticity</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Single Review Card */}
                <div className="bg-white p-10 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl transition-shadow duration-300 flex flex-col items-center">
                    <div className="bg-orange-50 p-4 rounded-full mb-6">
                        <Keyboard className="h-10 w-10 text-orange-500" />
                    </div>
                    <h3 className="text-2xl font-serif font-bold text-gray-800 mb-3">Single Review Analysis</h3>
                    <p className="text-gray-500 mb-8 max-w-sm">Enter text manually and get instant prediction using advanced ML models</p>
                    <Link to="/analyze/single" className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition">
                        ↓ Go to Form
                    </Link>
                </div>

                {/* Live URL Card */}
                <div className="bg-white p-10 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl transition-shadow duration-300 flex flex-col items-center">
                    <div className="bg-blue-50 p-4 rounded-full mb-6">
                        <Globe className="h-10 w-10 text-blue-500" />
                    </div>
                    <h3 className="text-2xl font-serif font-bold text-gray-800 mb-3">Live URL Analysis</h3>
                    <p className="text-gray-500 mb-8 max-w-sm">Paste product URLs to extract and analyze multiple reviews automatically</p>
                    <Link to="/analyze/url" className="px-6 py-2 bg-green-700 text-white font-medium rounded-lg hover:bg-green-800 transition">
                        ⚡ Try Live Analysis
                    </Link>
                </div>
            </div>
        </div>
    );
}
