'use client';

import { useEffect, useState, useCallback } from 'react';
import { FiFilter, FiX } from 'react-icons/fi';
import { productService, type ProductList } from '@/app/api/services/product.service';
import { useProductFilters } from '@/hooks/useProductFilters';
import ProductCard from '@/components/ProductCard';
import ProductFilters from '../components/ProductFilters';

export default function ProductsPage() {
    const { filters, updateFilters, clearFilters } = useProductFilters();
    const [products, setProducts] = useState<ProductList[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showFilters, setShowFilters] = useState(false);
    const [totalCount, setTotalCount] = useState(0);

    const fetchProducts = useCallback(async () => {
        setLoading(true);
        try {
            const response = await productService.getProducts(filters);
            setProducts(response.results);
            setTotalCount(response.count);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch products');
        } finally {
            setLoading(false);
        }
    }, [filters]);

    useEffect(() => {
        fetchProducts();
    }, [fetchProducts]);

    const handleFilterChange = (key: string, value: string | number | boolean | number[] | null) => {
        updateFilters({ [key]: value });
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="w-8 h-8 border-t-2 border-foreground rounded-full animate-spin"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-background p-6">
                <div className="max-w-7xl mx-auto">
                    <div className="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded">
                        {error}
                    </div>
                </div>
            </div>
        );
    }


    return (
        <div className="min-h-screen bg-background">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-bold text-foreground mb-2">All Products</h1>
                        <p className="text-foreground/70">{totalCount} products</p>
                    </div>
                    <button
                        onClick={() => setShowFilters(!showFilters)}
                        className="lg:hidden flex items-center gap-2 text-foreground"
                    >
                        <FiFilter />
                        Filters
                    </button>
                </div>

                <div className="flex gap-8">
                    {/* Filters Sidebar */}
                    <div
                        className={`
              fixed inset-y-0 left-0 z-40 w-full max-w-xs bg-background transform transition-transform duration-300 ease-in-out
              lg:relative lg:translate-x-0 lg:w-64 lg:min-w-[16rem]
              ${showFilters ? 'translate-x-0' : '-translate-x-full'}
            `}
                    >
                        <div className="h-full overflow-y-auto p-4 border-r border-foreground/10">
                            {/* Mobile Header */}
                            <div className="flex justify-between items-center lg:hidden mb-4">
                                <h2 className="text-lg font-medium text-foreground">Filters</h2>
                                <button
                                    onClick={() => setShowFilters(false)}
                                    className="text-foreground"
                                >
                                    <FiX className="w-6 h-6" />
                                </button>
                            </div>

                            <ProductFilters
                                filters={filters}
                                onFilterChange={handleFilterChange}
                                onClearFilters={clearFilters}
                            />
                        </div>
                    </div>

                    {/* Product Grid */}
                    <div className="flex-1">
                        {products.length === 0 ? (
                            <div className="text-center py-12">
                                <p className="text-foreground/70">No products found</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {products.map((product) => (
                                    <ProductCard
                                        key={product.id}
                                        id={product.id}
                                        name={product.name}
                                        slug={product.slug}
                                        price={product.price}
                                        salePrice={product.sale_price}
                                        mainImage={product.main_image}
                                        discountPercent={product.discount_percent}
                                        categoryName={product.category_name}
                                        brand={product.brand}
                                        availableSizes={product.available_sizes}
                                        availableColors={product.available_colors}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Mobile Overlay */}
            {showFilters && (
                <div
                    className="fixed inset-0 bg-black/50 z-30 lg:hidden"
                    onClick={() => setShowFilters(false)}
                />
            )}
        </div>
    );
}