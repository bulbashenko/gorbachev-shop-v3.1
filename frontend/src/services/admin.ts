import { authService } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

export interface OrderItem {
    product_id: number;
    quantity: number;
    price: number;
    product: {
        name: string;
        image_url: string;
    };
}

export interface Order {
    id: number;
    user_id: number;
    total_amount: number;
    status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
    payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
    created_at: string;
    updated_at: string;
    items: OrderItem[];
    user: {
        email: string;
        username: string;
    };
}

export interface OrderStats {
    byStatus: Record<string, number>;
    byPaymentStatus: Record<string, number>;
    recentOrders: number;
    totalRevenue: number;
    averageOrderValue: number;
}

interface OrderStatusStats {
    byStatus: Record<string, number>;
    byPaymentStatus: Record<string, number>;
}

interface DashboardStats {
    overview: {
        totalUsers: number;
        totalProducts: number;
        totalOrders: number;
        totalRevenue: number;
    };
    recent: {
        orders: number;
        revenue: number;
        activeUsers: number;
    };
    inventory: {
        totalProducts: number;
        lowStockProducts: number;
    };
    orders: OrderStatusStats;
}

interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    stock: number;
    image_url: string;
    category: string;
    created_at: string;
    updated_at: string | null;
}

interface User {
    id: number;
    email: string;
    username: string;
    is_active: boolean;
    is_superuser: boolean;
    created_at: string;
    updated_at: string | null;
}

interface OrderFilters {
    status?: string;
    payment_status?: string;
    from_date?: string;
    to_date?: string;
    page?: number;
    limit?: number;
}

export const adminService = {
    async getStats(): Promise<DashboardStats> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch stats');
        }

        return response.json();
    },

    async getProducts(page = 1, limit = 10): Promise<{ products: Product[], total: number }> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(
            `${API_URL}${API_PREFIX}/products?page=${page}&limit=${limit}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch products');
        }

        return response.json();
    },

    async createProduct(productData: Omit<Product, 'id' | 'created_at' | 'updated_at'>): Promise<Product> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/products`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData),
        });

        if (!response.ok) {
            throw new Error('Failed to create product');
        }

        return response.json();
    },

    async updateProduct(id: number, productData: Partial<Product>): Promise<Product> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/products/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData),
        });

        if (!response.ok) {
            throw new Error('Failed to update product');
        }

        return response.json();
    },

    async deleteProduct(id: number): Promise<void> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/products/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to delete product');
        }
    },

    async getUsers(page = 1, limit = 10): Promise<{ users: User[], total: number }> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(
            `${API_URL}${API_PREFIX}/admin/users?page=${page}&limit=${limit}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }

        return response.json();
    },

    async updateUser(id: number, userData: Partial<User>): Promise<User> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/admin/users/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            throw new Error('Failed to update user');
        }

        return response.json();
    },

    async deleteUser(id: number): Promise<void> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/admin/users/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to delete user');
        }
    },

    async getOrders(filters: OrderFilters = {}): Promise<{ orders: Order[], total: number }> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const queryParams = new URLSearchParams();
        if (filters.status) queryParams.append('status', filters.status);
        if (filters.payment_status) queryParams.append('payment_status', filters.payment_status);
        if (filters.from_date) queryParams.append('from_date', filters.from_date);
        if (filters.to_date) queryParams.append('to_date', filters.to_date);
        if (filters.page) queryParams.append('page', filters.page.toString());
        if (filters.limit) queryParams.append('limit', filters.limit.toString());

        const response = await fetch(
            `${API_URL}${API_PREFIX}/admin/orders?${queryParams.toString()}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch orders');
        }

        return response.json();
    },

    async getOrderStats(days: number = 30): Promise<OrderStats> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(
            `${API_URL}${API_PREFIX}/admin/orders/stats?days=${days}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch order stats');
        }

        return response.json();
    },

    async updateOrderStatus(id: number, status: string): Promise<Order> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/admin/orders/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status }),
        });

        if (!response.ok) {
            throw new Error('Failed to update order status');
        }

        return response.json();
    },

    async updateOrderPaymentStatus(id: number, payment_status: string): Promise<Order> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/admin/orders/${id}/payment`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ payment_status }),
        });

        if (!response.ok) {
            throw new Error('Failed to update order payment status');
        }

        return response.json();
    }
};