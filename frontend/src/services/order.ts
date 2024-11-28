import { authService } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

export interface OrderItem {
    product_id: number;
    quantity: number;
    color: string;
    size: string;
}

export interface Order {
    id: number;
    user_id: number;
    items: OrderItem[];
    total_amount: number;
    status: string;
    created_at: string;
    updated_at: string;
}

class OrderService {
    async createOrder(orderData: { items: OrderItem[] }): Promise<Order> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/orders`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.logout();
                throw new Error('Session expired');
            }
            throw new Error('Failed to create order');
        }

        return response.json();
    }

    async getUserOrders(): Promise<Order[]> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/orders`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.logout();
                throw new Error('Session expired');
            }
            throw new Error('Failed to fetch user orders');
        }

        return response.json();
    }

    async getOrder(orderId: number): Promise<Order> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/orders/${orderId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.logout();
                throw new Error('Session expired');
            }
            throw new Error('Failed to fetch order');
        }

        return response.json();
    }

    async cancelOrder(orderId: number): Promise<Order> {
        const token = authService.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/orders/${orderId}/cancel`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.logout();
                throw new Error('Session expired');
            }
            throw new Error('Failed to cancel order');
        }

        return response.json();
    }
}

export const orderService = new OrderService();