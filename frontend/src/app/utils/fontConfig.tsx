// fonts.js
import { DM_Sans, PT_Sans, DM_Mono, PT_Mono } from "next/font/google";

export const dm_sans = DM_Sans({
    weight: ['400', '700'],
    style: ['normal', 'italic'],
    subsets: ['latin'],
    display: 'swap'
});

export const pt_sans = PT_Sans({
    weight: ['400', '700'],
    style: ['normal', 'italic'],
    subsets: ['cyrillic'],
    display: 'swap'
});

export const dm_mono = DM_Mono({
    weight: ['400'],
    subsets: ['latin'],
    display: 'swap'
});

export const pt_mono = PT_Mono({
    weight: ['400'],
    style: ['normal'],
    subsets: ['cyrillic'],
    display: 'swap'
});
