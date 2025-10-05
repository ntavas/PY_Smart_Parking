import { useEffect, useMemo, useRef, useState } from "react";
import type { ParkingSpot } from "../types/parking";
import { normalizeSpot } from "../utils/normalizeSpot.ts";

// type SpotStatus = ParkingSpot["status"];
// const VALID_STATUSES = ["Available", "Occupied", "Reserved", "Maintenance"] as const;
//
// function asSpotStatus(x: unknown): SpotStatus | null {
//     return typeof x === "string" && (VALID_STATUSES as readonly string[]).includes(x as string)
//         ? (x as SpotStatus)
//         : null;
// }

function wsUrlFromApiBase(apiBase: string): string {
    const u = new URL(apiBase);
    u.pathname = "/ws";
    u.protocol = u.protocol === "https:" ? "wss:" : "ws:";
    return u.toString();
}

export function useLiveSpots(apiBase = "http://localhost:8000/api") {
    const [spots, setSpots] = useState<ParkingSpot[]>([]);
    const wsRef = useRef<WebSocket | null>(null);
    const retryRef = useRef(0);
    const wsUrl = useMemo(() => wsUrlFromApiBase(apiBase), [apiBase]);

    useEffect(() => {
        let cancelled = false;

        const fetchInitial = async () => {
            const res = await fetch(`${apiBase}/parking/spots`);
            if (!res.ok) return;
            const data: ParkingSpot[] = await res.json();
            if (!cancelled) setSpots(data);
        };

        const connect = () => {
            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => { retryRef.current = 0; };
            ws.onmessage = (ev) => {
                const msg = JSON.parse(ev.data);

                if (msg.type === "spot_update" && msg.spot) {
                    const spot = normalizeSpot(msg.spot);
                    setSpots((prev) => {
                        const idx = prev.findIndex((s) => s.id === spot.id);
                        if (idx === -1) return [...prev, spot];
                        const copy = prev.slice();
                        copy[idx] = { ...copy[idx], ...spot };
                        return copy;
                    });
                }

                if (msg.type === "spot_patch" && msg.spot) {
                    const partial = normalizeSpot({ ...msg.spot });
                    setSpots((prev) => {
                        const idx = prev.findIndex((s) => s.id === partial.id);
                        if (idx === -1) return prev;
                        const copy = prev.slice();
                        copy[idx] = { ...copy[idx], ...partial };
                        return copy;
                    });
                }
            };
            ws.onerror = () => {};
            ws.onclose = () => {
                if (cancelled) return;
                const delay = Math.min(30000, 1000 * Math.pow(2, retryRef.current++));
                setTimeout(connect, delay);
            };
        };

        fetchInitial();
        connect();
        return () => { cancelled = true; wsRef.current?.close(); };
    }, [apiBase, wsUrl]);

    return { spots };
}
