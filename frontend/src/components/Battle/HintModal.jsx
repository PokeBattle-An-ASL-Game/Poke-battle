export default function HintModal({ level, palette, moves, onClose }) {
  return (
    <div onClick={onClose} style={{ position: 'absolute', inset: 0, zIndex: 9, background: 'rgba(8,16,20,.62)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, fontFamily: "'IBM Plex Mono',monospace" }}>
      <div onClick={(e) => e.stopPropagation()} style={{ width: 'min(560px,96%)', maxHeight: '100%', overflow: 'auto', background: '#f7f3e3', border: '3px solid #3a3f4b', boxShadow: '7px 7px 0 rgba(20,32,36,.5)', display: 'flex', flexDirection: 'column', cursor: 'default' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '11px 14px', background: palette[0], borderBottom: '3px solid #3a3f4b' }}>
          <div style={{ fontFamily: "'Silkscreen',monospace", fontSize: 15, color: '#fff', textShadow: '0 2px 0 rgba(0,0,0,.28)' }}>HOW TO SIGN</div>
          <div style={{ fontSize: 11, letterSpacing: '.1em', color: 'rgba(255,255,255,.92)' }}>{level.name.toUpperCase()}</div>
          <button onClick={onClose} style={{ marginLeft: 'auto', fontFamily: "'Silkscreen',monospace", fontSize: 13, width: 26, height: 26, background: 'rgba(0,0,0,.22)', border: '2px solid rgba(255,255,255,.75)', color: '#fff', cursor: 'pointer' }}>×</button>
        </div>
        <div style={{ padding: 14, display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(130px,1fr))', gap: 10 }}>
          {moves.map((m) => (
            <div key={m.id} style={{ border: '2px solid #d8cbac', background: '#fbf8ee', padding: 7, display: 'flex', flexDirection: 'column', gap: 6 }}>
              <div style={{ height: 104, background: 'repeating-linear-gradient(135deg,#eee3c9 0 8px,#e6d9b8 8px 16px)', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: '#8a7a55', fontSize: 11, padding: 6 }}>
                photo of {m.word}
              </div>
              <div style={{ fontFamily: "'Silkscreen',monospace", fontSize: 11, color: '#3a3f4b' }}>{m.word}</div>
              <div style={{ fontSize: 10.5, color: '#6d7a80' }}>{m.difficulty} · {m.damage} dmg</div>
            </div>
          ))}
        </div>
        <div style={{ padding: '0 14px 14px', fontSize: 11, color: '#6d7a80' }}>Drop a reference photo onto any frame to keep your own cue for that sign.</div>
      </div>
    </div>
  );
}
