import { useEffect, useState } from 'react';

type Coords = { lat: number; lng: number };

export function useGeolocation() {
    const [coords, setCoords] = useState<Coords | null>(null);

    useEffect(() => {
        if (!('geolocation' in navigator)) return;

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
            },
            () => setCoords(null),
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
    }, []);

    return { coords };
}
