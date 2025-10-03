import { MapContainer, Marker, Popup, TileLayer, useMap, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L, { type LatLngExpression } from "leaflet";
import type { ParkingSpot } from "../types/parking";
import { isAvailable } from "../types/parking";
import { useEffect } from "react";

const DefaultIcon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

const LIGHT_TILES = {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap contributors",
};

const DARK_TILES = {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
        'contributors &copy; <a href="https://carto.com/attribution">CARTO</a>',
    subdomains: ["a", "b", "c", "d"] as const,
};

export type Bounds = { swLat: number; swLng: number; neLat: number; neLng: number };

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
            <button className="bg-white rounded shadow p-2" onClick={() => map.zoomIn()} aria-label="Zoom in">+</button>
            <button className="bg-white rounded shadow p-2" onClick={() => map.zoomOut()} aria-label="Zoom out">−</button>
            <button className="bg-white rounded shadow p-2" onClick={() => map.locate({ setView: true, maxZoom: 16 })} aria-label="Locate">📍</button>
        </div>
    );
}

type Props = {
    userCoords?: { lat: number; lng: number };
    spots: ParkingSpot[];
    onBounds: (b: Bounds) => void;
    isDark?: boolean;
};

export default function MapView({ userCoords, spots, onBounds, isDark = false }: Props) {
    const center: LatLngExpression = userCoords ? [userCoords.lat, userCoords.lng] : [37.9838, 23.7275];
    const tiles = isDark ? DARK_TILES : LIGHT_TILES;

    return (
        <div className="h-full w-full relative">
            <MapContainer center={center} zoom={13} scrollWheelZoom className="h-full w-full" zoomControl={false}>
                <TileLayer url={tiles.url} attribution={tiles.attribution} />
                <UseBounds onBounds={onBounds} />

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
                            </div>
                        </Popup>
                    </Marker>
                ))}

                <MapControls />
            </MapContainer>
        </div>
    );
}
