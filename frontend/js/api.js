const API_BASE = '';
let apiKey = localStorage.getItem('apiKey') || '';

export function setApiKey(key) {
    apiKey = key;
    localStorage.setItem('apiKey', key);
}

async function apiRequest(endpoint, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (apiKey) headers['X-API-Key'] = apiKey;

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(err.detail || `Request failed (${response.status})`);
    }

    if (endpoint.includes('/export') || options.responseType === 'blob') {
        return response;
    }

    return response.json();
}

export const api = {
    predict: (data) => apiRequest('/predict', {
        method: 'POST',
        body: JSON.stringify(data),
    }),

    predictBatch: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const headers = {};
        if (apiKey) headers['X-API-Key'] = apiKey;
        return fetch(`${API_BASE}/predict/batch`, {
            method: 'POST',
            body: formData,
            headers,
        }).then(async (res) => {
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                throw new Error(err.detail || `Batch request failed (${res.status})`);
            }
            return res.json();
        });
    },

    dashboard: {
        stats: () => apiRequest('/dashboard/stats'),
        history: (limit = 100, offset = 0) =>
            apiRequest(`/dashboard/history?limit=${limit}&offset=${offset}`),
        export: () => apiRequest('/dashboard/history/export'),
    },

    train: {
        start: () => apiRequest('/train', { method: 'POST' }),
        status: () => apiRequest('/train/status'),
    },

    health: () => apiRequest('/health'),
    models: () => apiRequest('/train/models'),
    rollback: (versionId) => apiRequest(`/train/rollback/${versionId}`, { method: 'POST' }),
    drift: (window = 100, baseline = 500) =>
        apiRequest(`/drift?window=${window}&baseline=${baseline}`),
};
