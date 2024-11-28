const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

export interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    category: string;
    brand: string;
    main_image: string;
    is_featured: boolean;
    is_new_arrival: boolean;
    is_bestseller: boolean;
    total_stock: number;
    average_rating?: number;
    review_count: number;
}

export interface QueryParams {
    [key: string]: string | number | boolean;
}

class ProductService {
    async getProducts(params: QueryParams = {}): Promise<Product[]> {
        const queryString = new URLSearchParams(params as Record<string, string>).toString();
        const response = await fetch(`${API_URL}${API_PREFIX}/products?${queryString}`);

        if (!response.ok) {
            throw new Error('Failed to fetch products');
        }

        return response.json();
    }

    async getProduct(productId: number): Promise<Product> {
        const response = await fetch(`${API_URL}${API_PREFIX}/products/${productId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch product');
        }

        return response.json();
    }

    async getFeaturedProducts(limit = 8): Promise<Product[]> {
        const response = await fetch(`${API_URL}${API_PREFIX}/products/featured/?limit=${limit}`);

        if (!response.ok) {
            throw new Error('Failed to fetch featured products');
        }

        return response.json();
    }

    async getNewArrivals(limit = 8): Promise<Product[]> {
        const response = await fetch(`${API_URL}${API_PREFIX}/products/new-arrivals/?limit=${limit}`);

        if (!response.ok) {
            throw new Error('Failed to fetch new arrivals');
        }

        return response.json();
    }

    async getBestsellers(limit = 8): Promise<Product[]> {
        const response = await fetch(`${API_URL}${API_PREFIX}/products/bestsellers/?limit=${limit}`);

        if (!response.ok) {
            throw new Error('Failed to fetch bestsellers');
        }

        return response.json();
    }

    async getSimilarProducts(productId: number, limit = 4): Promise<Product[]> {
        const response = await fetch(`${API_URL}${API_PREFIX}/products/${productId}/similar?limit=${limit}`);

        if (!response.ok) {
            throw new Error('Failed to fetch similar products');
        }

        return response.json();
    }

    async searchProducts(query: string, params: QueryParams = {}): Promise<Product[]> {
        const searchParams = new URLSearchParams({
            q: query,
            ...params as Record<string, string>
        });

        const response = await fetch(`${API_URL}${API_PREFIX}/products/search/?${searchParams}`);

        if (!response.ok) {
            throw new Error('Failed to search products');
        }

        return response.json();
    }

    async getProductsByCategory(category: string, params: QueryParams = {}): Promise<Product[]> {
        const queryString = new URLSearchParams(params as Record<string, string>).toString();
        const response = await fetch(`${API_URL}${API_PREFIX}/products/category/${category}?${queryString}`);

        if (!response.ok) {
            throw new Error('Failed to fetch products by category');
        }

        return response.json();
    }
}

export const productService = new ProductService();