import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L, {type LatLngExpression } from "leaflet";
import IconButton from "./ui/IconButton";
import type {ParkingSpot} from "../types/parking";
import { isAvailable } from "../types/parking";

// Fix default Leaflet marker icons when bundling
const DefaultIcon = L.icon({
    iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;


const LIGHT_TILES = {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '&copy; OpenStreetMap contributors'
};

const DARK_TILES = {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    // Carto + OSM attribution
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
        'contributors &copy; <a href="https://carto.com/attribution">CARTO</a>',
    subdomains: ["a","b","c","d"] as const
};



function MapControls() {
    const map = useMap();
    return (
        <div className="absolute right-4 bottom-4 z-[1000] flex flex-col gap-2">
            <IconButton onClick={() => map.zoomIn()} aria-label="Zoom in">
                +
            </IconButton>
            <IconButton onClick={() => map.zoomOut()} aria-label="Zoom out">
                −
            </IconButton>
            <IconButton
                onClick={() => map.locate({ setView: true, maxZoom: 16 })}
                aria-label="Locate"
            >
                📍
            </IconButton>
        </div>
    );
}

type Props = {
    userCoords?: { lat: number; lng: number };
    spots: ParkingSpot[];
    isAuthenticated: boolean;
    isDark?: boolean;
};

// …imports & DefaultIcon…

export default function MapView({ userCoords, spots, isAuthenticated, isDark = false }: Props) {
    const center: LatLngExpression = userCoords ? [userCoords.lat, userCoords.lng] : [37.9838, 23.7275];

    const tiles = isDark ? DARK_TILES : LIGHT_TILES;

    const handleNavigate = (spot: ParkingSpot) => {
        // Open Google Maps with directions
        const destination = `${spot.latitude},${spot.longitude}`;
        const url = `https://www.google.com/maps/dir/?api=1&destination=${destination}&travelmode=walking`;
        window.open(url, '_blank');
    };

    return (
        <div className="h-full w-full relative">
            <MapContainer
                center={center}
                zoom={13}
                scrollWheelZoom
                className="h-full w-full rounded-none"
                zoomControl={false}
            >
                <TileLayer
                    url={tiles.url}
                    attribution={tiles.attribution}
                />

                {userCoords && (
                    <Marker position={[userCoords.lat, userCoords.lng]}>
                        <Popup>Your location</Popup>
                    </Marker>
                )}

                {spots.filter(isAvailable).map((s) => (
                    <Marker key={s.id} position={[s.latitude, s.longitude]}>
                        <Popup>
                            <div className="text-sm">
                                <div className="font-medium">{s.location}</div>
                                <div className="mt-2">
                                    Status: <span className="font-semibold text-green-600">{s.status}</span>
                                </div>
                                <div className="mt-2 flex gap-2">
                                    {isAuthenticated ? (
                                        <>
                                            <button
                                                className="flex-1 rounded-md bg-blue-600 px-3 py-1.5 text-white text-sm hover:bg-blue-500 transition-colors"
                                                disabled
                                            >
                                                Reserve
                                            </button>
                                            <button
                                                onClick={() => handleNavigate(s)}
                                                className="flex-1 rounded-md bg-green-600 px-3 py-1.5 text-white text-sm hover:bg-green-500 transition-colors"
                                            >
                                                Navigate
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <div className="text-xs text-gray-500 dark:text-gray-400">Login to reserve</div>
                                            <button
                                                onClick={() => handleNavigate(s)}
                                                className="ml-auto rounded-md bg-green-600 px-3 py-1.5 text-white text-sm hover:bg-green-500 transition-colors"
                                            >
                                                Navigate
                                            </button>
                                        </>
                                    )}
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}

                <MapControls />
            </MapContainer>
        </div>
    );
}
