import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';

export default function Charts() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const res = await axios.get('http://localhost:5001/api/analytics');
                setData(res.data);
                setLoading(false);
            } catch (err) {
                console.error(err);
                setError("Failed to load analytics data. Please ensure a dataset is uploaded.");
                setLoading(false);
            }
        };
        fetchAnalytics();
    }, []);

    if (loading) return <div className="text-center mt-20 text-gray-600">Loading charts...</div>;
    if (error) return <div className="text-center mt-20 text-red-500">{error}</div>;
    if (!data) return <div className="text-center mt-20 text-gray-500">No data available</div>;

    // Prepare Data for Recharts
    const authData = Object.keys(data.authenticity || {}).map(key => ({
        name: key === 'OR' ? 'Real' : 'Fake',
        value: data.authenticity[key]
    }));

    const sentenceData = Object.keys(data.sentence_distribution || {}).map(key => ({
        range: key,
        count: data.sentence_distribution[key]
    }));

    // ratingData now receives [{rating: '1', Real: 10, Fake: 20}, ...] from backend
    const ratingData = data.rating_distribution || [];

    const AUTH_COLORS = ['#4ade80', '#f87171']; // Green for Real, Red for Fake if mapped correctly

    return (
        <div className="space-y-8 fade-in pb-12">
            <h1 className="text-3xl font-bold text-gray-800 text-center font-serif mb-8">Dataset Analytics</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* 1. Review Authenticity */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 text-center">Review Authenticity</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={authData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {authData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.name === 'Real' ? '#4ade80' : '#f87171'} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* 2. Vocabulary Richness */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col justify-center items-center">
                    <h3 className="text-lg font-semibold mb-4">Vocabulary Richness</h3>
                    <div className="text-5xl font-bold text-blue-600 mb-2">
                        {((data.vocabulary_richness || 0) * 100).toFixed(1)}%
                    </div>
                    <p className="text-gray-500 text-center">
                        Average Type-Token Ratio (Unique Words / Total Words)
                    </p>
                    <p className="text-sm text-gray-400 mt-4 text-center px-8">
                        Higher richness often indicates more complex and varied language usage.
                    </p>
                </div>

                {/* 3. Sentence Count Distribution */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 text-center">Sentence Count Distribution</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart
                                data={sentenceData}
                                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="range" />
                                <YAxis />
                                <Tooltip />
                                <Area type="monotone" dataKey="count" stroke="#8884d8" fill="#8884d8" name="Reviews" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* 4. Rating vs Authenticity Distribution */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 text-center">Rating vs Review Authenticity</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={ratingData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="rating" />
                                <YAxis />
                                <Tooltip cursor={{ fill: 'transparent' }} />
                                <Legend />
                                <Bar dataKey="Fake" stackId="a" fill="#f87171" name="Fake Reviews" />
                                <Bar dataKey="Real" stackId="a" fill="#4ade80" name="Real Reviews" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}
