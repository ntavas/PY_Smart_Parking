import { useEffect, useState } from 'react';

/**
 * Keeps a 'dark' class on <html> in sync with localStorage ("theme":"dark"|"light").
 * Comment: We avoid Tailwind's media strategy to give the user explicit control.
 */
export function useTheme() {
    const [isDark, setIsDark] = useState<boolean>(() => {
        // Check localStorage first, then default to light mode
        const stored = localStorage.getItem('theme');
        if (stored) return stored === 'dark';
        return false; // Default to light mode
    });

    useEffect(() => {
        const root = document.documentElement;
        if (isDark) {
            root.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            root.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, [isDark]);

    return { isDark, toggleTheme: () => setIsDark(d => !d) };
}
