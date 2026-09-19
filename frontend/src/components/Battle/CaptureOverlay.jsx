const OUTCOMES = ['correct', 'incorrect', 'retry'];

export default function CaptureOverlay({ state, selectedWord, onStartRecording, onCancel, onSetOutcome }) {
  const framePct = Math.min(100, state.frames * 4);
  const captureLabel = state.phase === 'SUBMITTING'
    ? 'submitting… awaiting validation'
    : Math.min(25, state.frames) + ' / 25 frames · ~2.5s';
  const canRecord = state.phase === 'CAPTURE' && !state.recording;
  const canCancel = state.phase === 'CAPTURE';

  return (
    <div style={{ position: 'absolute', inset: 0, background: 'rgba(8,16,20,.9)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1.6cqw', padding: '3%' }}>
      <div style={{ fontSize: '2cqw', color: '#8fa1a8', letterSpacing: '.1em' }}>SIGN THE WORD</div>
      <div style={{ fontSize: '5cqw', color: '#f4ead6' }}>{selectedWord}</div>
      <div style={{ width: '40%', aspectRatio: '4/3', border: '2px dashed #3f565f', background: 'repeating-linear-gradient(135deg,#101b20 0 10px,#0d171b 10px 20px)', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
        <span style={{ fontSize: '1.6cqw', color: '#6f8188', fontFamily: "'IBM Plex Mono',monospace" }}>webcam preview (mirrored)</span>
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
          <button onClick={onStartRecording} style={{ fontFamily: "'Silkscreen',monospace", fontSize: '1.9cqw', padding: '1.2cqw 2.4cqw', background: '#e0a13b', border: 'none', color: '#151f24', cursor: 'pointer' }}>RECORD 25 FRAMES</button>
        )}
        {canCancel && (
          <button onClick={onCancel} style={{ fontFamily: "'Silkscreen',monospace", fontSize: '1.9cqw', padding: '1.2cqw 2.4cqw', background: 'transparent', border: '1px solid #3f565f', color: '#9fb3ba', cursor: 'pointer' }}>CANCEL</button>
        )}
      </div>
      <div style={{ display: 'flex', gap: '1cqw', alignItems: 'center', fontFamily: "'IBM Plex Mono',monospace", fontSize: '1.4cqw', color: '#6f8188' }}>
        <span>simulated model reply:</span>
        {OUTCOMES.map((o) => (
          <button
            key={o}
            onClick={() => onSetOutcome(o)}
            style={{
              fontFamily: "'IBM Plex Mono',monospace", fontSize: '1.4cqw', padding: '.6cqw 1.2cqw',
              background: 'transparent', cursor: 'pointer',
              border: `1px solid ${state.outcome === o ? '#e0a13b' : '#33454d'}`,
              color: state.outcome === o ? '#e0a13b' : '#7f9299',
            }}
          >
            {o}
          </button>
        ))}
      </div>
    </div>
  );
}
