import { api } from '../api';

export interface CartItem {
    id: string;
    variant: {
        id: string;
        product: {
            name: string;
            price: string;
            images: Array<{
                id: string;
                image: string;
                is_main: boolean;
            }>;
        };
        size: {
            id: number;
            name: string;
        };
        color: {
            id: number;
            name: string;
            code: string;
        };
        stock: number;
        sku: string;
    };
    quantity: number;
    total: string; // Ensure this field exists
}

export interface Cart {
    id: string;
    items: CartItem[];
    total_items: number;
    total_price?: string; // Add total price field
}

export interface AddItemRequest {
    variant_id: string;
    quantity: number;
}

export interface UpdateQuantityRequest {
    quantity: number;
}

class CartServiceClass {
    async getCart() {
        try {
            const response = await api.get<Cart>('/cart/');
            if (!response.data) {
                throw new Error('Empty response from server');
            }
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async addItem(data: AddItemRequest) {
        try {
            const response = await api.post<CartItem>('/cart/add_item/', data);
            return response.data;
        } catch (error) {
            // Обработка ошибки
            throw error;
        }
    }

    async removeItem(cartId: string, itemId: string) {
        try {
            console.log('Removing item:', { itemId }); // Debug log
            await api.delete('/cart/remove_item/', {
                data: { item_id: itemId }
            });
        } catch (error) {
            console.error('Failed to remove item:', error);
            throw error;
        }
    }

    async updateQuantity(cartId: string, itemId: string, data: UpdateQuantityRequest) {
        try {
            console.log('Updating quantity:', { itemId, quantity: data.quantity }); // Debug log
            const response = await api.patch<Cart>('/cart/update_quantity/', {
                item_id: itemId,
                quantity: data.quantity
            });
            return response.data;
        } catch (error) {
            console.error('Failed to update quantity:', error);
            throw error;
        }
    }

    async clearCart() {
        try {
            console.log('Clearing cart'); // Debug log
            await api.post('/cart/clear/');
        } catch (error) {
            console.error('Failed to clear cart:', error);
            throw error;
        }
    }

    async validateCart() {
        try {
            const response = await api.get<{ status: string }>('/cart/validate/');
            return response.data;
        } catch (error) {
            // Обработка ошибки
            throw error;
        }
    }

    async transferGuestCart() {
        try {
            // Проверяем был ли гостевой cart_id в сессии
            const cartId = sessionStorage.getItem('cart_id');
            if (!cartId) {
                console.log('No guest cart to transfer');
                return null;
            }
            
            const response = await api.post<Cart>('/cart/transfer_to_user/');
            sessionStorage.removeItem('cart_id'); // Очищаем после успешного переноса
            return response.data;
        } catch (error) {
            console.error('Failed to transfer cart:', error);
            throw error;
        }
    }
}

export const cartService = new CartServiceClass();
