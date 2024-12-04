import { api } from '../api';

interface ChartData {
  // Will be extended based on actual API response
  [key: string]: any;
}

interface CategoryPerformance {
  // Will be extended based on actual API response
  category: string;
  sales: number;
  revenue: number;
}

interface CustomerSegment {
  // Will be extended based on actual API response
  segment: string;
  count: number;
  total_spent: number;
}

interface ProductPerformance {
  // Will be extended based on actual API response
  product: string;
  sales: number;
  revenue: number;
}

interface SalesReport {
  // Will be extended based on actual API response
  period: string;
  total_sales: number;
  total_revenue: number;
}

interface DashboardData {
  // Will be extended based on actual API response
  total_sales: number;
  total_revenue: number;
  active_customers: number;
}

class AnalyticsService {
  private checkAdminAccess() {
    // This should be implemented based on your auth logic
    const user = localStorage.getItem('user');
    if (!user) throw new Error('Authentication required');
    
    const userData = JSON.parse(user);
    if (!userData.is_staff) throw new Error('Admin access required');
  }

  async getCategoryPerformance() {
    this.checkAdminAccess();
    const response = await api.get<CategoryPerformance[]>('/api/analytics/analytics/category_performance/');
    return response.data;
  }

  async getChartData() {
    this.checkAdminAccess();
    const response = await api.get<ChartData>('/api/analytics/analytics/chart_data/');
    return response.data;
  }

  async getCustomerSegments() {
    this.checkAdminAccess();
    const response = await api.get<CustomerSegment[]>('/api/analytics/analytics/customer_segments/');
    return response.data;
  }

  async getDashboard() {
    this.checkAdminAccess();
    const response = await api.get<DashboardData>('/api/analytics/analytics/dashboard/');
    return response.data;
  }

  async exportReport() {
    this.checkAdminAccess();
    const response = await api.get('/api/analytics/analytics/export_report/', {
      responseType: 'blob'
    });
    return response.data;
  }

  async getProductPerformance() {
    this.checkAdminAccess();
    const response = await api.get<ProductPerformance[]>('/api/analytics/analytics/product_performance/');
    return response.data;
  }

  async getSalesReport() {
    this.checkAdminAccess();
    const response = await api.get<SalesReport[]>('/api/analytics/analytics/sales_report/');
    return response.data;
  }
}

export const analyticsService = new AnalyticsService();
