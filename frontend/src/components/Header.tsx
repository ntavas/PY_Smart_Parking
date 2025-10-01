type Props = {
    isAuthenticated: boolean;
    onLogin: () => void;
    onLogout: () => void;
    isDark: boolean;
    toggleTheme: () => void;
};

export default function Header({
                                   isAuthenticated,
                                   onLogin,
                                   onLogout,
                                   isDark,
                                   toggleTheme,
                               }: Props) {
    return (
        <header className="w-full border-b border-gray-300 bg-slate-100 shadow-md dark:border-gray-700 dark:bg-gray-800">
            <div className="flex items-center justify-between px-4 py-3 md:px-6">
                {/* Logo/Brand */}
                <div className="flex items-center gap-2">
                    <div className="text-xl font-bold text-slate-800 dark:text-white">
                        🅿️ SmartPark
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                    {/* Theme Toggle */}
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-lg bg-white/80 text-gray-700 hover:bg-white transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 shadow-sm"
                        aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
                    >
                        {isDark ? '☀️' : '🌙'}
                    </button>

                    {/* Auth Button */}
                    {isAuthenticated ? (
                        <button
                            onClick={onLogout}
                            className="px-4 py-2 rounded-lg bg-red-100 text-red-700 border border-red-300 hover:bg-red-200 transition-colors shadow-sm dark:bg-red-900/30 dark:text-red-400 dark:border-red-700 dark:hover:bg-red-900/40"
                        >
                            Logout
                        </button>
                    ) : (
                        <button
                            onClick={onLogin}
                            className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-sm"
                        >
                            Login
                        </button>
                    )}
                </div>
            </div>
        </header>
    );
}
