import React, { useState, useEffect } from 'react';
import client from '../api/config';
import { Globe, PlayCircle, Download, ShieldCheck, BarChart2, PieChart as PieIcon, FileText } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import LieDetectionCard from '../components/LieDetectionCard';
import WritingStyleCard from '../components/WritingStyleCard';

export default function UrlAnalysis() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [reviews, setReviews] = useState([]);
    const [results, setResults] = useState(null);
    const [csvFilename, setCsvFilename] = useState(null);
    const [selectedReview, setSelectedReview] = useState(null);

    useEffect(() => {
        console.log("UrlAnalysis Mounted");
    }, []);

    const handleScrape = async () => {
        if (!url) return;
        setLoading(true);
        setResults(null);
        setCsvFilename(null);
        try {
            const res = await client.post('/api/scrape', { url });
            setReviews(res.data.reviews || []);
            if (res.data.csv_saved) {
                setCsvFilename(res.data.csv_saved);
                alert(`Success! Reviews saved to ${res.data.csv_saved}`);
            }
        } catch (err) {
            console.error(err);
            const errorMsg = err.response?.data?.error || "Scraping failed. Check URL or try another source.";
            alert(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyzeAll = async () => {
        if (reviews.length === 0) return;
        setLoading(true);
        try {
            const res = await client.post('/api/predict_bulk', { reviews });
            setResults(res.data.results);
        } catch (err) {
            console.error(err);
            if (err.message === 'Network Error') {
                alert(`Network Error! Tried to reach: ${client.defaults.baseURL}/api/predict_bulk`);
            } else {
                alert(`Analysis failed: ${err.response?.data?.error || err.message}`);
            }
        } finally {
            setLoading(false);
        }
    };

    const handlePrint = () => {
        window.print();
    };

    const handleDownloadReport = async () => {
        if (!results) return;
        try {
            const avgTrust = results.reduce((acc, r) => acc + (r.trust_score || 0), 0) / (results.length || 1);

            const res = await client.post('/api/report/generate', {
                title: "TrustLens Analysis Report",
                url: url,
                trust_score: Math.round(avgTrust),
                reviews: results,
                keywords: ["quality", "shipping", "value"] // Placeholder for now
            });

            if (res.data.filename) {
                // Open download link
                window.open(`/api/download/${res.data.filename}`, '_blank');
            }
        } catch (err) {
            console.error(err);
            alert("Failed to generate report.");
        }
    };

    // Prepare Chart Data
    const getPieData = () => {
        if (!results) return [];
        const counts = results.reduce((acc, r) => {
            acc[r.label] = (acc[r.label] || 0) + 1;
            return acc;
        }, {});
        return Object.keys(counts).map(key => ({ name: key, value: counts[key] }));
    };

    // Prepare Trend Data
    const getTrendData = () => {
        if (!results) return [];
        // Filter items with dates
        const withDates = results.filter(r => r.date);

        // Return empty if no dates
        if (withDates.length === 0) {
            // Fallback: use index as sequence
            return results.map((r, i) => ({
                name: `Review ${i + 1}`,
                trust_score: r.trust_score || 0,
                sentiment: r.sentiment || 0
            }));
        }

        // Sort by date
        withDates.sort((a, b) => new Date(a.date) - new Date(b.date));

        // Simply returning the sequence for now as "Review Index" or try to group
        // For simplicity in this version, we map index to trust score to show "Review Sequence"
        return withDates.map((r, i) => ({
            name: r.date || `Review ${i + 1}`,
            trust_score: r.trust_score || 0,
            sentiment: r.sentiment || 0
        }));
    };

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    const [filter, setFilter] = useState('All');

    // Filter and Sort Results (Fakes First)
    const getFilteredResults = () => {
        if (!results) return [];
        let filtered = [...results];

        // Filter
        if (filter !== 'All') {
            const target = filter === 'Fake' ? ['Fake', 'CG'] : ['Real', 'OR'];
            filtered = filtered.filter(r => target.includes(r.label));
        }

        // Sort: Trust Score Ascending (Low Trust/Fake First)
        return filtered.sort((a, b) => (a.trust_score || 0) - (b.trust_score || 0));
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4 print:p-0">
            <div className="max-w-6xl mx-auto space-y-8">
                <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 print:hidden">
                    <h2 className="text-2xl font-serif font-bold text-gray-900 mb-6 flex items-center gap-3">
                        <Globe className="text-blue-600" /> Live URL Analysis
                    </h2>

                    <p className="text-gray-400 mb-8">
                        Supported Platforms: <span className="font-semibold text-white">Amazon (Global)</span>
                        <br />
                        <span className="text-sm">For others (Flipkart, etc.), please use the Manual Entry tab.</span>
                    </p>
                    <div className="flex gap-4">
                        <input
                            type="url"
                            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Paste product URL (Amazon, Flipkart, etc.)"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                        />
                        <button
                            onClick={handleScrape}
                            disabled={loading || !url}
                            className="px-6 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400"
                        >
                            {loading ? 'Processing...' : 'Fetch Reviews'}
                        </button>
                    </div>
                </div>

                {reviews.length > 0 && !results && (
                    <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden print:hidden">
                        <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                            <h3 className="font-bold text-gray-700">Extracted Reviews ({reviews.length})</h3>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={handleAnalyzeAll}
                                    disabled={loading}
                                    className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 flex items-center gap-2"
                                >
                                    <PlayCircle className="h-4 w-4" /> Analyze All
                                </button>
                                {csvFilename && (
                                    <button
                                        onClick={() => window.open(`/api/download/${csvFilename}`, '_blank')}
                                        className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 flex items-center gap-2"
                                    >
                                        <Download className="h-4 w-4" /> Download CSV
                                    </button>
                                )}
                            </div>
                        </div>
                        <div className="p-4 max-h-60 overflow-y-auto space-y-2">
                            {reviews.slice(0, 5).map((r, idx) => (
                                <div key={idx} className="p-3 bg-gray-50 rounded text-sm text-gray-600 truncate">"{r.text || r}"</div>
                            ))}
                            {reviews.length > 5 && <div className="text-center text-xs text-gray-400">...and {reviews.length - 5} more</div>}
                        </div>
                    </div>
                )}

                {results && (
                    <div className="space-y-8 animate-fade-in print:block">
                        {/* Header for Print */}
                        <div className="hidden print:block text-center mb-8">
                            <h1 className="text-2xl font-bold">TrustLens URL Analysis Report</h1>
                            <p className="text-gray-500">Source: {url}</p>
                            <p className="text-sm text-gray-400">Generated on {new Date().toLocaleDateString()}</p>
                        </div>

                        {/* Summary Statistics */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Total Reviews - Blue */}
                            <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl shadow-lg shadow-blue-200 text-white flex flex-col items-center justify-center transform transition-all hover:scale-105 duration-300">
                                <div className="flex items-center gap-2 mb-2 opacity-90">
                                    <BarChart2 className="h-6 w-6" />
                                    <span className="text-2xl font-bold">{results.length}</span>
                                </div>
                                <h3 className="font-medium text-blue-50 tracking-wide">Total Reviews Analyzed</h3>
                            </div>

                            {/* Genuine Reviews - Green */}
                            <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 p-6 rounded-xl shadow-lg shadow-emerald-200 text-white flex flex-col items-center justify-center transform transition-all hover:scale-105 duration-300">
                                <div className="flex items-center gap-2 mb-2 opacity-90">
                                    <ShieldCheck className="h-6 w-6" />
                                    <span className="text-2xl font-bold">
                                        {results.filter(r => ['Real', 'OR'].includes(r.label)).length}
                                    </span>
                                </div>
                                <h3 className="font-medium text-emerald-50 tracking-wide">Genuine Reviews</h3>
                            </div>

                            {/* Fake Reviews - Red */}
                            <div className="bg-gradient-to-br from-rose-500 to-rose-600 p-6 rounded-xl shadow-lg shadow-rose-200 text-white flex flex-col items-center justify-center transform transition-all hover:scale-105 duration-300">
                                <div className="flex items-center gap-2 mb-2 opacity-90">
                                    <PieIcon className="h-6 w-6" />
                                    <span className="text-2xl font-bold">
                                        {results.filter(r => ['Fake', 'CG'].includes(r.label)).length}
                                    </span>
                                </div>
                                <h3 className="font-medium text-rose-50 tracking-wide">Fake Reviews Detected</h3>
                            </div>
                        </div>

                        {/* Visualizations */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 print:break-inside-avoid">
                            {/* Pie Chart */}
                            <div className="bg-white p-6 rounded-xl shadow border border-gray-100">
                                <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2"><PieIcon className="h-5 w-5 text-indigo-500" /> Label Distribution</h3>
                                <div className="h-64">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie data={getPieData()} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" dataKey="value" label>
                                                {getPieData().map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                            <Legend />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Bar Chart - Sentiment */}
                            <div className="bg-white p-6 rounded-xl shadow border border-gray-100">
                                <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2"><BarChart2 className="h-5 w-5 text-green-500" /> Sentiment Analysis</h3>
                                <div className="h-64">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={results.slice(0, 15)}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="label" />
                                            <YAxis />
                                            <Tooltip />
                                            <Legend />
                                            <Bar dataKey="sentiment" fill="#82ca9d" name="Sentiment Score" />
                                            <Bar dataKey="confidence" fill="#8884d8" name="Confidence" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Trend Chart - Enterprise Feature */}
                            <div className="bg-white p-6 rounded-xl shadow border border-gray-100 md:col-span-2">
                                <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                    <BarChart2 className="h-5 w-5 text-purple-500" /> Trust Score Trend
                                </h3>
                                <div className="h-64">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={getTrendData().slice(-20)}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="name" />
                                            <YAxis domain={[0, 100]} />
                                            <Tooltip />
                                            <Legend />
                                            <Line type="monotone" dataKey="trust_score" stroke="#8884d8" name="Trust Score" strokeWidth={2} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>

                        {/* Detailed Table with Filter */}
                        <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
                            <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                                <div className="flex items-center gap-4">
                                    <h3 className="font-bold text-gray-800">Detailed Analysis Results</h3>
                                    <div className="flex rounded-md shadow-sm" role="group">
                                        {['All', 'Fake', 'Real'].map(type => (
                                            <button
                                                key={type}
                                                onClick={() => setFilter(type)}
                                                className={`px-3 py-1 text-sm font-medium border ${filter === type
                                                    ? 'bg-blue-600 text-white border-blue-600'
                                                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                                                    } ${type === 'All' ? 'rounded-l-md' : ''} ${type === 'Real' ? 'rounded-r-md' : ''}`}
                                            >
                                                {type}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <button onClick={handleDownloadReport} className="text-blue-600 hover:text-blue-800 flex items-center gap-1 text-sm font-medium print:hidden">
                                    <FileText className="h-4 w-4" />download Pdf







                                </button>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Review Text</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prediction</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trust Score</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sentiment</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {getFilteredResults().map((row, idx) => (
                                            <tr key={idx} className={`hover:bg-gray-50 ${['Fake', 'CG'].includes(row.label) ? 'bg-red-50' : ''}`}>
                                                <td className="px-6 py-4 text-sm text-gray-600 max-w-md truncate" title={row.text}>{row.text}</td>
                                                <td className="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">{row.date || '-'}</td>
                                                <td className="px-6 py-4 text-sm text-yellow-500 font-bold">{row.rating ? `★ ${row.rating}` : '-'}</td>
                                                <td className="px-6 py-4 text-sm font-bold text-gray-800">
                                                    <span className={`px-2 py-1 rounded-full text-xs ${['Fake', 'CG'].includes(row.label) ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                                                        {row.label === 'CG' ? 'Fake' : (row.label === 'OR' ? 'Real' : row.label)}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-sm font-mono text-blue-600 font-medium">
                                                    {row.trust_score ? row.trust_score.toFixed(1) : 'N/A'}
                                                </td>
                                                <td className="px-6 py-4 text-sm text-gray-600">{(row.sentiment || 0).toFixed(2)}</td>
                                                <td className="px-6 py-4 text-sm">
                                                    <button
                                                        onClick={() => setSelectedReview(row)}
                                                        className="text-purple-600 hover:text-purple-900 font-medium text-xs border border-purple-200 px-3 py-1 rounded bg-purple-50 hover:bg-purple-100"
                                                    >
                                                        Analyze Lies
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                        {getFilteredResults().length === 0 && (
                                            <tr>
                                                <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                                                    No reviews found matching filter "{filter}".
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}

                {/* Lie Analysis Modal */}
                {selectedReview && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 animate-fade-in" onClick={() => setSelectedReview(null)}>
                        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
                            <div className="p-6 border-b border-gray-100 flex justify-between items-center sticky top-0 bg-white z-10">
                                <h3 className="text-xl font-bold font-serif text-gray-800">Advanced Lie Analysis</h3>
                                <button onClick={() => setSelectedReview(null)} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
                            </div>
                            <div className="p-6 space-y-6">
                                <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-700 italic border-l-4 border-blue-400">
                                    "{selectedReview.text}"
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <LieDetectionCard data={selectedReview.lie_detection} />
                                    <WritingStyleCard data={selectedReview.author_dna} />
                                </div>

                                <div className="grid grid-cols-2 gap-4 text-center">
                                    <div className="p-4 bg-gray-50 rounded-lg">
                                        <div className="text-xs text-gray-500 uppercase tracking-wide">Prediction</div>
                                        <div className={`text-lg font-bold ${['Fake', 'CG'].includes(selectedReview.label) ? 'text-red-600' : 'text-green-600'}`}>
                                            {selectedReview.label}
                                        </div>
                                    </div>
                                    <div className="p-4 bg-gray-50 rounded-lg">
                                        <div className="text-xs text-gray-500 uppercase tracking-wide">Trust Score</div>
                                        <div className="text-lg font-bold text-blue-600">{selectedReview.trust_score}%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
