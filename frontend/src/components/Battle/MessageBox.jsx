export default function MessageBox({ typed, msgDone, onSkip }) {
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: '26%', background: '#8f92ad', padding: '.7%' }}>
      <div onClick={onSkip} style={{ height: '100%', background: '#f7f3e3', border: '5px solid #cd5b45', outline: '2px solid #3a3f4b', display: 'flex', alignItems: 'center', padding: '0 3%', position: 'relative', cursor: 'pointer' }}>
        <span style={{ fontSize: '3cqw', color: '#3a3f4b', lineHeight: 1.5 }}>{typed}</span>
        {msgDone && (
          <span style={{ position: 'absolute', right: '3%', bottom: '14%', fontSize: '2.4cqw', color: '#cd5b45', animation: 'sb-blink 1s steps(1) infinite' }}>▼</span>
        )}
      </div>
    </div>
  );
}
