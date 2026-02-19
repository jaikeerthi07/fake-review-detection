import React from 'react';
import { AlertTriangle, Zap, MessageSquare, Volume2, Tag, Info } from 'lucide-react';

const MetricBar = ({ label, value, color, icon: Icon, description }) => (
    <div className="mb-4 group relative">
        <div className="flex justify-between items-center mb-1">
            <div className="flex items-center gap-2">
                <Icon className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">{label}</span>
                <div className="group-hover:opacity-100 opacity-0 transition-opacity absolute left-0 -top-8 bg-gray-800 text-white text-xs p-2 rounded z-10 w-48 text-center pointer-events-none">
                    {description}
                </div>
            </div>
            <span className={`text-sm font-bold ${value > 50 ? 'text-red-500' : 'text-gray-600'}`}>
                {value.toFixed(0)}%
            </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
                className={`h-2.5 rounded-full transition-all duration-500 ${color}`}
                style={{ width: `${Math.min(value, 100)}%` }}
            ></div>
        </div>
    </div>
);

export default function LieDetectionCard({ data }) {
    if (!data) return null;

    // Calculate an overall risk score based on the sub-metrics
    const riskScore = Math.min(100, (
        (data.deception_score || 0) +
        (data.exaggeration_score || 0) +
        (data.promotional_score || 0) +
        (data.repetition_score || 0)
    ) / 2.5); // Heuristic normalization

    return (
        <div className="bg-white p-6 rounded-xl shadow border border-gray-100 relative overflow-hidden">
            <div className={`absolute top-0 right-0 p-2 rounded-bl-xl text-xs font-bold text-white ${riskScore > 50 ? 'bg-red-500' : 'bg-green-500'}`}>
                Risk: {riskScore.toFixed(0)}%
            </div>

            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Zap className="text-purple-600" /> AI Lie Detection Engine
            </h3>

            <div className="space-y-2">
                <MetricBar
                    label="Deceptive Patterns"
                    value={data.deception_score}
                    color="bg-red-500"
                    icon={AlertTriangle}
                    description="Detects phrases often used to manipulate trust (e.g., 'Trust me', 'Honestly')."
                />
                <MetricBar
                    label="Exaggeration"
                    value={data.exaggeration_score}
                    color="bg-orange-500"
                    icon={Volume2}
                    description="Measures excessive use of superlatives (e.g., 'Best ever', 'Amazing')."
                />
                <MetricBar
                    label="Emotional Intensity"
                    value={data.emotional_intensity}
                    color="bg-blue-500"
                    icon={Zap}
                    description="High intensity often correlates with fake negative reviews."
                />
                <MetricBar
                    label="Repetition"
                    value={data.repetition_score}
                    color="bg-yellow-500"
                    icon={MessageSquare}
                    description="Identifies repetitive phrasing common in generated text."
                />
                <MetricBar
                    label="Promotional Content"
                    value={data.promotional_score}
                    color="bg-green-600"
                    icon={Tag}
                    description="Flags marketing calls-to-action (e.g., 'Buy now', 'Check link')."
                />
            </div>
        </div>
    );
}
