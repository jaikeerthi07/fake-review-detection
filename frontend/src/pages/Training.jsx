import React, { useState } from 'react';
import client from '../api/config';
import { Play, CheckCircle, BarChart as IconBarChart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Training() {
    const [training, setTraining] = useState(false);
    const [metrics, setMetrics] = useState(null);
    const [datasetUploaded, setDatasetUploaded] = useState(false);
    const navigate = useNavigate();

    const startTraining = async () => {
        setTraining(true);
        try {
            const res = await client.post('/api/train', {
                text_column: 'review_text',
                label_column: 'label'
            });
            setMetrics(res.data.metrics);
        } catch (err) {
            console.error(err);
            alert("Training failed.");
        } finally {
            setTraining(false);
        }
    };

    // Prepare data for Comparison Chart
    const getComparisonData = () => {
        if (!metrics) return [];
        return Object.keys(metrics).map(model => ({
            name: model,
            Accuracy: (metrics[model].accuracy * 100).toFixed(1),
            Precision: (metrics[model].precision * 100).toFixed(1),
            Recall: (metrics[model].recall * 100).toFixed(1)
        }));
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8 p-6">
            <div className="text-center">
                <h2 className="text-3xl font-serif font-bold text-gray-900">Model Training Hub</h2>
                <p className="text-gray-500 mt-2">Train classifiers and compare their performance with advanced metrics.</p>
            </div>

            {!metrics && (
                <div className="flex flex-col items-center gap-8 py-8">
                    {/* File Upload Section */}
                    <div className="w-full max-w-md">
                        <label className="block text-sm font-medium text-gray-700 mb-2">1. Upload Dataset (CSV)</label>
                        <div className="flex items-center justify-center w-full">
                            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                    <svg className="w-8 h-8 mb-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                        <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2" />
                                    </svg>
                                    <p className="mb-2 text-sm text-gray-500"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                                    <p className="text-xs text-gray-500">CSV file (text, label columns)</p>
                                </div>
                                <input
                                    type="file"
                                    accept=".csv"
                                    className="hidden"
                                    onChange={async (e) => {
                                        const file = e.target.files[0];
                                        if (file) {
                                            const formData = new FormData();
                                            formData.append('file', file);
                                            try {
                                                const res = await client.post('/api/upload', formData);
                                                alert(`Dataset uploaded: ${res.data.filename}`);
                                                setDatasetUploaded(true);
                                            } catch (err) {
                                                alert("Upload failed");
                                            }
                                        }
                                    }}
                                />
                            </label>
                        </div>
                    </div>

                    {/* Start Training Button */}
                    <button
                        onClick={startTraining}
                        disabled={training || !datasetUploaded}
                        className={`px-10 py-4 text-white text-xl font-semibold rounded-full shadow-xl transition flex items-center gap-3 ${!datasetUploaded
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-indigo-600 hover:bg-indigo-700'
                            }`}
                    >
                        {training ? (
                            <>
                                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Training Models...
                            </>
                        ) : (
                            <>
                                <Play className="h-6 w-6" /> 2. Start Training Pipeline
                            </>
                        )}
                    </button>
                    {!datasetUploaded && <p className="text-sm text-red-500">Please upload a dataset first.</p>}
                </div>
            )}

            {metrics && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-12">

                    {/* 1. Comparison Chart */}
                    <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
                        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                            <IconBarChart className="h-5 w-5 text-indigo-500" /> Model Comparison
                        </h3>
                        <div className="h-80 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={getComparisonData()} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} />
                                    <YAxis axisLine={false} tickLine={false} domain={[0, 100]} />
                                    <Tooltip
                                        cursor={{ fill: '#f3f4f6' }}
                                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                                    />
                                    <Legend />
                                    <Bar dataKey="Accuracy" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="Precision" fill="#10b981" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="Recall" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* 2. Detailed Metrics & Confusion Matrix */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {Object.entries(metrics).map(([model, scores]) => (
                            <div key={model} className="bg-white p-6 rounded-2xl shadow border border-gray-100 flex flex-col h-full">
                                <h3 className="font-bold text-lg text-gray-800 mb-4 border-b pb-2">{model}</h3>

                                {/* Metrics */}
                                <div className="space-y-4 mb-6 flex-grow">
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-500">Accuracy</span>
                                        <span className="text-2xl font-bold text-gray-900">{(scores.accuracy * 100).toFixed(1)}%</span>
                                    </div>
                                    <div className="w-full bg-gray-100 rounded-full h-1.5">
                                        <div className="bg-indigo-600 h-1.5 rounded-full" style={{ width: `${scores.accuracy * 100}%` }}></div>
                                    </div>
                                </div>

                                {/* Confusion Matrix */}
                                {scores.cm && (
                                    <div className="mt-4">
                                        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Confusion Matrix</h4>
                                        <div className="grid grid-cols-2 gap-1 text-center text-sm">
                                            {/* Labels */}
                                            <div className="col-span-2 grid grid-cols-2 text-xs text-gray-400 mb-1">
                                                <span>Pred: Fake</span>
                                                <span>Pred: Real</span>
                                            </div>

                                            {/* Row 1: Actual Fake (CG) */}
                                            <div className="bg-red-50 p-2 rounded border border-red-100">
                                                <div className="text-red-800 font-bold">{scores.cm[0][0]}</div>
                                                <div className="text-[10px] text-red-400">True Fake</div>
                                            </div>
                                            <div className="bg-gray-50 p-2 rounded border border-gray-100">
                                                <div className="text-gray-800 font-bold">{scores.cm[0][1]}</div>
                                                <div className="text-[10px] text-gray-400">False Real</div>
                                            </div>

                                            {/* Row 2: Actual Real (OR) */}
                                            <div className="bg-gray-50 p-2 rounded border border-gray-100">
                                                <div className="text-gray-800 font-bold">{scores.cm[1][0]}</div>
                                                <div className="text-[10px] text-gray-400">False Fake</div>
                                            </div>
                                            <div className="bg-green-50 p-2 rounded border border-green-100">
                                                <div className="text-green-800 font-bold">{scores.cm[1][1]}</div>
                                                <div className="text-[10px] text-green-400">True Real</div>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 text-xs text-gray-400 mt-1">
                                            <span className="-rotate-90 origin-center translate-y-[-20px] absolute -left-4">Actual</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="flex justify-center mt-8 gap-4">
                        <button
                            onClick={() => navigate('/analyze/single')}
                            className="px-6 py-3 bg-blue-600 text-white font-bold rounded-lg shadow-md hover:bg-blue-700 transition transform hover:scale-105 flex items-center gap-2"
                        >
                            <CheckCircle className="h-5 w-5" /> Check Single Prediction
                        </button>
                        <button
                            onClick={() => navigate('/analyze/url')}
                            className="px-6 py-3 bg-purple-600 text-white font-bold rounded-lg shadow-md hover:bg-purple-700 transition transform hover:scale-105 flex items-center gap-2"
                        >
                            <CheckCircle className="h-5 w-5" /> Check Live URL
                        </button>
                        <button
                            onClick={() => navigate('/select-method')}
                            className="px-6 py-3 bg-green-600 text-white font-bold rounded-lg shadow-md hover:bg-green-700 transition transform hover:scale-105 flex items-center gap-2"
                        >
                            <CheckCircle className="h-5 w-5" /> Continue to Analysis
                        </button>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
