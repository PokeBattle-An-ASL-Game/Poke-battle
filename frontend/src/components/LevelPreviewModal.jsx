import { blurb, counterEvery, levelById, moveList, opponentImage, opponentName, pokemonPalette, spriteScale } from '../game/levels.js';

const TINT = { easy: '#cfe9d6', medium: '#f6e4bb', hard: '#f5d2cd' };

export default function LevelPreviewModal({ levelId, onClose, onStart }) {
  const level = levelById(levelId);
  const [color, shade] = pokemonPalette(level);
  const image = opponentImage(level);
  const scale = spriteScale(level);
  const moves = moveList(level);
  const stats = [
    { k: 'SIGNS', v: String(moves.length) },
    { k: 'TOTAL DAMAGE', v: String(moves.reduce((a, b) => a + b.damage, 0)) },
    { k: 'PP PER SIGN', v: '1' },
    { k: 'COUNTER EVERY', v: counterEvery(moves.length) + (counterEvery(moves.length) === 1 ? ' HIT' : ' HITS') },
  ];

  return (
    <div onClick={onClose} style={{ position: 'absolute', inset: 0, zIndex: 9, background: 'rgba(8,16,20,.62)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '96px 20px 24px' }}>
      <div onClick={(e) => e.stopPropagation()} style={{ width: 'min(430px,94%)', maxHeight: '100%', background: '#f4ead6', border: '3px solid #2b3a3f', boxShadow: '7px 7px 0 rgba(20,32,36,.5)', display: 'flex', flexDirection: 'column', animation: 'sb-rise .22s ease-out', cursor: 'default' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', background: color, borderBottom: '3px solid #2b3a3f' }}>
          <div style={{ position: 'relative', width: 54, height: 54, flex: 'none' }}>
            {image ? (
              <img src={image} alt={opponentName(level)} style={{ width: `${scale * 100}%`, height: `${scale * 100}%`, margin: 'auto', display: 'block', position: 'absolute', inset: 0, objectFit: 'contain', imageRendering: 'pixelated' }} />
            ) : (
              <>
                <div style={{ position: 'absolute', left: '14%', top: '6%', width: '20%', height: '26%', background: shade }} />
                <div style={{ position: 'absolute', right: '14%', top: '6%', width: '20%', height: '26%', background: shade }} />
                <div style={{ position: 'absolute', left: '8%', bottom: '4%', width: '84%', height: '74%', borderRadius: '46%', background: shade }} />
                <div style={{ position: 'absolute', left: 0, right: 0, bottom: '22%', textAlign: 'center', fontFamily: "'Silkscreen',monospace", fontSize: 17, color: 'rgba(255,255,255,.9)' }}>?</div>
              </>
            )}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 3, minWidth: 0 }}>
            <div style={{ fontFamily: "'Silkscreen',monospace", fontSize: 18, color: '#fff', textShadow: '0 2px 0 rgba(0,0,0,.28)' }}>{level.name.toUpperCase()}</div>
            <div style={{ fontFamily: "'IBM Plex Mono',monospace", fontSize: 11.5, letterSpacing: '.12em', color: 'rgba(255,255,255,.92)' }}>
              Nº {String(levelId).padStart(3, '0')} · {opponentName(level)}
            </div>
          </div>
          <button onClick={onClose} style={{ marginLeft: 'auto', flex: 'none', fontFamily: "'Silkscreen',monospace", fontSize: 13, width: 28, height: 28, background: 'rgba(0,0,0,.22)', border: '2px solid rgba(255,255,255,.75)', color: '#fff', cursor: 'pointer' }}>×</button>
        </div>

        <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 12, color: '#2b3a3f' }}>
          <div style={{ fontFamily: "'IBM Plex Mono',monospace", fontSize: 12.5, lineHeight: 1.5, color: '#3b4d53' }}>{blurb(levelId)}</div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
            <div style={{ fontFamily: "'Silkscreen',monospace", fontSize: 10.5, letterSpacing: '.14em', color: '#6d8087' }}>VOCABULARY</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {moves.map((m) => (
                <span key={m.id} style={{ fontFamily: "'Silkscreen',monospace", fontSize: 11, padding: '5px 9px', border: '2px solid #2b3a3f', background: TINT[m.difficulty], color: '#1d2a2e' }}>
                  {m.word} <span style={{ fontFamily: "'IBM Plex Mono',monospace", fontSize: 10, opacity: .72 }}>{m.damage} dmg</span>
                </span>
              ))}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 7 }}>
            {stats.map((st) => (
              <div key={st.k} style={{ border: '2px solid #cbbda0', background: '#efe3ca', padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: 3 }}>
                <span style={{ fontFamily: "'IBM Plex Mono',monospace", fontSize: 10, letterSpacing: '.1em', color: '#6d8087' }}>{st.k}</span>
                <span style={{ fontFamily: "'Silkscreen',monospace", fontSize: 14, color: '#2b3a3f' }}>{st.v}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ position: 'sticky', bottom: 0, padding: '14px 16px 16px', background: '#f4ead6', borderTop: '2px solid #ddd0b4' }}>
          <button
            onClick={() => onStart(levelId)}
            style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, fontFamily: "'Silkscreen',monospace", fontSize: 14, letterSpacing: '.08em', padding: '10px 12px', background: shade, border: '2px solid #2b3a3f', boxShadow: '0 4px 0 0 #2b3a3f', color: '#fff', cursor: 'pointer' }}
          >
            <span style={{ position: 'relative', width: 30, height: 30, flex: 'none', borderRadius: '50%', overflow: 'hidden', background: '#f4ead6', border: '2px solid #151f24', boxSizing: 'border-box' }}>
              <span style={{ position: 'absolute', left: 0, right: 0, top: 0, height: '46%', background: color }} />
              <span style={{ position: 'absolute', left: 0, right: 0, top: '46%', height: '16%', background: '#2b3a3f' }} />
              <span style={{ position: 'absolute', left: '50%', top: '50%', width: 11, height: 11, margin: '-5.5px 0 0 -5.5px', borderRadius: '50%', background: '#f4ead6', border: '2px solid #2b3a3f', boxSizing: 'border-box' }} />
            </span>
            <span>START BATTLE</span>
          </button>
        </div>
      </div>
    </div>
  );
}
