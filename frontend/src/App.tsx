import { useAuth } from "./contexts/AuthContext";
import MainLayout from "./components/MainLayout";
import LandingPage from "./components/LandingPage";

export default function App() {
    const { isAuthenticated } = useAuth();

    return (
        isAuthenticated ? <MainLayout /> : <LandingPage />
    );
}
