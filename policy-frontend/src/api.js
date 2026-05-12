import axios from 'axios';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8080/api";

// Ensure the baseURL ends with /api to match your FastAPI routes
const API = axios.create({ 
    baseURL: apiBaseUrl 
});

/**
 * AUTHENTICATION
 * Checks against policy_db.users table
 */
export const loginUser = async (username, password) => {
    // Keys MUST be 'username' and 'password' to match Pydantic LoginRequest
    const response = await API.post("/auth/login", { username, password });
    return response.data;
};

/**
 * POLICY EVALUATION
 * Triggers the RAG engine (Logic.py)
 */
export const evaluatePolicy = async (question, domain, userId) => {
    const response = await API.post("/policy/evaluate", { 
        question, 
        domain, 
        user_id: userId 
    });
    return response.data;
};

/**
 * ADMIN METRICS
 * Fetches dashboard intelligence for Managers
 */
export const getAdminMetrics = async () => {
    const response = await API.get("/admin/metrics");
    return response.data;
};

/**
 * AUDIT HISTORY
 * Fetches the global audit log for the History tab
 */
export const getAuditHistory = async () => {
    const response = await API.get("/policy/history");
    return response.data;
};

/**
 * USER FEEDBACK
 * Records whether the AI explanation was clear
 */
export const submitFeedback = async (queryId, rating, comments) => {
    const response = await API.post("/policy/feedback", { 
        query_id: queryId, 
        clarity_rating: rating, 
        comments 
    });
    return response.data;
};

export default API;