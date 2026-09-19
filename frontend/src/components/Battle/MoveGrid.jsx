const DIFF_COLOR = { easy: '#2f8f5b', medium: '#b4852a', hard: '#c0392b' };

export default function MoveGrid({ state, byId, moves, onPick, onBack }) {
  const slots = state.slotIds.map((id, i) => {
    const m = id ? byId[id] : null;
    const spent = id ? state.used.indexOf(id) >= 0 : true;
    return {
      key: i,
      label: m ? m.word : '—',
      tag: m ? (spent ? 'PP0' : 'PP1') : '',
      dotColor: m ? (spent ? '#8a8f9c' : DIFF_COLOR[m.difficulty]) : '#8a8f9c',
      disabled: !m || spent || state.phase !== 'CHOOSE_MOVE',
      opacity: m ? (spent ? .45 : 1) : .35,
      border: m ? '#3a3f4b' : '#cfd0d8',
      anim: state.refillSlot === i ? 'sb-slotin .35s ease-out' : 'none',
      pick: () => { if (m && !spent) onPick(id); },
    };
  });

  const remainingDamage = moves
    .filter((m) => state.used.indexOf(m.id) < 0)
    .reduce((a, b) => a + b.damage, 0);

  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: '30%', background: '#8f92ad', padding: '.7%', display: 'flex', gap: '.7%' }}>
      <div style={{ flex: 2.2, background: '#fbfbf7', border: '3px solid #3a3f4b', padding: '1.4%', display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: '1.2%' }}>
        {slots.map((s) => (
          <button
            key={s.key}
            onClick={s.pick}
            disabled={s.disabled}
            style={{
              border: `2px solid ${s.border}`, color: '#3a3f4b', fontFamily: "'Silkscreen',monospace",
              fontSize: '2.4cqw', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '0 3%', cursor: 'pointer', textAlign: 'left', animation: s.anim,
              opacity: s.opacity, background: '#fbfbf7',
            }}
          >
            <span>{s.label}</span>
            <span style={{ fontSize: '1.7cqw', color: s.dotColor }}>{s.tag}</span>
          </button>
        ))}
      </div>
      <div style={{ flex: 1, background: '#f7f3e3', border: '3px solid #3a3f4b', padding: '1.6%', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '.7cqw', color: '#3a3f4b' }}>
        <div style={{ fontSize: '1.9cqw', opacity: .8 }}>PP 1/1</div>
        <div style={{ fontSize: '1.9cqw' }}>DMG {remainingDamage}</div>
        <div style={{ fontSize: '1.6cqw', opacity: .8 }}>remaining damage</div>
        <button onClick={onBack} style={{ marginTop: '.6cqw', alignSelf: 'flex-start', background: 'none', border: 'none', fontFamily: "'Silkscreen',monospace", fontSize: '1.7cqw', color: '#cd5b45', cursor: 'pointer', padding: 0 }}>◀ BACK</button>
      </div>
    </div>
  );
}
