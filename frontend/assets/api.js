// API Client Wrapper for Pain-to-Idea Generator

// Global API Base URL
const API_BASE_URL = 'http://127.0.0.1:8000';

class ApiClient {
    constructor(baseUrl) {
        // Hardcoded for local development
        this.baseUrl = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ message: 'Неизвестная ошибка' }));
                throw new Error(error.message || `HTTP ${response.status}`);
            }

            // Handle different response types
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else if (contentType && contentType.includes('text/markdown')) {
                return await response.blob();
            }

            return response;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // Runs API
    async createRun(optionalDirection = null) {
        return this.request('/api/runs', {
            method: 'POST',
            body: JSON.stringify({
                optional_direction: optionalDirection || undefined
            })
        });
    }

    async getRunStatus(runId) {
        return this.request(`/api/runs/${runId}`);
    }

    async getRunIdeas(runId) {
        return this.request(`/api/runs/${runId}/ideas`);
    }

    // Ideas API
    async getIdeaDetail(ideaId) {
        return this.request(`/api/ideas/${ideaId}`);
    }

    // Export API
    async exportMarkdown(runId, ideaIds = null) {
        return this.request('/api/export/markdown', {
            method: 'POST',
            body: JSON.stringify({
                run_id: runId,
                idea_ids: ideaIds || undefined
            })
        });
    }

    // SSE Progress Stream
    createProgressStream(runId, handlers) {
        const url = `${this.baseUrl}/api/runs/${runId}/progress`;
        const eventSource = new EventSource(url);

        eventSource.addEventListener('progress', (event) => {
            const data = JSON.parse(event.data);
            if (handlers.onProgress) handlers.onProgress(data);
        });

        eventSource.addEventListener('complete', (event) => {
            const data = JSON.parse(event.data);
            eventSource.close();
            if (handlers.onComplete) handlers.onComplete(data);
        });

        eventSource.addEventListener('error', (event) => {
            try {
                const data = JSON.parse(event.data);
                eventSource.close();
                if (handlers.onError) handlers.onError(data);
            } catch (e) {
                eventSource.close();
                if (handlers.onError) {
                    handlers.onError({ error_message: 'Ошибка соединения' });
                }
            }
        });

        return eventSource;
    }
}

// Create global API client instance
window.apiClient = new ApiClient();
