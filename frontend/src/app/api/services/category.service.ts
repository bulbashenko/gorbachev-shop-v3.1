import { api } from '../api';

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  parent?: string;
  children: Category[];
  image?: string;
  icon?: string;
  is_active: boolean;
  show_in_menu: boolean;
  order: number;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryList {
  id: string;
  name: string;
  slug: string;
  parent?: string;
  is_active: boolean;
}

export interface CategoryTree {
  id: string;
  name: string;
  slug: string;
  children: CategoryTree[];
  product_count: number;
}

class CategoryService {
  async getCategories(page = 1) {
    const response = await api.get<{
      count: number;
      results: CategoryList[];
    }>('/api/categories/categories/', {
      params: { page }
    });
    return response.data;
  }

  async getCategory(slug: string) {
    const response = await api.get<Category>(`/api/categories/categories/${slug}/`);
    return response.data;
  }

  async getMenuCategories(page = 1) {
    const response = await api.get<{
      count: number;
      results: CategoryList[];
    }>('/api/categories/categories/menu/', {
      params: { page }
    });
    return response.data;
  }

  async getCategoryTree(page = 1) {
    const response = await api.get<{
      count: number;
      results: CategoryTree[];
    }>('/api/categories/categories/tree/', {
      params: { page }
    });
    return response.data;
  }
}

export const categoryService = new CategoryService();
