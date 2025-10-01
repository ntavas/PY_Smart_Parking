import Badge from "./ui/Badge";
import type { ParkingSpot } from "../types/parking";
import { drivingMinutes, haversineMeters } from "../utils/distance";
import { isAvailable } from "../types/parking";
import SpotList from "./spots/SpotList.tsx";

type Props = {
    isAuthenticated: boolean;
    spots: ParkingSpot[];
    userCoords?: { lat: number; lng: number };
    isOpen?: boolean;
    onClose?: () => void;
};

export default function Sidebar({
    isAuthenticated,
    spots,
    userCoords,
    isOpen = true,
    onClose,
}: Props) {
    const availableCount = spots.filter(isAvailable).length;

    // Compute nearest (only among available spots)
    const nearestMeters =
        userCoords && spots.length
            ? Math.min(
                ...spots
                    .filter(isAvailable)
                    .map((s) =>
                        haversineMeters(userCoords, {
                            lat: s.latitude,
                            lng: s.longitude,
                        })
                    )
            )
            : null;

    const nearestLabel =
        nearestMeters != null ? `${(nearestMeters / 1000).toFixed(1)}km` : "—";

    return (
        <>
            <aside className={`
                fixed md:relative top-0 right-0 h-full
                w-full md:w-[360px] md:max-w-none
                shrink-0 border-l border-gray-400 bg-gray-100 
                flex flex-col transition-transform duration-300 ease-in-out
                dark:bg-gray-900 dark:border-gray-600 z-[2000]
                ${isOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0'}
            `}>
                {/* Mobile header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-400 bg-gray-200 dark:border-gray-600 dark:bg-gray-800 md:hidden">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        Parking Spots
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg text-gray-600 hover:text-gray-800 hover:bg-gray-300 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Close sidebar"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4">
                    <div className="mb-4">
                        <div className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                            Available Spots
                        </div>
                        <div className="mt-2 grid grid-cols-2 gap-2">
                            <div className="rounded-lg border border-gray-400 bg-white p-3 shadow-sm dark:border-gray-500 dark:bg-gray-800">
                                <div className="text-xl md:text-2xl font-semibold text-gray-900 dark:text-gray-100">
                                    {availableCount}
                                </div>
                                <div className="text-xs text-gray-600 dark:text-gray-400">
                                    Available
                                </div>
                            </div>
                            <div className="rounded-lg border border-gray-400 bg-white p-3 shadow-sm dark:border-gray-500 dark:bg-gray-800">
                                <div className="text-xl md:text-2xl font-semibold text-gray-900 dark:text-gray-100">
                                    {nearestLabel}
                                </div>
                                <div className="text-xs text-gray-600 dark:text-gray-400">
                                    Nearest
                                </div>
                            </div>
                        </div>

                        <div className="mt-3 flex gap-2 flex-wrap">
                            <Badge>All</Badge>
                            <Badge>Free</Badge>
                            <Badge>Paid</Badge>
                        </div>
                    </div>

                    <div className="flex-1">
                        <SpotList
                            spots={spots}
                            userCoords={userCoords}
                            showReserve={isAuthenticated}
                            computeWalkMins={(m) => drivingMinutes(m)}
                        />
                    </div>
                </div>
            </aside>
        </>
    );
}
