import { useEffect, useRef, useState } from 'react';
import { CAPTURE_HEIGHT, CAPTURE_INTERVAL_MS, CAPTURE_WIDTH, FRAME_COUNT, JPEG_QUALITY } from '../../constants/capture.js';

function captureFrame(video, canvas) {
  canvas.width = CAPTURE_WIDTH;
  canvas.height = CAPTURE_HEIGHT;
  const videoWidth = video.videoWidth || CAPTURE_WIDTH;
  const videoHeight = video.videoHeight || CAPTURE_HEIGHT;
  const scale = Math.min(videoWidth / CAPTURE_WIDTH, videoHeight / CAPTURE_HEIGHT);
  const cropWidth = CAPTURE_WIDTH * scale;
  const cropHeight = CAPTURE_HEIGHT * scale;
  canvas.getContext('2d').drawImage(
    video,
    (videoWidth - cropWidth) / 2, (videoHeight - cropHeight) / 2, cropWidth, cropHeight,
    0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT,
  );
  return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY));
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function PokeballSpinner() {
  return (
    <div style={{
      width: '4.4cqw', height: '4.4cqw', borderRadius: '50%',
      background: '#f4ead6', border: '.3cqw solid #151f24', position: 'relative',
      overflow: 'hidden', animation: 'sb-pokeball-spin .8s linear infinite', flex: 'none',
    }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '50%', background: '#e35d4f', borderBottom: '.3cqw solid #151f24' }} />
      <div style={{
        position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)',
        width: '1.4cqw', height: '1.4cqw', borderRadius: '50%', background: '#f4ead6', border: '.3cqw solid #151f24',
      }} />
    </div>
  );
}

const COUNTDOWN_START = 3;
const COUNTDOWN_STEP_MS = 700;

export default function CaptureOverlay({ state, selectedWord, onSubmit, onCancel, setRecording, setFrameProgress }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [countdown, setCountdown] = useState(null);

  useEffect(() => {
    let cancelled = false;
    navigator.mediaDevices?.getUserMedia({ video: { width: CAPTURE_WIDTH, height: CAPTURE_HEIGHT }, audio: false })
      .then((stream) => {
        if (cancelled) { stream.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
        setCameraReady(true);
      })
      .catch((err) => setCameraError(err?.message || 'Camera access was denied.'));
    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    };
  }, []);

  // Auto-starts a 3-2-1 countdown as soon as the camera is ready — no manual
  // record button; a failed camera still needs a way out, so that keeps CANCEL.
  useEffect(() => {
    if (!cameraReady || state.phase !== 'CAPTURE' || state.recording || countdown !== null) return;
    setCountdown(COUNTDOWN_START);
  }, [cameraReady, state.phase, state.recording, countdown]);

  useEffect(() => {
    if (countdown === null) return;
    if (countdown === 0) {
      setCountdown(null);
      handleRecord();
      return;
    }
    const t = setTimeout(() => setCountdown((c) => c - 1), COUNTDOWN_STEP_MS);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [countdown]);

  const handleRecord = async () => {
    if (!cameraReady || !videoRef.current || !canvasRef.current) return;
    setRecording(true);
    const frames = [];
    const timestampsMs = [];
    const startedAt = performance.now();
    for (let i = 0; i < FRAME_COUNT; i += 1) {
      const blob = await captureFrame(videoRef.current, canvasRef.current);
      frames.push(blob);
      timestampsMs.push(Math.round(performance.now() - startedAt));
      setFrameProgress(frames.length);
      if (i < FRAME_COUNT - 1) await delay(CAPTURE_INTERVAL_MS);
    }
    setRecording(false);
    onSubmit(frames, timestampsMs);
  };

  const framePct = Math.min(100, (state.frames / FRAME_COUNT) * 100);
  const isLoading = state.phase === 'SUBMITTING';
  const captureLabel = isLoading ? 'CATCHING YOUR SIGN…' : Math.round(framePct) + '%';
  // No manual record button — recording starts itself once the countdown hits
  // zero. A failed camera can't count down, so CANCEL stays as the way out.
  const canCancel = state.phase === 'CAPTURE' && !state.recording && !!cameraError;

  return (
    <div style={{ position: 'absolute', inset: 0, background: 'rgba(8,16,20,.9)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1.6cqw', padding: '3%' }}>
      <div style={{ fontSize: '2cqw', color: '#8fa1a8', letterSpacing: '.1em' }}>SIGN THE WORD</div>
      <div style={{ fontSize: '5cqw', color: '#f4ead6' }}>{selectedWord}</div>
      <div style={{ width: '40%', aspectRatio: '4/3', border: '2px dashed #3f565f', background: '#0d171b', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
        <video ref={videoRef} autoPlay muted playsInline style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)', display: cameraReady ? 'block' : 'none' }} />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        {!cameraReady && !cameraError && (
          <span style={{ fontSize: '1.6cqw', color: '#6f8188', fontFamily: "'IBM Plex Mono',monospace" }}>requesting camera…</span>
        )}
        {cameraError && (
          <span style={{ fontSize: '1.4cqw', color: '#e35d4f', fontFamily: "'IBM Plex Mono',monospace", padding: '0 8%', textAlign: 'center' }}>{cameraError}</span>
        )}
        {state.recording && (
          <span style={{ position: 'absolute', top: '6%', left: '6%', fontSize: '1.6cqw', color: '#e35d4f', animation: 'sb-rec 1s steps(1) infinite' }}>● REC</span>
        )}
        {countdown !== null && countdown > 0 && (
          <div key={countdown} style={{ position: 'absolute', inset: 0, background: 'rgba(8,16,20,.45)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ fontFamily: "'Silkscreen',monospace", fontSize: '9cqw', color: '#f4ead6', textShadow: '0 4px 0 rgba(0,0,0,.4)', animation: 'sb-countdown-pulse .7s ease-out' }}>{countdown}</span>
          </div>
        )}
        {isLoading && (
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(8,16,20,.95)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1cqw' }}>
            <PokeballSpinner />
            <span style={{ fontFamily: "'Silkscreen',monospace", fontSize: '1.4cqw', letterSpacing: '.08em', color: '#e0a13b' }}>{captureLabel}</span>
          </div>
        )}
      </div>
      {!isLoading && (
        <>
          <div style={{ width: '40%', height: '1.2cqw', background: '#1c2a31' }}>
            <div style={{ height: '100%', background: '#e0a13b', transition: 'width .1s linear', width: framePct + '%' }} />
          </div>
          <div style={{ fontSize: '1.5cqw', color: '#8fa1a8', fontFamily: "'IBM Plex Mono',monospace" }}>{captureLabel}</div>
        </>
      )}
      {canCancel && (
        <button onClick={onCancel} style={{ fontFamily: "'Silkscreen',monospace", fontSize: '1.9cqw', padding: '1.2cqw 2.4cqw', background: 'transparent', border: '1px solid #3f565f', color: '#9fb3ba', cursor: 'pointer' }}>CANCEL</button>
      )}
    </div>
  );
}
