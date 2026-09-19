import { useEffect, useRef, useState } from 'react';
import { CAPTURE_HEIGHT, CAPTURE_INTERVAL_MS, CAPTURE_WIDTH, FRAME_COUNT, JPEG_QUALITY } from '../../constants/capture.js';

function captureFrame(video, canvas) {
  canvas.width = CAPTURE_WIDTH;
  canvas.height = CAPTURE_HEIGHT;
  canvas.getContext('2d').drawImage(video, 0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT);
  return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY));
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default function CaptureOverlay({ state, selectedWord, onSubmit, onCancel, setRecording, setFrameProgress }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState('');

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
  const captureLabel = state.phase === 'SUBMITTING'
    ? 'submitting… awaiting validation'
    : Math.min(FRAME_COUNT, state.frames) + ' / ' + FRAME_COUNT + ' frames';
  const canRecord = state.phase === 'CAPTURE' && !state.recording && cameraReady;
  const canCancel = state.phase === 'CAPTURE' && !state.recording;

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
      </div>
      <div style={{ width: '40%', height: '1.2cqw', background: '#1c2a31' }}>
        <div style={{ height: '100%', background: '#e0a13b', transition: 'width .1s linear', width: framePct + '%' }} />
      </div>
      <div style={{ fontSize: '1.5cqw', color: '#8fa1a8', fontFamily: "'IBM Plex Mono',monospace" }}>{captureLabel}</div>
      <div style={{ display: 'flex', gap: '1.2cqw', alignItems: 'center' }}>
        {canRecord && (
          <button onClick={handleRecord} style={{ fontFamily: "'Silkscreen',monospace", fontSize: '1.9cqw', padding: '1.2cqw 2.4cqw', background: '#e0a13b', border: 'none', color: '#151f24', cursor: 'pointer' }}>RECORD {FRAME_COUNT} FRAMES</button>
        )}
        {canCancel && (
          <button onClick={onCancel} style={{ fontFamily: "'Silkscreen',monospace", fontSize: '1.9cqw', padding: '1.2cqw 2.4cqw', background: 'transparent', border: '1px solid #3f565f', color: '#9fb3ba', cursor: 'pointer' }}>CANCEL</button>
        )}
      </div>
    </div>
  );
}
