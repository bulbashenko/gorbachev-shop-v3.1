// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import languageReducer from '@/store/slices/languageSlice';
import cartReducer from '@/store/slices/cartSlice'
import currencyReducer from '@/store/slices/currencySlice';

const store = configureStore({
  reducer: {
    language: languageReducer,
    cart: cartReducer,
    currency: currencyReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
