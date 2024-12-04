import { api } from '../api';
import { AxiosError } from 'axios';

export interface ProductVariant {
    id: string;
    size: {
        id: number;
        name: string;
    };
    color: {
        id: number;
        name: string;
        code: string;
    };
    sku: string;
    stock: number;
    available: boolean;
}

export interface ProductImage {
    id: string;
    image: string;
    color?: number;
    is_main: boolean;
    order: number;
}

export interface Size {
    id: number;
    name: string;
}

export interface Color {
    id: number;
    name: string;
    code: string;
}

export interface ProductList {
    id: string;
    name: string;
    slug: string;
    category_name: string;
    brand: string;
    price: string;
    sale_price?: string;
    main_image: string;
    discount_percent: number;
    available_sizes: string[];
    available_colors: string[];
}

export interface ProductDetail {
    id: string;
    name: string;
    slug: string;
    description: string;
    category: string;
    category_name: string;
    brand: string;
    gender: 'M' | 'W' | 'U';
    price: string;
    sale_price?: string;
    discount_percent: number;
    material?: string;
    care_instructions?: string;
    main_image: string;
    images: ProductImage[];
    variants: ProductVariant[];
    available_sizes: Size[];
    available_colors: Color[];
    related_products: ProductList[];
    created_at: string;
}

export interface ProductFilters {
    brand?: string;
    category?: number;
    category_slug?: string;
    colors?: number[];
    gender?: 'M' | 'W' | 'U';
    in_stock?: boolean;
    is_sale?: boolean;
    price_min?: number;
    price_max?: number;
    sizes?: number[];
    search?: string;
    ordering?: string;
    page?: number;
}

class ProductService {
    private async retryRequest<T>(requestFn: () => Promise<T>, retries = 3, delay = 1000): Promise<T> {
        try {
            return await requestFn();
        } catch (error) {
            if (retries > 0 && (error as AxiosError)?.response?.status === 429) {
                await new Promise(resolve => setTimeout(resolve, delay));
                return this.retryRequest(requestFn, retries - 1, delay * 2);
            }
            throw error;
        }
    }

    async getProducts(filters: ProductFilters = {}) {
        const cleanFilters = Object.fromEntries(
            Object.entries(filters).filter(([, value]) => value !== undefined && value !== null && value !== '')
        );

        return this.retryRequest(async () => {
            const response = await api.get<{
                count: number;
                results: ProductList[];
            }>('/products', {
                params: cleanFilters
            });
            return response.data;
        });
    }

    async getProduct(id: string) {
        return this.retryRequest(async () => {
            const response = await api.get<ProductDetail>(`/products/${id}`);
            return response.data;
        });
    }

    async checkStock(id: string) {
        return this.retryRequest(async () => {
            const response = await api.get<{
                in_stock: boolean;
                available_quantity: number;
            }>(`/products/${id}/check_stock`);
            return response.data;
        });
    }

    async getColors(id: string, filters: ProductFilters = {}) {
        return this.retryRequest(async () => {
            const response = await api.get<{
                count: number;
                results: Color[];
            }>(`/products/${id}/colors`, {
                params: filters
            });
            return response.data;
        });
    }

    async getSizes(id: string, filters: ProductFilters = {}) {
        return this.retryRequest(async () => {
            const response = await api.get<{
                count: number;
                results: Size[];
            }>(`/products/${id}/sizes`, {
                params: filters
            });
            return response.data;
        });
    }

    async getVariants(id: string, filters: ProductFilters = {}) {
        return this.retryRequest(async () => {
            const response = await api.get<{
                count: number;
                results: ProductVariant[];
            }>(`/products/${id}/variants`, {
                params: filters
            });
            return response.data;
        });
    }

    async getSimilarProducts(id: string, filters: ProductFilters = {}) {
        return this.retryRequest(async () => {
            const response = await api.get<{
                count: number;
                results: ProductList[];
            }>(`/products/${id}/similar`, {
                params: filters
            });
            return response.data;
        });
    }
}

export const productService = new ProductService();