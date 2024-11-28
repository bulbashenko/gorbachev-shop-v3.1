export interface UserLogin {
    email: string;
    password: string;
}

export interface UserRegister {
    email: string;
    username: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export interface User {
    id: number;
    email: string;
    username: string;
    is_active: boolean;
    is_superuser: boolean;
    created_at: string;
    updated_at: string | null;
}

export interface ApiError {
    detail: string;
}