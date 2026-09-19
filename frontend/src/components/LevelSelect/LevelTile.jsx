export default function LevelTile({ level, locked, palette, scale = 1, onOpen }) {
  const [color, shade] = palette;
  const image = level.opponentPokemon && level.opponentPokemon.image;
  return (
    <button
      onClick={() => !locked && onOpen(level.id)}
      disabled={locked}
      style={{
        background: 'none', border: 'none', padding: 0, width: '100%', height: '100%',
        minHeight: 0, display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'flex-end', gap: 8,
        cursor: locked ? 'not-allowed' : 'pointer',
        filter: locked ? 'grayscale(.6) brightness(.85) opacity(.75)' : 'none',
      }}
    >
      <div style={{ position: 'relative', flex: 1, minHeight: 0, aspectRatio: '1/1', maxWidth: image ? 208 : 104, maxHeight: image ? 208 : 104, alignSelf: 'center' }}>
        {image ? (
          <img src={image} alt={level.opponentPokemon.species} style={{ width: `${scale * 100}%`, height: `${scale * 100}%`, margin: 'auto', display: 'block', position: 'absolute', inset: 0, objectFit: 'contain', imageRendering: 'pixelated' }} />
        ) : (
          <>
            <div style={{ position: 'absolute', left: '14%', top: '6%', width: '20%', height: '26%', background: shade }} />
            <div style={{ position: 'absolute', right: '14%', top: '6%', width: '20%', height: '26%', background: shade }} />
            <div style={{ position: 'absolute', left: '8%', bottom: '4%', width: '84%', height: '74%', borderRadius: '46%', background: color, boxShadow: `inset 0 -14px 0 0 ${shade}` }} />
            <div style={{ position: 'absolute', right: '-4%', bottom: '26%', width: '22%', height: '22%', borderRadius: '50%', background: shade }} />
            <div style={{ position: 'absolute', left: 0, right: 0, bottom: '24%', textAlign: 'center', fontFamily: "'Silkscreen',monospace", fontSize: 26, color: 'rgba(255,255,255,.85)' }}>?</div>
          </>
        )}
      </div>
      <span style={{ fontFamily: "'Silkscreen',monospace", fontSize: 13, letterSpacing: '.05em', textShadow: '0 1px 0 rgba(255,255,255,.5)', color: locked ? '#2b3a3f' : '#12323f' }}>
        {level.name}
      </span>
    </button>
  );
}
