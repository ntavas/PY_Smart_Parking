import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Modal } from './ui/Modal';
import { LoginForm } from './auth/LoginForm';
import { RegisterForm } from './auth/RegisterForm';
import { UserMenu } from './ui/UserMenu';

type Props = {
    isDark: boolean;
    toggleTheme: () => void;
};

type AuthModalView = 'login' | 'register';

export default function Header({ isDark, toggleTheme }: Props) {
    const { isAuthenticated } = useAuth();
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
    const [authModalView, setAuthModalView] = useState<AuthModalView>('login');

    const handleOpenLogin = () => {
        setAuthModalView('login');
        setIsAuthModalOpen(true);
    };

    const handleSwitchToRegister = () => {
        setAuthModalView('register');
    };

    const handleSwitchToLogin = () => {
        setAuthModalView('login');
    };

    const handleCloseAuthModal = () => {
        setIsAuthModalOpen(false);
        // Reset to login view after closing
        setTimeout(() => setAuthModalView('login'), 300);
    };

    return (
        <>
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

                        {/* Auth Button / User Menu */}
                        {isAuthenticated ? (
                            <UserMenu />
                        ) : (
                            <button
                                onClick={handleOpenLogin}
                                className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-sm"
                            >
                                Login
                            </button>
                        )}
                    </div>
                </div>
            </header>

            {/* Auth Modal */}
            <Modal
                isOpen={isAuthModalOpen}
                onClose={handleCloseAuthModal}
                title={authModalView === 'login' ? 'Sign In' : 'Create Account'}
            >
                {authModalView === 'login' ? (
                    <LoginForm
                        onClose={handleCloseAuthModal}
                        onSwitchToRegister={handleSwitchToRegister}
                    />
                ) : (
                    <RegisterForm
                        onClose={handleCloseAuthModal}
                        onSwitchToLogin={handleSwitchToLogin}
                    />
                )}
            </Modal>
        </>
    );
}
