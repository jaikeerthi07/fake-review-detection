import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Search, FileText, Zap, BarChart, Lock, ArrowRight, CheckCircle } from 'lucide-react';

export default function Home() {
    const navigate = useNavigate();
    const [url, setUrl] = useState('');

    const handleAnalyze = () => {
        if (url) {
            // Navigate to URL analysis with the URL pre-filled (implementation choice)
            // For now, just go to the page
            navigate('/url-analysis');
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/50">
            {/* Hero Section */}
            <div className="relative overflow-hidden pt-20 pb-12 lg:pt-32 lg:pb-16">
                {/* Background Blobs */}
                <div className="absolute top-0 right-0 -translate-y-12 translate-x-12 w-96 h-96 bg-blue-400/20 rounded-full blur-3xl opacity-50 animate-pulse delay-1000"></div>
                <div className="absolute bottom-0 left-0 translate-y-12 -translate-x-12 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl opacity-50 animate-pulse"></div>

                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                    <div className="text-center max-w-4xl mx-auto">

                        <h1 className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 via-blue-800 to-gray-900 mb-6 tracking-tight leading-tight">
                            Fake Review Detection<br />
                            <span className="text-blue-600"></span>
                        </h1>
                        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
                            Protect your brand and wallet. Our advanced AI analyzes patterns, sentiment, and consensus to identify fraudulent reviews in seconds.
                        </p>

                        {/* Live Stats Ticker */}
                        <div className="flex justify-center gap-8 mb-10 text-sm font-medium text-gray-500 animate-fade-in">
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                <span>System Online</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                                <span>1.2M+ Reviews Analyzed</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                                <span>99.8% Uptime</span>
                            </div>
                        </div>

                    </div>

                    {/* Dashboard Actions */}
                    <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-fade-in-up delay-200">
                        {/* Prediction (Single Review) */}
                        <button onClick={() => navigate('/analyze/single')} className="group flex flex-col items-center p-6 bg-white/80 backdrop-blur-md rounded-2xl shadow-xl shadow-blue-100/20 border border-white/50 hover:border-blue-200 hover:scale-105 transition-all duration-300">
                            <div className="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                <FileText className="w-7 h-7" />
                            </div>
                            <h3 className="font-bold text-gray-800 mb-1">Prediction</h3>
                            <p className="text-sm text-gray-500 text-center">Analyze single text</p>
                        </button>

                        {/* Live Prediction (URL) */}
                        <button onClick={() => navigate('/analyze/url')} className="group flex flex-col items-center p-6 bg-white/80 backdrop-blur-md rounded-2xl shadow-xl shadow-purple-100/20 border border-white/50 hover:border-purple-200 hover:scale-105 transition-all duration-300">
                            <div className="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center text-purple-600 mb-4 group-hover:bg-purple-600 group-hover:text-white transition-colors">
                                <Search className="w-7 h-7" />
                            </div>
                            <h3 className="font-bold text-gray-800 mb-1">Live Prediction</h3>
                            <p className="text-sm text-gray-500 text-center">Analyze URLs</p>
                        </button>

                        {/* Performance Analysis */}
                        <button onClick={() => navigate('/performance')} className="group flex flex-col items-center p-6 bg-white/80 backdrop-blur-md rounded-2xl shadow-xl shadow-green-100/20 border border-white/50 hover:border-green-200 hover:scale-105 transition-all duration-300">
                            <div className="w-14 h-14 rounded-full bg-green-50 flex items-center justify-center text-green-600 mb-4 group-hover:bg-green-600 group-hover:text-white transition-colors">
                                <ShieldCheck className="w-7 h-7" />
                            </div>
                            <h3 className="font-bold text-gray-800 mb-1">Performance</h3>
                            <p className="text-sm text-gray-500 text-center">Model Metrics</p>
                        </button>

                        {/* Charts */}
                        <button onClick={() => navigate('/charts')} className="group flex flex-col items-center p-6 bg-white/80 backdrop-blur-md rounded-2xl shadow-xl shadow-orange-100/20 border border-white/50 hover:border-orange-200 hover:scale-105 transition-all duration-300">
                            <div className="w-14 h-14 rounded-full bg-orange-50 flex items-center justify-center text-orange-600 mb-4 group-hover:bg-orange-600 group-hover:text-white transition-colors">
                                <BarChart className="w-7 h-7" />
                            </div>
                            <h3 className="font-bold text-gray-800 mb-1">Charts</h3>
                            <p className="text-sm text-gray-500 text-center">Visual Analytics</p>
                        </button>
                    </div>
                </div>
            </div>

            {/* Features Grid */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Feature 1 */}
                    <div className="group relative p-8 rounded-3xl bg-white border border-gray-100 hover:border-blue-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-blue-100/50 to-transparent rounded-tr-3xl -z-10 transition-colors"></div>
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center text-white mb-6 shadow-lg shadow-blue-200 group-hover:scale-110 transition-transform">
                            <ShieldCheck className="w-8 h-8" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">Trust Score AI</h3>
                        <p className="text-gray-500 leading-relaxed">
                            Our proprietary algorithm aggregates sentiment, consensus, and linguistic patterns to give you a single, reliable 0-100 trust score.
                        </p>
                    </div>

                    {/* Feature 2 */}
                    <div className="group relative p-8 rounded-3xl bg-white border border-gray-100 hover:border-purple-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-purple-100/50 to-transparent rounded-tr-3xl -z-10 transition-colors"></div>
                        <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center text-white mb-6 shadow-lg shadow-purple-200 group-hover:scale-110 transition-transform">
                            <BarChart className="w-8 h-8" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-purple-600 transition-colors">Deep Analytics</h3>
                        <p className="text-gray-500 leading-relaxed">
                            Visualize data with Confusion Matrices, Consensus Charts, and detailed breakdowns of model performance.
                        </p>
                    </div>

                    {/* Feature 3 */}
                    <div className="group relative p-8 rounded-3xl bg-white border border-gray-100 hover:border-green-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-green-100/50 to-transparent rounded-tr-3xl -z-10 transition-colors"></div>
                        <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center text-white mb-6 shadow-lg shadow-green-200 group-hover:scale-110 transition-transform">
                            <Zap className="w-8 h-8" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-green-600 transition-colors">Real-time Scraping</h3>
                        <p className="text-gray-500 leading-relaxed">
                            Powered by Apify, scrape and analyze thousands of reviews in seconds. Export reports with a single click.
                        </p>
                    </div>
                </div>
            </div>

            {/* Trust Section */}
            <div className="bg-gray-900 text-white py-24 overflow-hidden relative">
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>
                <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-blue-900/20 to-transparent"></div>

                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                        <div>
                            <h2 className="text-3xl md:text-4xl font-bold mb-6">Why Industry Leaders Trust Us</h2>
                            <p className="text-gray-400 text-lg mb-8">
                                In an era of misinformation, data integrity is paramount. TrustLens uses state-of-the-art Machine Learning models (SVM, Naive Bayes, Logistic Regression) to ensure what you see is real.
                            </p>
                            <ul className="space-y-4">
                                <li className="flex items-center gap-3 text-lg font-medium text-gray-300">
                                    <CheckCircle className="text-green-500 w-6 h-6" /> 95% Detection Accuracy
                                </li>
                                <li className="flex items-center gap-3 text-lg font-medium text-gray-300">
                                    <CheckCircle className="text-green-500 w-6 h-6" /> Real-time Amazon & Flipkart Scraping
                                </li>
                                <li className="flex items-center gap-3 text-lg font-medium text-gray-300">
                                    <CheckCircle className="text-green-500 w-6 h-6" /> Exportable PDF Reports
                                </li>
                            </ul>

                            <button onClick={() => navigate('/training')} className="mt-10 px-8 py-3 rounded-lg border border-gray-700 hover:bg-gray-800 transition text-gray-300 font-semibold" >
                                View Model Performance
                            </button>
                        </div>
                        <div className="relative">
                            <div className="absolute -inset-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur-lg opacity-75 animate-pulse"></div>
                            <div className="relative bg-gray-800 rounded-2xl p-8 border border-gray-700 shadow-2xl">
                                <div className="flex items-center justify-between mb-8 border-b border-gray-700 pb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                                        <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                                        <div className="w-3 h-3 rounded-full bg-green-500"></div>
                                    </div>
                                    <div className="text-gray-500 font-mono text-sm">analysis_core.py</div>
                                </div>
                                <div className="space-y-4 font-mono text-sm">
                                    <div className="flex gap-4">
                                        <span className="text-blue-400">def</span>
                                        <span className="text-yellow-400">analyze_trust_score</span>(review):
                                    </div>
                                    <div className="pl-8 text-gray-300">
                                        consensus = <span className="text-purple-400">get_model_consensus</span>(review)
                                    </div>
                                    <div className="pl-8 text-gray-300">
                                        <span className="text-blue-400">if</span> consensus.score {' > '} <span className="text-green-400">0.9</span>:
                                    </div>
                                    <div className="pl-16 text-gray-300">
                                        <span className="text-blue-400">return</span> <span className="text-green-400">"Trusted"</span>
                                    </div>
                                    <div className="pl-8 text-gray-300">
                                        <span className="text-blue-400">else</span>:
                                    </div>
                                    <div className="pl-16 text-gray-300">
                                        <span className="text-blue-400">return</span> <span className="text-red-400">"Suspicious"</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
