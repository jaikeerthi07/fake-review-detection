import axios from 'axios';

// Automatically detect environment
// In Vite, import.meta.env.PROD is true during production build
const IS_PROD = import.meta.env.PROD;

// If you want to force a specific URL in production, set VITE_API_URL in Render
const API_URL = import.meta.env.VITE_API_URL || (IS_PROD ? 'https://fake-review-detection-backend.onrender.com' : '/api');

console.log(`API Configuration: ${IS_PROD ? 'Production' : 'Development'} Mode`);
console.log(`Base URL: ${API_URL}`);

const client = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to include JWT token if available
client.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default client;
