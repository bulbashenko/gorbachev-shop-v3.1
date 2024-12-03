'use client';

import { use, useEffect, useState, useCallback } from 'react';
import ProductImage from '@/components/ProductImage';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store';
import { addToCart } from '@/store/slices/cartSlice';
import { productService, type ProductDetail, type Size, type Color, type ProductImage as ProductImageType, type ProductList } from '@/app/api/services/product.service';
import { FiHeart, FiMinus, FiPlus } from 'react-icons/fi';
import ProductCard from '@/components/ProductCard';

export default function ProductDetailPage({ params }: { params: { id: string } }) {
    const id = use(params).id;
    const dispatch = useDispatch<AppDispatch>();
    const [product, setProduct] = useState<ProductDetail | null>(null);
    const [selectedSize, setSelectedSize] = useState<Size | null>(null);
    const [selectedColor, setSelectedColor] = useState<Color | null>(null);
    const [quantity, setQuantity] = useState(1);
    const [selectedImage, setSelectedImage] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [addingToCart, setAddingToCart] = useState(false);
    const [addedToCart, setAddedToCart] = useState(false);

    const fetchProductDetails = useCallback(async () => {
        try {
            const data = await productService.getProduct(id);
            setProduct(data);
            // Устанавливаем главное изображение, если оно есть
            setSelectedImage(data.main_image || null);

            // Pre-select first available variant if exists
            if (data.available_sizes?.length > 0) {
                setSelectedSize(data.available_sizes[0]);
            }
            if (data.available_colors?.length > 0) {
                setSelectedColor(data.available_colors[0]);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch product details');
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        fetchProductDetails();
    }, [fetchProductDetails]);

    const getSelectedVariant = useCallback(() => {
        if (!product || !selectedSize || !selectedColor) return null;
        return product.variants?.find(
            variant =>
                variant.size.id === selectedSize.id &&
                variant.color.id === selectedColor.id
        );
    }, [product, selectedSize, selectedColor]);

    const handleAddToCart = async () => {
        const variant = getSelectedVariant();
        if (!variant) {
            setError('Please select size and color');
            return;
        }

        setAddingToCart(true);
        try {
            await dispatch(addToCart({
                variant_id: variant.id,
                quantity: quantity
            })).unwrap();
            
            setAddedToCart(true);
            setError(null);
        } catch (err) {
            setError(typeof err === 'string' ? err : 'Failed to add to cart');
            setAddedToCart(false);
        } finally {
            setAddingToCart(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="w-8 h-8 border-t-2 border-foreground rounded-full animate-spin"></div>
            </div>
        );
    }

    if (error || !product) {
        return (
            <div className="min-h-screen bg-background p-6">
                <div className="max-w-7xl mx-auto">
                    <div className="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded">
                        {error || 'Product not found'}
                    </div>
                </div>
            </div>
        );
    }

    const selectedVariant = getSelectedVariant();
    const isOutOfStock = selectedVariant ? selectedVariant.stock === 0 : true;

    return (
        <div className="min-h-screen bg-background">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="flex flex-col lg:flex-row gap-8">
                    {/* Product Images */}
                    <div className="flex-1">
                        <div className="sticky top-8 space-y-4">
                            {/* Main Image */}
                            <div className="aspect-square relative rounded-lg overflow-hidden bg-secondary">
                                <ProductImage
                                    src={selectedImage || product.main_image || '/images/placeholder.jpg'}
                                    alt={product.name}
                                    priority
                                />
                            </div>

                            {/* Image Thumbnails */}
                            {product.images && product.images.length > 0 && (
                                <div className="grid grid-cols-6 gap-2">
                                    {product.images.map((image: ProductImageType) => (
                                        <button
                                            key={image.id}
                                            onClick={() => setSelectedImage(image.image)}
                                            className={`aspect-square relative rounded-lg overflow-hidden ${
                                                selectedImage === image.image ? 'ring-2 ring-foreground' : ''
                                            }`}
                                        >
                                            <ProductImage
                                                src={image.image || '/images/placeholder.jpg'}
                                                alt={product.name}
                                            />
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Product Info */}
                    <div className="flex-1 space-y-6">
                        {/* Brand & Category */}
                        <div className="text-sm text-foreground/70">
                            <span className="font-medium">{product.brand}</span> · {product.category_name}
                        </div>

                        {/* Product Name & Price */}
                        <div>
                            <h1 className="text-3xl font-bold text-foreground mb-4">{product.name}</h1>
                            <div className="flex items-center gap-4">
                                <span className={`text-2xl font-bold ${product.sale_price ? 'text-red-500' : 'text-foreground'}`}>
                                    ${product.sale_price || product.price}
                                </span>
                                {product.sale_price && (
                                    <>
                                        <span className="text-lg text-foreground/70 line-through">${product.price}</span>
                                        <span className="text-sm text-red-500">-{product.discount_percent}%</span>
                                    </>
                                )}
                            </div>
                        </div>

                        {/* Size Selection */}
                        {product.available_sizes && product.available_sizes.length > 0 && (
                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-medium text-foreground">Size</span>
                                    <button className="text-sm text-foreground/70 hover:text-foreground">Size Guide</button>
                                </div>
                                <div className="grid grid-cols-4 gap-2">
                                    {product.available_sizes.map((size: Size) => (
                                        <button
                                            key={size.id}
                                            onClick={() => setSelectedSize(size)}
                                            className={`py-2 border rounded ${
                                                selectedSize?.id === size.id ? 'border-foreground' : 'border-foreground/30'
                                            }`}
                                        >
                                            {size.name}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Color Selection */}
                        {product.available_colors && product.available_colors.length > 0 && (
                            <div>
                                <span className="font-medium text-foreground block mb-2">Color</span>
                                <div className="flex flex-wrap gap-2">
                                    {product.available_colors.map((color: Color) => (
                                        <button
                                            key={color.id}
                                            onClick={() => setSelectedColor(color)}
                                            className={`w-10 h-10 rounded-full border-2 ${
                                                selectedColor?.id === color.id
                                                    ? 'border-foreground'
                                                    : 'border-transparent hover:border-foreground/30'
                                            }`}
                                            style={{ backgroundColor: color.code }}
                                            title={color.name}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Quantity Selection */}
                        <div>
                            <span className="font-medium text-foreground block mb-2">Quantity</span>
                            <div className="flex items-center gap-4 w-32">
                                <button
                                    onClick={() => setQuantity(prev => Math.max(1, prev - 1))}
                                    className="p-2 border border-foreground/30 rounded hover:border-foreground"
                                    disabled={quantity <= 1}
                                >
                                    <FiMinus />
                                </button>
                                <span className="flex-1 text-center text-foreground">{quantity}</span>
                                <button
                                    onClick={() => setQuantity(prev => prev + 1)}
                                    className="p-2 border border-foreground/30 rounded hover:border-foreground"
                                    disabled={selectedVariant ? quantity >= selectedVariant.stock : true}
                                >
                                    <FiPlus />
                                </button>
                            </div>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded">
                                {error}
                            </div>
                        )}

                        {/* Add to Cart & Wishlist */}
                        <div className="flex gap-4">
                            <button
                                onClick={handleAddToCart}
                                disabled={isOutOfStock || addingToCart || !selectedSize || !selectedColor || addedToCart}
                                className={`flex-1 py-3 rounded font-medium transition-colors ${
                                    addedToCart 
                                        ? 'bg-green-500 text-white cursor-default'
                                        : 'bg-foreground text-background hover:bg-foreground/90 disabled:opacity-50 disabled:cursor-not-allowed'
                                }`}
                            >
                                {isOutOfStock 
                                    ? 'Out of Stock' 
                                    : addingToCart 
                                        ? 'Adding...' 
                                        : addedToCart
                                            ? 'Added to Cart'
                                            : 'Add to Cart'
                                }
                            </button>
                            <button
                                className="p-3 border border-foreground/30 rounded hover:border-foreground"
                                aria-label="Add to wishlist"
                            >
                                <FiHeart className="w-6 h-6" />
                            </button>
                        </div>

                        {/* Product Details */}
                        <div className="border-t border-foreground/10 pt-6 space-y-4">
                            <div>
                                <h2 className="font-medium text-foreground mb-2">Description</h2>
                                <p className="text-foreground/70 whitespace-pre-line">{product.description}</p>
                            </div>

                            {product.material && (
                                <div>
                                    <h2 className="font-medium text-foreground mb-2">Material</h2>
                                    <p className="text-foreground/70">{product.material}</p>
                                </div>
                            )}

                            {product.care_instructions && (
                                <div>
                                    <h2 className="font-medium text-foreground mb-2">Care Instructions</h2>
                                    <p className="text-foreground/70">{product.care_instructions}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Similar Products */}
                {product.related_products && product.related_products.length > 0 && (
                    <div className="mt-16">
                        <h2 className="text-2xl font-bold text-foreground mb-6">You may also like</h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {product.related_products.map((relatedProduct: ProductList) => (
                                <ProductCard
                                    key={relatedProduct.id}
                                    id={relatedProduct.id}
                                    name={relatedProduct.name}
                                    slug={relatedProduct.slug}
                                    price={relatedProduct.price}
                                    salePrice={relatedProduct.sale_price}
                                    mainImage={relatedProduct.main_image || '/images/placeholder.jpg'}
                                    discountPercent={relatedProduct.discount_percent}
                                    categoryName={relatedProduct.category_name}
                                    brand={relatedProduct.brand}
                                    availableSizes={relatedProduct.available_sizes}
                                    availableColors={relatedProduct.available_colors}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
