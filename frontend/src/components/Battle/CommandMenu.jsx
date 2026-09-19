export default function CommandMenu({ cmdIndex, onFight, onRun, onHint, onHover }) {
  const caret = (i) => (cmdIndex === i ? '#cd5b45' : 'transparent');
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: '26%', background: '#8f92ad', padding: '.7%', display: 'flex', gap: '.7%' }}>
      <div style={{ flex: 1.45, background: '#f7f3e3', border: '5px solid #cd5b45', outline: '2px solid #3a3f4b', display: 'flex', alignItems: 'center', padding: '0 3%' }}>
        <span style={{ fontSize: '3cqw', color: '#3a3f4b', lineHeight: 1.5 }}>What will<br />SIGNER do?</span>
      </div>
      <div style={{ flex: 1, background: '#fbfbf7', border: '3px solid #3a3f4b', outline: '2px solid #fbfbf7', display: 'grid', gridTemplateColumns: '1fr 1fr', alignContent: 'center', padding: '0 3%' }}>
        <button onClick={onFight} onMouseEnter={() => onHover(0)} style={{ background: 'none', border: 'none', fontFamily: "'Silkscreen',monospace", fontSize: '2.6cqw', color: '#3a3f4b', display: 'flex', alignItems: 'center', gap: '1cqw', cursor: 'pointer', padding: '.8cqw 0' }}>
          <span style={{ color: caret(0) }}>▶</span>FIGHT
        </button>
        <button onClick={onRun} onMouseEnter={() => onHover(1)} style={{ background: 'none', border: 'none', fontFamily: "'Silkscreen',monospace", fontSize: '2.6cqw', color: '#3a3f4b', display: 'flex', alignItems: 'center', gap: '1cqw', cursor: 'pointer', padding: '.8cqw 0', justifyContent: 'flex-end' }}>
          <span style={{ color: caret(1) }}>▶</span>RUN
        </button>
        <button onClick={onHint} onMouseEnter={() => onHover(2)} style={{ background: 'none', border: 'none', fontFamily: "'Silkscreen',monospace", fontSize: '2.6cqw', color: '#3a3f4b', display: 'flex', alignItems: 'center', gap: '1cqw', cursor: 'pointer', padding: '.8cqw 0' }}>
          <span style={{ color: caret(2) }}>▶</span>HINT
        </button>
      </div>
    </div>
  );
}
