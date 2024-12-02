'use client';

import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

export interface ApiError {
    message: string;
    status: number;
    errors?: Record<string, string[]>;
}

interface ApiErrorResponse {
    detail?: string;
    message?: string;
    error?: string;
    errors?: Record<string, string[]>;
}

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});


// Request interceptor
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // Удалить слеш в конце URL, если он есть
        if (config.url?.endsWith('/')) {
            config.url = config.url.slice(0, -1);
        }

        // Get CSRF token from cookie if it exists
        const csrfToken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];

        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken;
        }

        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError<ApiErrorResponse>) => {
        const apiError: ApiError = {
            message: 'An error occurred',
            status: error.response?.status || 500,
        };

        if (error.response?.data) {
            const data = error.response.data;

            if (typeof data === 'string') {
                apiError.message = data;
            } else {
                if (data.detail) {
                    apiError.message = data.detail;
                } else if (data.message) {
                    apiError.message = data.message;
                } else if (data.error) {
                    apiError.message = data.error;
                }

                if (data.errors) {
                    apiError.errors = data.errors;
                }
            }
        }

        // Handle authentication errors
        if (error.response?.status === 401 || error.response?.status === 403) {
            // Redirect to login page if not authenticated
            if (typeof window !== 'undefined') {
                window.location.href = '/auth/login';
            }
        }

        return Promise.reject(apiError);
    }
);

export { api };