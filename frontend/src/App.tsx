import { useMemo, useState } from 'react';
import { useTheme } from './hooks/useTheme';
import { useGeolocation } from './hooks/useGeolocation';
import { spots as mockSpots } from './data/mockSpots';
// import { getNearestDistanceMeters, walkingMinutes } from './utils/distance';
import type {ParkingSpot} from './types/parking';
import {SpotStatus, toLatLng} from './types/parking';
import Header from "./components/Header.tsx";
import Sidebar from "./components/Siderbar.tsx";
import MapView from "./components/MapView.tsx";

export default function App() {
    // Simulated auth state (replace with real auth later)
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

    // Theme handler: adds/removes `dark` class on <html>, persisted in localStorage
    const { isDark, toggleTheme } = useTheme();

    // Ask for user location to compute distances
    const { coords } = useGeolocation(); // { lat, lng } | null

    // Only show available pins on map
    const availableSpots: ParkingSpot[] = useMemo(
        () => mockSpots.filter(s => s.status === SpotStatus.Available),
        []
    );

    // Compute "nearest" in meters based on current location (if allowed)
    // const nearestMeters = useMemo(() => {
    //     if (!coords) return null;
    //     return getNearestDistanceMeters(coords, availableSpots.map(s => toLatLng(s)));
    // }, [coords, availableSpots]);
    //
    // const nearestLabel = nearestMeters != null ? `${(nearestMeters / 1000).toFixed(1)}km` : '—';

    return (
        <div className="h-screen w-screen flex flex-col">
            <Header
                isAuthenticated={isAuthenticated}
                onLogin={() => setIsAuthenticated(true)}
                onLogout={() => setIsAuthenticated(false)}
                isDark={isDark}
                toggleTheme={toggleTheme}
            />

            <div className="flex flex-1 overflow-hidden relative">
                {/* Map Area */}
                <div className="flex-1 relative">
                    {/* Search input */}
                    <div className="absolute top-2 left-2 right-16 z-[1000] md:top-4 md:left-4 md:right-auto md:w-80">
                        <input
                            type="text"
                            placeholder="Search for parking spots…"
                            className="w-full rounded-md border border-gray-200 bg-white/90 backdrop-blur px-3 py-2 text-sm shadow-sm outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800/90 dark:border-gray-700 dark:text-gray-100 md:px-4"
                            // TODO: wire to SearchValidation & actual search
                            readOnly
                        />
                    </div>

                    {/* Mobile toggle button - top right corner */}
                    <button
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        className="absolute top-2 right-2 z-[1000] md:hidden bg-blue-600 text-white p-3 rounded-lg shadow-lg hover:bg-blue-700 active:bg-blue-800 transition-colors flex items-center justify-center border border-blue-500"
                        aria-label="Open parking spots"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>

                    <MapView
                        userCoords={coords || undefined}
                        spots={availableSpots}
                        isAuthenticated={isAuthenticated}
                        isDark={isDark}
                    />
                </div>

                {/* Sidebar */}
                <Sidebar
                    isAuthenticated={isAuthenticated}
                    spots={availableSpots}
                    userCoords={coords || undefined}
                    isOpen={isSidebarOpen}
                    onClose={() => setIsSidebarOpen(false)}
                />

                {/* Mobile overlay */}
                {isSidebarOpen && (
                    <div
                        className="fixed inset-0 bg-black/50 z-[1500] md:hidden"
                        onClick={() => setIsSidebarOpen(false)}
                    />
                )}
            </div>
        </div>
    );
}
