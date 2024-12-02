// src/store/languageSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import Cookies from 'js-cookie';

interface LanguageState {
  locale: string;
}

const initialState: LanguageState = {
  locale: 'en', // Значение по умолчанию
};

const languageSlice = createSlice({
  name: 'language',
  initialState,
  reducers: {
    setLocale(state, action: PayloadAction<string>) {
      state.locale = action.payload;
      Cookies.set('NEXT_LOCALE', action.payload); // Сохраняем в куки
    },
  },
});

export const { setLocale } = languageSlice.actions;
export default languageSlice.reducer;
