// store/slices/cartSlice.ts
import { createSlice } from '@reduxjs/toolkit';

interface CartState {
  items: number;
}

const initialState: CartState = {
  items: 0,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    addItem(state) {
      state.items += 1;
    },
    removeItem(state) {
      if (state.items > 0) state.items -= 1;
    },
  },
});

export const { addItem, removeItem } = cartSlice.actions;
export default cartSlice.reducer;
