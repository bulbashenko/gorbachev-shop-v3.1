'use client';

import React, { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { adminService } from '../../../../services/admin';
import { FiEdit2, FiTrash2, FiPlus } from 'react-icons/fi';

interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    stock: number;
    image_url: string;
    category: string;
    created_at: string;
    updated_at: string | null;
}

const ProductsPage = () => {
    const t = useTranslations('Admin');
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showForm, setShowForm] = useState(false);
    const [editingProduct, setEditingProduct] = useState<Product | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        price: 0,
        stock: 0,
        image_url: '',
        category: 'SHIRTS'
    });

    const loadProducts = async () => {
        try {
            setLoading(true);
            const response = await adminService.getProducts();
            setProducts(response.products);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load products');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadProducts();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingProduct) {
                await adminService.updateProduct(editingProduct.id, formData);
            } else {
                await adminService.createProduct(formData);
            }
            setShowForm(false);
            setEditingProduct(null);
            setFormData({
                name: '',
                description: '',
                price: 0,
                stock: 0,
                image_url: '',
                category: 'SHIRTS'
            });
            loadProducts();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save product');
        }
    };

    const handleEdit = (product: Product) => {
        setEditingProduct(product);
        setFormData({
            name: product.name,
            description: product.description,
            price: product.price,
            stock: product.stock,
            image_url: product.image_url,
            category: product.category
        });
        setShowForm(true);
    };

    const handleDelete = async (id: number) => {
        if (window.confirm(t('products.deleteConfirm'))) {
            try {
                await adminService.deleteProduct(id);
                loadProducts();
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to delete product');
            }
        }
    };

    if (loading) {
        return <div className="flex justify-center items-center h-64">Loading...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">{t('products.title')}</h1>
                <button
                    onClick={() => setShowForm(true)}
                    className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                    <FiPlus className="w-5 h-5 mr-2" />
                    {t('products.add')}
                </button>
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg">
                    {error}
                </div>
            )}

            {showForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full">
                        <h2 className="text-xl font-bold mb-4">
                            {editingProduct ? t('products.edit') : t('products.create')}
                        </h2>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    {t('products.name')}
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    {t('products.description')}
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    rows={3}
                                    required
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">
                                        {t('products.price')}
                                    </label>
                                    <input
                                        type="number"
                                        value={formData.price}
                                        onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                                        className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                        min="0"
                                        step="0.01"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">
                                        {t('products.stock')}
                                    </label>
                                    <input
                                        type="number"
                                        value={formData.stock}
                                        onChange={(e) => setFormData({ ...formData, stock: parseInt(e.target.value) })}
                                        className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                        min="0"
                                        required
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    {t('products.imageUrl')}
                                </label>
                                <input
                                    type="url"
                                    value={formData.image_url}
                                    onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                                    className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    {t('products.category')}
                                </label>
                                <select
                                    value={formData.category}
                                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                    className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    required
                                >
                                    <option value="SHIRTS">Shirts</option>
                                    <option value="PANTS">Pants</option>
                                    <option value="DRESSES">Dresses</option>
                                    <option value="ACCESSORIES">Accessories</option>
                                </select>
                            </div>
                            <div className="flex justify-end space-x-4">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowForm(false);
                                        setEditingProduct(null);
                                    }}
                                    className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg dark:text-gray-300 dark:hover:bg-gray-700"
                                >
                                    {t('common.cancel')}
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                                >
                                    {editingProduct ? t('common.save') : t('common.create')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {products.map((product) => (
                    <div
                        key={product.id}
                        className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border dark:border-gray-700"
                    >
                        <img
                            src={product.image_url}
                            alt={product.name}
                            className="w-full h-48 object-cover rounded-lg mb-4"
                        />
                        <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
                        <p className="text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
                            {product.description}
                        </p>
                        <div className="flex justify-between items-center mb-4">
                            <span className="text-lg font-bold">${product.price}</span>
                            <span className="text-sm text-gray-500">
                                {t('products.inStock', { count: product.stock })}
                            </span>
                        </div>
                        <div className="flex justify-end space-x-2">
                            <button
                                onClick={() => handleEdit(product)}
                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg dark:text-blue-400 dark:hover:bg-gray-700"
                            >
                                <FiEdit2 className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => handleDelete(product.id)}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg dark:text-red-400 dark:hover:bg-gray-700"
                            >
                                <FiTrash2 className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ProductsPage;