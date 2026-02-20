import React, { useState } from 'react';
import client from '../api/config';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, User } from 'lucide-react';

export default function Login() {
    const [formData, setFormData] = useState({ username: '', password: '' });
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await client.post('/api/auth/login', formData);
            localStorage.setItem('token', res.data.access_token);
            localStorage.setItem('username', res.data.username);
            window.location.href = '/'; // Force refresh to update Navbar state
        } catch (err) {
            console.error("Login Error:", err);
            const errorMsg = err.response?.data?.error || err.message || 'Login failed';

            // Debugging helper: if it's a network error, show what URL it tried to hit
            if (err.message === 'Network Error') {
                alert(`Network Error! Tried to reach: ${client.defaults.baseURL}/api/auth/login`);
            } else {
                alert(typeof errorMsg === 'object' ? JSON.stringify(errorMsg) : errorMsg);
            }
        }
    };

    return (
        <div className="max-w-md mx-auto mt-20 bg-white p-8 rounded-xl shadow-md border border-gray-100">
            <div className="text-center mb-8">
                <h2 className="text-3xl font-serif font-bold text-gray-900">Fake review Detection</h2>
                <p className="text-gray-500">Sign in to access all features</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                    <div className="relative">
                        <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                        <input
                            type="text"
                            name="username"
                            required
                            className="w-full pl-10 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter your username"
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                    <div className="relative">
                        <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                        <input
                            type="password"
                            name="password"
                            required
                            className="w-full pl-10 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="••••••••"
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <button type="submit" className="w-full py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition">
                    Sign In
                </button>
            </form>

            <p className="mt-6 text-center text-sm text-gray-600">
                Don't have an account? <Link to="/register" className="text-blue-600 font-medium hover:underline">Sign up</Link>
            </p>
        </div>
    );
}
