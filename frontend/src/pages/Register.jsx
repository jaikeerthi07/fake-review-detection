import React, { useState } from 'react';
import client from '../api/config';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, User, UserPlus } from 'lucide-react';

export default function Register() {
    const [formData, setFormData] = useState({ username: '', password: '' });
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await client.post('/api/auth/register', formData);
            alert('Registration successful! Please login.');
            navigate('/login');
        } catch (err) {
            alert(err.response?.data?.error || 'Registration failed');
        }
    };

    return (
        <div className="max-w-md mx-auto mt-20 bg-white p-8 rounded-xl shadow-md border border-gray-100">
            <div className="text-center mb-8">
                <h2 className="text-3xl font-serif font-bold text-gray-900">Create Account</h2>
                <p className="text-gray-500">Join TrustLens Pro today</p>
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
                            placeholder="Choose a username"
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
                            placeholder="Choose a secure password"
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <button type="submit" className="w-full py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition flex justify-center items-center gap-2">
                    <UserPlus className="h-5 w-5" /> Register
                </button>
            </form>

            <p className="mt-6 text-center text-sm text-gray-600">
                Already have an account? <Link to="/login" className="text-blue-600 font-medium hover:underline">Login here</Link>
            </p>
        </div>
    );
}
