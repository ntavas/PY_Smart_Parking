const API_BASE_URL = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options?.headers,
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
    post: <T>(endpoint: string, body?: any) => request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) }),
    put: <T>(endpoint: string, body?: any) => request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
    delete: <T>(endpoint: string) => request<T>(endpoint, { method: 'DELETE' }),
};
