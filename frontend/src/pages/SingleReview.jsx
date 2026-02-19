import React, { useState } from 'react';
import axios from 'axios';
import { Search, AlertTriangle, CheckCircle, BarChart as IconBarChart, PieChart as IconPieChart, ShieldCheck, Activity, Download } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

const MODELS = ['SVM', 'NaiveBayes', 'LogisticRegression'];

export default function SingleReview() {
    const [text, setText] = useState('');
    const [model, setModel] = useState('SVM');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleAnalyze = async () => {
        if (!text) return;
        setLoading(true);
        try {
            const res = await axios.post('http://localhost:5001/api/predict', {
                text,
                model
            });
            setResult(res.data);
        } catch (err) {
            console.error(err);
            alert("Analysis failed");
        } finally {
            setLoading(false);
        }
    };

    const handlePrint = () => {
        window.print();
    };

    const getPieData = () => {
        if (!result || !result.probs) return [];
        return Object.entries(result.probs).map(([key, value]) => ({ name: key, value: value }));
    };

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    return (
        <div className="max-w-5xl mx-auto space-y-8 p-4 print:p-0">
            <div className="text-center space-y-2 print:hidden">
                <h2 className="text-3xl font-serif font-bold text-gray-900">Single Review Prediction</h2>
                <p className="text-gray-500">Fake Review Detection & Advanced Analytics</p>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 print:hidden">
                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Enter Review Text:</label>
                        <textarea
                            rows="4"
                            className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                            placeholder="Paste or type the review text here..."
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                            required
                        ></textarea>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Select Primary Model:</label>
                            <select
                                value={model}
                                onChange={(e) => setModel(e.target.value)}
                                className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="" disabled>-- Choose Model --</option>
                                {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
                            </select>
                        </div>
                        <button
                            onClick={handleAnalyze}
                            disabled={loading || !text}
                            className="w-full py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition shadow flex justify-center items-center gap-2 mt-auto"
                        >
                            {loading ? 'Analyzing...' : <><Search className="h-5 w-5" /> Analyze Review</>}
                        </button>
                    </div>
                </div>
            </div>

            {result && (
                <div className="space-y-8 animate-fade-in print:block">
                    {/* Header for Print */}
                    <div className="hidden print:block text-center mb-8">
                        <h1 className="text-2xl font-bold">TrustLens Analysis Report</h1>
                        <p className="text-gray-500">Generated on {new Date().toLocaleDateString()}</p>
                    </div>

                    {/* Main Verdict & Trust Score */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Verdict */}
                        <div className={`col-span-2 p-6 rounded-xl border-l-4 shadow-md ${['Fake', 'CG'].includes(result.label) ? 'bg-red-50 border-red-500' : 'bg-green-50 border-green-500'}`}>
                            <div className="flex items-start gap-4">
                                <div className={`p-3 rounded-full ${['Fake', 'CG'].includes(result.label) ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>
                                    {['Fake', 'CG'].includes(result.label) ? <AlertTriangle className="h-8 w-8" /> : <CheckCircle className="h-8 w-8" />}
                                </div>
                                <div>
                                    <h3 className={`text-xl font-bold ${['Fake', 'CG'].includes(result.label) ? 'text-red-800' : 'text-green-800'}`}>
                                        Prediction: {result.label}
                                    </h3>
                                    <p className="text-gray-600 mt-1">
                                        Primary verification complete. {['Fake', 'CG'].includes(result.label) ? 'Caution advised.' : 'Appears authentic.'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Trust Score */}
                        <div className="bg-white p-6 rounded-xl shadow border border-gray-100 flex flex-col justify-center items-center text-center">
                            <div className="flex items-center gap-2 mb-2 text-gray-500 font-medium">
                                <ShieldCheck className="h-5 w-5 text-blue-500" /> Trust Score
                            </div>
                            <div className="relative w-32 h-32 flex items-center justify-center">
                                <svg className="w-full h-full" viewBox="0 0 36 36">
                                    <path className="text-gray-200" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
                                    <path className={`${result.trust_score > 70 ? 'text-green-500' : result.trust_score > 40 ? 'text-yellow-500' : 'text-red-500'}`}
                                        strokeDasharray={`${result.trust_score}, 100`}
                                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                        fill="none" stroke="currentColor" strokeWidth="3" />
                                </svg>
                                <div className="absolute text-2xl font-bold text-gray-800">{result.trust_score}</div>
                            </div>
                        </div>
                    </div>

                    {/* Consensus & Charts */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Model Consensus */}
                        <div className="bg-white p-6 rounded-xl shadow border border-gray-100">
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2"><Activity className="h-5 w-5 text-purple-500" /> Model Consensus</h3>
                            <div className="space-y-3">
                                {result.consensus && Object.entries(result.consensus).map(([mName, mPred]) => (
                                    <div key={mName} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                        <span className="text-sm font-medium text-gray-700">{mName}</span>
                                        <span className={`text-sm font-bold px-3 py-1 rounded-full ${['Fake', 'CG'].includes(mPred) ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>
                                            {mPred}
                                        </span>
                                    </div>
                                ))}
                                {!result.consensus && <p className="text-gray-400 text-sm italic">Consensus data unavailable.</p>}
                            </div>
                        </div>

                        {/* Sentiment Chart */}
                        <div className="bg-white p-6 rounded-xl shadow border border-gray-100">
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2"><IconBarChart className="h-5 w-5 text-green-500" /> Sentiment Analysis</h3>
                            <div className="h-48">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart layout="vertical" data={[{ name: 'Sentiment', score: result.sentiment }]}>
                                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                        <XAxis type="number" domain={[-1, 1]} hide />
                                        <YAxis dataKey="name" type="category" hide />
                                        <Tooltip />
                                        <Bar dataKey="score" fill={result.sentiment >= 0 ? '#82ca9d' : '#ff7f7f'} barSize={30} radius={[0, 4, 4, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                                <div className="text-center mt-2 text-sm text-gray-500">
                                    Polarity: {result.sentiment.toFixed(2)} ({-1} to {1})
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Detailed Table */}
                    <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
                        <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                            <h3 className="font-bold text-gray-800">Analysis Details</h3>
                            <button onClick={handlePrint} className="text-blue-600 hover:text-blue-800 flex items-center gap-1 text-sm font-medium print:hidden">
                                <Download className="h-4 w-4" /> Download Report
                            </button>
                        </div>
                        <table className="min-w-full divide-y divide-gray-200">
                            <tbody className="bg-white divide-y divide-gray-200">
                                <tr>
                                    <td className="px-6 py-4 text-sm font-medium text-gray-900">Review Length</td>
                                    <td className="px-6 py-4 text-sm text-gray-600">{text.length} characters</td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 text-sm font-medium text-gray-900">Confidence</td>
                                    <td className="px-6 py-4 text-sm text-gray-600">{(result.confidence * 100).toFixed(2)}%</td>
                                </tr>
                                <tr>
                                    <td className="px-6 py-4 text-sm font-medium text-gray-900">Probabilities</td>
                                    <td className="px-6 py-4 text-sm text-gray-600">
                                        {result.probs ? Object.entries(result.probs).map(([k, v]) => `${k}: ${(v * 100).toFixed(1)}%`).join(', ') : 'N/A'}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
