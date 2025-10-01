import { useEffect, useState } from 'react';

type Coords = { lat: number; lng: number };

export function useGeolocation() {
    const [coords, setCoords] = useState<Coords | null>(null);

    useEffect(() => {
        if (!('geolocation' in navigator)) return;

        // Comment: Request once on load. We keep it simple—no watchPosition yet.
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
            },
            // On denial/error we stay null; UI will show "—" for nearest.
            () => setCoords(null),
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
    }, []);

    return { coords };
}
