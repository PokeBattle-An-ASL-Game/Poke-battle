import { hpColor } from '../../game/levels.js';

export function OpponentHPBar({ name, hp, float }) {
  const pct = Math.round(hp);
  return (
    <div style={{ position: 'absolute', left: '3%', top: '9%', width: '40%', background: '#f4ead6', border: '2px solid #2b3a3f', boxShadow: '5px 5px 0 rgba(43,58,63,.45)', padding: '2.2% 2.6%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: '2.4cqw', color: '#2b3a3f' }}>
        <span>{name}</span><span style={{ fontSize: '1.9cqw' }}>Lv50</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.4cqw', marginTop: '1.4cqw' }}>
        <span style={{ fontSize: '1.8cqw', color: '#e0a13b' }}>HP</span>
        <div style={{ flex: 1, height: '1.5cqw', background: '#2b3a3f', borderRadius: '1cqw', padding: 2 }}>
          <div style={{ height: '100%', borderRadius: '1cqw', transition: 'width .5s linear', width: pct + '%', background: hpColor(pct) }} />
        </div>
      </div>
      {float && (
        <div style={{ position: 'absolute', right: '6%', top: '-10%', fontSize: '2.6cqw', color: '#c0392b', animation: 'sb-float 1s ease-out forwards' }}>{float}</div>
      )}
    </div>
  );
}

export function PlayerHPBar({ hp, float }) {
  const pct = Math.round(hp);
  return (
    <div style={{ position: 'absolute', right: '4%', bottom: '33%', width: '40%', background: '#f4ead6', border: '2px solid #2b3a3f', boxShadow: '5px 5px 0 rgba(43,58,63,.45)', padding: '1.5% 2.2%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: '2.1cqw', color: '#2b3a3f' }}>
        <span>SIGNER</span><span style={{ fontSize: '1.7cqw' }}>Lv50</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.2cqw', marginTop: '1cqw' }}>
        <span style={{ fontSize: '1.6cqw', color: '#e0a13b' }}>HP</span>
        <div style={{ flex: 1, height: '1.3cqw', background: '#2b3a3f', borderRadius: '1cqw', padding: 2 }}>
          <div style={{ height: '100%', borderRadius: '1cqw', transition: 'width .5s linear', width: pct + '%', background: hpColor(pct) }} />
        </div>
      </div>
      <div style={{ textAlign: 'right', fontSize: '1.8cqw', color: '#2b3a3f', marginTop: '.4cqw' }}>{Math.round(hp)}/100</div>
      {float && (
        <div style={{ position: 'absolute', left: '6%', top: '-12%', fontSize: '2.6cqw', color: '#c0392b', animation: 'sb-float 1s ease-out forwards' }}>{float}</div>
      )}
    </div>
  );
}
