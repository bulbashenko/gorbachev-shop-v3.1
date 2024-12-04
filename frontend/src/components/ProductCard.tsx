import React from 'react';
import Link from 'next/link';
import ProductImage from './ProductImage';
import { FiHeart } from 'react-icons/fi';

interface ProductCardProps {
    id: string;
    name: string;
    slug: string;
    price: string;
    salePrice?: string | null;
    mainImage: string;
    discountPercent: number;
    categoryName: string;
    brand: string;
    availableSizes: string[];
    availableColors: string[];
}

const ProductCard = ({
    id,
    name,
    price,
    salePrice,
    mainImage,
    discountPercent,
    categoryName,
    brand,
    availableSizes,
    availableColors
}: ProductCardProps) => {
    return (
        <div className="group relative bg-background rounded-lg overflow-hidden">
            {/* Image Container */}
            <div className="relative aspect-square overflow-hidden">
                <Link href={`/products/${id}`}>
                    <ProductImage
                        src={mainImage}
                        alt={name}
                        className="group-hover:scale-105 transition-transform duration-300"
                    />
                </Link>

                {/* Discount Badge */}
                {discountPercent > 0 && (
                    <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 text-sm rounded">
                        -{discountPercent}%
                    </div>
                )}

                {/* Quick Actions */}
                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        className="bg-white/90 hover:bg-white p-2 rounded-full text-black"
                        aria-label="Add to wishlist"
                    >
                        <FiHeart className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Product Info */}
            <div className="p-4">
                {/* Brand & Category */}
                <div className="text-sm text-foreground/70 mb-1">
                    <span className="font-medium">{brand}</span> · {categoryName}
                </div>

                {/* Product Name */}
                <Link href={`/products/${id}`} className="block">
                    <h3 className="font-medium text-foreground mb-2 hover:text-foreground/80 transition-colors line-clamp-2">
                        {name}
                    </h3>
                </Link>

                {/* Price */}
                <div className="flex items-center gap-2">
                    <span className={`text-lg font-medium ${salePrice ? 'text-red-500' : 'text-foreground'}`}>
                        ${salePrice || price}
                    </span>
                    {salePrice && (
                        <span className="text-sm text-foreground/70 line-through">
                            ${price}
                        </span>
                    )}
                </div>

                {/* Available Options */}
                <div className="mt-2 text-sm text-foreground/70">
                    <div className="flex flex-wrap gap-1">
                        {availableColors.length > 0 && (
                            <span>{availableColors.length} color{availableColors.length !== 1 ? 's' : ''}</span>
                        )}
                        {availableColors.length > 0 && availableSizes.length > 0 && (
                            <span>·</span>
                        )}
                        {availableSizes.length > 0 && (
                            <span>{availableSizes.length} size{availableSizes.length !== 1 ? 's' : ''}</span>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProductCard;