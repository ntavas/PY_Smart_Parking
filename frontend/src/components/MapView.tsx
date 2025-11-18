import { MapContainer, Marker, Popup, TileLayer, useMap, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L, { type LatLngExpression } from "leaflet";
import type { ParkingSpot } from "../types/parking";
import { isAvailable } from "../types/parking";
import { useCallback, useEffect, useMemo, useRef } from "react";
import type { Tab } from "../App";
import { type SearchResult } from "./SearchModal";

const DefaultIcon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

const FreeIcon = L.icon({
    iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
});

const UserIcon = L.icon({
    iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
});

// This component now manages its own "has flown" state to prevent re-triggers.
function FlyTo({ center, zoom, onFlyEnd }: { center: LatLngExpression; zoom: number; onFlyEnd: () => void }) {
    const map = useMap();
    // useRef is used to track if the flight has already been performed for this search result.
    // This prevents the effect from re-running if the parent component re-renders.
    const hasFlownRef = useRef(false);

    useEffect(() => {
        // Only fly if we haven't already for this specific search instance.
        if (!hasFlownRef.current) {
            hasFlownRef.current = true; // Mark as "flying" immediately.

            const handleMoveEnd = () => {
                // Once the flight is complete, call the handler to reset the parent state.
                onFlyEnd();
                // IMPORTANT: Clean up the listener to avoid it firing on subsequent map moves.
                map.off('moveend', handleMoveEnd);
            };

            map.on('moveend', handleMoveEnd);
            map.flyTo(center, zoom, {
                animate: true,
                duration: 1.5,
            });

            // Cleanup function in case the component unmounts mid-flight.
            return () => {
                map.off('moveend', handleMoveEnd);
            };
        }
    }, [center, zoom, map, onFlyEnd]);

    return null;
}

const LIGHT_TILES = {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap contributors",
};

const DARK_TILES = {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attribution">CARTO</a>',
    subdomains: ["a", "b", "c", "d"] as const,
};

export type Bounds = {
    swLat: number;
    swLng: number;
    neLat: number;
    neLng: number;
};

function UseBounds({ onBounds }: { onBounds: (b: Bounds) => void }) {
    const map = useMapEvents({
        moveend() {
            const b = map.getBounds();
            onBounds({
                swLat: b.getSouthWest().lat,
                swLng: b.getSouthWest().lng,
                neLat: b.getNorthEast().lat,
                neLng: b.getNorthEast().lng,
            });
        },
    });

    useEffect(() => {
        map.whenReady(() => {
            const b = map.getBounds();
            onBounds({
                swLat: b.getSouthWest().lat,
                swLng: b.getSouthWest().lng,
                neLat: b.getNorthEast().lat,
                neLng: b.getNorthEast().lng,
            });
        });
    }, [map, onBounds]);

    return null;
}

function MapControls() {
    const map = useMap();

    return (
        <div className="absolute right-4 bottom-4 z-[1000] flex flex-col gap-2">
            <button
                className="bg-white rounded shadow p-2"
                onClick={() => map.zoomIn()}
                aria-label="Zoom in"
            >
                +
            </button>
            <button
                className="bg-white rounded shadow p-2"
                onClick={() => map.zoomOut()}
                aria-label="Zoom out"
            >
                −
            </button>
            <button
                className="bg-white rounded shadow p-2"
                onClick={() => map.locate({ setView: true, maxZoom: 16 })}
                aria-label="Locate"
            >
                📍
            </button>
        </div>
    );
}

type Props = {
    userCoords?: { lat: number; lng: number };
    spots: ParkingSpot[];
    onBounds: (b: Bounds) => void;
    isDark?: boolean;
    selectedTab: Tab;
    isAuthenticated?: boolean;
    searchResult?: SearchResult | null;
    onSearchResultHandled: () => void; // Callback to clear the search result
};

export default function MapView({
    userCoords,
    spots,
    onBounds,
    isDark = false,
    selectedTab,
    isAuthenticated = false,
    searchResult,
    onSearchResultHandled, // Receive the callback
}: Props) {
    const center: LatLngExpression = userCoords ? [userCoords.lat, userCoords.lng] : [37.9838, 23.7275];
    const tiles = isDark ? DARK_TILES : LIGHT_TILES;

    const markers = useMemo(() => {
        const avail = spots.filter(isAvailable);
        if (selectedTab === "free") return avail.filter((s) => s.pricePerHour == null);
        if (selectedTab === "paid") return avail.filter((s) => s.pricePerHour != null);
        return avail;
    }, [spots, selectedTab]);

    const handleReserve = useCallback((spot: ParkingSpot) => {
        console.log("Reserve clicked for spot", spot.id);
        alert("Reservation flow will be implemented next ✅");
    }, []);

    return (
        <div className="h-full w-full relative">
            <MapContainer
                center={center}
                zoom={13}
                scrollWheelZoom={true}
                className="h-full w-full"
                zoomControl={false}
            >
                {/* When a search result exists, render the FlyTo component */}
                {searchResult && (
                    <FlyTo
                        center={[searchResult.latitude, searchResult.longitude]}
                        zoom={16}
                        onFlyEnd={onSearchResultHandled} // Pass the handler to be called on completion
                    />
                )}
                <TileLayer {...tiles} />
                <UseBounds onBounds={onBounds} />
                <MapControls />

                {userCoords && (
                    <Marker position={[userCoords.lat, userCoords.lng]} icon={UserIcon}>
                        <Popup offset={[0, -16]}>
                            Your location
                        </Popup>
                    </Marker>
                )}

                {markers.map((s) => {
                    const isPaid = s.pricePerHour != null;
                    const icon = isPaid ? DefaultIcon : FreeIcon;

                    return (
                        <Marker key={s.id} position={[s.latitude, s.longitude]} icon={icon}>
                            <Popup offset={[0, -18]}>
                                <div className="text-sm">
                                    <div className="font-medium">{s.location}</div>
                                    <div className="mt-2">
                                        Status: <span className="font-semibold text-green-600">{s.status}</span>
                                    </div>

                                    {isPaid ? (
                                        <div className="mt-1">
                                            Price: <span className="font-semibold">€{s.pricePerHour!.toFixed(2)}/hr</span>
                                        </div>
                                    ) : (
                                        <div className="mt-1">
                                            <span className="font-semibold text-green-700">Free parking</span>
                                        </div>
                                    )}

                                    {isAuthenticated && (
                                        <div className="mt-3">
                                            <button
                                                onClick={() => handleReserve(s)}
                                                className="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                                            >
                                                Reserve (10 min)
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>
        </div>
    );
}
