// Single shared music channel — starting a new track stops whatever was playing.
// playMusic is idempotent per track: calling it again for the track that's
// already current (e.g. from a React effect firing more than once) reuses
// the same element instead of spawning a second one that never gets paused.
let current = null;
let currentSrc = null;
let pending = null;

function unlock() {
  // Only ever resume the track that's still current — a click can arrive long
  // after a stale `pending` was left over from a track we've since switched
  // away from, and resuming that would play two tracks at once.
  if (pending && pending === current) {
    const audio = pending;
    pending = null;
    audio.play().catch(() => { /* still blocked — will retry on next interaction */ });
  } else {
    pending = null;
  }
}

if (typeof window !== 'undefined') {
  // Capture phase + several event types: some UI layers stop bubble-phase
  // events before they'd otherwise reach window, and different input methods
  // (mouse, touch, keyboard) fire different first events.
  const opts = { capture: true, passive: true };
  window.addEventListener('pointerdown', unlock, opts);
  window.addEventListener('touchstart', unlock, opts);
  window.addEventListener('mousedown', unlock, opts);
  window.addEventListener('keydown', unlock, opts);
}

export function playMusic(src, { loop = true, volume = 0.4 } = {}) {
  const resolved = encodeURI(src);

  if (current && currentSrc === resolved) {
    pending = null;
    if (current.paused) {
      current.play().catch(() => { pending = current; });
    }
    return current;
  }

  if (current) {
    current.pause();
    current.currentTime = 0;
  }
  const audio = new Audio(resolved);
  audio.loop = loop;
  audio.volume = volume;
  current = audio;
  currentSrc = resolved;
  pending = null;
  audio.play().catch(() => { pending = audio; });
  return audio;
}

export function stopMusic() {
  if (current) {
    current.pause();
    current.currentTime = 0;
    current = null;
    currentSrc = null;
  }
  pending = null;
}
