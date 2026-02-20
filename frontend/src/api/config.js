import axios from 'axios';

// Automatically detect environment
// In Vite, import.meta.env.PROD is true during production build
const IS_PROD = import.meta.env.PROD;

// Render provides just the hostname (e.g., app.onrender.com) via 'host' property
let envApiUrl = import.meta.env.VITE_API_URL;
if (envApiUrl && !envApiUrl.startsWith('http')) {
    envApiUrl = `https://${envApiUrl}`;
}

const API_URL = envApiUrl || (IS_PROD ? 'https://fake-review-backend.onrender.com' : '');

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
