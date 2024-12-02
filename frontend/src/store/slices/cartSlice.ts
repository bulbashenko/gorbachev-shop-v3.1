import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { cartService, type Cart, type AddItemRequest, type UpdateQuantityRequest } from '@/app/api/services/cart.service';

interface CartState {
    data: Cart | null;
    loading: boolean;
    error: string | null;
    addingItem: boolean;
    removingItem: boolean;
    updatingQuantity: boolean;
}

const initialState: CartState = {
    data: null,
    loading: false,
    error: null,
    addingItem: false,
    removingItem: false,
    updatingQuantity: false,
};

// Async thunks
export const fetchCart = createAsyncThunk(
    'cart/fetchCart',
    async () => {
        try {
            const response = await cartService.getCart();

            // If we have results - return the first cart
            if (response.results && response.results.length > 0) {
                return response.results[0];
            }

            // If no results - return null (empty cart)
            return null;
        } catch (error) {
            // In case of error also return null instead of rejecting promise
            console.error('Cart fetch error in slice:', error);
            return null;
        }
    }
);

export const addToCart = createAsyncThunk(
    'cart/addItem',
    async (data: AddItemRequest, { rejectWithValue }) => {
        try {
            return await cartService.addItem(data);
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'Failed to add item to cart');
        }
    }
);

export const removeFromCart = createAsyncThunk(
    'cart/removeItem',
    async ({ cartId, itemId }: { cartId: string; itemId: string }, { rejectWithValue }) => {
        try {
            await cartService.removeItem(cartId, itemId);
            return itemId;
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'Failed to remove item from cart');
        }
    }
);

export const updateItemQuantity = createAsyncThunk(
    'cart/updateQuantity',
    async (
        { cartId, itemId, data }: { cartId: string; itemId: string; data: UpdateQuantityRequest },
        { rejectWithValue }
    ) => {
        try {
            return await cartService.updateQuantity(cartId, itemId, data);
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'Failed to update quantity');
        }
    }
);

export const clearCart = createAsyncThunk(
    'cart/clear',
    async (_, { rejectWithValue }) => {
        try {
            await cartService.clearCart();
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'Failed to clear cart');
        }
    }
);

export const validateCart = createAsyncThunk(
    'cart/validate',
    async (_, { rejectWithValue }) => {
        try {
            return await cartService.validateCart();
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'Cart validation failed');
        }
    }
);

export const transferGuestCart = createAsyncThunk(
    'cart/transferGuestCart',
    async (_, { rejectWithValue }) => {
        try {
            return await cartService.transferGuestCart();
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'Failed to transfer guest cart');
        }
    }
);

const cartSlice = createSlice({
    name: 'cart',
    initialState,
    reducers: {
        resetCartError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        // Fetch Cart
        builder.addCase(fetchCart.pending, (state) => {
            state.loading = true;
            state.error = null;
        });
        builder.addCase(fetchCart.fulfilled, (state, action) => {
            state.loading = false;
            state.data = action.payload;
            state.error = null;
        });
        builder.addCase(fetchCart.rejected, (state, action) => {
            state.loading = false;
            state.error = action.payload as string || 'Failed to fetch cart';
        });

        // Add to Cart
        builder.addCase(addToCart.pending, (state) => {
            state.addingItem = true;
            state.error = null;
        });
        builder.addCase(addToCart.fulfilled, (state) => {
            state.addingItem = false;
        });
        builder.addCase(addToCart.rejected, (state, action) => {
            state.addingItem = false;
            state.error = action.payload as string || 'Failed to add item to cart';
        });

        // Remove from Cart
        builder.addCase(removeFromCart.pending, (state) => {
            state.removingItem = true;
            state.error = null;
        });
        builder.addCase(removeFromCart.fulfilled, (state) => {
            state.removingItem = false;
        });
        builder.addCase(removeFromCart.rejected, (state, action) => {
            state.removingItem = false;
            state.error = action.payload as string || 'Failed to remove item from cart';
        });

        // Update Quantity
        builder.addCase(updateItemQuantity.pending, (state) => {
            state.updatingQuantity = true;
            state.error = null;
        });
        builder.addCase(updateItemQuantity.fulfilled, (state) => {
            state.updatingQuantity = false;
        });
        builder.addCase(updateItemQuantity.rejected, (state, action) => {
            state.updatingQuantity = false;
            state.error = action.payload as string || 'Failed to update quantity';
        });

        // Clear Cart
        builder.addCase(clearCart.fulfilled, (state) => {
            state.data = null;
            state.error = null;
        });
        builder.addCase(clearCart.rejected, (state, action) => {
            state.error = action.payload as string || 'Failed to clear cart';
        });

        // Transfer Guest Cart
        builder.addCase(transferGuestCart.fulfilled, (state, action) => {
            state.data = action.payload;
            state.error = null;
        });
        builder.addCase(transferGuestCart.rejected, (state, action) => {
            state.error = action.payload as string || 'Failed to transfer guest cart';
        });
    },
});

export const { resetCartError } = cartSlice.actions;
export default cartSlice.reducer;
