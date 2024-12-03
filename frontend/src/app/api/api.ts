// src/app/api/api.ts
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
        // Ensure URL ends with slash for Django
        if (config.url && !config.url.endsWith('/')) {
            config.url += '/';
        }

        // Get CSRF token from cookie if it exists
        const csrfToken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];

        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken;
        }

        // Get access token from localStorage
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

// Flag to prevent multiple redirects
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (value?: unknown) => void;
    reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });

    failedQueue = [];
};

// Response interceptor
api.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError<ApiErrorResponse>) => {
        const originalRequest = error.config;

        // Проверяем, что это ошибка авторизации и у нас есть конфиг запроса
        if (error.response?.status === 401 && originalRequest) {
            if (!isRefreshing) {
                isRefreshing = true;

                try {
                    const refreshToken = localStorage.getItem('refresh_token');
                    if (!refreshToken) {
                        throw new Error('No refresh token');
                    }

                    // Пытаемся обновить токен
                    const response = await axios.post(
                        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/users/auth/refresh/`,
                        { refresh: refreshToken },
                        { withCredentials: true }
                    );

                    const { access } = response.data;
                    localStorage.setItem('access_token', access);

                    // Обновляем токен в оригинальном запросе
                    if (originalRequest.headers) {
                        originalRequest.headers.Authorization = `Bearer ${access}`;
                    }

                    processQueue(null, access);
                    return axios(originalRequest);
                } catch (refreshError) {
                    processQueue(refreshError as Error);
                    // Только если не удалось обновить токен - очищаем localStorage и редиректим
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/auth')) {
                        window.location.href = '/auth/login';
                    }
                } finally {
                    isRefreshing = false;
                }
            }

            // Если уже идет обновление токена, добавляем запрос в очередь
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            });
        }

        // Формируем объект ошибки
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

        return Promise.reject(apiError);
    }
);

export { api };