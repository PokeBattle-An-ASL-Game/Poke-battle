// Must match the backend's Config.FRAME_COUNT (backend/app/config.py, POOKIE_FRAME_COUNT).
// Priyanka's 25 vs 48 vs 64 comparison on the WLASL model favored 64.
export const FRAME_COUNT = 64;

// 64 frames * 40ms ~= 2.56s, inside the backend's [MIN_SEQUENCE_SPAN_MS, MAX_SEQUENCE_SPAN_MS] (1000-5000ms).
export const CAPTURE_INTERVAL_MS = 40;

export const CAPTURE_WIDTH = 640;
export const CAPTURE_HEIGHT = 480;
export const JPEG_QUALITY = 0.75;

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';
