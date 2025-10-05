import { useMemo, useState } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Siderbar";
import MapView, { type Bounds } from "./components/MapView";
import { useTheme } from "./hooks/useTheme";
import { useGeolocation } from "./hooks/useGeolocation";
import { useLiveSpots } from "./hooks/useLiveSpots";
import { useViewportSpots } from "./hooks/useViewportSpots";
import type { ParkingSpot } from "./types/parking";
import { isAvailable } from "./types/parking";

export type Tab = "all" | "free" | "paid";

export default function App() {
    const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [tab, setTab] = useState<Tab>("all"); // <-- lifted tab

    const { isDark, toggleTheme } = useTheme();
    const { coords } = useGeolocation();

    const [bounds, setBounds] = useState<Bounds>({
        swLat: 37.9,
        swLng: 23.6,
        neLat: 38.1,
        neLng: 23.9,
    });

    // Cache-backed viewport fetch
    const viewportSpots = useViewportSpots(API_BASE, bounds, "Available");

    // Live deltas from WS
    const { spots: liveSpots } = useLiveSpots(API_BASE);

    // Merge: overlay live statuses on the viewport list
    const merged: ParkingSpot[] = useMemo(() => {
        if (!liveSpots.length) return viewportSpots;
        const statusMap = new Map(liveSpots.map((s) => [s.id, s.status]));
        return viewportSpots.map((s) =>
            statusMap.has(s.id) ? { ...s, status: statusMap.get(s.id)! } : s
        );
    }, [viewportSpots, liveSpots]);

    const availableSpots = useMemo(() => merged.filter(isAvailable), [merged]);

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
                <div className="flex-1 relative">
                    {/* Search input (read-only placeholder) */}
                    <div className="absolute top-2 left-2 right-16 z-[1000] md:top-4 md:left-4 md:right-auto md:w-80">
                        <input
                            type="text"
                            placeholder="Search for parking spots…"
                            className="w-full rounded-md border border-gray-200 bg-white/90 backdrop-blur px-3 py-2 text-sm shadow-sm outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800/90 dark:border-gray-700 dark:text-gray-100 md:px-4"
                            readOnly
                        />
                    </div>

                    {/* Mobile toggle button */}
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
                        userCoords={coords || { lat: 37.9838, lng: 23.7275 }}
                        spots={merged}
                        onBounds={setBounds}
                        isDark={isDark}
                        selectedTab={tab}            // <-- pass tab to map
                    />
                </div>

                <Sidebar
                    isAuthenticated={isAuthenticated}
                    spots={availableSpots}
                    userCoords={coords || undefined}
                    isOpen={isSidebarOpen}
                    onClose={() => setIsSidebarOpen(false)}
                    selectedTab={tab}             // <-- controlled tab
                    onChangeTab={setTab}          // <-- change handler
                />

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
