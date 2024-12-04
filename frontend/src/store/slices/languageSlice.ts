import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import Cookies from 'js-cookie';

interface LanguageState {
  locale: string;
}

const initialState: LanguageState = {
  locale: 'en',
};

const languageSlice = createSlice({
  name: 'language',
  initialState,
  reducers: {
    setLocale(state, action: PayloadAction<string>) {
      state.locale = action.payload;
      Cookies.set('NEXT_LOCALE', action.payload);
    },
  },
});

export const { setLocale } = languageSlice.actions;
export default languageSlice.reducer;
