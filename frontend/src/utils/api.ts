/**
 * api.ts - Generic API Client
 *
 * Provides a simple wrapper around fetch for making API requests.
 * Automatically handles JSON serialization and error handling.
 */

import { authService } from '../services/authService';

const API_BASE_URL = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    // Merge auth headers with any custom headers
    const authHeaders = authService.getAuthHeaders();
    const headers = {
        ...authHeaders, // 'Content-Type': 'application/json', 'Authorization': ...
        ...options?.headers as Record<string, string>,
    };

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'API request failed');
    }

    return response.json();
}

export const api = {
    get: <T>(endpoint: string) => request<T>(endpoint, { method: 'GET' }),
    post: <T>(endpoint: string, body?: any) => request<T>(endpoint, {
        method: 'POST',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' }
    }),
    put: <T>(endpoint: string, body?: any) => request<T>(endpoint, {
        method: 'PUT',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' }
    }),
    delete: <T>(endpoint: string) => request<T>(endpoint, { method: 'DELETE' }),
};
