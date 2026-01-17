/**
 * normalizeSpot.ts - API Response Normalizer
 *
 * Converts raw API/WebSocket parking spot data into a typed ParkingSpot object.
 * Handles various field naming conventions (camelCase vs snake_case).
 */

import type { ParkingSpot } from "../types/parking";

/** Accepts whatever the API/WS sends and returns a typed ParkingSpot */
export function normalizeSpot(raw: any): ParkingSpot {
    const price =
        raw.pricePerHour ?? raw.price_per_hour ?? null;

    return {
        id: Number(raw.id),
        latitude: Number(raw.latitude),
        longitude: Number(raw.longitude),
        location: String(raw.location ?? ""),
        status: String(raw.status ?? "Available"),
        last_updated: raw.last_updated ?? raw.lastUpdated ?? null,
        pricePerHour: price !== null && price !== undefined ? Number(price) : null,
    };
}
