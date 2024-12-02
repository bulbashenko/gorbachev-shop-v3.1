import React from 'react';
import { FiChevronDown } from 'react-icons/fi';
import { ProductFilters as ProductFiltersType } from '@/app/api/services/product.service';

interface FilterSection {
    title: string;
    isOpen: boolean;
    onToggle: () => void;
    children: React.ReactNode;
}

interface ProductFiltersProps {
    filters: ProductFiltersType;
    onFilterChange: (key: string, value: string | number | boolean | number[] | null) => void;
    onClearFilters: () => void;
}

const FilterSection: React.FC<FilterSection> = ({ title, isOpen, onToggle, children }) => (
    <div className="border-b border-foreground/10 pb-4">
        <button
            onClick={onToggle}
            className="flex items-center justify-between w-full py-2 text-foreground"
        >
            <span className="font-medium">{title}</span>
            <FiChevronDown className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>
        {isOpen && <div className="mt-2">{children}</div>}
    </div>
);

const ProductFilters: React.FC<ProductFiltersProps> = ({
    filters,
    onFilterChange,
    onClearFilters
}) => {
    const [openSections, setOpenSections] = React.useState({
        gender: true,
        price: true,
        availability: true,
        sort: true
    });

    const toggleSection = (section: keyof typeof openSections) => {
        setOpenSections(prev => ({ ...prev, [section]: !prev[section] }));
    };

    return (
        <div className="space-y-4">
            {/* Gender Filter */}
            <FilterSection
                title="Gender"
                isOpen={openSections.gender}
                onToggle={() => toggleSection('gender')}
            >
                <div className="space-y-2">
                    {[
                        { value: 'M', label: 'Men' },
                        { value: 'W', label: 'Women' },
                        { value: 'U', label: 'Unisex' }
                    ].map(option => (
                        <label key={option.value} className="flex items-center gap-2 text-foreground/70">
                            <input
                                type="radio"
                                name="gender"
                                value={option.value}
                                checked={filters.gender === option.value}
                                onChange={(e) => onFilterChange('gender', e.target.value)}
                                className="border-foreground/30"
                            />
                            {option.label}
                        </label>
                    ))}
                </div>
            </FilterSection>

            {/* Price Range Filter */}
            <FilterSection
                title="Price Range"
                isOpen={openSections.price}
                onToggle={() => toggleSection('price')}
            >
                <div className="space-y-4">
                    <div className="flex gap-4">
                        <div>
                            <label className="text-sm text-foreground/70 block mb-1">Min</label>
                            <input
                                type="number"
                                value={filters.price_min || ''}
                                onChange={(e) => onFilterChange('price_min', e.target.value ? Number(e.target.value) : null)}
                                className="w-full px-2 py-1 bg-transparent border border-foreground/30 rounded text-foreground"
                                placeholder="0"
                            />
                        </div>
                        <div>
                            <label className="text-sm text-foreground/70 block mb-1">Max</label>
                            <input
                                type="number"
                                value={filters.price_max || ''}
                                onChange={(e) => onFilterChange('price_max', e.target.value ? Number(e.target.value) : null)}
                                className="w-full px-2 py-1 bg-transparent border border-foreground/30 rounded text-foreground"
                                placeholder="1000"
                            />
                        </div>
                    </div>
                </div>
            </FilterSection>

            {/* Availability Filter */}
            <FilterSection
                title="Availability"
                isOpen={openSections.availability}
                onToggle={() => toggleSection('availability')}
            >
                <div className="space-y-2">
                    <label className="flex items-center gap-2 text-foreground/70">
                        <input
                            type="checkbox"
                            checked={filters.in_stock || false}
                            onChange={(e) => onFilterChange('in_stock', e.target.checked)}
                            className="rounded border-foreground/30"
                        />
                        In Stock
                    </label>
                    <label className="flex items-center gap-2 text-foreground/70">
                        <input
                            type="checkbox"
                            checked={filters.is_sale || false}
                            onChange={(e) => onFilterChange('is_sale', e.target.checked)}
                            className="rounded border-foreground/30"
                        />
                        On Sale
                    </label>
                </div>
            </FilterSection>

            {/* Sort Filter */}
            <FilterSection
                title="Sort By"
                isOpen={openSections.sort}
                onToggle={() => toggleSection('sort')}
            >
                <div className="space-y-2">
                    {[
                        { value: 'price', label: 'Price: Low to High' },
                        { value: '-price', label: 'Price: High to Low' },
                        { value: 'name', label: 'Name: A to Z' },
                        { value: '-name', label: 'Name: Z to A' },
                        { value: '-created_at', label: 'Newest First' }
                    ].map(option => (
                        <label key={option.value} className="flex items-center gap-2 text-foreground/70">
                            <input
                                type="radio"
                                name="sort"
                                value={option.value}
                                checked={filters.ordering === option.value}
                                onChange={(e) => onFilterChange('ordering', e.target.value)}
                                className="border-foreground/30"
                            />
                            {option.label}
                        </label>
                    ))}
                </div>
            </FilterSection>

            {/* Clear Filters Button */}
            <button
                onClick={onClearFilters}
                className="w-full py-2 text-foreground/70 hover:text-foreground transition-colors"
            >
                Clear all filters
            </button>
        </div>
    );
};

export default ProductFilters;