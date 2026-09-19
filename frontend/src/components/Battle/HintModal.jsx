export default function HintModal({ level, palette, moves, onClose }) {
  return (
    <div onClick={onClose} style={{ position: 'absolute', inset: 0, zIndex: 9, background: 'rgba(8,16,20,.62)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, fontFamily: "'IBM Plex Mono',monospace" }}>
      <div onClick={(e) => e.stopPropagation()} style={{ width: 'min(880px,96%)', maxHeight: '92%', overflow: 'auto', background: '#f7f3e3', border: '3px solid #3a3f4b', boxShadow: '9px 9px 0 rgba(20,32,36,.5)', display: 'flex', flexDirection: 'column', cursor: 'default' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '16px 20px', background: palette[0], borderBottom: '3px solid #3a3f4b' }}>
          <div style={{ fontFamily: "'Silkscreen',monospace", fontSize: 21, color: '#fff', textShadow: '0 2px 0 rgba(0,0,0,.28)' }}>HOW TO SIGN</div>
          <div style={{ fontSize: 14, letterSpacing: '.1em', color: 'rgba(255,255,255,.92)' }}>{level.name.toUpperCase()}</div>
          <button onClick={onClose} style={{ marginLeft: 'auto', fontFamily: "'Silkscreen',monospace", fontSize: 17, width: 34, height: 34, background: 'rgba(0,0,0,.22)', border: '2px solid rgba(255,255,255,.75)', color: '#fff', cursor: 'pointer' }}>×</button>
        </div>
        <div style={{ padding: 20, display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(190px,1fr))', gap: 16, alignItems: 'start' }}>
          {moves.map((m) => (
            <div key={m.id} style={{ border: '2px solid #d8cbac', background: '#fbf8ee', padding: 10, display: 'flex', flexDirection: 'column', gap: 9 }}>
              <div style={{ minHeight: 90, maxHeight: 280, background: '#eee3c9', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', overflow: 'hidden' }}>
                {m.hintImage ? (
                  <img src={m.hintImage} alt={'ASL sign for ' + m.word} style={{ width: '100%', height: 'auto', maxHeight: 280, objectFit: 'contain', display: 'block' }} />
                ) : (
                  <span style={{ color: '#8a7a55', fontSize: 14, padding: 8 }}>photo of {m.word}</span>
                )}
              </div>
              <div style={{ fontFamily: "'Silkscreen',monospace", fontSize: 15, color: '#3a3f4b' }}>{m.word}</div>
              <div style={{ fontSize: 13, color: '#6d7a80' }}>{m.difficulty} · {m.damage} dmg</div>
            </div>
          ))}
        </div>
        <div style={{ padding: '0 20px 18px', fontSize: 13, color: '#6d7a80' }}>Match your hand shape and movement to the reference photo before recording.</div>
      </div>
    </div>
  );
}
