import { api } from '../api';

export interface CartItem {
    id: string;
    variant: {
        id: string;
        product_name: string;
        product_image: string;
        price: number;
        stock: number;
        size: {
            id: string;
            name: string;
        };
        color: {
            id: string;
            name: string;
        };
    };
    quantity: number;
    total: number;
}

export interface Cart {
    id: string;
    items: CartItem[];
    subtotal: number;
    total_price: number;
    total_items: number;
    session_id?: string;
    user?: string;
    created_at: string;
    updated_at: string;
}

export interface AddItemRequest {
    variant_id: string;
    quantity: number;
}

export interface UpdateQuantityRequest {
    quantity: number;
}

export interface CartValidationResponse {
    status: string;
    invalid_items?: Array<{
        id: string;
        product: string;
        variant: string;
        requested: number;
        available: number;
    }>;
}

export const cartService = {
    async getCart() {
        try {
            const response = await api.get<{ results: Cart[] }>('/cart/cart/', {
                params: {
                    create_if_not_exists: true
                }
            });
            return response.data;
        } catch (error) {
            console.error('Failed to fetch cart:', error);
            throw error;
        }
    },

    async addItem(data: AddItemRequest) {
        try {
            const response = await api.post<CartItem>('/cart/cart/add_item/', data);
            return response.data;
        } catch (error) {
            console.error('Failed to add item to cart:', error);
            throw error;
        }
    },

    async removeItem(cartId: string, itemId: string) {
        try {
            await api.delete(`/cart/cart/${cartId}/remove_item/${itemId}/`);
        } catch (error) {
            console.error('Failed to remove item from cart:', error);
            throw error;
        }
    },

    async updateQuantity(cartId: string, itemId: string, data: UpdateQuantityRequest) {
        try {
            const response = await api.patch<CartItem>(
                `/cart/cart/${cartId}/update_quantity/${itemId}/`,
                data
            );
            return response.data;
        } catch (error) {
            console.error('Failed to update quantity:', error);
            throw error;
        }
    },

    async clearCart() {
        try {
            await api.post('/cart/cart/clear/');
        } catch (error) {
            console.error('Failed to clear cart:', error);
            throw error;
        }
    },

    async validateCart() {
        try {
            const response = await api.get<CartValidationResponse>('/cart/cart/validate/');
            return response.data;
        } catch (error) {
            console.error('Failed to validate cart:', error);
            throw error;
        }
    },

    async transferGuestCart() {
        try {
            const response = await api.post<Cart>('/cart/cart/transfer_to_user/');
            return response.data;
        } catch (error) {
            console.error('Failed to transfer guest cart:', error);
            throw error;
        }
    }
};