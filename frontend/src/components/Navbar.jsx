import React from 'react';
import { ShieldCheck, Database, Zap, BookOpen } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
    const location = useLocation();

    return (
        <nav className="bg-[#1a1a1a] text-[#e5e5e5] border-b border-gray-800 font-serif">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16 items-center">
                    <div className="flex">
                        <Link to="/" className="flex-shrink-0 flex items-center gap-2">
                            <span className="text-2xl font-bold text-[#fbbf24] tracking-wide">Fake Review Detection</span>
                        </Link>
                    </div>
                    <div className="flex items-center space-x-8">
                        <Link to="/select-method" className="hover:text-[#fbbf24] transition-colors text-sm font-medium">Prediction</Link>
                        <Link to="/analyze/url" className="hover:text-[#fbbf24] transition-colors text-sm font-medium">Live Prediction</Link>
                        <Link to="/performance" className="hover:text-[#fbbf24] transition-colors text-sm font-medium">Performance Analysis</Link>
                        <Link to="/charts" className="hover:text-[#fbbf24] transition-colors text-sm font-medium">Charts</Link>

                        {localStorage.getItem('token') ? (
                            <button
                                onClick={() => {
                                    localStorage.removeItem('token');
                                    localStorage.removeItem('username');
                                    window.location.href = '/login';
                                }}
                                className="hover:text-red-400 transition-colors text-sm font-medium"
                            >
                                Logout
                            </button>
                        ) : (
                            <Link to="/login" className="hover:text-[#fbbf24] transition-colors text-sm font-medium">Login</Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
