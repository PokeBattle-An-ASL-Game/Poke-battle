export function OpponentSprite({ label, anim, opacity }) {
  return (
    <div style={{ position: 'absolute', right: '9%', top: '8%', width: '19%', animation: anim }}>
      <div style={{ aspectRatio: '1/1', background: 'repeating-linear-gradient(135deg,#9fb6c4 0 9px,#8aa4b4 9px 18px)', border: '2px solid #4c6472', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', flexDirection: 'column', fontSize: '2.1cqw', color: '#26343d', padding: '4%', opacity }}>
        {label}<br /><span style={{ fontSize: '1.5cqw', color: '#3c5260' }}>art placeholder</span>
      </div>
    </div>
  );
}

export function PlayerSprite({ anim, opacity }) {
  return (
    <div style={{ position: 'absolute', left: '8%', bottom: '35.5%', width: '20%', animation: anim }}>
      <div style={{ aspectRatio: '1/1', background: 'repeating-linear-gradient(135deg,#c7b48c 0 9px,#b8a57d 9px 18px)', border: '2px solid #6a5c3d', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', flexDirection: 'column', fontSize: '2.1cqw', color: '#332b18', padding: '4%', opacity }}>
        SIGNER<br /><span style={{ fontSize: '1.5cqw', color: '#4d411f' }}>you</span>
      </div>
    </div>
  );
}

function Ball({ side }) {
  const isRight = side === 'right';
  return (
    <div style={{
      position: 'absolute',
      [isRight ? 'right' : 'left']: isRight ? '16%' : '14%',
      [isRight ? 'top' : 'bottom']: isRight ? '40%' : '36.5%',
      width: isRight ? 30 : 34, height: isRight ? 30 : 34,
      pointerEvents: 'none',
      animation: isRight ? 'sb-ball-r .7s cubic-bezier(.4,0,.6,1) forwards' : 'sb-ball .7s cubic-bezier(.4,0,.6,1) forwards',
    }}>
      <div style={{ position: 'relative', width: '100%', height: '100%', borderRadius: '50%', overflow: 'hidden', background: '#f7f3e3', border: '3px solid #2b3a3f', boxSizing: 'border-box' }}>
        <div style={{ position: 'absolute', left: 0, right: 0, top: 0, height: '46%', background: isRight ? '#5e7ca6' : '#cd5b45' }} />
        <div style={{ position: 'absolute', left: 0, right: 0, top: '46%', height: '16%', background: '#2b3a3f' }} />
        <div style={{ position: 'absolute', left: '50%', top: '50%', width: isRight ? 10 : 11, height: isRight ? 10 : 11, margin: isRight ? '-5px 0 0 -5px' : '-5.5px 0 0 -5.5px', borderRadius: '50%', background: '#f7f3e3', border: '2px solid #2b3a3f', boxSizing: 'border-box' }} />
      </div>
    </div>
  );
}

function Burst({ side }) {
  const isRight = side === 'right';
  return (
    <div style={{
      position: 'absolute',
      [isRight ? 'right' : 'left']: isRight ? '15%' : '13%',
      [isRight ? 'top' : 'bottom']: isRight ? '36%' : '33.5%',
      width: isRight ? 64 : 72, height: isRight ? 64 : 72,
      borderRadius: '50%', background: 'radial-gradient(#fff 40%,rgba(255,255,255,0) 70%)',
      pointerEvents: 'none', animation: 'sb-burst .45s ease-out forwards',
    }} />
  );
}

export function EntranceEffects({ oppEnter, entering }) {
  return (
    <>
      {oppEnter === 'ball' && <Ball side="right" />}
      {oppEnter === 'burst' && <Burst side="right" />}
      {entering === 'ball' && <Ball side="left" />}
      {entering === 'burst' && <Burst side="left" />}
    </>
  );
}
