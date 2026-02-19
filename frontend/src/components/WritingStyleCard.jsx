import React from 'react';
import { PenTool, Hash, BookOpen, Percent, Type } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

const StatBox = ({ label, value, icon: Icon, color }) => (
    <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 flex items-center justify-between">
        <div>
            <div className="text-xs text-gray-500 uppercase font-semibold">{label}</div>
            <div className={`text-lg font-bold ${color}`}>{value}</div>
        </div>
        <Icon className={`w-5 h-5 ${color} opacity-80`} />
    </div>
);

export default function WritingStyleCard({ data }) {
    if (!data) return null;

    const radarData = [
        { subject: 'Nouns', A: (data.pos_ratios?.noun || 0) * 100, fullMark: 100 },
        { subject: 'Verbs', A: (data.pos_ratios?.verb || 0) * 100, fullMark: 100 },
        { subject: 'Adjectives', A: (data.pos_ratios?.adj || 0) * 100, fullMark: 100 },
        { subject: 'Exclamations', A: Math.min((data.punctuation?.exclamation_density || 0) * 20, 100), fullMark: 100 }, // Scale up for visibility
        { subject: 'Questions', A: Math.min((data.punctuation?.question_density || 0) * 20, 100), fullMark: 100 },
    ];

    return (
        <div className="bg-white p-6 rounded-xl shadow border border-gray-100 relative overflow-hidden h-full">
            <div className="flex justify-between items-start mb-6">
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                    <PenTool className="text-indigo-600" /> Writing Fingerprint
                </h3>
                <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-bold rounded-full border border-indigo-200">
                    {data.style_label}
                </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 gap-3">
                    <StatBox
                        label="Avg Sentence Length"
                        value={data.avg_sentence_len}
                        icon={Type}
                        color="text-blue-600"
                    />
                    <StatBox
                        label="Vocabulary Diversity"
                        value={`${(data.vocab_diversity * 100).toFixed(0)}%`}
                        icon={BookOpen}
                        color="text-green-600"
                    />
                    <StatBox
                        label="Stopword Ratio"
                        value={`${(data.stopword_ratio * 100).toFixed(0)}%`}
                        icon={Hash}
                        color="text-gray-600"
                    />
                </div>

                {/* Radar Chart */}
                <div className="h-48 relative">
                    <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                            <PolarGrid stroke="#e5e7eb" />
                            <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 10 }} />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                            <Radar
                                name="Style"
                                dataKey="A"
                                stroke="#6366f1"
                                strokeWidth={2}
                                fill="#818cf8"
                                fillOpacity={0.4}
                            />
                        </RadarChart>
                    </ResponsiveContainer>
                    <div className="absolute bottom-0 w-full text-center text-xs text-gray-400">
                        Grammar & Punctuation Profile
                    </div>
                </div>
            </div>
        </div>
    );
}
