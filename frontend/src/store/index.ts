import { configureStore } from '@reduxjs/toolkit';
import cartReducer from './slices/cartSlice';
import languageReducer from './slices/languageSlice';

export const store = configureStore({
    reducer: {
        cart: cartReducer,
        language: languageReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
