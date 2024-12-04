import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { cartService, type Cart, type AddItemRequest, type UpdateQuantityRequest } from '@/app/api/services/cart.service';
import { type RootState } from '@/store';
import { ApiError } from '@/app/api/api';

interface CartState {
    data: Cart | null;
    loading: boolean;
    error: string | null;
    addingItem: boolean;
    removingItem: boolean;
    updatingQuantity: boolean;
    validating: boolean;
}

const initialState: CartState = {
    data: null,
    loading: false,
    error: null,
    addingItem: false,
    removingItem: false,
    updatingQuantity: false,
    validating: false
};

// Async thunks
export const fetchCart = createAsyncThunk(
    'cart/fetchCart',
    async (_, { rejectWithValue }) => {
        try {
            const cart = await cartService.getCart();
            return cart;
        } catch (error) {
            const apiError = error as ApiError;
            return rejectWithValue(apiError.message || 'Failed to fetch cart');
        }
    }
);

export const addToCart = createAsyncThunk(
    'cart/addItem',
    async (data: AddItemRequest, { dispatch, rejectWithValue }) => {
        try {
            const response = await cartService.addItem(data);
            await dispatch(fetchCart());
            return response;
        } catch (error) {
            // Улучшенная обработка ошибок
            if (error instanceof Error) {
                console.error('Add to cart error:', error);
                return rejectWithValue(error.message);
            }
            return rejectWithValue('Failed to add item to cart');
        }
    }
);

export const removeFromCart = createAsyncThunk(
    'cart/removeItem',
    async ({ cartId, itemId }: { cartId: string; itemId: string }, { dispatch, rejectWithValue }) => {
        try {
            await cartService.removeItem(cartId, itemId);
            await dispatch(fetchCart());
            return itemId;
        } catch (error) {
            const apiError = error as ApiError;
            return rejectWithValue(apiError.message || 'Failed to remove item from cart');
        }
    }
);

export const updateQuantity = createAsyncThunk(
    'cart/updateQuantity',
    async ({ cartId, itemId, data }: {
        cartId: string;
        itemId: string;
        data: UpdateQuantityRequest;
    }, { dispatch, rejectWithValue }) => {
        try {
            const updatedItem = await cartService.updateQuantity(cartId, itemId, data);
            await dispatch(fetchCart());
            return updatedItem;
        } catch (error) {
            const apiError = error as ApiError;
            return rejectWithValue(apiError.message || 'Failed to update quantity');
        }
    }
);

export const clearCart = createAsyncThunk(
    'cart/clear',
    async (_, { dispatch, rejectWithValue }) => {
        try {
            await cartService.clearCart();
            await dispatch(fetchCart());
        } catch (error) {
            const apiError = error as ApiError;
            return rejectWithValue(apiError.message || 'Failed to clear cart');
        }
    }
);

export const validateCart = createAsyncThunk(
    'cart/validate',
    async (_, { rejectWithValue }) => {
        try {
            return await cartService.validateCart();
        } catch (error) {
            const apiError = error as ApiError;
            return rejectWithValue(apiError.message || 'Failed to validate cart');
        }
    }
);

export const transferGuestCart = createAsyncThunk(
    'cart/transferGuestCart',
    async (_, { rejectWithValue }) => {
        try {
            return await cartService.transferGuestCart();
        } catch (error) {
            const apiError = error as ApiError;
            return rejectWithValue(apiError.message || 'Failed to transfer guest cart');
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
        builder
            .addCase(fetchCart.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchCart.fulfilled, (state, action) => {
                state.loading = false;
                state.data = action.payload;
            })
            .addCase(fetchCart.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload as string;
            })

        // Add to Cart
        builder
            .addCase(addToCart.pending, (state) => {
                state.addingItem = true;
                state.error = null;
            })
            .addCase(addToCart.fulfilled, (state) => {
                state.addingItem = false;
            })
            .addCase(addToCart.rejected, (state, action) => {
                state.addingItem = false;
                state.error = action.payload as string;
            })

        // Remove from Cart
        builder
            .addCase(removeFromCart.pending, (state) => {
                state.removingItem = true;
                state.error = null;
            })
            .addCase(removeFromCart.fulfilled, (state) => {
                state.removingItem = false;
            })
            .addCase(removeFromCart.rejected, (state, action) => {
                state.removingItem = false;
                state.error = action.payload as string;
            })

        // Update Quantity
        builder
            .addCase(updateQuantity.pending, (state) => {
                state.updatingQuantity = true;
                state.error = null;
            })
            .addCase(updateQuantity.fulfilled, (state) => {
                state.updatingQuantity = false;
            })
            .addCase(updateQuantity.rejected, (state, action) => {
                state.updatingQuantity = false;
                state.error = action.payload as string;
            })

        // Clear Cart
        builder
            .addCase(clearCart.fulfilled, (state) => {
                state.data = null;
            })
            .addCase(clearCart.rejected, (state, action) => {
                state.error = action.payload as string;
            })

        // Validate Cart
        builder
            .addCase(validateCart.pending, (state) => {
                state.validating = true;
                state.error = null;
            })
            .addCase(validateCart.fulfilled, (state) => {
                state.validating = false;
            })
            .addCase(validateCart.rejected, (state, action) => {
                state.validating = false;
                state.error = action.payload as string;
            })

        // Transfer Guest Cart
        builder
            .addCase(transferGuestCart.fulfilled, (state, action) => {
                state.data = action.payload;
            })
            .addCase(transferGuestCart.rejected, (state, action) => {
                state.error = action.payload as string;
            })
    },
});

// Selectors
export const selectCart = (state: RootState) => state.cart.data;
export const selectCartLoading = (state: RootState) => state.cart.loading;
export const selectCartError = (state: RootState) => state.cart.error;
export const selectAddingItem = (state: RootState) => state.cart.addingItem;
export const selectRemovingItem = (state: RootState) => state.cart.removingItem;
export const selectUpdatingQuantity = (state: RootState) => state.cart.updatingQuantity;
export const selectValidating = (state: RootState) => state.cart.validating;

export const { resetCartError } = cartSlice.actions;
export default cartSlice.reducer;
