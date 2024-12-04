// src/app/api/services/orders.service.ts
import { authService } from './auth.service';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface OrderItem {
    id: string;
    product_name: string;
    product_image: string;
    size: string;
    color: string;
    quantity: number;
    price: string;
    total: string;
}

export interface OrderStatus {
    status: string;
    notes: string;
    created_at: string;
    created_by: string;
}

export interface Order {
    id: string;
    order_number: string;
    status: 'awaiting_payment' | 'processing' | 'confirmed' | 'assembling' | 'shipped' | 'delivered' | 'cancelled' | 'returned';
    items: OrderItem[];
    total: string;
    created_at: string;
    shipping_method: string;
    shipping_address_details: string;
    tracking_number?: string;
    payment_status: string;
    status_history: OrderStatus[];
    subtotal: string;
    tax: string;
    shipping_cost: string;
    customer_notes?: string;
    email: string;
    phone: string;
}

export interface OrderTracking {
    order_number: string;
    current_status: string;
    status_history: OrderStatus[];
    tracking_number: string | null;
    shipping_method: string;
    shipping_address: string;
    created_at: string;
    shipped_at: string | null;
    delivered_at: string | null;
}

export const ordersService = {
    async getOrders() {
        const token = authService.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${API_URL}/orders/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('Failed to fetch orders');
        }

        return response.json();
    },

    async getOrderById(id: string) {
        const token = authService.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${API_URL}/orders/${id}/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('Failed to fetch order');
        }

        return response.json();
    },

    async cancelOrder(id: string, reason?: string) {
        const token = authService.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${API_URL}/orders/${id}/cancel/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ reason }),
            credentials: 'include',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to cancel order');
        }

        return response.json();
    },

    async getOrderTracking(id: string) {
        const token = authService.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${API_URL}/orders/${id}/tracking/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('Failed to fetch tracking information');
        }

        return response.json();
    },

    // Обновляет статус заказа
    async updateOrderStatus(id: string, data: { status: string; notes?: string }) {
        const token = authService.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${API_URL}/orders/${id}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('Failed to update order status');
        }

        return response.json();
    },

    // Создание заказа из корзины
    async createFromCart(data: {
        shipping_address: string;
        shipping_method: string;
        payment_method: string;
        customer_notes?: string;
    }) {
        const token = authService.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${API_URL}/orders/create_from_cart/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'include',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create order');
        }

        return response.json();
    }
};