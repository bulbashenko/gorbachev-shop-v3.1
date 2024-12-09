import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import Cookies from 'js-cookie';

type ThemeState = {
  currentTheme: string;
};

const initialState: ThemeState = {
  currentTheme: Cookies.get('theme') || 'dark', // Берем тему из куки или ставим "dark" по умолчанию
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<string>) => {
      state.currentTheme = action.payload;
      Cookies.set('theme', action.payload); // Сохраняем тему в куки
    },
  },
});

export const { setTheme } = themeSlice.actions;

export default themeSlice.reducer;
