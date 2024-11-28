export interface OrderItem {
    product_id: number;
    quantity: number;
    price: number;
    product?: {
        name: string;
        image_url: string;
    };
}

export interface Order {
    id: number;
    user_id: number;
    total_amount: number;
    status: OrderStatus;
    payment_status: PaymentStatus;
    created_at: string;
    updated_at: string;
    items: OrderItem[];
    user?: {
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

export interface OrderFilters {
    status?: string;
    payment_status?: string;
    from_date?: string;
    to_date?: string;
    page: number;
    limit: number;
}

export type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded';

export interface FilterState {
    status: OrderStatus | '';
    payment_status: PaymentStatus | '';
    from_date?: string;
    to_date?: string;
    page: number;
    limit: number;
}