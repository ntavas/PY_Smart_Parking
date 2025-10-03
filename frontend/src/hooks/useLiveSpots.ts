import { useEffect, useMemo, useRef, useState } from "react";
import type { ParkingSpot } from "../types/parking";

type SpotStatus = ParkingSpot["status"];
const VALID_STATUSES = ["Available", "Occupied", "Reserved", "Maintenance"] as const;
function asSpotStatus(x: unknown): SpotStatus | null {
    return typeof x === "string" && (VALID_STATUSES as readonly string[]).includes(x as string)
        ? (x as SpotStatus)
        : null;
}

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
                try {
                    const msg = JSON.parse(ev.data);
                    if (msg?.type === "spot_update") {
                        const id = Number(msg.spot_id);
                        const next = asSpotStatus(msg.status);
                        if (!Number.isFinite(id) || !next) return;

                        setSpots((prev) => {
                            const idx = prev.findIndex((s) => s.id === id);
                            if (idx >= 0) {
                                const copy = [...prev];
                                copy[idx] = { ...copy[idx], status: next } as ParkingSpot;
                                return copy;
                            } else {
                                fetch(`${apiBase}/parking/spots/${id}`)
                                    .then((r) => (r.ok ? r.json() : null))
                                    .then((spot: ParkingSpot | null) => {
                                        if (!spot) return;
                                        setSpots((cur) => (cur.some((x) => x.id === spot.id) ? cur : [...cur, spot]));
                                    })
                                    .catch(() => {});
                                return prev;
                            }
                        });
                    }
                } catch {}
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
