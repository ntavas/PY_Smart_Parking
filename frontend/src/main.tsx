import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import NotFound from './components/NotFound.tsx'
import './styles/tailwind.css';
import { AuthProvider } from './contexts/AuthContext';

const path = window.location.pathname;

createRoot(document.getElementById('root')!).render(
    <AuthProvider>
        {path === '/' ? <App /> : <NotFound />}
    </AuthProvider>
)
