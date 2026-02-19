import React, { useEffect, useState } from 'react';
import client from '../api/config';
import { ArrowRight, Table } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Preview() {
    const [data, setData] = useState([]);
    const [columns, setColumns] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await client.get('/api/preview');
                if (res.data.data.length > 0) {
                    setData(res.data.data);
                    setColumns(Object.keys(res.data.data[0]));
                }
            } catch (err) {
                console.error(err);
                alert("Failed to load preview. Ensure dataset is uploaded.");
            }
        };
        fetchData();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold font-serif text-gray-800 flex items-center gap-2">
                    <Table className="h-6 w-6 text-blue-500" /> Data Preview
                </h2>
                <button
                    onClick={() => navigate('/training')}
                    className="px-6 py-2 bg-green-600 text-white rounded-lg flex items-center gap-2 hover:bg-green-700 transition"
                >
                    Proceed to Training <ArrowRight className="h-4 w-4" />
                </button>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                {columns.map(col => (
                                    <th key={col} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{col}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {data.map((row, idx) => (
                                <tr key={idx} className="hover:bg-gray-50">
                                    {columns.map(col => (
                                        <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 max-w-xs truncate">{row[col]}</td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
