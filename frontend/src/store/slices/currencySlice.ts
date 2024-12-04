// src/store/slices/currencySlice.ts
import { createSlice } from '@reduxjs/toolkit';

interface CurrencyState {
  currency: string;
}

const initialState: CurrencyState = {
  currency: 'EUR',
};

const currencySlice = createSlice({
  name: 'currency',
  initialState,
  reducers: {
    setCurrency(state, action) {
      state.currency = action.payload;
    },
  },
});

export const { setCurrency } = currencySlice.actions;
export default currencySlice.reducer;
