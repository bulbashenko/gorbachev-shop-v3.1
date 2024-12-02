import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ProductFilters } from '@/app/api/services/product.service';

export const useProductFilters = () => {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [filters, setFilters] = useState<ProductFilters>({});

    // Initialize filters from URL params
    useEffect(() => {
        const newFilters: ProductFilters = {};

        // Only add filters that are explicitly set in URL
        if (searchParams.has('category')) {
            newFilters.category_slug = searchParams.get('category') || undefined;
        }

        if (searchParams.has('price_min')) {
            const minPrice = searchParams.get('price_min');
            if (minPrice) newFilters.price_min = parseFloat(minPrice);
        }

        if (searchParams.has('price_max')) {
            const maxPrice = searchParams.get('price_max');
            if (maxPrice) newFilters.price_max = parseFloat(maxPrice);
        }

        if (searchParams.has('gender')) {
            const gender = searchParams.get('gender');
            if (gender && ['M', 'W', 'U'].includes(gender)) {
                newFilters.gender = gender as 'M' | 'W' | 'U';
            }
        }

        if (searchParams.has('in_stock')) {
            newFilters.in_stock = searchParams.get('in_stock') === 'true';
        }

        if (searchParams.has('is_sale')) {
            newFilters.is_sale = searchParams.get('is_sale') === 'true';
        }

        if (searchParams.has('colors')) {
            const colors = searchParams.get('colors');
            if (colors) {
                newFilters.colors = colors.split(',').map(Number);
            }
        }

        if (searchParams.has('sizes')) {
            const sizes = searchParams.get('sizes');
            if (sizes) {
                newFilters.sizes = sizes.split(',').map(Number);
            }
        }

        if (searchParams.has('brand')) {
            newFilters.brand = searchParams.get('brand') || undefined;
        }

        if (searchParams.has('sort')) {
            newFilters.ordering = searchParams.get('sort') || undefined;
        }

        setFilters(newFilters);
    }, [searchParams]);

    const updateFilters = (newFilters: Partial<ProductFilters>) => {
        const updatedFilters = { ...filters, ...newFilters };
        setFilters(updatedFilters);

        // Construct URL params, only including non-null/undefined values
        const params = new URLSearchParams();

        if (updatedFilters.category_slug) {
            params.set('category', updatedFilters.category_slug);
        }

        if (updatedFilters.price_min) {
            params.set('price_min', updatedFilters.price_min.toString());
        }

        if (updatedFilters.price_max) {
            params.set('price_max', updatedFilters.price_max.toString());
        }

        if (updatedFilters.gender) {
            params.set('gender', updatedFilters.gender);
        }

        if (updatedFilters.in_stock) {
            params.set('in_stock', 'true');
        }

        if (updatedFilters.is_sale) {
            params.set('is_sale', 'true');
        }

        if (updatedFilters.colors?.length) {
            params.set('colors', updatedFilters.colors.join(','));
        }

        if (updatedFilters.sizes?.length) {
            params.set('sizes', updatedFilters.sizes.join(','));
        }

        if (updatedFilters.brand) {
            params.set('brand', updatedFilters.brand);
        }

        if (updatedFilters.ordering) {
            params.set('sort', updatedFilters.ordering);
        }

        // Update URL without reloading the page
        const newUrl = params.toString() ? `?${params.toString()}` : '';
        router.push(newUrl, { scroll: false });
    };

    const clearFilters = () => {
        setFilters({});
        router.push('', { scroll: false });
    };

    return {
        filters,
        updateFilters,
        clearFilters
    };
};