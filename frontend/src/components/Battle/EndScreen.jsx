export default function EndScreen({ phase, level, levelId, moveCount, onNext, onRestart, onGoSelect }) {
  const isVictory = phase === 'VICTORY';
  const endTitle = isVictory ? 'VICTORY' : 'DEFEAT';
  const endColor = isVictory ? '#63c98a' : '#e35d4f';
  const hasNext = isVictory && levelId + 1 <= 7;
  const endNote = isVictory
    ? `${level.opp} was defeated! All ${moveCount} signs landed. ${levelId + 1 <= 7 ? 'Level ' + (levelId + 1) + ' is now open.' : 'That is the last level for now.'}`
    : 'HP reached 0. PP and slots reset on restart; completion history and per-sign attempt counts are kept.';

  return (
    <div style={{ position: 'absolute', inset: 0, background: 'rgba(8,16,20,.92)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '2cqw' }}>
      <div style={{ fontSize: '5cqw', color: endColor }}>{endTitle}</div>
      <div style={{ fontSize: '1.8cqw', color: '#9fb3ba', fontFamily: "'IBM Plex Mono',monospace", textAlign: 'center', maxWidth: '70%' }}>{endNote}</div>
      <div style={{ display: 'flex', gap: '1.4cqw' }}>
        {hasNext && (
          <button onClick={onNext} style={{ fontFamily: "'Silkscreen',monospace", fontSize: '2cqw', padding: '1.4cqw 2.6cqw', background: '#63c98a', border: 'none', color: '#12261c', cursor: 'pointer' }}>
            LEVEL {levelId + 1} ▶
          </button>
        )}
        <button onClick={onRestart} style={{ fontFamily: "'Silkscreen',monospace", fontSize: '2cqw', padding: '1.4cqw 2.6cqw', background: '#e0a13b', border: 'none', color: '#151f24', cursor: 'pointer' }}>RESTART</button>
        <button onClick={onGoSelect} style={{ fontFamily: "'Silkscreen',monospace", fontSize: '2cqw', padding: '1.4cqw 2.6cqw', background: 'transparent', border: '1px solid #3f565f', color: '#9fb3ba', cursor: 'pointer' }}>LEVELS</button>
      </div>
    </div>
  );
}
